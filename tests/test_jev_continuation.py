"""Offline mocks only. Temporary outputs are not hosted/model observations."""
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_jev_continuation as continuation


class JevContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests, cls.prior, cls.plan = continuation.prepare()
        cls.context = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'storminator89/clef-benchmark',
                       'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REF': 'refs/heads/main',
                       'GITHUB_RUN_ATTEMPT': '1'}

    def response(self, body, tokens=10):
        request = json.loads(body)
        answers = {}
        for key, question in request['questions'].items():
            options = list(question['criteria'])
            probabilities = {option: 0 for option in options}
            probabilities[options[0]] = 0.6000000000000001
            probabilities[options[1]] = 0.3999999999999999
            answers[key] = {'type': 'choice', 'choice': options[0], 'confidence': 0.3212345678901234,
                            'probabilities': probabilities}
        return 200, json.dumps({'model': continuation.runner.MODEL, 'answers': answers,
                               'usage': {'input_tokens': tokens, 'output_tokens': 1}}).encode(), None

    def small_request(self):
        return {'model': continuation.runner.MODEL, 'state': 'Public mock text', 'questions': {
            'decision': {'type': 'choice', 'instructions': 'Choose', 'criteria': {'a': None, 'b': None}}}}

    def run_temp(self, transport, cap=3):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        out = Path(temporary.name) / 'run'
        result = continuation.run(out, cap, transport, sleep=lambda _: None)
        return out, result

    def assert_prefix(self, out):
        for name in ('predictions.jsonl', 'attempts.jsonl'):
            self.assertTrue((out / name).read_bytes().startswith(self.prior[name]))
        all_predictions = continuation.runner.rows(out / 'predictions.jsonl')
        self.assertEqual(all_predictions[180], json.loads(self.prior['predictions.jsonl'].splitlines()[180]))
        self.assertEqual(all_predictions[180]['status'], 'failed')
        return all_predictions

    def test_full_793_mock_run_preserves_prefix_and_native_vectors_exactly(self):
        sent = []
        def transport(body):
            sent.append(body)
            return self.response(body)
        out, result = self.run_temp(transport)
        self.assertEqual(set(p.name for p in out.iterdir()), {
            'run_summary.json', 'predictions.jsonl', 'attempts.jsonl',
            'connection_check.json', 'validation_diagnostics.jsonl'})
        self.assertEqual(sent, [continuation.runner.dumps(r['request']).encode() for r in self.requests[181:]])
        self.assertEqual(len(sent), 793)
        self.assertEqual(result['status'], 'completed_with_failures')
        self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (973, 1, 0))
        self.assertEqual((result['prior_completed_cases'], result['prior_failed_cases']), (180, 1))
        self.assertEqual((result['current_completed_cases'], result['current_failed_cases']), (793, 0))
        self.assertEqual((result['wire_attempts_reserved'], result['current_wire_attempts_reserved']), (974, 793))
        self.assertEqual(result['current_transport_calls_started'], 793)
        self.assertEqual(result['retry_attempts'], 0)
        self.assertEqual(result['historical_first_case_latency_note'], json.loads(self.prior['run_summary.json'])['first_case_latency_note'])
        self.assertEqual(result['known_success_input_tokens'], 229691 + 7930)
        self.assertEqual(result['known_success_cost_usd'], '0.009980082')
        self.assertEqual(result['attempt_reservations_without_valid_billing'], 1)
        self.assertEqual(result['capacity_reserved_usd'], str(continuation.runner.RESERVE * 974))
        predictions = self.assert_prefix(out)
        new_ids = [(p['suite'], p['id']) for p in predictions[181:]]
        self.assertEqual(new_ids, [(r['suite'], r['id']) for r in self.requests[181:]])
        self.assertFalse(set(new_ids) & {(r['suite'], r['id']) for r in self.requests[:181]})
        for body, record in zip(sent, predictions[181:]):
            expected = json.loads(self.response(body)[1])
            self.assertEqual(record['answers'], expected['answers'])
            self.assertEqual(record['probabilities_unrounded'], {k: v['probabilities'] for k, v in expected['answers'].items()})
        events = continuation.runner.rows(out / 'attempts.jsonl')
        reservations = [e for e in events if e['event'] == 'reserved']
        self.assertEqual([e['attempt'] for e in reservations], list(range(1, 975)))
        self.assertEqual(reservations[181]['id'], 'bank_cards_06')
        gate = json.loads((out / 'connection_check.json').read_bytes())
        self.assertTrue(gate['connection_valid'])
        self.assertEqual(gate['extra_requests'], 0)
        self.assertEqual(gate['original_case_number'], 182)
        self.assertEqual((out / 'validation_diagnostics.jsonl').read_bytes(), b'')

    def test_full_mock_retry_cap_is_shared_50_and_1024_not_reset(self):
        calls = 0
        case = -1
        pending = False
        def transport(body):
            nonlocal calls, case, pending
            calls += 1
            if pending:
                pending = False
                return self.response(body)
            case += 1
            if 1 <= case <= 51:
                pending = case <= 50
                return (429 if case % 2 else 529), b'SECRET_ECHO', 0
            return self.response(body)
        out, result = self.run_temp(transport)
        self.assertEqual(calls, 843)
        self.assertEqual(result['wire_attempts_reserved'], 1024)
        self.assertEqual(result['retry_attempts'], 50)
        self.assertEqual(result['current_wire_attempts_reserved'], 843)
        self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (972, 2, 0))
        self.assertEqual(result['capacity_reserved_usd'], '2.818572288')
        events = continuation.runner.rows(out / 'attempts.jsonl')
        reserves = [e for e in events if e['event'] == 'reserved']
        self.assertEqual(max(e['attempt'] for e in reserves), 1024)
        self.assertTrue(all(e['case_attempt'] <= 2 for e in reserves))
        self.assertEqual(sum(e['retry'] for e in reserves), 50)
        self.assert_prefix(out)
        self.assertNotIn('SECRET_ECHO', ''.join(p.read_text() for p in out.iterdir()))

    def test_first_new_case_never_retries_any_failure(self):
        for status, raw in [(429, b'SECRET_ECHO'), (529, b'SECRET_ECHO'),
                            (401, b'SECRET_ECHO'), (200, b'bad SECRET_ECHO')]:
            with self.subTest(status=status):
                calls = []
                def transport(body):
                    calls.append(body)
                    return status, raw, None
                out, result = self.run_temp(transport)
                self.assertEqual(len(calls), 1)
                self.assertEqual(calls[0], continuation.runner.dumps(self.requests[181]['request']).encode())
                self.assertEqual(result['status'], 'halted')
                self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (180, 2, 792))
                self.assertEqual(result['wire_attempts_reserved'], 182)
                self.assertEqual(result['retry_attempts'], 0)
                self.assertEqual(result['known_success_input_tokens'], 229691)
                self.assertFalse(json.loads((out / 'connection_check.json').read_bytes())['connection_valid'])
                self.assert_prefix(out)
                self.assertNotIn('SECRET_ECHO', ''.join(p.read_text() for p in out.iterdir()))

    def test_timeout_unknown_billing_is_reserved_never_retried_or_logged(self):
        def transport(body):
            raise RuntimeError('SECRET_ECHO')
        out, result = self.run_temp(transport)
        self.assertEqual(result['halt_reason'], 'transport_failure_unknown_billing')
        self.assertEqual(result['capacity_reserved_usd'], str(continuation.runner.RESERVE * 182))
        self.assertEqual(result['known_success_cost_usd'], '0.009647022')
        self.assertEqual(result['current_known_success_input_tokens'], 0)
        self.assertEqual(result['attempt_reservations_without_valid_billing'], 2)
        self.assertNotIn('SECRET_ECHO', ''.join(p.read_text() for p in out.iterdir()))

    def test_later_validation_or_nonretryable_http_stops_immediately(self):
        for failure in [(200, b'{}', None), (500, b'SECRET_ECHO', None), (302, b'SECRET_ECHO', None)]:
            with self.subTest(status=failure[0]):
                calls = []
                def transport(body):
                    calls.append(body)
                    return self.response(body) if len(calls) == 1 else failure
                out, result = self.run_temp(transport)
                self.assertEqual(len(calls), 2)
                self.assertEqual(result['status'], 'halted')
                self.assertEqual(result['wire_attempts_reserved'], 183)
                self.assertEqual(result['retry_attempts'], 0)
                self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (181, 2, 791))
                self.assertNotIn('SECRET_ECHO', ''.join(p.read_text() for p in out.iterdir()))

    def test_bounded_retry_after_halts_without_waiting_121_seconds(self):
        calls = []
        def transport(body):
            calls.append(body)
            return self.response(body) if len(calls) == 1 else (429, b'', 121)
        _, result = self.run_temp(transport)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result['halt_reason'], 'retry_after_exceeds_bounded_wait')
        self.assertEqual(result['retry_attempts'], 0)

    def test_ledger_caps_include_all_prior_reservations(self):
        ledger = continuation.ContinuationLedger(3)
        self.assertEqual(ledger.attempts, 181)
        self.assertEqual(ledger.status()['capacity_reserved_usd'], '0.498204672')
        self.assertEqual(ledger.known_input_tokens, 229691)
        for _ in range(793):
            ledger.reserve()
        for _ in range(50):
            ledger.reserve(retry=True)
        self.assertEqual(ledger.attempts, 1024)
        self.assertEqual(ledger.retries, 50)
        with self.assertRaises(continuation.runner.BudgetError):
            ledger.reserve()
        with self.assertRaises(continuation.runner.BudgetError):
            ledger.reserve(retry=True)
        for cap in (0, -1, '3.01', 'NaN', 'Infinity'):
            with self.subTest(cap=cap), self.assertRaises(continuation.runner.BudgetError):
                continuation.ContinuationLedger(cap)
        with self.assertRaises(continuation.runner.ContractError):
            continuation.ContinuationLedger('0.498204671')

    def test_cap_before_any_new_send_has_no_fabricated_failed_case(self):
        out, result = self.run_temp(lambda _: self.fail('No call is affordable'), cap='0.498204672')
        self.assertEqual(result['halt_reason'], 'local_budget_or_attempt_limit')
        self.assertEqual(result['current_transport_calls_started'], 0)
        self.assertEqual(result['wire_attempts_reserved'], 181)
        self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (180, 1, 793))
        self.assertEqual((out / 'predictions.jsonl').read_bytes(), self.prior['predictions.jsonl'])

    def test_cap_denied_retry_accounts_for_already_attempted_case(self):
        calls = []
        def transport(body):
            calls.append(body)
            return self.response(body) if len(calls) == 1 else (429, b'', None)
        out, result = self.run_temp(transport, cap=continuation.runner.RESERVE * 183)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result['halt_reason'], 'local_budget_or_attempt_limit')
        self.assertEqual(result['wire_attempts_reserved'], 183)
        self.assertEqual((result['completed_cases'], result['failed_cases'], result['remaining_cases']), (181, 2, 791))
        self.assertEqual(len(continuation.runner.rows(out / 'predictions.jsonl')), 183)

    def test_existing_output_never_resumes_or_overwrites(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'old'
            out.mkdir()
            marker = out / 'predictions.jsonl'
            marker.write_bytes(b'SAVED')
            with self.assertRaises(continuation.runner.ContractError):
                continuation.run(out, 3, lambda _: self.fail('No network'), sleep=lambda _: None)
            self.assertEqual(marker.read_bytes(), b'SAVED')
            self.assertEqual([p.name for p in out.iterdir()], ['predictions.jsonl'])

    def test_plan_is_exact_793_order_locked_and_model_is_only_payload_change(self):
        self.assertEqual(continuation.sha(continuation.PLAN.read_bytes()), continuation.PLAN_SHA256)
        self.assertEqual(continuation.PLAN.read_bytes(), continuation.encoded(self.plan))
        self.assertEqual([p['original_case_number'] for p in self.plan['requests']], list(range(182, 975)))
        self.assertEqual(self.plan['max_total_attempts_including_prior'], 1024)
        self.assertFalse(self.plan['retry_previously_attempted_cases'])
        manifest = json.loads((continuation.BUNDLE / 'manifest.json').read_bytes())
        originals = []
        for suite in manifest['suites']:
            originals.extend(continuation.runner.rows(continuation.BUNDLE / 'inputs' / suite['id'] / 'requests.jsonl'))
        for original, request in zip(originals, self.requests):
            source = copy.deepcopy(original['request'])
            self.assertEqual(source['model'], 'clef-flash')
            source['model'] = continuation.runner.MODEL
            self.assertEqual(continuation.runner.dumps(source), continuation.runner.dumps(request['request']))

    def test_changed_plan_rejected_even_when_other_inputs_are_valid(self):
        with tempfile.TemporaryDirectory() as td:
            plan = Path(td) / 'plan.json'
            changed = copy.deepcopy(self.plan)
            changed['requests'][0] = changed['requests'][1]
            plan.write_bytes(continuation.encoded(changed))
            with self.assertRaisesRegex(continuation.runner.ContractError, 'plan checksum'):
                continuation.prepare(plan_path=plan)
            with patch.object(continuation, 'PLAN_SHA256', continuation.sha(plan.read_bytes())):
                with self.assertRaisesRegex(continuation.runner.ContractError, 'plan scope'):
                    continuation.prepare(plan_path=plan)

    def test_frozen_manifest_and_first_run_tampering_fail(self):
        with tempfile.TemporaryDirectory() as td:
            first = Path(td) / 'first'
            shutil.copytree(continuation.FIRST_RUN, first)
            (first / 'predictions.jsonl').write_bytes(self.prior['predictions.jsonl'] + b'\n')
            with self.assertRaisesRegex(continuation.runner.ContractError, 'checksum'):
                continuation.verify_prior(first, self.requests)
            (first / 'FILE_SHA256.json').write_bytes(b'{}\n')
            with self.assertRaisesRegex(continuation.runner.ContractError, 'lock mismatch'):
                continuation.verify_prior(first, self.requests)
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td) / 'bundle'
            shutil.copytree(continuation.BUNDLE, bundle)
            (bundle / 'manifest.json').write_bytes(b'{}\n')
            with self.assertRaises(continuation.runner.ContractError):
                continuation.verify_bundle(bundle)

    def test_order_identity_retry_and_ledger_reconciliation_are_semantically_checked(self):
        for mutation in ('prediction_order', 'ledger_order', 'prior_retry', 'cost', 'last_failure'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                first = Path(td) / 'first'
                shutil.copytree(continuation.FIRST_RUN, first)
                if mutation in ('prediction_order', 'last_failure'):
                    file = first / 'predictions.jsonl'
                    rows = continuation.runner.rows(file)
                    if mutation == 'prediction_order':
                        rows[0], rows[1] = rows[1], rows[0]
                    else:
                        rows[180]['status'] = 'valid'
                    file.write_text(''.join(continuation.runner.dumps(r) + '\n' for r in rows))
                else:
                    file = first / 'attempts.jsonl'
                    rows = continuation.runner.rows(file)
                    if mutation == 'ledger_order':
                        rows[2]['id'] = rows[0]['id']
                    elif mutation == 'prior_retry':
                        rows[0]['retry'] = True
                    else:
                        rows[0]['reserved_usd'] = '0'
                    file.write_text(''.join(continuation.runner.dumps(r) + '\n' for r in rows))
                hashes = json.loads((first / 'FILE_SHA256.json').read_bytes())
                hashes[file.name] = continuation.sha(file.read_bytes())
                (first / 'FILE_SHA256.json').write_bytes(continuation.encoded(hashes))
                with patch.object(continuation, 'FIRST_RUN_LOCK_SHA256', continuation.sha((first / 'FILE_SHA256.json').read_bytes())):
                    with self.assertRaises(continuation.runner.ContractError):
                        continuation.verify_prior(first, self.requests)

    def test_diagnostics_fixed_contract_clauses_and_no_provider_text(self):
        request = self.small_request()
        valid = json.loads(self.response(json.dumps(request).encode())[1])
        cases = []
        def add(code, mutate):
            response = copy.deepcopy(valid)
            mutate(response)
            cases.append((code, response))
        add('provider_model_mismatch', lambda r: r.update(model='SECRET_MODEL'))
        add('answer_fields_mismatch', lambda r: r['answers'].update(SECRET_FIELD='SECRET_ECHO'))
        add('response_primitive_mismatch', lambda r: r['answers']['decision'].update(type='SECRET_TYPE'))
        add('probability_option_keys_mismatch', lambda r: r['answers']['decision']['probabilities'].update(SECRET_OPTION=0))
        add('invalid_native_probability', lambda r: r['answers']['decision']['probabilities'].update(a='SECRET_NUMBER'))
        add('probability_sum_outside_tolerance', lambda r: r['answers']['decision']['probabilities'].update(a=0.5, b=0.4))
        add('choice_not_native_maximum', lambda r: r['answers']['decision'].update(choice='SECRET_CHOICE'))
        add('invalid_native_confidence', lambda r: r['answers']['decision'].update(confidence='SECRET_CONFIDENCE'))
        add('billing_units_missing_or_invalid', lambda r: r.update(usage={'input_tokens': 'SECRET_USAGE'}))
        add('usage_exceeds_capacity', lambda r: r['usage'].update(input_tokens=65537))
        self.assertEqual({c for c, _ in cases}, set(continuation.CONTRACT_CODES.values()))
        for code, response in cases:
            with self.subTest(code=code):
                native, diagnostic = continuation.validate_with_diagnostic(request, json.dumps(response).encode())
                self.assertIsNone(native)
                self.assertEqual(diagnostic['contract_code'], code)
                self.assertNotIn('SECRET', json.dumps(diagnostic))
                self.assertEqual(set(diagnostic['expected_fields']), {'decision'})
                self.assertNotIn('usage', diagnostic)
                entry = diagnostic['expected_fields']['decision']
                if code in ('invalid_native_probability', 'probability_option_keys_mismatch'):
                    self.assertNotIn('normalization_within_tolerance', entry)
                if code == 'probability_sum_outside_tolerance':
                    self.assertIs(entry['normalization_within_tolerance'], False)
        native, diagnostic = continuation.validate_with_diagnostic(request, b'invalid SECRET_JSON')
        self.assertIsNone(native)
        self.assertEqual(diagnostic['contract_code'], 'invalid_json')
        self.assertNotIn('SECRET', json.dumps(diagnostic))

    def test_missing_billing_has_no_invented_usage_or_vectors_in_output(self):
        def transport(body):
            response = json.loads(self.response(body)[1])
            response.pop('usage')
            response['SECRET_FIELD'] = 'SECRET_ECHO'
            return 200, json.dumps(response).encode(), None
        out, result = self.run_temp(transport)
        record = continuation.runner.rows(out / 'predictions.jsonl')[-1]
        self.assertEqual(record['status'], 'failed')
        self.assertFalse({'answers', 'usage', 'probabilities_unrounded', 'input_tokens'} & set(record))
        self.assertEqual(result['known_success_input_tokens'], 229691)
        diag_rows = continuation.runner.rows(out / 'validation_diagnostics.jsonl')
        self.assertEqual(len(diag_rows), 1)
        self.assertEqual(diag_rows[0]['attempt'], 182)
        self.assertEqual(diag_rows[0]['diagnostic']['contract_code'], 'billing_units_missing_or_invalid')
        self.assertNotIn('SECRET', ''.join(p.read_text() for p in out.iterdir()))

    def test_unexpected_validation_exceptions_never_echo_exception_text(self):
        request = self.small_request()
        raw = self.response(json.dumps(request).encode())[1]
        for error in (RuntimeError('SECRET_ECHO'), continuation.runner.ContractError('SECRET_ECHO')):
            with self.subTest(type=type(error)), patch.object(continuation.runner, 'validate_response', side_effect=error):
                native, diagnostic = continuation.validate_with_diagnostic(request, raw)
                self.assertIsNone(native)
                self.assertEqual(diagnostic['contract_code'], 'unexpected_validation_exception')
                self.assertNotIn('SECRET', json.dumps(diagnostic))

    def test_malformed_native_shapes_nan_huge_integer_and_unknown_names_are_safe(self):
        request = self.small_request()
        valid = json.loads(self.response(json.dumps(request).encode())[1])
        for value in ([1], {}, 'SECRET_ECHO', None):
            native, diagnostic = continuation.validate_with_diagnostic(request, json.dumps(value).encode())
            self.assertIsNone(native)
            self.assertNotIn('SECRET', json.dumps(diagnostic))
        for bad in (float('nan'), float('inf'), 10 ** 400, True, -1, 2):
            response = copy.deepcopy(valid)
            response['answers']['decision']['probabilities']['a'] = bad
            native, diagnostic = continuation.validate_with_diagnostic(request, json.dumps(response).encode())
            self.assertIsNone(native)
            self.assertNotIn('normalization_within_tolerance', diagnostic['expected_fields']['decision'])
            json.dumps(diagnostic, allow_nan=False)
        response = copy.deepcopy(valid)
        response['answers']['decision']['choice'] = {'SECRET_ECHO': 'SECRET_ECHO'}
        native, diagnostic = continuation.validate_with_diagnostic(request, json.dumps(response).encode())
        self.assertIsNone(native)
        self.assertEqual(diagnostic['contract_code'], 'unexpected_validation_exception')
        self.assertNotIn('SECRET', json.dumps(diagnostic))

    def test_invalid_transport_contract_is_sanitized_and_not_retried(self):
        for result in [('SECRET_STATUS', b'SECRET_ECHO', None), (200, 'SECRET_BODY', None),
                       (429, b'', 'SECRET_DELAY'), (429, b'', float('nan'))]:
            with self.subTest(result=result):
                out, summary = self.run_temp(lambda _: result)
                self.assertEqual(summary['halt_reason'], 'transport_failure_unknown_billing')
                self.assertEqual(summary['current_transport_calls_started'], 1)
                self.assertNotIn('SECRET', ''.join(p.read_text() for p in out.iterdir()))

    def test_context_guards_every_exact_required_field(self):
        continuation.require_manual_context(self.context)
        for key in self.context:
            with self.subTest(key=key), self.assertRaises(continuation.runner.ContractError):
                continuation.require_manual_context({**self.context, key: 'unexpected'})

    def test_offline_default_never_reads_credentials_or_network(self):
        class ForbiddenEnvironment(dict):
            def get(self, key, *args):
                if key not in {'LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG', 'COLUMNS', 'LINES'}:
                    raise AssertionError('Offline must not read credentials')
                return super().get(key, *args)
            def __iter__(self):
                raise AssertionError('Offline must not inspect environment')
        with tempfile.TemporaryDirectory() as td, patch.object(continuation.os, 'environ', ForbiddenEnvironment()), \
                patch.object(continuation.runner, 'HttpTransport', side_effect=AssertionError('No network')), \
                patch.object(continuation.subprocess, 'run', side_effect=AssertionError('No subprocess required')):
            out = Path(td) / 'plan.json'
            self.assertEqual(continuation.main(['--output', str(out)]), 0)
            self.assertEqual(out.read_bytes(), continuation.PLAN.read_bytes())
            with self.assertRaises(FileExistsError):
                continuation.main(['--output', str(out)])

    def test_execute_validates_inputs_approval_output_and_context_before_secret(self):
        class GuardEnvironment(dict):
            def get(self, key, *args):
                if key == 'JEV_API_KEY':
                    raise AssertionError('Credential read before all guards')
                return super().get(key, *args)
        with tempfile.TemporaryDirectory() as td, patch.object(continuation.os, 'environ', GuardEnvironment(self.context)):
            out = Path(td) / 'new'
            valid_args = ['--execute', '--approval', continuation.APPROVAL, '--approved-api-usd', '3', '--output', str(out)]
            for args in (['--execute', '--output', str(out)],
                         ['--execute', '--approval', continuation.APPROVAL, '--approved-api-usd', '2', '--output', str(out)]):
                with self.assertRaises(continuation.runner.ContractError):
                    continuation.main(args)
            with patch.object(continuation, 'prepare', side_effect=continuation.runner.ContractError('Bad input')):
                with self.assertRaises(continuation.runner.ContractError):
                    continuation.main(valid_args)
            with patch.object(continuation.subprocess, 'run', side_effect=RuntimeError('Preflight failed')):
                with self.assertRaises(RuntimeError):
                    continuation.main(valid_args)
            with patch.object(continuation.os, 'environ', GuardEnvironment({**self.context, 'GITHUB_RUN_ATTEMPT': '2'})):
                with self.assertRaises(continuation.runner.ContractError):
                    continuation.main(valid_args)
            out.mkdir()
            with self.assertRaises(continuation.runner.ContractError):
                continuation.main(valid_args)

    def test_execute_child_environment_excludes_secret_and_success_exit_is_partial_aggregate(self):
        sequence = []
        class TrackingEnvironment(dict):
            def get(self, key, *args):
                if key == 'JEV_API_KEY':
                    sequence.append('credential')
                return super().get(key, *args)
        def preflight(*args, **kwargs):
            sequence.append('preflight')
            self.assertEqual(kwargs['env'], {'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertNotIn('SECRET_ECHO', repr(kwargs))
        outcome = {'status': 'completed_with_failures', 'completed_cases': 973, 'failed_cases': 1,
                   'remaining_cases': 0, 'current_completed_cases': 793, 'current_failed_cases': 0,
                   'current_wire_attempts_reserved': 793, 'wire_attempts_reserved': 974,
                   'retry_attempts': 0, 'capacity_reserved_usd': '2.680948', 'known_success_cost_usd': '0.01'}
        with tempfile.TemporaryDirectory() as td, \
                patch.object(continuation.os, 'environ', TrackingEnvironment({**self.context, 'JEV_API_KEY': 'SECRET_ECHO', 'PYTHONPATH': 'SECRET_ECHO'})), \
                patch.object(continuation.subprocess, 'run', side_effect=preflight), \
                patch.object(continuation.runner, 'HttpTransport', return_value=object()) as transport, \
                patch.object(continuation, 'run', return_value=outcome), \
                patch('sys.stdout', new_callable=io.StringIO) as stdout:
            result = continuation.main(['--execute', '--approval', continuation.APPROVAL, '--approved-api-usd', '3', '--output', str(Path(td) / 'out')])
            self.assertEqual(result, 0)
            self.assertEqual(sequence, ['preflight', 'credential'])
            transport.assert_called_once_with('SECRET_ECHO')
            self.assertNotIn('SECRET_ECHO', stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
