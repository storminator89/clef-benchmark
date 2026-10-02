"""Model-free custom evaluator coverage. All predictions here are test doubles."""
from __future__ import annotations

import copy
import csv
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import evaluate_custom as evaluator
from server import Workbench, make_server


def question():
    return {'type': 'choice', 'instructions': 'Which synthetic label applies?',
            'criteria': {'yes': 'Synthetic positive', 'no': 'Synthetic negative'}}


def case(identifier='case_1', labelled=True):
    value = {'id': identifier, 'state': 'Synthetic test fixture; never a benchmark result.',
             'questions': {'decision': question(), 'evidence': question()}}
    if labelled:
        value['gold'] = {'decision': 'yes', 'evidence': 'yes'}
    return value


def suite(cases=None):
    return {'schema_version': 1, 'name': 'Synthetic fixtures', 'cases': cases or [case()]}


def response(request=None):
    request = request or case()
    return {'source': 'live_local_inference', 'model': 'Cloudflare/clef-flash',
            'model_key': 'flash-9b', 'model_id': 'Cloudflare/clef-flash', 'requested_profile': 'cpu-nf4', 'revision': 'test-double-only', 'benchmark_result': False, 'truncated': False,
            'answers': {field: {'type': 'choice', 'choice': 'yes', 'confidence': 0.75,
                               'probabilities': {'yes': 0.75, 'no': 0.25}}
                        for field in request['questions']},
            'probabilities_unrounded': {field: {'no': 0.25, 'yes': 0.75}
                                       for field in request['questions']},
            'input_tokens': 20, 'device': 'test-double', 'precision': 'test-double',
            'runtime': {'device': 'test-double', 'precision': 'test-double', 'profile': 'cpu-nf4',
                        'model_key': 'flash-9b', 'model_id': 'Cloudflare/clef-flash', 'revision': 'test-double-only'},
            'latency_ms': 0.0, 'test_fixture_only': True}


class FakeClient:
    endpoint = 'http://127.0.0.1:8765'

    def __init__(self, replies=None, stop=None, enabled=True, busy=False):
        self.replies = replies or []
        self.stop = stop
        self.health_value = {'inference_enabled': enabled, 'busy': busy, 'runtime': None,
                             'model_key': 'flash-9b', 'model_id': 'Cloudflare/clef-flash', 'model': 'Cloudflare/clef-flash',
                             'revision': 'test-double-only', 'requested_profile': 'cpu-nf4'}
        self.calls = []

    def health(self):
        return copy.deepcopy(self.health_value)

    def request(self, method, path, body=None):
        self.calls.append((method, path, json.loads(body)))
        if self.stop:
            self.stop.requested = True
        reply = self.replies.pop(0) if self.replies else (200, response(json.loads(body)))
        if isinstance(reply, BaseException):
            raise reply
        return reply


