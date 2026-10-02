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


if __name__ == '__main__': unittest.main()
