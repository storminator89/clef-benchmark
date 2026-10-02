"""Model-free insurance importer regression and publication-gate tests.

Synthetic predictions below exist only in temporary directories; never ship them.
The checked-in UI input is the actual, authored insurance benchmark.
"""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('insurance_import', ROOT / 'scripts/build_insurance_web_data.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


def vendor_function(name):
    """Extract only a pure vendor helper; importing the model would load torch."""
    source = ast.parse((ROOT / 'runtime/joint_schema_model.py').read_text())
    function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == name)
    isolated = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {'json': json, 'Any': object}
    exec(compile(isolated, '<vendor-pure-helper>', 'exec'), namespace)
    return namespace[name]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def write_lines(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n' for row in rows), encoding='utf-8')


class InsuranceImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui = json.loads((ROOT / 'web/data/insurance.json').read_text())
        cls.render = staticmethod(vendor_function('render'))
        cls.answer = staticmethod(vendor_function('systemone_answer'))
        cls.original_keys = ('id', 'document_id', 'area', 'scenario', 'claim', 'expected',
                             'rationale', 'tags', 'evidence_options', 'decision_options')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.benchmark = {'metadata': copy.deepcopy(self.ui['metadata']),
                          'documents': copy.deepcopy(self.ui['documents']),
                          'cases': [{key: copy.deepcopy(case[key]) for key in self.original_keys} for case in self.ui['cases']]}
        self.requests = [{'id': case['id'], 'request': {'model': 'clef-flash', 'state': json.loads(case['input']),
                                                       'questions': copy.deepcopy(case['questions'])}} for case in self.ui['cases']]
        write_json(self.base / 'benchmark.json', self.benchmark)
        write_lines(self.base / 'requests.jsonl', self.requests)
        self.raw = []
        for index, (case, request) in enumerate(zip(self.benchmark['cases'], self.requests)):
            fields = {}
            answers = {}
            for field in importer.FIELDS:
                options = case[field + '_options']
                choice = case['expected'][field]
                if (index == 0 and field == 'decision') or (index == 1 and field == 'evidence'):
                    choice = next(key for key in options if key != choice)
                confidence = .6234567890123456
                probs = {key: confidence if key == choice else (1 - confidence) / (len(options) - 1) for key in options}
                fields[field] = probs
                answers[field] = self.answer(request['request']['questions'][field], probs)
            seconds = .100000012345678 + index / 10
            self.raw.append({'id': case['id'], 'answers': answers, 'probabilities_unrounded': fields,
                             'input_tokens': 600 + index, 'truncated': False, 'inference_seconds': seconds,
                             'encode_seconds': .00123456789, 'latency_ms': seconds * 1000, 'rss_bytes': 1_000_000})
        write_lines(self.base / 'predictions.jsonl', self.raw)
        self.metadata = {'status': 'completed', 'model': importer.MODEL, 'revision': importer.REVISION,
                         'started_at': '2026-10-02T00:00:00Z', 'completed_at': '2026-10-02T01:00:00Z',
                         'request_count': 60, 'requests_sha256': importer.digest(self.base / 'requests.jsonl'),
                         'request_order_ids': [row['id'] for row in self.requests], 'max_length': 2048,
                         'benchmark_requests_only_no_gold': True, 'source_code_sha256': importer.OFFICIAL_SOURCE_SHA256,
                         'test_fixture_only': True}
        self.save_valid_results()

    def save_valid_results(self):
        write_lines(self.base / 'predictions.jsonl', self.raw)
        write_json(self.base / 'predictions.metadata.json', self.metadata)
        self.results = {'status': 'completed', 'schema_version': '1.0.0', 'benchmark': self.benchmark['metadata'],
                        'run_metadata': self.metadata, **importer.recompute(self.benchmark, self.raw),
                        'input_hashes': {key: importer.digest(self.base / filename) for key, filename in
                                         (('benchmark', 'benchmark.json'), ('predictions', 'predictions.jsonl'),
                                          ('metadata', 'predictions.metadata.json'))}}
        write_json(self.base / 'results.json', self.results)
        self.refresh_gate()

    def refresh_gate(self):
        self.gate = {'status': 'verified', 'verified_at': '2026-10-02T02:00:00Z', 'case_count': 60, 'field_count': 120,
                     'pre_inference_audit': 'pass', 'post_inference_audit': 'pass', 'no_truncation': True,
                     'single_primary_run': True, 'input_hashes': {name: importer.digest(self.base / name) for name in
                        ('benchmark.json', 'requests.jsonl', 'results.json', 'predictions.jsonl', 'predictions.metadata.json')}}
        write_json(self.base / 'verification.json', self.gate)

    def edit(self, name, function, refresh=False):
        path = self.base / name
        value = json.loads(path.read_text())
        function(value)
        write_json(path, value)
        if refresh:
            self.refresh_gate()

    def rejected(self):
        with self.assertRaises(ValueError):
            importer.build(self.base)

    def test_completed_native_two_field_results(self):
        data = importer.build(self.base)
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['schema_version'], 2)
        self.assertEqual(data['suite']['id'], 'insurance')
        self.assertEqual(data['suite']['primary_split'], 'german_insurance_primary')
        self.assertEqual(data['summary']['decision']['correct'], 59)
        self.assertEqual(data['summary']['evidence']['correct'], 59)
        self.assertEqual(data['summary']['exact_case']['correct'], 58)
        self.assertEqual(data['summary']['field_accuracy']['correct'], 118)
        self.assertEqual(data['documents'], self.benchmark['documents'])
        for case, raw, original in zip(data['cases'], self.raw, self.benchmark['cases']):
            for key in self.original_keys:
                self.assertEqual(case[key], original[key])
            self.assertEqual(case['category'], original['area'])
            self.assertEqual(case['title'], original['claim'])
            self.assertEqual(case['gold_rationale'], original['rationale'])
            self.assertEqual(set(case['result']['fields']), {'decision', 'evidence'})
            self.assertIs(case['result']['schema_valid'], True)
            self.assertEqual(case['latency_ms'], raw['latency_ms'])
            self.assertEqual(case['input_tokens'], raw['input_tokens'])
            for field in importer.FIELDS:
                result = case['result']['fields'][field]
                self.assertEqual(result['probabilities'], raw['probabilities_unrounded'][field])
                self.assertNotEqual(result['probabilities'], raw['answers'][field]['probabilities'])
                self.assertEqual(result['prediction'], raw['answers'][field]['choice'])
                self.assertIs(result['schema_valid'], True)
            expected_clauses = original['evidence_options'][raw['answers']['evidence']['choice']]
            self.assertEqual(case['result']['actual_evidence_clauses'], expected_clauses)
        self.assertFalse(data['cases'][0]['result']['correct'])
        self.assertFalse(data['cases'][1]['result']['correct'])
        self.assertTrue(data['cases'][2]['result']['correct'])

    def test_every_request_is_vendor_render_identical(self):
        data = importer.build(self.base, cases_only=True)
        for case, request in zip(data['cases'], self.requests):
            original = request['request']
            self.assertEqual(case['input'], self.render(original['state']))
            self.assertEqual(self.render(case['input']), self.render(original['state']))
            self.assertEqual(json.loads(case['input']), original['state'])
            self.assertEqual(case['questions'], original['questions'])

    def test_cases_only_never_exposes_results(self):
        self.benchmark['cases'][0].update(result={'correct': True}, latency_ms=12, input_tokens=700)
        write_json(self.base / 'benchmark.json', self.benchmark)
        (self.base / 'verification.json').unlink()
        data = importer.build(self.base, cases_only=True)
        self.assertEqual(data['status'], 'test_data_only')
        self.assertEqual(data['verification']['status'], 'pending')
        self.assertEqual(data['run_metadata'], {})
        for key in ('summary', 'scores', 'by_area', 'by_document', 'model'):
            self.assertNotIn(key, data)
        for case in data['cases']:
            for key in ('result', 'latency_ms', 'input_tokens'):
                self.assertNotIn(key, case)

    def test_deterministic_output_and_source_is_unchanged(self):
        before = {path.name: path.read_bytes() for path in self.base.iterdir()}
        self.assertEqual(importer.build(self.base), importer.build(self.base))
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.base.iterdir()})

    def test_pending_or_incomplete_gate_rejected(self):
        for field, value in [('status', 'pending'), ('case_count', 59), ('field_count', 119),
                             ('pre_inference_audit', 'pending'), ('post_inference_audit', 'pending'),
                             ('no_truncation', False), ('single_primary_run', False), ('verified_at', '')]:
            with self.subTest(field=field):
                self.refresh_gate()
                self.edit('verification.json', lambda data: data.update({field: value}))
                self.rejected()

    def test_each_missing_gate_artifact_rejected(self):
        for name in ('verification.json', 'benchmark.json', 'requests.jsonl', 'results.json', 'predictions.jsonl', 'predictions.metadata.json'):
            with self.subTest(name=name):
                path = self.base / name
                content = path.read_bytes()
                path.unlink()
                self.rejected()
                path.write_bytes(content)

    def test_each_corrupted_gate_hash_rejected(self):
        for name in self.gate['input_hashes']:
            with self.subTest(name=name):
                self.refresh_gate()
                self.edit('verification.json', lambda data: data['input_hashes'].update({name: '0' * 64}))
                self.rejected()

    def test_running_or_wrong_model_metadata_rejected(self):
        for field, value in [('status', 'running'), ('model', 'another-model'), ('revision', 'wrong'),
                             ('request_count', 59), ('requests_sha256', 'bad'), ('source_code_sha256', 'bad'), ('request_order_ids', []),
                             ('max_length', 4096), ('benchmark_requests_only_no_gold', False), ('completed_at', None)]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.metadata)
                self.metadata[field] = value
                self.save_valid_results()
                self.rejected()
                self.metadata = original

    def test_score_corruption_rejected_even_with_refreshed_hash_gate(self):
        mutations = [lambda result: result['summary']['decision'].update(correct=60),
                     lambda result: result['summary']['field_accuracy'].update(accuracy=1),
                     lambda result: result['cases'][0]['correct'].update(exact_case=True),
                     lambda result: result['cases'][0]['correct'].update(exact_case=0),
                     lambda result: result['cases'][0]['actual'].update(decision='invented'),
                     lambda result: result['cases'][0]['probabilities']['decision'].update(ja=.123),
                     lambda result: result['cases'][0].update(actual_evidence_clauses=['BAD']),
                     lambda result: result.update(by_document={}),
                     lambda result: result.update(date_version_subset={}),
                     lambda result: result.update(cases=result['cases'][:-1]),
                     lambda result: result.update(status='running')]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                self.save_valid_results()
                self.edit('results.json', mutate, refresh=True)
                self.rejected()

    def test_partial_extra_invalid_and_truncated_raw_results_rejected(self):
        mutations = [lambda row: row['answers'].pop('evidence'),
                     lambda row: row['probabilities_unrounded'].pop('decision'),
                     lambda row: row['answers'].update(extra={}),
                     lambda row: row['answers']['decision'].pop('type'),
                     lambda row: row['answers']['decision'].update(confidence=.9),
                     lambda row: row['probabilities_unrounded']['decision'].update(unknown=0),
                     lambda row: row['probabilities_unrounded']['decision'].update(ja=-.1),
                     lambda row: row['probabilities_unrounded']['decision'].update(ja=True),
                     lambda row: row.update(truncated=True),
                     lambda row: row.update(input_tokens=2049),
                     lambda row: row.update(latency_ms=-1),
                     lambda row: row.update(latency_ms=row['latency_ms'] + 1)]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                raw = copy.deepcopy(self.raw)
                mutate(raw[0])
                write_lines(self.base / 'predictions.jsonl', raw)
                self.edit('results.json', lambda data: data['input_hashes'].update(predictions=importer.digest(self.base / 'predictions.jsonl')), refresh=True)
                self.rejected()

    def test_unknown_duplicate_missing_and_reordered_predictions_rejected(self):
        rows = copy.deepcopy(self.raw)
        rows[0]['id'] = 'unknown'
        for raw in (rows, self.raw[:-1], self.raw + self.raw[:1], list(reversed(self.raw))):
            with self.subTest(count=len(raw), first=raw[0]['id']):
                write_lines(self.base / 'predictions.jsonl', raw)
                self.refresh_gate()
                self.rejected()

    def test_request_document_gold_and_schema_mismatch_rejected(self):
        mutations = [lambda row: row['request']['state'].update(sachverhalt='Wrong scenario'),
                     lambda row: row['request']['state']['unterlagen'][0].update(text='Wrong clause'),
                     lambda row: row['request']['questions'].pop('evidence'),
                     lambda row: row['request']['questions']['decision']['criteria'].update(ja='Wrong option'),
                     lambda row: row['request']['state'].update(expected='ja'),
                     lambda row: row.update(gold='ja')]
        for mutate in mutations:
            rows = copy.deepcopy(self.requests)
            mutate(rows[0])
            write_lines(self.base / 'requests.jsonl', rows)
            with self.assertRaises(ValueError):
                importer.build(self.base, cases_only=True)

    def test_duplicate_json_keys_and_nonfinite_values_rejected(self):
        for text in ('{"metadata": {}, "metadata": {}}', '{"bad": NaN}', '{"bad": Infinity}', '{'):
            (self.base / 'benchmark.json').write_text(text)
            with self.assertRaises(ValueError):
                importer.build(self.base, cases_only=True)

    def test_source_metadata_hash_and_embedded_metadata_mismatch_rejected(self):
        self.edit('results.json', lambda data: data['input_hashes'].update(metadata='bad'), refresh=True)
        self.rejected()
        self.save_valid_results()
        self.edit('predictions.metadata.json', lambda data: data.update(device='different'), refresh=True)
        self.rejected()

    def test_cli_failure_does_not_replace_existing_output(self):
        output = self.base / 'output.json'
        output.write_text('preserve me')
        (self.base / 'verification.json').unlink()
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_insurance_web_data.py'),
                                 '--source', str(self.base), '--out', str(output)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_text(), 'preserve me')
        self.assertFalse(output.with_suffix('.json.tmp').exists())

    def test_actual_export_manifest_and_shipped_ui_match(self):
        package = ROOT / 'experiments/insurance'
        public = package / 'public'
        manifest = json.loads((package / 'EXPORT_MANIFEST.json').read_text())
        self.assertIs(manifest['public_safe'], True)
        self.assertEqual(importer.digest(package / 'EXPORT_MANIFEST.json'),
                         '64c66048012c8bb67197cf5e6c1fdf48a9eb5b9308a6a14801ac4be62373a851')
        actual_files = {str(path.relative_to(package)) for path in package.rglob('*') if path.is_file()}
        self.assertEqual(actual_files, set(manifest['files']) | {'EXPORT_MANIFEST.json'})
        for name, metadata in manifest['files'].items():
            self.assertEqual(importer.digest(package / name), metadata['sha256'], name)
            self.assertEqual((package / name).stat().st_size, metadata['bytes'], name)
        data = importer.build(package)
        generated = (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
        self.assertEqual(generated, (ROOT / 'web/data/insurance.json').read_bytes())
        self.assertEqual(data['summary']['decision']['correct'], 51)
        self.assertEqual(data['summary']['evidence']['correct'], 58)
        self.assertEqual(data['summary']['exact_case']['correct'], 50)
        self.assertEqual(data['summary']['field_accuracy']['correct'], 109)
        actual_benchmark = json.loads((public / 'benchmark.json').read_text())
        actual_requests = {row['id']: row['request'] for row in importer.load_json(public / 'requests.jsonl', jsonl=True)}
        actual_predictions = {row['id']: row for row in importer.load_json(public / 'predictions.jsonl', jsonl=True)}
        self.assertEqual(data['documents'], actual_benchmark['documents'])
        for case, original in zip(data['cases'], actual_benchmark['cases']):
            request = actual_requests[case['id']]
            raw = actual_predictions[case['id']]
            self.assertEqual(case['input'], self.render(request['state']))
            self.assertEqual(self.render(case['input']), self.render(request['state']))
            self.assertEqual(case['questions'], request['questions'])
            for key in self.original_keys:
                self.assertEqual(case[key], original[key])
            for field in importer.FIELDS:
                self.assertEqual(case['result']['fields'][field]['probabilities'], raw['probabilities_unrounded'][field])
                self.assertEqual(case['result']['fields'][field]['prediction'], raw['answers'][field]['choice'])
            self.assertEqual(case['latency_ms'], raw['latency_ms'])
            self.assertEqual(case['input_tokens'], raw['input_tokens'])

    def test_public_package_has_no_private_paths_or_credentials(self):
        audit_spec = importlib.util.spec_from_file_location('insurance_privacy_audit', ROOT / 'scripts/audit_public.py')
        audit = importlib.util.module_from_spec(audit_spec)
        audit_spec.loader.exec_module(audit)
        package = ROOT / 'experiments/insurance'
        for path in sorted(package.rglob('*')):
            if not path.is_file():
                continue
            content = audit.extracted_text(path)
            for kind, pattern in audit.PATTERNS.items():
                self.assertIsNone(pattern.search(content), f'{path.relative_to(package)}: {kind}')

    def test_previous_benchmark_bytes_unchanged(self):
        expected = {'benchmark.json': '98729655de727e9941f5044111a0b456896b099a0709b49d0242746393611a1c',
                    'finance.json': '75dc1e910766ae370258c25af82eac3f962036c6fa1bf859c6158d56b2ead999',
                    'clean72.json': '3762fa3a3e47332a9e83e4d1da0b592811b7ede047605f66b9376656a53890f6'}
        for name, sha256 in expected.items():
            self.assertEqual(importer.digest(ROOT / 'web/data' / name), sha256)


if __name__ == '__main__':
    unittest.main()
