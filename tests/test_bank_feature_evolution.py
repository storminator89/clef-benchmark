"""The bank baseline remains immutable; only three exact runtime evolutions apply."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
spec = importlib.util.spec_from_file_location('bank_feature_checks', ROOT/'scripts/check_bank_support.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class BankFeatureEvolutionTests(unittest.TestCase):
    def fixture(self, root):
        (root/'provenance').mkdir()
        protected = {}
        changes = {}
        for name in (*sorted(checks.FEATURE_RUNTIME_FILES), 'runtime/run_clef.py',
                     'runtime/joint_schema_model.py', 'runtime/model_file_manifest.json',
                     'results/predictions.jsonl', 'benchmark/requests.jsonl'):
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            old = f'old {name}'.encode()
            protected[name] = hashlib.sha256(old).hexdigest()
            if name in checks.FEATURE_RUNTIME_FILES:
                path.write_bytes(f'new {name}'.encode())
                changes[name] = {'from_sha256': protected[name], 'to_sha256': checks.sha(path), 'reason': 'Explicit reviewed feature'}
            else:
                path.write_bytes(old)
        baseline = {'baseline_commit': '1b899c5900a74ad0406bd6a25ad2ab87eec2e26d', 'protected_files_sha256': protected}
        (root/'provenance/bank_support_baseline.json').write_text(json.dumps(baseline))
        record = {'schema_version': 1, 'baseline_commit': baseline['baseline_commit'],
                  'bank_release_tree': '915e65b952241d028e88b29941cb2ff9440e46d9', 'changes': changes}
        self.save(root, record)
        return record

    def save(self, root, record):
        (root/'provenance/bank_feature_evolution.json').write_text(json.dumps(record))

    def test_actual_bank_tree(self):
        self.assertEqual(checks.verify_protected_files(ROOT), (212, 3))

    def test_exact_three_runtime_changes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self.fixture(root); checks.verify_protected_files(root)

    def test_immutable_artifacts_cannot_change_or_be_exempted(self):
        for name in ('runtime/run_clef.py', 'runtime/joint_schema_model.py', 'runtime/model_file_manifest.json',
                     'results/predictions.jsonl', 'benchmark/requests.jsonl'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                root = Path(td); record = self.fixture(root)
                (root/name).write_text('mutated')
                with self.assertRaises(AssertionError): checks.verify_protected_files(root)
                record['changes'][name] = {'from_sha256': '0'*64, 'to_sha256': checks.sha(root/name), 'reason': 'attempt'}
                self.save(root, record)
                with self.assertRaises(AssertionError): checks.verify_protected_files(root)

    def test_wrong_before_after_identity_or_reason_rejected(self):
        for key in ('from_sha256', 'to_sha256', 'reason'):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as td:
                root = Path(td); record = self.fixture(root)
                record['changes']['runtime/live_adapter.py'][key] = '' if key == 'reason' else '0'*64
                self.save(root, record)
                with self.assertRaises(AssertionError): checks.verify_protected_files(root)

    def test_missing_change_or_wrong_baseline_rejected(self):
        for kind in ('missing', 'baseline', 'tree'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                root = Path(td); record = self.fixture(root)
                if kind == 'missing': del record['changes']['runtime/live_adapter.py']
                elif kind == 'baseline': record['baseline_commit'] = '0'*40
                else: record['bank_release_tree'] = '0'*40
                self.save(root, record)
                with self.assertRaises(AssertionError): checks.verify_protected_files(root)


if __name__ == '__main__': unittest.main()