class TemporaryFiles(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def file(self, name, value, raw=False):
        path = self.directory / name
        path.write_text(value if raw else json.dumps(value, ensure_ascii=False), encoding='utf-8', newline='')
        return path

    def execute(self, value=None, client=None, stop=None):
        report = evaluator.new_report(value or suite())
        evaluator.run_evaluation(report, client or FakeClient(), self.directory / 'report.json', stop=stop)
        return report


class InputValidationTests(TemporaryFiles):
    def test_unicode_blank_only_text_uses_browser_cli_union(self):
        for blank in ('\ufeff', '\u0085', '\u001c', '\u001d', '\u001e', '\u001f', ' \ufeff\u0085 '):
            for field in ('name', 'state', 'instructions', 'description'):
                value = suite()
                if field == 'name':
                    value['name'] = blank
                elif field == 'state':
                    value['cases'][0]['state'] = blank
                elif field == 'instructions':
                    value['cases'][0]['questions']['decision']['instructions'] = blank
                else:
                    value['cases'][0]['questions']['decision']['criteria']['yes'] = blank
                with self.subTest(blank=repr(blank), field=field), self.assertRaises(ValueError):
                    evaluator.validate_suite(value)

    def test_json_unicode_bom_preserves_text(self):
        original = suite()
        original['cases'][0]['state'] = '  Grün\n🙂\u2028Ende\t  '
        path = self.file('unicode.json', '\ufeff' + json.dumps(original, ensure_ascii=False), raw=True)
        self.assertEqual(evaluator.load_suite(path), original)

    def test_numeric_schema_version_one_is_normalized(self):
        original = suite()
        original['schema_version'] = 1.0
        validated = evaluator.validate_suite(original)
        self.assertIs(type(validated['schema_version']), int)
        self.assertEqual(evaluator.suite_fingerprint(validated), evaluator.suite_fingerprint(suite()))

    def test_invalid_schema_versions(self):
        for version in (True, False, 0, 2, '1', None):
            with self.subTest(version=version), self.assertRaises(ValueError):
                evaluator.validate_suite({**suite(), 'schema_version': version})

    def test_duplicate_keys_rejected_at_every_depth(self):
        for raw in ('{"a":1,"a":2}', '{"q":{"a":1,"a":2}}', '{"a":[{"x":0,"x":1}]}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, 'Duplicate'):
                evaluator.parse_json(raw)

    def test_forbidden_object_keys(self):
        for name in evaluator.FORBIDDEN_KEYS:
            with self.subTest(name=name), self.assertRaises(ValueError):
                evaluator.parse_json(json.dumps({'questions': {name: question()}}))

    def test_nonfinite_surrogates_and_depth(self):
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":1e999}', '"\\ud800"', '"\\udfff"', '[' * 13 + '0' + ']' * 13):
            with self.subTest(text=text), self.assertRaises(ValueError):
                evaluator.parse_json(text)
        self.assertEqual(evaluator.parse_json('"\\ud83d\\ude00"'), '😀')
        self.assertEqual(evaluator.parse_json('"' + '{' * 20 + '"'), '{' * 20)
        evaluator.parse_json('[' * 12 + '0' + ']' * 12)

    def test_rejects_unknown_root_case_question_gold_keys(self):
        inputs = []
        inputs.append({**suite(), 'verified': True})
        for key in ('expected', 'response', 'benchmark_result', 'image_url'):
            bad = suite()
            bad['cases'][0][key] = 'forbidden'
            inputs.append(bad)
        bad = suite(); bad['cases'][0]['questions']['decision']['extra'] = 'no'; inputs.append(bad)
        bad = suite(); bad['cases'][0]['gold']['unknown'] = 'yes'; inputs.append(bad)
        bad = suite(); bad['cases'][0]['gold']['decision'] = 'unknown'; inputs.append(bad)
        bad = suite(); bad['cases'][0]['gold'] = None; inputs.append(bad)
        for value in inputs:
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluator.validate_suite(value)

    def test_case_ids_safe_unique_digit_allowed(self):
        evaluator.validate_suite(suite([case('9_case')]))
        for identifier in ('', '../escape', 'a/b', '<script>', '_start', 'a' * 65, 'é', 'a\n'):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                evaluator.validate_suite(suite([case(identifier)]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            evaluator.validate_suite(suite([case(), case()]))

    def test_case_count_bounds(self):
        with self.assertRaises(ValueError):
            evaluator.validate_suite({**suite(), 'cases': []})
        with self.assertRaises(ValueError):
            evaluator.validate_suite(suite([case(str(i)) for i in range(501)]))
        evaluator.validate_suite(suite([case(str(i)) for i in range(500)]))

    def test_string_and_question_limits_match_server(self):
        alterations = [('state', 'x' * 6001), ('state', '  '), ('state', {})]
        for field, value in alterations:
            invalid = case(); invalid[field] = value
            with self.subTest(value=str(value)[:20]), self.assertRaises(ValueError):
                evaluator.validate_suite(suite([invalid]))
        for fields in (0, 9):
            invalid = case(); invalid['questions'] = {f'q{i}': question() for i in range(fields)}
            with self.assertRaises(ValueError):
                evaluator.validate_suite(suite([invalid]))
        for key, value in [('instructions', 'x' * 4001), ('type', 'text'), ('criteria', {'a': 'A'})]:
            invalid = case(); invalid['questions']['decision'][key] = value
            with self.assertRaises(ValueError):
                evaluator.validate_suite(suite([invalid]))

    def test_request_byte_limit_not_character_count(self):
        invalid = case(); invalid['state'] = '🙂' * 6000
        for question_value in invalid['questions'].values():
            question_value['instructions'] = '🙂' * 4000
        with self.assertRaisesRegex(ValueError, 'serialized HTTP'):
            evaluator.validate_suite(suite([invalid]))

    def test_file_byte_limit_and_invalid_utf8(self):
        path = self.directory / 'large.json'
        path.write_bytes(b' ' * (evaluator.MAX_INPUT_BYTES + 1))
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            evaluator.load_suite(path)
        path.write_bytes(b'\xff')
        with self.assertRaisesRegex(ValueError, 'UTF-8'):
            evaluator.load_suite(path)

    def test_jsonl_preserves_rows_and_handles_line_endings(self):
        for newline in ('\n', '\r\n', '\r'):
            first, second = case('first'), case('second', False)
            first['state'] = 'U+2028\u2028is still the same string'
            raw = newline.join(json.dumps(value, ensure_ascii=False) for value in (first, second)) + newline
            result = evaluator.load_suite(self.file('rows.jsonl', raw, raw=True))
            self.assertEqual(result['name'], 'rows')
            self.assertEqual(result['cases'], [first, second])

    def test_jsonl_blank_bad_and_extra_terminal_rows_rejected(self):
        row = json.dumps(case())
        for raw in ('', row + '\n\n', row + '\n \n' + row, row + '\nnot json'):
            with self.subTest(raw=raw[-30:]), self.assertRaises(ValueError):
                evaluator.load_suite(self.file('rows.jsonl', raw, raw=True))

    def test_csv_bom_multiline_quotes_blank_gold(self):
        spec = self.file('spec.json', {'schema_version': 1, 'questions': case()['questions']})
        raw = '\ufeffid,state,gold.decision,gold.evidence\r\nfirst,"line1, ""quoted""\nline2",yes,\r\n'
        result = evaluator.load_suite(self.file('input.csv', raw, raw=True), spec=spec)
        self.assertEqual(result['cases'][0]['state'], 'line1, "quoted"\nline2')
        self.assertEqual(result['cases'][0]['gold'], {'decision': 'yes'})
        no_gold = evaluator.load_suite(self.file('input.csv', 'id,state,gold.decision\nfirst,State,\n', raw=True), spec=spec)
        self.assertNotIn('gold', no_gold['cases'][0])

    def test_csv_header_rows_quotes_and_spec_are_strict(self):
        spec = self.file('spec.json', {'schema_version': 1, 'questions': case()['questions']})
        for raw in ('id,state,id\na,State,a\n', 'id,state,extra\na,State,x\n',
                    'state\nState\n', 'id,state\na,State,extra\n', 'id,state\na\n',
                    'id,state\n\na,State\n', 'id,state\na,"unclosed',
                    'id,state\na,un"quoted\n', 'id,state\na,"closed"x\n',
                    'id,state,gold.nope\na,State,yes\n', 'id,state\n'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                evaluator.load_suite(self.file('input.csv', raw, raw=True), spec=spec)
        path = self.file('input.csv', 'id,state\na,State\n', raw=True)
        with self.assertRaisesRegex(ValueError, '--spec'):
            evaluator.load_suite(path)
        bad_spec = self.file('bad-spec.json', {'schema_version': 1, 'questions': case()['questions'], 'extra': 0})
        with self.assertRaises(ValueError):
            evaluator.load_suite(path, spec=bad_spec)
        with self.assertRaises(ValueError):
            evaluator.load_suite(self.file('data.json', suite()), spec=spec)


class FingerprintAndResumeTests(TemporaryFiles):
    def test_resume_relabels_supplied_results_without_trusting_provenance(self):
        report = self.execute()
        self.assertEqual(report['result_provenance'], 'local_execution')
        for claimed_provenance in ('verified', 'local_execution', 'independently_verified'):
            report['result_provenance'] = claimed_provenance
            restored = evaluator.load_resume(self.file('resume.json', report), suite())
            self.assertEqual(restored['result_provenance'], 'user_supplied_resume_plus_local_execution')
            self.assertFalse(restored['benchmark_result'])
            self.assertEqual(restored['summary']['cases_succeeded'], 1)

    def test_fingerprint_exact_canonical_wrapper(self):
        value = suite()
        expected = hashlib.sha256(json.dumps({'suite': value, 'question_order': [['decision', 'evidence']]}, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(evaluator.suite_fingerprint(value), expected)

    def test_object_key_order_ignored_question_order_preserved(self):
        value = suite()
        changed = copy.deepcopy(value)
        changed['cases'][0] = dict(reversed(list(changed['cases'][0].items())))
        self.assertEqual(evaluator.suite_fingerprint(value), evaluator.suite_fingerprint(changed))
        changed['cases'][0]['questions'] = dict(reversed(list(changed['cases'][0]['questions'].items())))
        self.assertNotEqual(evaluator.suite_fingerprint(value), evaluator.suite_fingerprint(changed))

    def test_gold_absent_and_empty_have_distinct_fingerprints(self):
        absent = suite([case(labelled=False)])
        empty = copy.deepcopy(absent); empty['cases'][0]['gold'] = {}
        self.assertNotEqual(evaluator.suite_fingerprint(absent), evaluator.suite_fingerprint(empty))

    def test_resume_only_pending_not_success_or_error(self):
        value = suite([case('first'), case('second'), case('third')])
        stop = evaluator.StopFlag()
        report = self.execute(value, FakeClient(stop=stop), stop)
        report['results'][1].update(status='error', error={'kind': 'http', 'message': 'Known fixture failure'}, elapsed_seconds=0)
        evaluator.save_report(report, self.directory / 'resume.json')
        loaded = evaluator.load_resume(self.directory / 'resume.json', value)
        client = FakeClient()
        evaluator.run_evaluation(loaded, client, self.directory / 'next.json')
        self.assertEqual(len(client.calls), 1)
        self.assertEqual([row['status'] for row in loaded['results']], ['success', 'error', 'success'])
        self.assertEqual(loaded['summary']['field_accuracy'], 2 / 3)

    def test_resume_rejects_input_and_embedded_fingerprint_changes(self):
        report = evaluator.new_report(suite())
        path = self.file('resume.json', report)
        changed = suite(); changed['cases'][0]['state'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            evaluator.load_resume(path, changed)
        report['suite']['cases'][0]['state'] += ' changed'
        self.file('resume.json', report)
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            evaluator.load_resume(path, suite())

    def test_resume_recomputes_summary_rejects_forged_success(self):
        report = evaluator.new_report(suite())
        report['summary']['field_accuracy'] = 1.0
        path = self.file('resume.json', report)
        self.assertEqual(evaluator.load_resume(path, suite())['summary']['field_accuracy'], 0)
        report['results'][0]['status'] = 'success'
        self.file('resume.json', report)
        with self.assertRaises(ValueError):
            evaluator.load_resume(path, suite())

    def test_resume_rejects_missing_duplicate_out_of_order_or_dirty_pending(self):
        for alteration in ('missing', 'id', 'pending_response', 'unknown_status', 'nan_duration'):
            report = evaluator.new_report(suite())
            if alteration == 'missing': report['results'] = []
            elif alteration == 'id': report['results'][0]['id'] = 'wrong'
            elif alteration == 'pending_response': report['results'][0]['response'] = {}
            elif alteration == 'unknown_status': report['results'][0]['status'] = 'verified'
            else: report['results'][0]['elapsed_seconds'] = -1
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                evaluator.load_resume(self.file('resume.json', report), suite())


    def test_resume_rejects_model_identity_fingerprint_tampering(self):
        report = self.execute()
        report['model_identity']['revision'] = 'different'
        with self.assertRaisesRegex(ValueError, 'identity fingerprint'):
            evaluator.load_resume(self.file('resume.json', report), suite())

    def test_resume_rejects_attempts_without_model_identity(self):
        report = self.execute()
        report['model_identity'] = None
        report['model_identity_sha256'] = None
        with self.assertRaisesRegex(ValueError, 'no pinned model identity'):
            evaluator.load_resume(self.file('resume.json', report), suite())

    def test_identity_fingerprint_exact_canonical_wrapper(self):
        report = self.execute()
        expected = hashlib.sha256(json.dumps({'suite_sha256': report['suite_sha256'],
                                              'model_identity': report['model_identity']},
                                             ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(report['model_identity_sha256'], expected)



class ResponseAndScoreTests(TemporaryFiles):
    def test_forward_latency_must_be_present_finite_nonnegative_and_numeric(self):
        for latency in (None, True, False, -1, float('nan'), float('inf'), float('-inf'), '1'):
            invalid = response()
            if latency is None:
                invalid.pop('latency_ms')
            else:
                invalid['latency_ms'] = latency
            with self.subTest(latency=latency), self.assertRaisesRegex(ValueError, 'latency'):
                evaluator.validate_response(case(), invalid)
        for latency in (0, 0.5, 1000000):
            valid = response(); valid['latency_ms'] = latency
            self.assertEqual(evaluator.validate_response(case(), valid)['latency_ms'], latency)

    def test_complete_fixture_accepted_with_option_key_mapping(self):
        self.assertIs(evaluator.validate_response(case(), response()).get('test_fixture_only'), True)

    def test_invalid_response_contract(self):
        mutations = [lambda r: r.pop('answers'), lambda r: r['answers'].pop('evidence'),
                     lambda r: r['answers'].update(extra=r['answers']['decision']),
                     lambda r: r.update(answers=dict(reversed(list(r['answers'].items())))),
                     lambda r: r['answers']['decision'].pop('confidence'),
                     lambda r: r['answers']['decision'].update(choice='absent'),
                     lambda r: r['answers']['decision'].update(confidence=0.5),
                     lambda r: r['answers']['decision'].update(confidence=True),
                     lambda r: r['answers']['decision']['probabilities'].update(yes=0.5),
                     lambda r: r['probabilities_unrounded']['decision'].update(yes=float('nan')),
                     lambda r: r['probabilities_unrounded']['decision'].update(yes=2),
                     lambda r: r['probabilities_unrounded']['decision'].pop('no'),
                     lambda r: r.update(truncated=True), lambda r: r.update(benchmark_result=True),
                     lambda r: r.update(source='archived'), lambda r: r.update(model=''),
                     lambda r: r.pop('runtime'), lambda r: r.update(device='invented'),
                     lambda r: r.update(input_tokens=2049), lambda r: r.pop('revision')]
        for number, mutate in enumerate(mutations):
            invalid = response(); mutate(invalid)
            with self.subTest(number=number), self.assertRaises(ValueError):
                evaluator.validate_response(case(), invalid)

    def test_failed_pending_and_unlabelled_denominators(self):
        first = case('first')
        partial = case('partial'); partial['gold'] = {'decision': 'yes'}
        missing = case('missing')
        unlabelled = case('unlabelled', False)
        value = suite([first, partial, missing, unlabelled])
        report = evaluator.new_report(value)
        report['results'][0].update(status='success', response=response(first))
        report['results'][1].update(status='error', error={'message': 'failure'})
        summary = evaluator.summarize(value, report['results'])
        self.assertEqual(summary['labelled_fields'], 5)
        self.assertEqual(summary['unlabelled_fields'], 3)
        self.assertEqual(summary['field_accuracy'], 2 / 5)
        self.assertEqual(summary['field_coverage'], 2 / 5)
        self.assertEqual(summary['case_accuracy'], 1 / 2)
        self.assertEqual(summary['completion_coverage'], 1 / 2)
        self.assertEqual(summary['prediction_coverage'], 1 / 4)
        self.assertEqual(summary['gold_coverage'], 5 / 8)
        self.assertEqual(summary['by_field']['decision']['labelled'], 3)
        self.assertEqual(summary['by_field']['decision']['accuracy'], 1 / 3)

    def test_no_labels_no_accuracy_claim(self):
        summary = evaluator.new_report(suite([case(labelled=False)]))['summary']
        for key in ('field_accuracy', 'field_coverage', 'case_accuracy', 'case_coverage'):
            self.assertIsNone(summary[key])
        self.assertEqual(summary['gold_coverage'], 0)

    def test_only_fully_labelled_case_counts_for_case_accuracy(self):
        partial = case(); partial['gold'].pop('evidence')
        report = self.execute(suite([partial]))
        self.assertEqual(report['summary']['field_accuracy'], 1)
        self.assertIsNone(report['summary']['case_accuracy'])


class RunAndOutputTests(TemporaryFiles):
    def test_cli_registers_and_restores_graceful_interrupt_and_terminate_handlers(self):
        original_handlers = {signal.SIGINT: object()}
        if hasattr(signal, 'SIGTERM'):
            original_handlers[signal.SIGTERM] = object()
        for fail in (False, True):
            calls = []
            def register(signum, handler):
                calls.append((signum, handler))
                return original_handlers[signum]
            def execute(report, client, output, csv_output, stop):
                self.assertEqual([signum for signum, _ in calls], list(original_handlers))
                self.assertTrue(all(handler.__self__ is stop for _, handler in calls))
                if fail:
                    raise ValueError('fixture interruption')
                report['status'] = 'completed'
            with self.subTest(fail=fail), patch.object(evaluator, 'load_suite', return_value=suite()), patch.object(evaluator, 'reserve_output'), patch.object(evaluator, 'run_evaluation', execute), patch.object(evaluator.signal, 'signal', register):
                exit_code = evaluator.main(['--input', str(self.directory / 'source.json'), '--output', str(self.directory / 'signal-report.json')])
                self.assertEqual(exit_code, 2 if fail else 0)
            self.assertEqual(calls[len(original_handlers):], list(original_handlers.items()))

    def test_csv_formula_escape_covers_python_and_browser_unicode_whitespace(self):
        for prefix in ('\ufeff', '\u0085', '\u001c', '\u001d', '\u001e', '\u001f', '\u2000', ' \ufeff\u0085'):
            for operator in ('=', '+', '-', '@'):
                value = prefix + operator + 'formula'
                with self.subTest(value=repr(value)):
                    self.assertEqual(evaluator.escape_csv(value), "'" + value)

    def test_sequential_real_wire_payload_never_contains_gold_or_model(self):
        client = FakeClient()
        report = self.execute(suite([case('first'), case('second')]), client)
        self.assertEqual(report['status'], 'completed')
        self.assertEqual(len(client.calls), 2)
        for method, path, body in client.calls:
            self.assertEqual((method, path), ('POST', '/api/infer'))
            self.assertEqual(set(body), {'state', 'questions'})
        self.assertEqual(report['summary']['field_accuracy'], 1)

    def test_each_case_checkpoint_atomic_and_private(self):
        client = FakeClient()
        real_save = evaluator.save_report
        checkpoints = []
        def save(report, output, csv_output=None):
            real_save(report, output, csv_output)
            saved = json.loads(Path(output).read_text())
            checkpoints.append(saved['summary']['cases_succeeded'])
            self.assertEqual(stat.S_IMODE(Path(output).stat().st_mode), 0o600)
        with patch.object(evaluator, 'save_report', save):
            self.execute(suite([case('first'), case('second')]), client)
        self.assertIn(1, checkpoints)
        self.assertIn(2, checkpoints)
        self.assertFalse(list(self.directory.glob('.report.json.*')))

    def test_request_has_durable_uncertain_marker_before_http(self):
        parent = self
        class CheckpointClient(FakeClient):
            def request(self, method, path, body=None):
                checkpoint = json.loads((parent.directory / 'report.json').read_text())
                row = checkpoint['results'][0]
                parent.assertEqual(row['status'], 'error')
                parent.assertEqual(row['error']['kind'], 'in_flight')
                parent.assertIsNone(row['response'])
                return super().request(method, path, body)
        report = self.execute(client=CheckpointClient())
        self.assertEqual(report['results'][0]['status'], 'success')
        self.assertIsNone(report['results'][0]['error'])

    def test_busy_and_disabled_prevent_any_post(self):
        for client in (FakeClient(busy=True), FakeClient(enabled=False)):
            with self.subTest(health=client.health_value):
                report = self.execute(client=client)
                self.assertEqual(report['status'], 'blocked')
                self.assertEqual(client.calls, [])
                self.assertEqual(report['summary']['cases_pending'], 1)

    def test_stop_finishes_current_and_preserves_future(self):
        stop = evaluator.StopFlag()
        client = FakeClient(stop=stop)
        report = self.execute(suite([case('first'), case('second')]), client, stop)
        self.assertEqual(report['status'], 'interrupted')
        self.assertEqual([row['status'] for row in report['results']], ['success', 'pending'])
        self.assertEqual(len(client.calls), 1)

    def test_health_model_identity_is_required_before_inference(self):
        client = FakeClient()
        client.health_value.pop('model_key')
        report = self.execute(client=client)
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual(client.calls, [])
        self.assertIsNone(report['model_identity'])

    def test_resume_model_switch_stops_before_post(self):
        stop = evaluator.StopFlag()
        value = suite([case('first'), case('second')])
        report = self.execute(value, FakeClient(stop=stop), stop)
        before = copy.deepcopy(report['model_identity'])
        client = FakeClient()
        client.health_value.update(model_key='clef-27b', model_id='Cloudflare/clef', model='Cloudflare/clef')
        evaluator.run_evaluation(report, client, self.directory / 'resume.json')
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual(client.calls, [])
        self.assertEqual(report['model_identity'], before)
        self.assertEqual([row['status'] for row in report['results']], ['success', 'pending'])

    def test_response_identity_changes_block_without_mixing_results(self):
        invalid = response()
        invalid.update(model_key='clef-27b', model_id='Cloudflare/clef', model='Cloudflare/clef')
        invalid['runtime'].update(model_key='clef-27b', model_id='Cloudflare/clef')
        client = FakeClient([(200, invalid)])
        report = self.execute(suite([case('first'), case('second')]), client)
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual(report['summary']['cases_succeeded'], 0)
        self.assertIn('pinned run identity', report['results'][0]['error']['message'])
        self.assertEqual(len(client.calls), 1)

    def test_http_422_counted_failed_and_continues(self):
        client = FakeClient([(422, {'error': 'fixture token budget failure'})])
        report = self.execute(suite([case('first'), case('second')]), client)
        self.assertEqual(report['status'], 'completed')
        self.assertEqual(report['summary']['field_accuracy'], 0.5)
        self.assertEqual(report['results'][0]['response']['error'], 'fixture token budget failure')
        self.assertEqual(report['results'][0]['error']['http_status'], 422)

    def test_uncertain_or_server_errors_block_without_next_post(self):
        for reply in ((409, {'error': 'busy'}), (500, {'error': 'server failed'}),
                      (302, {'message': 'redirect'}), OSError('network stopped'),
                      (200, {'answers': {}})):
            with self.subTest(reply=reply):
                client = FakeClient([reply])
                report = self.execute(suite([case('first'), case('second')]), client)
                self.assertEqual(report['status'], 'blocked')
                self.assertEqual(len(client.calls), 1)
                self.assertEqual([row['status'] for row in report['results']], ['error', 'pending'])

    def test_keyboard_interrupt_during_request_marks_uncertain_terminal_error(self):
        client = FakeClient([KeyboardInterrupt()])
        report = self.execute(suite([case('first'), case('second')]), client)
        self.assertEqual(report['status'], 'interrupted')
        self.assertEqual(report['results'][0]['error']['kind'], 'interrupted')
        self.assertEqual(len(client.calls), 1)

    def test_csv_formula_escape_and_json_lossless(self):
        for text in ('=SUM(A1)', '+1', '-1', '@cmd', '\tX', '\nX', '\rX', '  =1', '\u00a0=1'):
            with self.subTest(text=text):
                self.assertEqual(evaluator.escape_csv(text), "'" + text)
        report = evaluator.new_report(suite())
        report['results'][0].update(status='error', error={'message': '=UNSAFE()'}, elapsed_seconds=0)
        evaluator.save_report(report, self.directory / 'output.json', self.directory / 'output.csv')
        self.assertEqual(json.loads((self.directory / 'output.json').read_text())['results'][0]['error']['message'], '=UNSAFE()')
        rows = list(csv.reader(io.StringIO((self.directory / 'output.csv').read_text(encoding='utf-8-sig'))))
        self.assertEqual(rows[1][-1], "'=UNSAFE()")
        self.assertEqual(stat.S_IMODE((self.directory / 'output.csv').stat().st_mode), 0o600)

    def test_existing_output_and_symlink_refused(self):
        existing = self.file('existing.json', {'keep': True})
        with self.assertRaises(ValueError): evaluator.reserve_output(existing)
        link = self.directory / 'link.json'; link.symlink_to(existing)
        with self.assertRaises(ValueError): evaluator.atomic_private_write(link, 'bad')
        self.assertEqual(json.loads(existing.read_text()), {'keep': True})

    def test_validate_only_from_other_cwd_makes_no_http_calls(self):
        input_path = self.file('input.json', suite())
        output = self.directory / 'private' / 'report.json'
        completed = subprocess.run([sys.executable, str(ROOT / 'scripts/evaluate_custom.py'),
                                    '--input', str(input_path), '--output', str(output), '--validate-only',
                                    '--endpoint', 'http://127.0.0.1:1'], cwd=self.directory,
                                   capture_output=True, text=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(output.read_text())
        self.assertEqual(report['status'], 'validated')
        self.assertIsNone(report['endpoint'])
        self.assertTrue(all(row['response'] is None for row in report['results']))
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(output.parent.stat().st_mode), 0o700)

    def test_output_cannot_overwrite_input_or_existing_evidence(self):
        path = self.file('input.json', suite())
        self.assertEqual(evaluator.main(['--input', str(path), '--output', str(path), '--validate-only']), 2)
        output = self.file('existing.json', {'keep': True})
        self.assertEqual(evaluator.main(['--input', str(path), '--output', str(output), '--validate-only']), 2)
        self.assertEqual(json.loads(output.read_text()), {'keep': True})

    def test_import_loads_no_model_library(self):
        completed = subprocess.run([sys.executable, '-c',
            f"import sys;sys.path.insert(0,{str(ROOT)!r});from scripts import evaluate_custom;assert not any(x in sys.modules for x in ['torch','transformers','runtime.live_adapter'])"],
            capture_output=True, text=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)


class LoopbackHTTPTests(TemporaryFiles):
    def start_server(self, server):
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(lambda: (server.shutdown(), server.server_close(), thread.join()))
        return f'http://127.0.0.1:{server.server_address[1]}'

    def test_only_loopback_origins_and_no_url_payloads(self):
        for url in ('http://127.0.0.1:8765', 'http://localhost:8765/', 'http://[::1]:8765'):
            evaluator.parse_endpoint(url)
        for url in ('https://localhost:8765', 'http://example.com', 'http://127.0.0.2',
                    'http://127.0.0.1.evil', 'http://user@localhost', 'http://localhost/path',
                    'http://localhost?url=https://evil', 'http://localhost#x',
                    'http://localhost:0', 'http://localhost:99999', 'file:///tmp/file',
                    'http://localhost\n:8765', 'http://[::ffff:127.0.0.1]'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                evaluator.parse_endpoint(url)

    def test_real_handler_validates_headers_and_exact_wire_contract(self):
        received = []
        class FixtureRuntime:
            def status(self): return {'state': 'ready', 'runtime': {'device': 'test-double'}}
            def infer(self, request):
                received.append(request)
                return response(request)
        app = Workbench(True, Path('.'), lambda _: FixtureRuntime())
        original_health = app.health
        app.health = lambda: {**original_health(), 'model_key': 'flash-9b', 'model_id': 'Cloudflare/clef-flash',
                              'model': 'Cloudflare/clef-flash', 'revision': 'test-double-only'}
        server = make_server(0, app)
        client = evaluator.LocalClient(self.start_server(server), timeout=3)
        report = self.execute(client=client)
        self.assertEqual(report['status'], 'completed')
        self.assertEqual(report['summary']['cases_succeeded'], 1)
        self.assertEqual(set(received[0]), {'model', 'state', 'questions'})
        self.assertEqual(received[0]['model'], 'clef-flash')

    def test_redirect_is_returned_never_followed_and_proxy_ignored(self):
        paths = []
        class RedirectHandler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_GET(self):
                paths.append(self.path)
                self.send_response(302)
                self.send_header('Location', 'http://example.com/forbidden')
                self.end_headers()
                self.wfile.write(b'{"redirect":true}')
        client = evaluator.LocalClient(self.start_server(ThreadingHTTPServer(('127.0.0.1', 0), RedirectHandler)), timeout=3)
        with patch.dict(os.environ, {'http_proxy': 'http://example.com:9', 'HTTP_PROXY': 'http://example.com:9'}):
            status, value = client.request('GET', '/api/health')
        self.assertEqual(status, 302)
        self.assertEqual(value, {'redirect': True})
        self.assertEqual(paths, ['/api/health'])

    @unittest.skipUnless(hasattr(signal, 'SIGINT'), 'SIGINT unavailable')
    def test_sigint_cli_keeps_current_response_and_stops_next_request(self):
        entered, release = threading.Event(), threading.Event()
        calls = []
        class SlowHandler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def send(self, data):
                encoded = json.dumps(data).encode()
                self.send_response(200); self.send_header('Content-Length', str(len(encoded)))
                self.end_headers(); self.wfile.write(encoded)
            def do_GET(self): self.send(FakeClient().health())
            def do_POST(self):
                request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                calls.append(request); entered.set(); release.wait(5)
                self.send(response(request))
        endpoint = self.start_server(ThreadingHTTPServer(('127.0.0.1', 0), SlowHandler))
        source = self.file('input.json', suite([case('first'), case('second')]))
        target = self.directory / 'interrupted.json'
        process = subprocess.Popen([sys.executable, str(ROOT / 'scripts/evaluate_custom.py'),
                                    '--input', str(source), '--output', str(target), '--endpoint', endpoint],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertTrue(entered.wait(5), 'CLI never reached the test server')
            process.send_signal(signal.SIGINT)
            # Reading its acknowledged stop ensures the signal was handled
            # before releasing the in-flight response; no timing assumptions.
            acknowledgement = process.stderr.readline()
            self.assertIn('Stopping after', acknowledgement)
            release.set()
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 130, stdout + stderr)
            report = json.loads(target.read_text())
            self.assertEqual(report['status'], 'interrupted')
            self.assertEqual([row['status'] for row in report['results']], ['success', 'pending'])
            self.assertEqual(len(calls), 1)
        finally:
            release.set()
            if process.poll() is None:
                process.kill(); process.communicate(timeout=5)

    def test_invalid_duplicate_json_response_retained_as_hex(self):
        class BrokenHandler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_GET(self):
                self.send_response(200); self.end_headers()
                self.wfile.write(b'{"a":1,"a":2}')
        client = evaluator.LocalClient(self.start_server(ThreadingHTTPServer(('127.0.0.1', 0), BrokenHandler)), timeout=3)
        status, value = client.request('GET', '/api/health')
        self.assertEqual(status, 200)
        self.assertEqual(bytes.fromhex(value['invalid_response_utf8_hex']), b'{"a":1,"a":2}')


if __name__ == '__main__':
    unittest.main()
