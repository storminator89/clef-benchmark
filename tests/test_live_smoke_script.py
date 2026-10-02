"""Smoke-script guard tests. These tests never start a model or a live server."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('clef_http_smoke_script', ROOT / 'scripts/smoke_multifield_http.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LiveSmokeScriptTests(unittest.TestCase):
    def test_default_prepares_only_and_never_imports_torch_or_runs_inference(self):
        before = 'torch' in sys.modules
        stdout = io.StringIO()
        with patch.object(module, 'run_smoke') as run, redirect_stdout(stdout):
            self.assertEqual(module.main([]), 0)
        run.assert_not_called()
        result = json.loads(stdout.getvalue())
        self.assertEqual(result['mode'], 'prepare_only_no_inference')
        self.assertEqual('torch' in sys.modules, before)
        self.assertEqual(list(result['request']['questions']), ['decision', 'evidence'])
        self.assertEqual(result['body_bytes'], len(module.request_bytes()))

    def test_expected_answers_are_not_part_of_model_input(self):
        request = json.loads(module.request_bytes())
        self.assertEqual(set(request), {'state', 'questions'})
        self.assertNotIn('expected_answers', request)
        self.assertEqual(module.EXPECTED_ANSWERS, {'decision': 'nein', 'evidence': 'b1'})
        # Input fixed before the real run, independently of its eventual answer.
        self.assertEqual(hashlib.sha256(module.request_bytes()).hexdigest(),
                         'f23664ab5106e2a75e4d2283cfd04fabc2d08294e937fe756ffa3e087c25815d')

    def test_run_requires_exclusive_runtime_confirmation(self):
        with patch.object(module, 'run_smoke') as run, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            module.main(['--run'])
        run.assert_not_called()

    def test_run_requires_existing_model_directory(self):
        with patch.object(module, 'run_smoke') as run, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            module.main(['--run', '--confirm-exclusive-runtime'])
        run.assert_not_called()

    def test_never_replaces_existing_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / 'existing.json'
            output.write_text('original evidence')
            with patch.object(module, 'run_smoke') as run, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                module.main(['--run', '--confirm-exclusive-runtime', '--model-dir', str(root), '--output', str(output)])
            run.assert_not_called()
            self.assertEqual(output.read_text(), 'original evidence')

    def test_explicit_complete_configuration_invokes_once_without_real_inference(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / 'new.json'
            with patch.object(module, 'run_smoke', return_value=0) as run:
                self.assertEqual(module.main(['--run', '--confirm-exclusive-runtime', '--model-dir', str(root), '--output', str(output)]), 0)
            run.assert_called_once_with(root, output)
            self.assertFalse(output.exists())

    def test_insufficient_ram_fails_before_server_or_model(self):
        from types import SimpleNamespace
        fake_psutil = SimpleNamespace(virtual_memory=lambda: SimpleNamespace(available=1))
        with patch.dict(sys.modules, {'psutil': fake_psutil}), patch.object(module, 'make_server') as server, self.assertRaisesRegex(RuntimeError, '7.5 GiB'):
            module.run_smoke(Path('.'), Path('must-not-exist.json'))
        server.assert_not_called()


class RecordedLiveSmokeTests(unittest.TestCase):
    """Read archived real evidence only; these tests do not rerun inference."""

    def test_recorded_http_run_is_complete_real_and_excluded_from_benchmarks(self):
        evidence = json.loads((ROOT / 'qa/live_multifield_smoke.json').read_text())
        self.assertEqual(evidence['status'], 'pass')
        self.assertTrue(all(evidence['assertions'].values()))
        self.assertFalse(evidence['benchmark_inclusion'])
        self.assertEqual(evidence['request'], module.REQUEST)
        self.assertEqual(evidence['expected_answers_not_sent_to_model'], module.EXPECTED_ANSWERS)
        self.assertEqual(evidence['request_body_sha256'], hashlib.sha256(module.request_bytes()).hexdigest())
        self.assertEqual(evidence['http']['status'], 200)
        self.assertEqual(evidence['response']['source'], 'live_local_inference')
        self.assertEqual(evidence['runtime_status']['successful_requests'], 1)
        self.assertFalse(evidence['response']['truncated'])
        self.assertEqual(evidence['response']['input_tokens'], 442)
        module.validate_result(module.REQUEST, evidence['response'])
        for name, expected in module.EXPECTED_ANSWERS.items():
            self.assertEqual(evidence['response']['answers'][name]['choice'], expected)
        for name, expected in evidence['source_files_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)

    def test_process_completion_evidence_is_linked_and_ram_was_released(self):
        evidence_path = ROOT / 'qa/live_multifield_smoke.json'
        completion = json.loads((ROOT / 'qa/live_multifield_smoke_completion.json').read_text())
        self.assertEqual(completion['status'], 'pass')
        self.assertEqual(completion['smoke_evidence_sha256'], hashlib.sha256(evidence_path.read_bytes()).hexdigest())
        self.assertEqual(completion['observed_smoke_exit_code'], 0)
        self.assertEqual(completion['smoke_processes_remaining'], 0)
        self.assertGreaterEqual(completion['available_ram_after_process_exit_bytes'], 7.5 * 1024**3)
        self.assertFalse(completion['benchmark_inclusion'])


if __name__ == '__main__':
    unittest.main()
