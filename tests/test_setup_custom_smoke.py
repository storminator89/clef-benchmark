"""Guard and archived-proof checks only: never run the model during tests."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('feature_smoke', ROOT/'scripts/smoke_setup_custom.py')
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


class SetupCustomSmokeTests(unittest.TestCase):
    def test_default_prepares_only(self):
        imported = 'torch' in sys.modules
        out = io.StringIO()
        with patch.object(smoke, 'run') as run, redirect_stdout(out):
            self.assertEqual(smoke.main([]), 0)
        run.assert_not_called()
        self.assertEqual(json.loads(out.getvalue())['mode'], 'prepare_only_no_inference')
        self.assertEqual('torch' in sys.modules, imported)

    def test_three_field_request_never_contains_gold(self):
        case = smoke.SUITE['cases'][0]
        wire = json.loads(smoke.custom.encode_request(case))
        self.assertEqual(set(wire), {'state', 'questions'})
        self.assertEqual(len(wire['questions']), 3)
        self.assertEqual(wire['questions'], case['questions'])
        self.assertLess(len(smoke.custom.encode_request(case)), 2000)

    def test_explicit_exclusive_runtime_and_existing_model_required(self):
        for args in (['--run'], ['--run','--confirm-exclusive-runtime']):
            with patch.object(smoke, 'run') as run, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                smoke.main(args)
            run.assert_not_called()

    def test_existing_proof_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); output = root/'old.json'; output.write_text('unchanged')
            with patch.object(smoke, 'run') as run, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                smoke.main(['--run','--confirm-exclusive-runtime','--model-dir',td,'--output',str(output)])
            run.assert_not_called(); self.assertEqual(output.read_text(), 'unchanged')

    def test_sufficient_authorization_invokes_exactly_once(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch.object(smoke, 'run', return_value=0) as run:
                self.assertEqual(smoke.main(['--run','--confirm-exclusive-runtime','--model-dir',td,'--output',str(root/'new.json')]), 0)
            run.assert_called_once_with(root, root/'new.json')

    def test_low_ram_stops_before_server(self):
        from types import SimpleNamespace
        fake = SimpleNamespace(virtual_memory=lambda: SimpleNamespace(available=1))
        with patch.dict(sys.modules, {'psutil': fake}), patch.object(smoke, 'make_server') as server, self.assertRaisesRegex(RuntimeError, '7.5 GiB'):
            smoke.run(Path('.'), Path('not-created.json'))
        server.assert_not_called()

    def test_real_proof_and_completion_are_bound_to_current_sources(self):
        proof = json.loads((ROOT/'qa/setup_custom_smoke.json').read_text())
        completion = json.loads((ROOT/'qa/setup_custom_smoke_completion.json').read_text())
        self.assertEqual(proof['status'], 'pass'); self.assertEqual(completion['status'], 'pass')
        self.assertFalse(proof['benchmark_result']); self.assertFalse(proof['benchmark_inclusion'])
        self.assertEqual(proof['custom_evaluation_report']['suite'], smoke.SUITE)
        self.assertEqual(set(proof['source_files_sha256']), set(smoke.SOURCE_FILES))
        for name, digest in proof['source_files_sha256'].items():
            self.assertEqual(smoke.digest(ROOT/name), digest, name)
        self.assertTrue(all(smoke.verify(proof['custom_evaluation_report'], proof['runtime_status'], proof['http_exchanges']).values()))
        self.assertTrue(all(proof['assertions'].values()))
        self.assertEqual(completion['evidence_sha256'], smoke.digest(ROOT/completion['evidence_file']))
        self.assertEqual(completion['process_exit_code'], 0)
        self.assertTrue(completion['model_process_exited']); self.assertTrue(completion['model_ram_released'])
        self.assertNotIn('environment', proof); self.assertNotIn('resources', proof)


if __name__ == '__main__': unittest.main()
