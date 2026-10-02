"""Bounded multi-field API regression. Test doubles only; no ML imports or inference."""
from contextlib import nullcontext
from copy import deepcopy
import ast
import http.client
import json
from pathlib import Path
import sys
import threading
from types import SimpleNamespace
from typing import Any
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime.device_profiles import resolve_profile
from runtime.live_adapter import ClefRuntime
from server import MAX_BODY, MAX_QUESTIONS, Workbench, make_server, validate_request, validate_result


REQUEST = {
    'state': 'Synthetischer Vertrag: Hausrat ist versichert. Fundstelle: Abschnitt 2.',
    'questions': {
        'decision': {'type': 'choice', 'instructions': 'Welcher Schutz ist genannt?',
                     'criteria': {'hausrat': 'Hausratversicherung', 'other': 'Andere Versicherung'}},
        'evidence': {'type': 'choice', 'instructions': 'Wähle die passende Fundstelle.',
                     'criteria': {'section_1': 'Abschnitt 1', 'section_2': 'Abschnitt 2', 'absent': 'Nicht angegeben'}},
    },
}


def native_answer(question, probabilities):
    choice = max(probabilities, key=probabilities.get)
    return {'type': 'choice', 'choice': choice, 'confidence': round(probabilities[choice], 4),
            'probabilities': {key: round(value, 4) for key, value in probabilities.items()}}


def mock_values(probabilities):
    values = MagicMock()
    values.float.return_value.softmax.return_value.tolist.return_value = probabilities
    return values


def stub_runtime(request=None):
    """Run the production adapter around a stub model, tokenizer and encoder."""
    request = request or REQUEST
    runtime = ClefRuntime(Path('.'))
    runtime._torch = SimpleNamespace(__version__='test-double', version=SimpleNamespace(hip=None),
                                      inference_mode=nullcontext, device=lambda value: value)
    runtime._runtime_info = resolve_profile(runtime._torch)
    runtime._processor = SimpleNamespace(tokenizer=SimpleNamespace(pad_token_id=0))
    encoded = SimpleNamespace(input_ids=[1, 2, 3], questions=[
        SimpleNamespace(question_id=name, option_ids=sorted(question['criteria']))
        for name, question in request['questions'].items()])
    # Different winners and option counts expose field/option mixing.
    logits = [mock_values([0.75, 0.25]), mock_values([0.1, 0.1, 0.8])]
    if len(encoded.questions) != 2:
        logits = [mock_values([1 / len(q.option_ids)] * len(q.option_ids)) for q in encoded.questions]
    runtime._model = MagicMock(return_value=[logits])
    runtime._vendor = SimpleNamespace(encode_record=MagicMock(return_value=encoded),
                                      collate_records=MagicMock(return_value='stub-batch'),
                                      systemone_answer=MagicMock(side_effect=native_answer))
    runtime._ensure_loaded = MagicMock()
    runtime._state = 'ready'
    return runtime, encoded


class MultiFieldValidationTests(unittest.TestCase):
    def test_accepts_one_two_and_maximum_fields_in_input_order(self):
        for count in (1, 2, MAX_QUESTIONS):
            request = deepcopy(REQUEST)
            request['questions'] = {f'field_{i}': deepcopy(REQUEST['questions']['decision']) for i in range(count)}
            with self.subTest(count=count):
                clean = validate_request(request)
                self.assertEqual(list(clean['questions']), list(request['questions']))
                self.assertEqual(clean['model'], 'clef-flash')

    def test_rejects_empty_excessive_or_nonobject_questions(self):
        for questions in ({}, [], None, {'field_' + str(i): REQUEST['questions']['decision'] for i in range(MAX_QUESTIONS + 1)}):
            with self.subTest(questions=type(questions).__name__), self.assertRaises(ValueError):
                validate_request({**REQUEST, 'questions': questions})

    def test_checks_bounds_and_schema_of_every_field_not_only_decision(self):
        for replacement in (
            {'type': 'score'}, {'instructions': ' '}, {'instructions': 'a' * 4001},
            {'criteria': {'a': 'Only one'}}, {'criteria': {f'opt{i}': 'x' for i in range(13)}},
            {'criteria': {'a': 'x' * 301, 'b': 'b'}}, {'criteria': {'a': ' ', 'b': 'b'}},
            {'criteria': {'0invalid': 'A', 'b': 'B'}}, {'criteria': {1: 'A', 'b': 'B'}},
            {'images': ['example.png']}, {'expected': 'section_2'},
        ):
            request = deepcopy(REQUEST)
            request['questions']['evidence'].update(replacement)
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                validate_request(request)

    def test_accepts_existing_per_field_boundaries(self):
        request = deepcopy(REQUEST)
        request['state'] = 'a' * 6000
        request['questions']['evidence']['instructions'] = 'b' * 4000
        request['questions']['evidence']['criteria'] = {f'option{i}': 'c' * 300 for i in range(12)}
        self.assertEqual(validate_request(request)['questions'], request['questions'])

    def test_question_ids_and_media_restrictions_still_apply(self):
        for name in (1, '', '1wrong', 'a' * 65):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_request({**REQUEST, 'questions': {name: REQUEST['questions']['decision']}})
        for extra in ('images', 'videos', 'image_url', 'expected', 'model'):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                validate_request({**REQUEST, extra: 'not allowed'})
        with self.assertRaises(ValueError):
            validate_request({**REQUEST, 'state': {'image': 'not text'}})


