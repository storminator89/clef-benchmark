#!/usr/bin/env python3
"""Synthetic-only tests for independent_result_check; never reads actual results."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('independent_checker', ROOT / 'scripts/independent_result_check.py')
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)
CASES = [json.loads(line) for line in (ROOT / 'data/cases.jsonl').read_text().splitlines()]
CASE_MAP = {row['id']: row for row in CASES}
REQUESTS = {row['id']: row for row in map(json.loads, (ROOT / 'data/requests.jsonl').read_text().splitlines())}
PREFLIGHT = json.loads((ROOT / 'audit/encoding_preflight.json').read_text())
TOKENS = {row['id']: row['input_tokens'] for row in PREFLIGHT['cases']}
MANIFEST = json.loads((ROOT / 'freeze_manifest.json').read_text())
IDS = [row['id'] for row in CASES]


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))


def prediction(ident, action=None, determination=None, pa=.97, pd=.97):
    gold = CASE_MAP[ident]['expected']
    selected = {'action': action or gold['action'], 'determination': determination or gold['determination']}
    probs = {}
    for field, confidence in (('action', pa), ('determination', pd)):
        options = REQUESTS[ident]['request']['questions'][field]['criteria']
        probs[field] = {option: confidence if option == selected[field] else (1-confidence)/(len(options)-1) for option in options}
    return {'id': ident,
            'answers': {field: {'type': 'choice', 'choice': selected[field], 'confidence': probs[field][selected[field]]} for field in selected},
            'probabilities_unrounded': probs, 'input_tokens': TOKENS[ident], 'truncated': False,
            'encode_seconds': .01, 'inference_seconds': .1, 'total_seconds': .11, 'rss_bytes': 1_000_000_000}


def base_summary():
    # Explicit perfect-fixture oracle, not created by the checker under test.
    ratio = lambda n, d: {'numerator': n, 'denominator': d, 'rate': n/d if d else None}
    answers = [case['id'] for case in CASES if case['expected']['action'] == 'answer']
    events = {name: {'count': 0, 'ids': []} for name in (
        'invalid_or_missing', 'missed_required_clarifications', 'required_clarifications_not_successfully_requested',
        'excess_clarifications', 'wrong_clarification_kind', 'inconsistent_fields', 'risky_wrong_answers')}
    events['substantive_answer_cases'] = {'count': 36, 'ids': answers}
    for threshold in (.8, .9, .95):
        events[f'confident_answers_{threshold}'] = {'count': 36, 'ids': answers}
        events[f'confident_wrong_answers_{threshold}'] = {'count': 0, 'ids': []}
    strata = {}
    for field in ('domain', 'stratum', 'family'):
        names = set(case[field] for case in CASES)
        strata[field] = {}
        for name in names:
            size = sum(case[field] == name for case in CASES)
            strata[field][name] = {'cases': size, 'all_fields_exact': ratio(size, size), 'action': ratio(size, size), 'determination': ratio(size, size)}
    return {'suite_id': 'clarification', 'case_count': 72, 'field_count': 2,
            'metrics': {'action': ratio(72,72), 'determination': ratio(72,72), 'all_fields_exact': ratio(72,72), 'all_field_decisions': ratio(144,144)},
            'denominators': {'clarification_required':36, 'answerable':36, 'valid_cases':72, 'substantive_answers':36},
            'behavior_rates': {**{name:ratio(0,36) for name in ('missed_required_clarifications','required_clarifications_not_successfully_requested','excess_clarifications','wrong_clarification_kind')},
                               'risky_wrong_answers_all_cases':ratio(0,72), 'risky_wrong_answers_among_substantive':ratio(0,36)},
            'high_confidence': {str(threshold): {'confident_answers':36,'confident_wrong':0,'wrong_rate_among_confident':ratio(0,36)} for threshold in (.8,.9,.95)},
            'events':events,
            'confusion_matrices':{'action':{label:{label:n} for label,n in [('answer',36),('ask_fact',12),('ask_target',12),('resolve_conflict',12)]},
                                  'determination':{'yes':{'yes':18},'no':{'no':18},'unresolved':{'unresolved':36}}},
            'strata':strata,
            'technical':{'recorded_predictions':72,'valid_cases':72,'missing_predictions':0,'invalid_existing_predictions':0,
                         'input_tokens_min':min(TOKENS.values()),'input_tokens_max':max(TOKENS.values()),
                         'forward_seconds_median':.1,'forward_seconds_p95':.1,'forward_seconds_total':7.2,'peak_observed_rss_bytes':1_000_000_000}}


def prepare_fixture(root):
    # Copy only files named in the frozen manifest, which contains no results.
    for name in MANIFEST['files']:
        destination = root/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,destination)
    shutil.copyfile(ROOT/'freeze_manifest.json',root/'freeze_manifest.json')
    (root/'results').mkdir()
    rows = [prediction(ident) for ident in IDS]
    write_rows(root/'results/predictions.jsonl',rows)
    metadata = {'status':'completed','started_at':'2026-10-02T14:01:00+00:00','completed_at':'2026-10-02T14:30:00+00:00',
                'request_count':72,'request_order_ids':IDS,'requests_sha256':CHECKER.sha256(ROOT/'data/requests.jsonl'),
                'revision':MANIFEST['revision'],'source_code_sha256':MANIFEST['files']['reference_runtime/joint_schema_model.py'],
                'runner_sha256':MANIFEST['files']['reference_runtime/run_clef.py'],'max_length':2048,'threads':6,'batch_size':1,
                'device':'cpu','dtype':'bfloat16','benchmark_requests_only_no_gold':True,
                'packages':{'torch':'2.11.0+cpu','transformers':'5.10.2','bitsandbytes':'0.50.2'}}
    write_json(root/'results/predictions.metadata.json',metadata)
    write_json(root/'results/run_outcome.json',{'exit_code':0,'finished_at_utc':'2026-10-02T14:31:00+00:00'})
    summary = base_summary()
    summary['provenance'] = {f'{name}_sha256':CHECKER.sha256(root/path) for name,path in (
        ('requests','data/requests.jsonl'),('gold','data/gold.jsonl'),('predictions','results/predictions.jsonl'))}
    write_json(root/'results/summary.json',summary)
    write_rows(root/'results/errors.jsonl',[])
    return rows,summary


class IndependentCheckerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='independent_checker_synthetic_')
        self.root = Path(self.temporary.name)
        self.rows,self.summary = prepare_fixture(self.root)
    def tearDown(self):
        self.temporary.cleanup()
    def run_check(self):
        return CHECKER.check(self.root,completed_authorized=True)
    def rewrite_predictions(self,rows):
        write_rows(self.root/'results/predictions.jsonl',rows)
        self.summary['provenance']['predictions_sha256']=CHECKER.sha256(self.root/'results/predictions.jsonl')
        write_json(self.root/'results/summary.json',self.summary)
    def test_perfect_fixture_against_explicit_oracle(self):
        report=self.run_check()
        self.assertTrue(report['passed'],report['mismatches'])
        self.assertEqual(report['prediction_count'],72)
        self.assertEqual(report['error_ids'],[])
        self.assertNotIn(str(self.root),json.dumps(report))
    def test_permission_gate_reads_no_result(self):
        report=CHECKER.check(self.root)
        self.assertFalse(report['passed']);self.assertIsNone(report['predictions_sha256'])
    def test_incomplete_metadata_reads_no_predictions(self):
        write_json(self.root/'results/predictions.metadata.json',{'status':'running'})
        report=self.run_check();self.assertFalse(report['passed']);self.assertIsNone(report['predictions_sha256'])
    def test_nonzero_or_boolean_exit_reads_no_predictions(self):
        for code in (1,False):
            write_json(self.root/'results/run_outcome.json',{'exit_code':code})
            report=self.run_check();self.assertFalse(report['passed']);self.assertIsNone(report['predictions_sha256'])
    def test_frozen_file_tamper_detected(self):
        (self.root/'data/policy.json').write_text('{}')
        report=self.run_check();self.assertFalse(report['passed']);self.assertIsNone(report['predictions_sha256'])
    def test_manifest_tamper_detected(self):
        manifest=deepcopy(MANIFEST);manifest['version']='changed';write_json(self.root/'freeze_manifest.json',manifest)
        report=self.run_check();self.assertFalse(report['passed']);self.assertIsNone(report['predictions_sha256'])
    def test_wrong_metadata_request_hash(self):
        path=self.root/'results/predictions.metadata.json';meta=json.loads(path.read_text());meta['requests_sha256']='0'*64;write_json(path,meta)
        self.assertFalse(self.run_check()['passed'])
    def test_chronology_inverted(self):
        path=self.root/'results/run_outcome.json';write_json(path,{'exit_code':0,'finished_at_utc':'2026-10-02T14:00:00+00:00'})
        self.assertFalse(self.run_check()['passed'])
    def test_missing_duplicate_unexpected_or_reordered_rows(self):
        unknown=deepcopy(self.rows[0]);unknown['id']='unknown_case'
        variants=[self.rows[:-1],self.rows+[self.rows[0]],self.rows[:-1]+[unknown],list(reversed(self.rows))]
        for rows in variants:
            self.rewrite_predictions(rows);self.assertFalse(self.run_check()['passed'])
    def test_malformed_metadata_and_summary_types(self):
        path=self.root/'results/predictions.metadata.json';meta=json.loads(path.read_text());meta['packages']=None;meta['started_at']=3;write_json(path,meta)
        self.assertFalse(self.run_check()['passed'])
        write_json(self.root/'results/summary.json',[])
        self.assertFalse(self.run_check()['passed'])
    def test_summary_disagreement(self):
        self.summary['metrics']['all_fields_exact']['numerator']=71
        write_json(self.root/'results/summary.json',self.summary)
        self.assertFalse(self.run_check()['passed'])
    def test_spurious_error_id(self):
        write_rows(self.root/'results/errors.jsonl',[{'id':IDS[0]}])
        self.assertFalse(self.run_check()['passed'])
    def test_invalid_option_probability_argmax_confidence_and_telemetry(self):
        ident=IDS[0];base=prediction(ident);q=REQUESTS[ident]['request'];mutations=[]
        row=deepcopy(base);row['probabilities_unrounded']['action'].pop('answer');mutations.append(row)
        row=deepcopy(base);row['probabilities_unrounded']['action']['answer']=float('nan');mutations.append(row)
        row=deepcopy(base);row['probabilities_unrounded']['action']['answer']=-.1;mutations.append(row)
        row=deepcopy(base);row['probabilities_unrounded']['action']['answer']=True;mutations.append(row)
        row=deepcopy(base);row['probabilities_unrounded']['action']={k:.1 for k in CHECKER.OPTIONS['action']};mutations.append(row)
        row=deepcopy(base);row['answers']['action']['choice']='impossible';mutations.append(row)
        row=deepcopy(base);row['answers']['action']['choice']=['answer'];mutations.append(row)
        row=deepcopy(base);row['answers']['action']['choice']=next(k for k in CHECKER.OPTIONS['action'] if k!=base['answers']['action']['choice']);mutations.append(row)
        row=deepcopy(base);row['answers']['action']['confidence']=.1;mutations.append(row)
        row=deepcopy(base);row['input_tokens']=2049;mutations.append(row)
        row=deepcopy(base);row['input_tokens']=True;mutations.append(row)
        row=deepcopy(base);row['input_tokens']+=1;mutations.append(row)
        row=deepcopy(base);row['truncated']=True;mutations.append(row)
        row=deepcopy(base);row['rss_bytes']=-1;mutations.append(row)
        row=deepcopy(base);row['answers'].pop('determination');mutations.append(row)
        for row in mutations:
            choices,selected,issues=CHECKER.inspect_prediction(row,q,TOKENS[ident])
            self.assertTrue(issues);self.assertEqual(choices,{'action':None,'determination':None});self.assertEqual(selected,{})
    def test_perturbed_metrics_against_manual_counts(self):
        rows={row['id']:row for row in self.rows}
        rows['clarify_giro_fee_01']=prediction('clarify_giro_fee_01','answer','yes',.93,.89)
        rows['clarify_giro_fee_02']=prediction('clarify_giro_fee_02','resolve_conflict','unresolved')
        rows['clarify_giro_fee_03']=prediction('clarify_giro_fee_03','answer','unresolved')
        rows['clarify_giro_fee_04']=prediction('clarify_giro_fee_04','ask_fact','unresolved')
        rows['clarify_giro_fee_05']=prediction('clarify_giro_fee_05','answer','yes',.95,.95)
        rows['clarify_giro_fee_06']=prediction('clarify_giro_fee_06','ask_target','yes')
        del rows['clarify_card_replacement_01']
        rows['clarify_card_replacement_04']['input_tokens']=2049
        result,records=CHECKER.recompute(CASES,REQUESTS,rows,TOKENS)
        self.assertEqual({key:value['numerator'] for key,value in result['metrics'].items()},
                         {'action':65,'determination':66,'all_fields_exact':64,'all_field_decisions':131})
        expected={'invalid_or_missing':2,'missed_required_clarifications':2,
                  'required_clarifications_not_successfully_requested':3,'excess_clarifications':2,
                  'wrong_clarification_kind':1,'inconsistent_fields':2,'risky_wrong_answers':2,'substantive_answer_cases':34}
        for key,count in expected.items():self.assertEqual(result['events'][key]['count'],count,key)
        self.assertEqual(result['events']['confident_wrong_answers_0.8']['count'],2)
        self.assertEqual(result['events']['confident_wrong_answers_0.9']['count'],1)
        self.assertEqual(result['events']['confident_wrong_answers_0.95']['count'],1)
        self.assertEqual(set(result['events']['risky_wrong_answers']['ids']),{'clarify_giro_fee_01','clarify_giro_fee_05'})
    def test_one_wrong_result_full_error_comparison(self):
        ident='clarify_giro_fee_01';wrong=prediction(ident,'answer','yes',.93,.89)
        rows=[wrong if row['id']==ident else row for row in self.rows]
        ratio=lambda n,d:{'numerator':n,'denominator':d,'rate':n/d}
        summary=self.summary
        for field in ('action','determination','all_fields_exact'):summary['metrics'][field]=ratio(71,72)
        summary['metrics']['all_field_decisions']=ratio(142,144)
        summary['denominators']['substantive_answers']=37
        for name in ('missed_required_clarifications','required_clarifications_not_successfully_requested'):
            summary['behavior_rates'][name]=ratio(1,36);summary['events'][name]={'count':1,'ids':[ident]}
        summary['behavior_rates']['risky_wrong_answers_all_cases']=ratio(1,72)
        summary['behavior_rates']['risky_wrong_answers_among_substantive']=ratio(1,37)
        summary['events']['risky_wrong_answers']={'count':1,'ids':[ident]}
        concrete=[case['id'] for case in CASES if case['expected']['action']=='answer' or case['id']==ident]
        summary['events']['substantive_answer_cases']={'count':37,'ids':concrete}
        summary['events']['confident_answers_0.8']={'count':37,'ids':concrete}
        summary['events']['confident_wrong_answers_0.8']={'count':1,'ids':[ident]}
        summary['high_confidence']['0.8']={'confident_answers':37,'confident_wrong':1,'wrong_rate_among_confident':ratio(1,37)}
        summary['confusion_matrices']['action']['ask_fact']={'ask_fact':11,'answer':1}
        summary['confusion_matrices']['determination']['unresolved']={'unresolved':35,'yes':1}
        for field,name,size in [('domain','banking',24),('stratum','missing_fact',12),('family','giro_fee',6)]:
            for metric in ('action','determination','all_fields_exact'):summary['strata'][field][name][metric]=ratio(size-1,size)
        error={'id':ident,'valid':True,'expected':CASE_MAP[ident]['expected'],'predicted':{'action':'answer','determination':'yes'},
               'field_correct':{'action':False,'determination':False},'all_fields_exact':False,
               'selected_probabilities':{'action':.93,'determination':.89},'required_clarification':True,
               'model_requested_clarification':False,'risky_wrong_answer':True,'technical_issues':[],
               'probabilities_unrounded':wrong['probabilities_unrounded']}
        for key in ('domain','family','stratum','rule','message','question','rationale','clarification_target'):error[key]=CASE_MAP[ident][key]
        self.rewrite_predictions(rows);write_rows(self.root/'results/errors.jsonl',[error])
        report=self.run_check();self.assertTrue(report['passed'],report['mismatches']);self.assertEqual(report['error_ids'],[ident])
        error['message']='tampered';write_rows(self.root/'results/errors.jsonl',[error]);self.assertFalse(self.run_check()['passed'])


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(IndependentCheckerTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'purpose':'Synthetic independent-checker tests only; actual predictions not accessed',
            'tests_run':result.testsRun,'failed':len(result.failures)+len(result.errors),'passed':result.wasSuccessful(),
            'checker_sha256':CHECKER.sha256(ROOT/'scripts/independent_result_check.py'),
            'tests_sha256':CHECKER.sha256(Path(__file__)),
            'pinned_freeze_manifest_sha256':CHECKER.EXPECTED_FREEZE_SHA256}
    write_json(ROOT/'audit/independent_checker_self_tests.json',report)
    raise SystemExit(0 if result.wasSuccessful() else 1)
