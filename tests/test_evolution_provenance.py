"""Bounded runtime evolution must not weaken immutable result protection."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('followup_checks', ROOT/'scripts/check_followups.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


class EvolutionTests(unittest.TestCase):
    def fixture(self, root):
        (root/'provenance').mkdir()
        (root/'runtime').mkdir()
        (root/'server.py').write_text('new server')
        (root/'runtime/run_clef.py').write_text('immutable runner')
        baseline = {'protected_files_sha256': {'server.py': sha('old server'),
                    'runtime/run_clef.py': sha('immutable runner')}}
        evolution = {'changes': {'server.py': {'from_sha256': sha('old server'),
                     'to_sha256': sha('new server'), 'reason': 'Bounded multi-field API'}}}
        (root/'provenance/followup_baseline.json').write_text(json.dumps(baseline))
        self.save(root, evolution)
        return evolution

    @staticmethod
    def save(root, value):
        (root/'provenance/workbench_evolution.json').write_text(json.dumps(value))

    def test_actual_protected_tree(self):
        checks.verify_protected_files(ROOT)

    def test_exact_evolution_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root);checks.verify_protected_files(root)

    def test_undeclared_runtime_change_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            (root/'runtime/run_clef.py').write_text('changed runner')
            with self.assertRaises(AssertionError):checks.verify_protected_files(root)

    def test_immutable_runner_cannot_be_exempted(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);value=self.fixture(root)
            value['changes']['runtime/run_clef.py']={'from_sha256':sha('immutable runner'),'to_sha256':sha('changed runner'),'reason':'attempt'}
            self.save(root,value)
            with self.assertRaises(AssertionError):checks.verify_protected_files(root)

    def test_wrong_baseline_or_new_hash_rejected(self):
        for field in ('from_sha256','to_sha256'):
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory);value=self.fixture(root)
                value['changes']['server.py'][field]='0'*64;self.save(root,value)
                with self.assertRaises(AssertionError):checks.verify_protected_files(root)


if __name__ == '__main__':unittest.main()
