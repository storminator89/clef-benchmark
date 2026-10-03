"""NEWREVISION offline mock tests; no provider/model observations or credentials."""
import copy
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_jev_final_continuation as c


class FinalContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests, cls.prior, cls.plan = c.prepare()

    def response(self, body, *, flagged=False):
        request = json.loads(body)
        answers = {}
        for key, question in request['questions'].items():
            options = list(question['criteria'])
            p = dict.fromkeys(options, 0)
            p[options[0]] = 0.6000000000000001
            p[options[1]] = 0.3999999999999999 if not flagged else 0.2
            answers[key] = {'type': 'choice', 'choice': options[0],
                            'confidence': 0.3212345678901234, 'probabilities': p}
        return 200, json.dumps({'model': c.runner.MODEL, 'answers': answers,
                               'usage': {'input_tokens': 10, 'output_tokens': 1}}).encode(), None

    def run_temp(self, transport, **kwargs):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / 'run'
        result = c.run(out, kwargs.pop('cap', 3), transport, sleep=lambda _: None, **kwargs)
        return out, result

    def assert_prefix(self, out):
        for name in ('attempts.jsonl', 'predictions.jsonl', 'validation_diagnostics.jsonl'):
            self.assertTrue((out / name).read_bytes().startswith(self.prior[name]))
        predictions = c.runner.rows(out / 'predictions.jsonl')
        self.assertEqual(predictions[:454], c.read_json_lines(self.prior['predictions.jsonl']))
        return predictions

    def test_exact_plan_and_no_scientific_changes(self):
        self.assertEqual(c.encoded(self.plan), c.PLAN.read_bytes())
        self.assertEqual(len(self.plan['requests']), 520)
        self.assertEqual(self.plan['requests'][0]['original_case_number'], 455)
        self.assertEqual(self.plan['requests'][-1]['original_case_number'], 974)
        self.assertEqual(c.sha(c.PLAN.read_bytes()), c.PLAN_SHA256)
        self.assertEqual(self.plan['prior_completed_cases'], 452)
        self.assertEqual(self.plan['prior_failed_cases'], 2)

    def test_full520_strict_mock_exact_order_and_unrounded_values(self):
        sent = []
        def transport(body):
            sent.append(body)
            return self.response(body)
        out, result = self.run_temp(transport)
        self.assertEqual(sent, [c.runner.dumps(r['request']).encode() for r in self.requests[454:]])
        self.assertEqual(set(p.name for p in out.iterdir()), {'run_summary.json', 'predictions.jsonl',
            'attempts.jsonl', 'validation_diagnostics.jsonl', 'connection_check.json', 'flagged_native.jsonl'})
        self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (972, 2, 0))
        self.assertEqual(result['wire_attempts_reserved'], 974)
        self.assertEqual(result['retry_attempts'], 0)
        self.assertEqual(result['current_transport_calls_started'], 520)
        self.assertEqual(result['known_success_input_tokens'], 437597 + 5200)
        self.assertEqual(result['current_flagged_native_cases'], 0)
        self.assertEqual(result['attempt_reservations_without_valid_billing'], 2)
        self.assertEqual((out / 'flagged_native.jsonl').read_bytes(), b'')
        self.assertEqual((out / 'validation_diagnostics.jsonl').read_bytes(), self.prior['validation_diagnostics.jsonl'])
        for record, body in zip(self.assert_prefix(out)[454:], sent):
            self.assertEqual(record['answers'], json.loads(self.response(body)[1])['answers'])
        gate = json.loads((out / 'connection_check.json').read_bytes())
        self.assertEqual((gate['original_case_number'], gate['connection_valid'], gate['extra_requests']), (455, True, 0))

    def test_sum_only_gate_and_all520_vectors_are_failures_not_successes(self):
        out, result = self.run_temp(lambda body: self.response(body, flagged=True))
        self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (452, 522, 0))
        self.assertEqual(result['current_flagged_native_cases'], 520)
        self.assertEqual(result['known_success_input_tokens'], 437597)
        self.assertEqual(result['flagged_native_input_tokens'], 5200)
        self.assertEqual(result['attempt_reservations_without_valid_billing'], 2)
        records = c.runner.rows(out / 'flagged_native.jsonl')
        self.assertEqual(len(records), 520)
        for record, request in zip(records, self.requests[454:]):
            body = c.runner.dumps(request['request']).encode()
            native = json.loads(self.response(body, flagged=True)[1])
            self.assertEqual(record['answers'], native['answers'])
            self.assertFalse(record['strict_scoring_eligible'])
            self.assertTrue(record['diagnostic']['sum_only_deviation'])
            self.assertTrue(all(not x['normalization_within_tolerance'] for x in record['diagnostic']['probability_sums'].values()))
        for record in self.assert_prefix(out)[454:]:
            self.assertEqual(record['status'], 'failed')
            self.assertEqual(record['error_code'], 'probability_sum_outside_tolerance')
            self.assertFalse(record['strict_scoring_eligible'])
            self.assertNotIn('answers', record)
        gate = json.loads((out / 'connection_check.json').read_bytes())
        self.assertTrue(gate['connection_valid'])
        self.assertEqual(gate['status'], 'flagged_native')

    def test_sum_deviation_does_not_hide_any_other_violation(self):
        req = copy.deepcopy(self.requests[454]['request'])
        req['questions']['second'] = copy.deepcopy(next(iter(req['questions'].values())))
        body = c.runner.dumps(req).encode()
        response = json.loads(self.response(body, flagged=True)[1])
        field = 'second'
        bad = []
        def add(change):
            r = copy.deepcopy(response)
            change(r)
            bad.append(r)
        add(lambda r: r.update(model='other'))
        add(lambda r: r['answers'].pop(field))
        add(lambda r: r['answers'][field].update(type='text'))
        add(lambda r: r['answers'][field]['probabilities'].update(unknown=0))
        add(lambda r: r['answers'][field]['probabilities'].update({next(iter(r['answers'][field]['probabilities'])): True}))
        add(lambda r: r['answers'][field]['probabilities'].update({next(iter(r['answers'][field]['probabilities'])): -0.1}))
        add(lambda r: r['answers'][field].update(choice=list(r['answers'][field]['probabilities'])[1]))
        add(lambda r: r['answers'][field].update(confidence=1.1))
        add(lambda r: r['answers'][field].update(confidence=True))
        add(lambda r: r.update(usage=None))
        add(lambda r: r['usage'].update(input_tokens=True))
        add(lambda r: r['usage'].update(output_tokens=-1))
        add(lambda r: r['usage'].update(input_tokens=c.runner.CAPACITY+1))
        for r in bad:
            with self.subTest(response=r):
                native, diagnostic = c.validate_with_diagnostic(req, json.dumps(r).encode())
                self.assertIsNone(native)
                self.assertNotIn('sum_only_deviation', diagnostic)

    def test_duplicate_json_keys_nan_and_infinite_are_rejected(self):
        req = self.requests[454]['request']
        body = self.response(c.runner.dumps(req).encode())[1]
        cases = [b'{"model":"wrong","model":"'+c.runner.MODEL.encode()+b'"}',
                 body.replace(b'0.3212345678901234', b'NaN'),
                 body.replace(b'0.3212345678901234', b'Infinity'), b'[]', b'{}', b'not json']
        for raw in cases:
            self.assertIsNone(c.validate_with_diagnostic(req, raw)[0])

    def test_first_request_gate_never_retries(self):
        for status in (429, 529, 401, 500):
            calls = []
            out, result = self.run_temp(lambda body: (calls.append(body) or (status, b'SECRET_ECHO', 1)))
            self.assertEqual(len(calls), 1)
            self.assertEqual(result['wire_attempts_reserved'], 455)
            self.assertEqual(result['retry_attempts'], 0)
            self.assertEqual(result['remaining_cases'], 519)
            self.assertEqual(result['status'], 'halted')
            self.assertNotIn('SECRET_ECHO', ''.join(p.read_text() for p in out.iterdir()))

    def test_global50_retries_and1024_attempts_shared(self):
        case = -1
        pending = False
        calls = []
        def transport(body):
            nonlocal case, pending
            calls.append(body)
            if pending:
                pending = False
                return self.response(body)
            case += 1
            if 1 <= case <= 51:
                pending = case <= 50
                return (429 if case % 2 else 529), b'', 0
            return self.response(body)
        out, result = self.run_temp(transport)
        self.assertEqual(len(calls), 570)
        self.assertEqual(result['wire_attempts_reserved'], 1024)
        self.assertEqual(result['retry_attempts'], 50)
        self.assertEqual(result['capacity_reserved_usd'], '2.818572288')
        self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (971, 3, 0))
        reservations = [e for e in c.runner.rows(out / 'attempts.jsonl') if e['event']=='reserved']
        self.assertEqual([e['attempt'] for e in reservations], list(range(1,1025)))
        self.assertTrue(all(e['case_attempt'] <= 2 for e in reservations))

    def test_durable_reservation_precedes_transport_even_unknown_billing(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name)/'run'
        def transport(body):
            last = c.runner.rows(out/'attempts.jsonl')[-1]
            self.assertEqual((last['event'],last['attempt']), ('reserved',455))
            raise TimeoutError('SECRET_ECHO')
        result = c.run(out,3,transport,sleep=lambda _: None)
        self.assertEqual(result['halt_reason'], 'transport_failure_unknown_billing')
        self.assertEqual(result['capacity_reserved_usd'], str(c.runner.RESERVE*455))
        self.assertEqual(result['attempt_reservations_without_valid_billing'], 3)
        self.assertNotIn('SECRET_ECHO', ''.join(p.read_text() for p in out.iterdir()))

    def test_fsync_failure_prevents_request(self):
        calls = []
        with patch.object(c.os, 'fsync', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                self.run_temp(lambda body: calls.append(body))
        self.assertEqual(calls, [])

    def test_output_cannot_modify_inputs_or_use_symlink_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            alias = Path(tmp) / 'alias'
            alias.symlink_to(Path(tmp), target_is_directory=True)
            with self.assertRaises(c.runner.ContractError):
                c.run(alias / 'new', 3, lambda body: self.fail('no send'))
        for protected in (c.BUNDLE, c.FIRST_RUN, c.ROOT / 'execution/jev/first-run'):
            with self.assertRaises(c.runner.ContractError):
                c.run(protected / 'unwanted-output', 3, lambda body: self.fail('no send'))
            self.assertFalse((protected / 'unwanted-output').exists())

    def test_no_resume_or_cap_reset(self):
        calls = []
        out, result = self.run_temp(lambda body: calls.append(body), cap=c.runner.RESERVE*454)
        self.assertEqual(calls, [])
        self.assertEqual(result['current_failed_cases'], 0)
        with self.assertRaises(c.runner.ContractError):
            c.run(out,3,lambda body: calls.append(body))
        for invalid in (0, 3.01, float('nan'), float('inf')):
            with self.assertRaises(c.runner.BudgetError):
                c.ContinuationLedger(invalid)

    def test_bounded_retry_after_and_total_time(self):
        calls = []
        def transport(body):
            calls.append(body)
            return self.response(body) if len(calls)==1 else (429,b'',121)
        _, result = self.run_temp(transport)
        self.assertEqual(len(calls),2)
        self.assertEqual(result['halt_reason'],'retry_after_exceeds_bounded_wait')
        ticks = iter([0,7200])
        _, result = self.run_temp(lambda body: self.fail('no send'), now=lambda: next(ticks))
        self.assertEqual(result['halt_reason'],'total_time_limit')
        self.assertEqual(result['wire_attempts_reserved'],454)

    def test_changed_plan_archive_and_bundle_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan=Path(tmp)/'plan.json'
            plan.write_bytes(c.PLAN.read_bytes()+b' ')
            with self.assertRaises(c.runner.ContractError):
                c.prepare(plan_path=plan)
            archive=Path(tmp)/'prior'
            shutil.copytree(c.FIRST_RUN,archive)
            (archive/'predictions.jsonl').write_bytes(self.prior['predictions.jsonl']+b'{}\n')
            with self.assertRaises(c.runner.ContractError):
                c.prepare(first_run=archive)

    def test_offline_default_never_reads_environment_or_network(self):
        with patch.object(c.os, 'environ', {}) as env, patch.object(c, 'BoundedHttpTransport', side_effect=AssertionError('network')), patch('sys.stdout',new_callable=io.StringIO):
            self.assertEqual(c.main([]),0)
            self.assertEqual(env,{})

    def test_manual_context_requires_every_exact_field(self):
        env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':'storminator89/clef-benchmark',
             'GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_REF':'refs/heads/main','GITHUB_RUN_ATTEMPT':'1'}
        c.require_manual_context(env)
        for key in env:
            with self.assertRaises(c.runner.ContractError):
                c.require_manual_context({**env,key:'wrong'})

    def test_production_transport_arms_and_clears_hard_deadline(self):
        transport=object.__new__(c.BoundedHttpTransport)
        with patch.object(c.signal,'signal',return_value='old') as signal, patch.object(c.signal,'setitimer') as timer, patch.object(c.runner.HttpTransport,'__call__',return_value=(200,b'{}',None)):
            self.assertEqual(transport(b'{}'),(200,b'{}',None))
            self.assertEqual(timer.call_args_list[0].args,(c.signal.ITIMER_REAL,95))
            self.assertEqual(timer.call_args_list[-1].args,(c.signal.ITIMER_REAL,0))
            self.assertEqual(signal.call_args_list[-1].args,(c.signal.SIGALRM,'old'))


if __name__ == '__main__':
    unittest.main()
