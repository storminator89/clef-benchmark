"""Private custom inputs/reports/setup logs must fail public-tree admission."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('feature_public_audit', ROOT/'scripts/audit_public.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class FeaturePublicAuditTests(unittest.TestCase):
    def test_private_feature_directories_fail_even_for_innocuous_json(self):
        for folder in ('user_cases', 'user_runs', '.clef', '.venvs', '.venv-rocm', 'runtime/model-clef-27b'):
            with self.subTest(folder=folder), tempfile.TemporaryDirectory() as td:
                root = Path(td); target = root/folder/'example.json'; target.parent.mkdir(parents=True); target.write_text('{}')
                with patch.object(audit, 'ROOT', root): report, _ = audit.audit()
                self.assertEqual(report['status'], 'fail')
                self.assertIn({'path': f'{folder}/example.json', 'reason': 'excluded_baggage'}, report['findings'])

    def test_public_synthetic_custom_examples_remain_allowed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); target = root/'examples/custom_cases/example.json'; target.parent.mkdir(parents=True); target.write_text('{}')
            with patch.object(audit, 'ROOT', root): report, _ = audit.audit()
            self.assertEqual(report['status'], 'pass')


    def test_public_inventory_is_deterministic_aggregate_without_file_identifiers(self):
        rows = [{'path': 'synthetic_example.json', 'bytes': 10, 'sha256': 'a' * 64},
                {'path': 'second_example.json', 'bytes': 20, 'sha256': 'b' * 64}]
        value = audit.public_inventory_summary(rows)
        self.assertEqual(value, audit.public_inventory_summary(list(reversed(rows))))
        self.assertEqual(value['file_count'], 2); self.assertEqual(value['total_bytes'], 30)
        self.assertNotIn('files', value)
        self.assertNotIn('synthetic_example.json', str(value))
        self.assertNotIn('a' * 64, str(value))
        changed = [dict(row) for row in rows]; changed[0]['bytes'] += 1
        self.assertNotEqual(value['aggregate_sha256'], audit.public_inventory_summary(changed)['aggregate_sha256'])

    def test_public_inventory_excludes_both_self_reports_without_recursion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / 'provenance').mkdir(); (root / 'README.md').write_text('public example')
            with patch.object(audit, 'ROOT', root): _, first = audit.audit()
            for name in audit.EXCLUDED: (root / name).write_text('self-report placeholder')
            with patch.object(audit, 'ROOT', root): _, second = audit.audit()
            self.assertEqual(first, second)
            self.assertEqual(audit.public_inventory_summary(first), audit.public_inventory_summary(second))


if __name__ == '__main__': unittest.main()
