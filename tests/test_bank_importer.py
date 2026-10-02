"""Strict bank importer tests; generated predictions here are test fixtures only."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bank_web_importer', ROOT/'scripts/build_bank_web_data.py')
bank = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bank)


def fixture():
    criteria = {'intent': {'cards': 'Cards', 'security': 'Security'},
                'priority': {'critical': 'Critical', 'urgent': 'Urgent', 'routine': 'Routine'},
                'next_step': {'security_handoff': 'Security', 'specialist_review': 'Specialist', 'clarify': 'Clarify', 'guidance': 'Guidance'}}
    cases = []; requests = []; raw = []
    for i in range(80):
        cid = f'test_only_bank_{i}'
        expected = {'intent': 'cards', 'priority': 'critical' if i == 0 else 'urgent' if i == 1 else 'routine',
                    'next_step': 'security_handoff' if i == 0 else 'clarify' if i == 2 else 'guidance'}
        cases.append({'id': cid, 'expected': expected})
        requests.append({'id': cid, 'request': {'questions': {f: {'criteria': opts} for f, opts in criteria.items()}}})
        p = {'id': cid, 'answers': {}, 'probabilities_unrounded': {}, 'truncated': False,
             'input_tokens': 100, 'inference_seconds': 1.25, 'encode_seconds': .1, 'latency_ms': 1250, 'rss_bytes': 1000}
        for f, options in criteria.items():
            set_choice(p, f, options, expected[f])
        raw.append(p)
    return cases, requests, raw


def set_choice(p, field, options, choice):
    probs = {k: .94 if k == choice else .06 / (len(options) - 1) for k in options}
    p['probabilities_unrounded'][field] = probs
    p['answers'][field] = {'type': 'choice', 'choice': choice, 'confidence': round(probs[choice], 4),
                          'probabilities': {k: round(v, 4) for k, v in probs.items()}}


class BankImporterTests(unittest.TestCase):
    def test_final_export_and_exact_probability_preservation(self):
        source = ROOT/'experiments/bank-support'
        data = bank.build(source)
        self.assertEqual([data['summary']['metrics'][f]['correct'] for f in bank.FIELDS], [76, 77, 75])
        self.assertEqual(data['summary']['metrics']['all_fields_exact']['correct'], 68)
        raw = bank.load(source/'results/predictions.jsonl', True)
        self.assertEqual(len(data['cases']), 80)
        for c, p in zip(data['cases'], raw):
            self.assertEqual(c['input'], 'Synthetische Kundennachricht:\n' + c['message'])
            self.assertEqual(c['service_policy'], '\n\n'.join(c['questions'][f]['instructions'] for f in bank.FIELDS))
            self.assertEqual({f: c['result']['fields'][f]['probabilities'] for f in bank.FIELDS}, p['probabilities_unrounded'])

    def test_final_export_rejects_changed_bytes_and_stale_reports(self):
        source = ROOT/'experiments/bank-support'
        for scenario in ('changed_bytes', 'stale_report', 'partial_report'):
            with tempfile.TemporaryDirectory() as td:
                copied = Path(td)/'bank'; shutil.copytree(source, copied)
                if scenario == 'partial_report':
                    name = 'audit/independent_score_check.json'; value = bank.load(copied/name)
                    value['independently_recomputed'] = {'provenance': value['independently_recomputed']['provenance']}
                    (copied/name).write_text(json.dumps(value))
                else:
                    name = 'results/summary.json'; value = bank.load(copied/name)
                    value['errors_count'] += 1; (copied/name).write_text(json.dumps(value))
                if scenario != 'changed_bytes':
                    manifest = bank.load(copied/'FILE_SHA256.json'); manifest[name] = bank.sha(copied/name)
                    (copied/'FILE_SHA256.json').write_text(json.dumps(manifest))
                with self.assertRaises(ValueError): bank.build(copied)

    def test_independent_all_field_denominators(self):
        fresh = bank.recompute(*fixture())
        self.assertEqual(fresh['metrics']['all_fields_exact'], {'correct': 80, 'total': 80, 'accuracy': 1.0})
        self.assertEqual(fresh['metrics']['all_field_decisions']['total'], 240)
        self.assertTrue(all(fresh['metrics'][f]['correct'] == 80 for f in bank.FIELDS))

    def test_safety_definitions_and_exact_case_counts(self):
        cases, requests, raw = fixture()
        set_choice(raw[0], 'priority', requests[0]['request']['questions']['priority']['criteria'], 'urgent')
        set_choice(raw[0], 'next_step', requests[0]['request']['questions']['next_step']['criteria'], 'specialist_review')
        set_choice(raw[1], 'priority', requests[1]['request']['questions']['priority']['criteria'], 'routine')
        set_choice(raw[2], 'next_step', requests[2]['request']['questions']['next_step']['criteria'], 'security_handoff')
        fresh = bank.recompute(cases, requests, raw)
        self.assertEqual(fresh['metrics']['priority']['correct'], 78)
        self.assertEqual(fresh['metrics']['next_step']['correct'], 78)
        self.assertEqual(fresh['metrics']['all_fields_exact']['correct'], 77)
        for key in ['critical_priority_misses', 'critical_handoff_misses', 'critical_safety_case_errors',
                    'urgent_undertriage', 'unnecessary_security_handoffs', 'unnecessary_escalations', 'missed_clarifications']:
            self.assertEqual(fresh['safety'][key]['count'], 1, key)

    def test_partial_extra_or_duplicate_predictions_rejected(self):
        for edit in (lambda raw: raw.pop(), lambda raw: raw.append(copy.deepcopy(raw[0])),
                     lambda raw: raw[0].update(id=raw[1]['id']), lambda raw: raw.reverse()):
            cases, requests, raw = fixture(); edit(raw)
            with self.assertRaises(ValueError): bank.recompute(cases, requests, raw)

    def test_partial_field_rejected(self):
        for key in ('answers', 'probabilities_unrounded'):
            cases, requests, raw = fixture(); del raw[0][key]['next_step']
            with self.assertRaises(ValueError): bank.recompute(cases, requests, raw)

    def test_invalid_probabilities_rejected(self):
        for bad in (float('nan'), float('inf'), True, -.1, 1.1):
            cases, requests, raw = fixture(); raw[0]['probabilities_unrounded']['intent']['cards'] = bad
            with self.assertRaises(ValueError): bank.recompute(cases, requests, raw)

    def test_nonmaximal_choice_rejected(self):
        cases, requests, raw = fixture()
        raw[0]['answers']['intent']['choice'] = 'security'
        with self.assertRaises(ValueError): bank.recompute(cases, requests, raw)

    def test_wrong_confidence_or_rounded_vector_rejected(self):
        for change in (lambda p: p['answers']['intent'].update(confidence=.3),
                       lambda p: p['answers']['intent']['probabilities'].update(cards=.1)):
            cases, requests, raw = fixture(); change(raw[0])
            with self.assertRaises(ValueError): bank.recompute(cases, requests, raw)

    def test_boolean_native_confidence_or_rounded_probability_rejected(self):
        for mutate in (lambda a: a.update(confidence=True), lambda a: a.update(probabilities={'cards': True, 'security': False})):
            cases, requests, raw = fixture()
            raw[0]['probabilities_unrounded']['intent'] = {'cards': 1.0, 'security': 0.0}
            raw[0]['answers']['intent'].update(confidence=1.0, probabilities={'cards': 1.0, 'security': 0.0})
            mutate(raw[0]['answers']['intent'])
            with self.assertRaises(ValueError): bank.recompute(cases, requests, raw)

    def test_truncated_or_over_cap_rejected(self):
        for key, value in [('truncated', True), ('input_tokens', 2049), ('input_tokens', False), ('input_tokens', 0)]:
            cases, requests, raw = fixture(); raw[0][key] = value
            with self.assertRaises(ValueError): bank.recompute(cases, requests, raw)

    def test_latency_and_timing_rejected(self):
        for key, value in [('latency_ms', 12), ('inference_seconds', -1), ('rss_bytes', False)]:
            cases, requests, raw = fixture(); raw[0][key] = value
            with self.assertRaises(ValueError): bank.recompute(cases, requests, raw)

    def test_truncated_independent_report_never_satisfies_gate(self):
        for partial in ({}, {'provenance': {'requests_sha256': '0'*64, 'gold_sha256': '0'*64, 'predictions_sha256': '0'*64}}):
            with self.assertRaises(ValueError): bank.validate_independent_summary(partial, partial)

    def test_derived_float_tolerance_is_narrow_and_never_coerces_counts(self):
        self.assertTrue(bank.derived_equal({'p95': 28.78910478834562}, {'p95': 28.789104788345625}))
        for changed in (28.8, float('nan'), True):
            self.assertFalse(bank.derived_equal({'p95': 28.78910478834562}, {'p95': changed}))
        self.assertFalse(bank.derived_equal({'count': 1}, {'count': True}))
        self.assertFalse(bank.derived_equal({'count': 1}, {'count': 1.0}))
        self.assertFalse(bank.derived_equal({'ids': ['a']}, {'ids': ['b']}))
        self.assertFalse(bank.derived_equal({'ids': ['a']}, {'ids': ['a'], 'extra': 0}))

    def test_duplicate_json_keys_and_nonfinite_values_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'bad.json'
            for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
                p.write_text(text)
                with self.assertRaises(ValueError): bank.load(p)


if __name__ == '__main__': unittest.main()
