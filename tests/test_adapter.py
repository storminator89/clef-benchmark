"""Lightweight adapter safety tests, with no model import/load/download."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('clef_test_adapter',ROOT/'runtime/live_adapter.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class AdapterSafetyTests(unittest.TestCase):
    def test_construction_does_not_import_torch(self):
        before='torch' in sys.modules
        runtime=module.ClefRuntime(Path('/nonexistent-local-model'))
        self.assertEqual(runtime.status()['state'],'unloaded');self.assertEqual('torch' in sys.modules,before)
    def test_reject_bad_configuration(self):
        for arguments in [{'threads':0},{'max_length':2049}]:
            with self.assertRaises(ValueError):module.ClefRuntime(Path('.'),**arguments)
    def test_missing_model_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime=module.ClefRuntime(Path(directory))
            with self.assertRaises(ValueError):runtime._verify_files()
            self.assertEqual(runtime.status()['state'],'unloaded')
    def test_changed_file_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);(path/'sample.txt').write_bytes(b'bad')
            with patch.object(module,'EXPECTED_FILES',{'sample.txt':{'bytes':3,'sha256':hashlib.sha256(b'yes').hexdigest()}}):
                with self.assertRaisesRegex(ValueError,'checksum'):module.ClefRuntime(path)._verify_files()
    def test_failed_load_reports_error(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime=module.ClefRuntime(Path(directory))
            with self.assertRaises(ValueError):runtime._ensure_loaded()
            self.assertEqual(runtime.status()['state'],'error')
            self.assertEqual(runtime.status()['successful_requests'],0)
if __name__=='__main__':unittest.main()
