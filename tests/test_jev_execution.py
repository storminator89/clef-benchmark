"""Offline activation tests. All responses are mock fixtures, never model results."""
from pathlib import Path
from unittest.mock import patch
import json
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_jev_workflow as workflow

class JevExecutionTests(unittest.TestCase):
    def response(self, body):
        request = json.loads(body)
        answers = {}
        for key, q in request['questions'].items():
            choices = list(q['criteria'])
            answers[key] = {'type': 'choice', 'choice': choices[0], 'confidence': 1,
                            'probabilities': {c: int(i == 0) for i, c in enumerate(choices)}}
        return 200, json.dumps({'model': workflow.runner.MODEL, 'answers': answers,
                               'usage': {'input_tokens': 10, 'output_tokens': 1}}).encode(), None

    def test_context_rejects_push_other_repo_other_ref_and_rerun(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'storminator89/clef-benchmark',
               'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REF': 'refs/heads/main',
               'GITHUB_RUN_ATTEMPT': '1'}
        workflow.require_manual_context(env)
        for key in env:
            with self.assertRaises(workflow.runner.ContractError):
                workflow.require_manual_context({**env, key: 'unexpected'})

    def test_probe_is_first_case_same_ledger_no_duplicate(self):
        manifest, rows = workflow.runner.load_requests(workflow.BUNDLE)
        sent = []
        def transport(body):
            sent.append(body)
            return self.response(body)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'run'
            gate = workflow.FirstCaseGate(transport, out / 'connection_check.json')
            with patch.object(workflow.runner, 'load_requests', return_value=(manifest, rows[:3])):
                result = workflow.runner.run(workflow.BUNDLE, out, 3, gate, sleep=lambda _: None)
            self.assertEqual(result['completed_cases'], 3)
            self.assertEqual(result['wire_attempts_reserved'], 3)
            self.assertEqual(len(sent), 3)
            self.assertEqual(sent[0], workflow.runner.dumps(rows[0]['request']).encode())
            check = json.loads((out / 'connection_check.json').read_text())
            self.assertTrue(check['connection_valid'])
            self.assertEqual(check['extra_requests'], 0)

    def test_probe_failures_stop_after_one_and_never_persist_raw_error(self):
        manifest, rows = workflow.runner.load_requests(workflow.BUNDLE)
        for status, raw in [(401, b'PRIVATE_ECHO_TEST'), (429, b'PRIVATE_ECHO_TEST'),
                            (529, b'PRIVATE_ECHO_TEST'), (200, b'PRIVATE_ECHO_TEST')]:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as td:
                out = Path(td) / 'run'
                gate = workflow.FirstCaseGate(lambda body: (status, raw, None), out / 'connection_check.json')
                with patch.object(workflow.runner, 'load_requests', return_value=(manifest, rows[:3])):
                    result = workflow.runner.run(workflow.BUNDLE, out, 3, gate, sleep=lambda _: None)
                self.assertEqual(result['wire_attempts_reserved'], 1)
                self.assertEqual(result['completed_cases'], 0)
                self.assertEqual(result['status'], 'halted')
                self.assertFalse(json.loads((out / 'connection_check.json').read_text())['connection_valid'])
                for p in out.iterdir(): self.assertNotIn('PRIVATE_ECHO_TEST', p.read_text())

    def test_transport_exception_sanitized(self):
        with tempfile.TemporaryDirectory() as td:
            def fail(body): raise RuntimeError('PRIVATE_ECHO_TEST')
            gate = workflow.FirstCaseGate(fail, Path(td) / 'check.json')
            with self.assertRaises(workflow.runner.ContractError) as raised: gate(b'{}')
            self.assertNotIn('PRIVATE_ECHO_TEST', str(raised.exception))
            self.assertNotIn('PRIVATE_ECHO_TEST', (Path(td) / 'check.json').read_text())

    def test_dry_plan_does_not_read_credentials_or_network(self):
        with tempfile.TemporaryDirectory() as td, patch.object(workflow.runner, 'HttpTransport', side_effect=AssertionError('No network')):
            with patch.object(workflow.os, 'environ', {}):
                target = Path(td) / 'plan.json'
                self.assertEqual(workflow.main(['--output', str(target)]), 0)
                self.assertEqual(json.loads(target.read_text())['one_pass_requests'], 974)

if __name__ == '__main__': unittest.main()