class MultiFieldAdapterTests(unittest.TestCase):
    def test_choice_option_sorting_matches_pinned_vendor_without_importing_torch(self):
        source = Path(__file__).resolve().parents[1] / 'runtime/joint_schema_model.py'
        helper = next(node for node in ast.parse(source.read_text()).body
                      if isinstance(node, ast.FunctionDef) and node.name == 'question_options')
        namespace = {'Any': Any}
        before = 'torch' in sys.modules
        exec(compile(ast.Module(body=[helper], type_ignores=[]), str(source), 'exec'), namespace)
        question = REQUEST['questions']['evidence']
        self.assertEqual([key for key, _ in namespace['question_options'](question)], ['absent', 'section_1', 'section_2'])
        runtime, encoded = stub_runtime()
        self.assertEqual(encoded.questions[1].option_ids, ['absent', 'section_1', 'section_2'])
        self.assertEqual(runtime.infer(REQUEST)['answers']['evidence']['choice'], 'section_2')
        self.assertEqual('torch' in sys.modules, before)

    def test_every_field_survives_adapter_and_keeps_probabilities(self):
        runtime, _ = stub_runtime()
        result = runtime.infer(validate_request(REQUEST))
        self.assertEqual(list(result['answers']), ['decision', 'evidence'])
        self.assertEqual(result['answers']['decision']['choice'], 'hausrat')
        self.assertEqual(result['answers']['evidence']['choice'], 'section_2')
        self.assertEqual(result['probabilities_unrounded']['evidence'], {'section_1': 0.1, 'section_2': 0.8, 'absent': 0.1})
        self.assertFalse(result['truncated'])
        self.assertFalse(result['benchmark_result'])
        self.assertEqual(result['runtime']['backend'], 'cpu')
        self.assertEqual(runtime.status()['successful_requests'], 1)
        self.assertEqual(runtime._vendor.systemone_answer.call_count, 2)
        validate_result(REQUEST, result)

    def test_maximum_question_count_survives_adapter(self):
        request = deepcopy(REQUEST)
        request['questions'] = {f'field{i}': deepcopy(REQUEST['questions']['decision']) for i in range(MAX_QUESTIONS)}
        runtime, _ = stub_runtime(request)
        result = runtime.infer(validate_request(request))
        self.assertEqual(list(result['answers']), list(request['questions']))
        self.assertEqual(len(result['probabilities_unrounded']), MAX_QUESTIONS)

    def test_missing_extra_duplicate_or_reordered_encoded_fields_refused_before_forward(self):
        for kind in ('missing', 'extra', 'duplicate', 'reordered'):
            runtime, encoded = stub_runtime()
            if kind == 'missing': encoded.questions.pop()
            if kind == 'extra': encoded.questions.append(SimpleNamespace(question_id='unexpected', option_ids=['a', 'b']))
            if kind == 'duplicate': encoded.questions[1] = encoded.questions[0]
            if kind == 'reordered': encoded.questions.reverse()
            with self.subTest(kind=kind), self.assertRaisesRegex(RuntimeError, 'Encoded questions'):
                runtime.infer(REQUEST)
            runtime._model.assert_not_called()
            self.assertEqual(runtime.status()['successful_requests'], 0)

    def test_missing_extra_duplicate_or_reordered_options_refused_before_forward(self):
        for options in (['section_1', 'section_2'], ['section_1', 'section_2', 'absent', 'extra'],
                        ['section_1', 'section_1', 'absent'], ['absent', 'section_2', 'section_1']):
            runtime, encoded = stub_runtime()
            encoded.questions[1].option_ids = options
            with self.subTest(options=options), self.assertRaisesRegex(RuntimeError, 'Encoded choice options'):
                runtime.infer(REQUEST)
            runtime._model.assert_not_called()

    def test_both_encoder_passes_are_checked(self):
        runtime, encoded = stub_runtime()
        bounded = deepcopy(encoded)
        bounded.questions.pop()
        runtime._vendor.encode_record.side_effect = [encoded, bounded]
        with self.assertRaisesRegex(RuntimeError, 'Encoded questions'):
            runtime.infer(REQUEST)
        runtime._model.assert_not_called()

    def test_missing_or_extra_model_question_outputs_refused(self):
        for count in (0, 1, 3):
            runtime, _ = stub_runtime()
            runtime._model.return_value = [[mock_values([0.75, 0.25])] * count]
            with self.subTest(count=count), self.assertRaisesRegex(RuntimeError, 'question count'):
                runtime.infer(REQUEST)
            self.assertEqual(runtime.status()['successful_requests'], 0)

    def test_wrong_batch_count_refused(self):
        for output in ([], [[], []], None):
            runtime, _ = stub_runtime()
            runtime._model.return_value = output
            with self.subTest(output=output), self.assertRaisesRegex(RuntimeError, 'batch count'):
                runtime.infer(REQUEST)
            self.assertEqual(runtime.status()['successful_requests'], 0)

    def test_missing_extra_and_nonfinite_option_probabilities_refused(self):
        for probabilities in ([1.0], [0.5, 0.5, 0.0], [float('nan'), 0.0], [float('inf'), 0.0],
                              [-0.1, 1.1], [0.5, 0.6], [[0.5], [0.5]], [True, False]):
            runtime, _ = stub_runtime()
            runtime._model.return_value[0][0] = mock_values(probabilities)
            with self.subTest(probabilities=probabilities), self.assertRaises(RuntimeError):
                runtime.infer(REQUEST)
            self.assertEqual(runtime.status()['successful_requests'], 0)

    def test_invalid_native_answers_refused(self):
        for answer in ({}, None, {'type': 'choice', 'choice': 'not-an-option'}):
            runtime, _ = stub_runtime()
            runtime._vendor.systemone_answer.side_effect = None
            runtime._vendor.systemone_answer.return_value = answer
            with self.subTest(answer=answer), self.assertRaisesRegex(RuntimeError, 'invalid choice'):
                runtime.infer(REQUEST)
            self.assertEqual(runtime.status()['successful_requests'], 0)

    def test_token_limit_and_no_truncation_remain_enforced(self):
        runtime, encoded = stub_runtime()
        encoded.input_ids = list(range(2049))
        with self.assertRaisesRegex(ValueError, 'maximum is 2048.*Nothing was truncated'):
            runtime.infer(REQUEST)
        runtime._model.assert_not_called()
        runtime, encoded = stub_runtime()
        bounded = deepcopy(encoded)
        bounded.input_ids.pop()
        runtime._vendor.encode_record.side_effect = [encoded, bounded]
        with self.assertRaisesRegex(RuntimeError, 'truncation detected'):
            runtime.infer(REQUEST)
        runtime._model.assert_not_called()

    def test_exact_token_limit_is_accepted(self):
        runtime, encoded = stub_runtime()
        encoded.input_ids = list(range(2048))
        result = runtime.infer(REQUEST)
        self.assertEqual(result['input_tokens'], 2048)
        self.assertFalse(result['truncated'])


class MultiFieldHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime, _ = stub_runtime()
        cls.app = Workbench(True, Path('.'), lambda _: cls.runtime)
        cls.server = make_server(0, app=cls.app)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.runtime, self.encoded = stub_runtime()
        self.app.runtime = self.runtime

    def call(self, body, headers=None):
        headers = headers or {'Content-Type': 'application/json', 'X-Clef-Request': '1',
                              'Origin': f'http://127.0.0.1:{self.port}'}
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        try:
            conn.request('POST', '/api/infer', body, headers)
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), json.loads(response.read())
        finally:
            conn.close()

    def test_full_http_adapter_path_returns_every_field_and_security_headers(self):
        status, headers, result = self.call(json.dumps(REQUEST))
        self.assertEqual(status, 200)
        self.assertEqual(list(result['answers']), ['decision', 'evidence'])
        self.assertEqual(result['answers']['evidence']['choice'], 'section_2')
        self.assertEqual(result['source'], 'live_local_inference')
        self.assertFalse(result['benchmark_result'])
        self.assertEqual(result['runtime']['backend'], 'cpu')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertIn("connect-src 'self'", headers['Content-Security-Policy'])
        self.assertNotIn('Access-Control-Allow-Origin', headers)

    def test_http_question_bounds_are_checked_before_runtime(self):
        for count in (0, MAX_QUESTIONS + 1):
            request = deepcopy(REQUEST)
            request['questions'] = {f'q{i}': REQUEST['questions']['decision'] for i in range(count)}
            with self.subTest(count=count):
                self.assertEqual(self.call(json.dumps(request))[0], 400)
        self.runtime._ensure_loaded.assert_not_called()

    def test_http_maximum_fields_complete(self):
        request = deepcopy(REQUEST)
        request['questions'] = {f'q{i}': deepcopy(REQUEST['questions']['decision']) for i in range(MAX_QUESTIONS)}
        self.app.runtime, _ = stub_runtime(request)
        status, _, result = self.call(json.dumps(request))
        self.assertEqual(status, 200)
        self.assertEqual(list(result['answers']), list(request['questions']))

    def test_duplicate_json_keys_are_refused_instead_of_overwritten(self):
        original = json.dumps(REQUEST)
        payloads = [original.replace('"questions":', '"state":"overwritten", "questions":', 1),
                    original.replace('"evidence":', '"decision": {}, "evidence":', 1),
                    original.replace('"section_2":', '"section_1":"overwritten", "section_2":', 1)]
        for body in payloads:
            with self.subTest(body=body):
                self.assertEqual(self.call(body)[0], 400)
        self.runtime._ensure_loaded.assert_not_called()

    def test_incomplete_adapter_logits_return_error_without_partial_answers(self):
        self.runtime._model.return_value[0].pop()
        with patch('traceback.print_exc'):
            status, _, result = self.call(json.dumps(REQUEST))
        self.assertEqual(status, 500)
        self.assertNotIn('answers', result)
        self.assertNotIn('probabilities_unrounded', result)
        self.assertFalse(self.app.lock.locked())
        self.app.runtime, _ = stub_runtime()
        status, _, result = self.call(json.dumps(REQUEST))
        self.assertEqual(status, 200)
        self.assertEqual(list(result['answers']), list(REQUEST['questions']))

    def test_alternate_runtime_cannot_return_incomplete_or_invalid_results(self):
        complete = self.runtime.infer(REQUEST)
        mutations = []
        for field in ('answers', 'probabilities_unrounded'):
            invalid = deepcopy(complete)
            invalid[field].pop('evidence')
            mutations.append(invalid)
        invalid = deepcopy(complete)
        invalid['probabilities_unrounded']['evidence'].pop('absent')
        mutations.append(invalid)
        invalid = deepcopy(complete)
        invalid['answers']['evidence']['choice'] = 'not-an-option'
        mutations.append(invalid)
        for invalid in mutations:
            self.app.runtime = SimpleNamespace(infer=lambda request: invalid)
            with self.subTest(invalid=invalid), patch('traceback.print_exc'):
                status, _, result = self.call(json.dumps(REQUEST))
            self.assertEqual(status, 500)
            self.assertNotIn('answers', result)

    def test_token_overflow_is_422_without_partial_answers(self):
        self.encoded.input_ids = list(range(2049))
        status, _, result = self.call(json.dumps(REQUEST))
        self.assertEqual(status, 422)
        self.assertNotIn('answers', result)
        self.assertIn('Nothing was truncated', result['error'])
        self.runtime._model.assert_not_called()
        self.assertFalse(self.app.lock.locked())

    def test_media_origins_headers_host_and_body_limit_remain_restricted(self):
        for media in ('images', 'videos', 'image_url'):
            with self.subTest(media=media):
                self.assertEqual(self.call(json.dumps({**REQUEST, media: ['file.png']}))[0], 400)
        headers = {'Content-Type': 'application/json', 'X-Clef-Request': '1', 'Origin': 'https://example.invalid'}
        self.assertEqual(self.call(json.dumps(REQUEST), headers)[0], 403)
        self.assertEqual(self.call(json.dumps(REQUEST), {'Content-Type': 'application/json'})[0], 415)
        self.assertEqual(self.call(json.dumps(REQUEST), {**headers, 'Host': f'example.invalid:{self.port}'})[0], 403)
        self.assertEqual(self.call(' ' * (MAX_BODY + 1))[0], 413)
        self.runtime._ensure_loaded.assert_not_called()


if __name__ == '__main__':
    unittest.main()
