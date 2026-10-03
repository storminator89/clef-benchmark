#!/usr/bin/env python3
"""New recovery scorer synthetic tests; no benchmark outputs or model imports."""
import copy
import datetime
import json
import tempfile
from pathlib import Path
import score

R = Path(__file__).resolve().parents[1]
DATA = R/'data'
X = score.validate(DATA)
TMP = tempfile.TemporaryDirectory()
PREFLIGHT = R/'evidence/encoding_preflight.json'
PREFLIGHT_KIND = 'real_tokenizer_preflight'
if not PREFLIGHT.exists():
    PREFLIGHT_KIND = 'explicit_synthetic_token_fixture_not_tokenizer_evidence'
    PREFLIGHT = Path(TMP.name)/'synthetic_preflight.json'
    PREFLIGHT.write_text(json.dumps({'requests_sha256': score.digest(DATA/'requests.jsonl'),
                                    'count': 72, 'all_full_cap_equal': True,
                                    'cases': [{'id': id_, 'input_tokens': 700, 'full_cap_equal': True, 'truncated': False,
                                               'encoded_questions': [{'question_id': f, 'question_type': 1, 'question_span': [1,2],
                                                                      'option_ids': sorted(score.OPTIONS[f]),
                                                                      'option_spans': [[3+i*2,4+i*2] for i in range(len(score.OPTIONS[f]))]} for f in score.FIELDS]}
                                              for id_ in X['requests']]}))
TOKENS = score.validate_preflight(PREFLIGHT, DATA, X['requests'])
BASE = []
for id_, q in X['requests'].items():
    g = X['gold'][id_]['expected']
    p = {f: {k: float(k == g[f]) for k in q['request']['questions'][f]['criteria']} for f in score.FIELDS}
    BASE.append({'id': id_, 'answers': {f: {'type': 'choice', 'choice': g[f], 'confidence': 1.0, 'probabilities': p[f].copy()} for f in score.FIELDS},
                 'probabilities_unrounded': p, 'input_tokens': TOKENS[id_]['input_tokens'], 'truncated': False,
                 'encode_seconds': .1, 'inference_seconds': 1., 'total_seconds': 1.1, 'latency_ms': 1000., 'rss_bytes': 1000})


def run(rows=None, raw=None, data=DATA, preflight=PREFLIGHT):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)/'synthetic.jsonl'
        p.write_bytes((raw if raw is not None else ''.join(json.dumps(r, allow_nan=False)+'\n' for r in rows)).encode())
        return score.score(data, p, preflight)


def alter(rows, id_, field, choice, probability=1., probs=None):
    r = next(r for r in rows if r['id'] == id_)
    opts = X['requests'][id_]['request']['questions'][field]['criteria']
    if probs is None:
        probs = {k: probability if k == choice else (1-probability)/(len(opts)-1) for k in opts}
    r['probabilities_unrounded'][field] = probs
    r['answers'][field] = {'type': 'choice', 'choice': choice, 'confidence': round(probs[choice],4),
                            'probabilities': {k: round(v,4) for k,v in probs.items()}}


def eq(a,b):
    if a != b:
        raise AssertionError(f'{a!r} != {b!r}')


def reject(fn):
    try:
        fn()
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return
    raise AssertionError('Expected global rejection')


RESULT = []

def check(name, fn):
    try:
        fn()
        RESULT.append({'test': name, 'passed': True})
    except Exception as e:
        RESULT.append({'test': name, 'passed': False, 'error': str(e)})


def perfect():
    s = run(BASE)['summary']
    eq(s['all_cases']['all_fields_exact'], score.metric(72,72))
    eq(s['all_field_decisions'], score.metric(144,144))
    eq(s['by_group']['invariant']['all_fields_exact'], score.metric(60,60))
    eq(s['by_group']['ambiguity_change']['all_fields_exact'], score.metric(12,12))
    eq(s['invariant_pairs']['both_correct'], score.metric(48,48))
    eq(s['invariant_pairs']['stable_wrong'], score.metric(0,48))
    eq(s['ambiguity_controls']['correct_directional_change'], score.metric(6,6))
    eq(s['cluster_robustness']['all_five_correct'], score.metric(12,12))
    eq(s['technical']['complete_pairs'], score.metric(54,54))
    for style in ('canonical',)+score.STYLES:
        eq(s['invariant_views'][style]['all_fields_exact'], score.metric(12,12))
    for style in score.STYLES:
        eq(s['invariant_by_transformation'][style]['both_correct'], score.metric(12,12))
    for subtype in score.SUBTYPES:
        eq(s['ambiguity_by_subtype'][subtype]['both_correct'], score.metric(3,3))
    for domain in score.DOMAINS:
        d = s['by_domain'][domain]
        eq(d['all_cases']['all_fields_exact'], score.metric(24,24))
        eq(d['by_group']['invariant']['count'],20)
        eq(d['by_group']['ambiguity_change']['count'],4)
        eq(d['invariant_pairs']['both_correct'], score.metric(16,16))
        eq(d['ambiguity_controls']['both_correct'], score.metric(2,2))
        eq(d['cluster_robustness']['all_five_correct'], score.metric(4,4))
        for style in score.STYLES:
            eq(d['invariant_by_transformation'][style]['both_correct'], score.metric(4,4))
        for subtype in score.SUBTYPES:
            eq(d['ambiguity_by_subtype'][subtype]['both_correct'], score.metric(1,1))


check('perfect_all_case_pair_cluster_group_style_domain_denominators', perfect)


def missing_canonical():
    s = run(BASE[1:])['summary']
    eq(s['all_cases']['all_fields_exact'], score.metric(71,72))
    eq(s['invariant_pairs']['both_correct'], score.metric(44,48))
    eq(s['invariant_pairs']['invalid_or_missing'], score.metric(4,48))
    eq(s['invariant_pairs']['improvement'], score.metric(4,48))
    eq(s['invariant_pairs']['observed_change_among_valid'], score.metric(0,44))
    eq(s['invariant_pairs']['conditional_loss_given_correct_canonical'], score.metric(0,44))
    eq(s['technical']['complete_pairs'], score.metric(50,54))
    eq(s['cluster_robustness']['all_five_correct'], score.metric(11,12))


check('missing_shared_canonical_four_pairs_one_unique_case', missing_canonical)


def missing_variant():
    s = run([r for r in BASE if r['id'] != 'gv_b1_typo'])['summary']
    eq(s['invariant_pairs']['degradation'], score.metric(1,48))
    eq(s['invariant_pairs']['conditional_loss_given_correct_canonical'], score.metric(1,48))
    eq(s['invariant_pairs']['failed_invariance'], score.metric(1,48))
    eq(s['invariant_pairs']['observed_change'], score.metric(0,48))


check('missing_variant_loss_not_observed_change', missing_variant)


def empty():
    s = run([])['summary']
    eq(s['all_cases']['all_fields_exact'], score.metric(0,72))
    eq(s['technical']['failures'], score.metric(72,72))
    eq(s['technical']['complete_pairs'], score.metric(0,54))
    eq(s['invariant_pairs']['failed_invariance'], score.metric(48,48))
    eq(s['invariant_pairs']['conditional_loss_given_correct_canonical'], score.metric(0,0))
    eq(s['invariant_pairs']['observed_change_among_valid'], score.metric(0,0))
    eq(s['all_cases']['high_score']['wrong_among_selected'], score.metric(0,0))


check('empty_missing_and_zero_denominators_na', empty)


def stable_wrong():
    b = copy.deepcopy(BASE)
    for r in b:
        if r['id'].startswith('gv_b1_'):
            alter(b,r['id'],'determination','no')
    s = run(b)['summary']
    eq(s['all_cases']['all_fields_exact'], score.metric(67,72))
    eq(s['invariant_pairs']['stability'], score.metric(48,48))
    eq(s['invariant_pairs']['stable_wrong'], score.metric(4,48))
    eq(s['invariant_pairs']['both_correct'], score.metric(44,48))
    eq(s['cluster_robustness']['all_five_correct'], score.metric(11,12))


check('stable_wrong_is_not_both_correct', stable_wrong)


def transitions():
    b = copy.deepcopy(BASE)
    alter(b,'gv_b1_typo','determination','no')
    alter(b,'gv_b2_canonical','determination','yes')
    s = run(b)['summary']
    eq(s['invariant_pairs']['degradation'], score.metric(1,48))
    eq(s['invariant_pairs']['improvement'], score.metric(4,48))
    eq(s['invariant_pairs']['conditional_loss_given_correct_canonical'], score.metric(1,44))
    eq(s['invariant_pairs']['observed_change'], score.metric(5,48))
    eq(s['invariant_pairs']['both_correct'], score.metric(43,48))


check('loss_improvement_shared_canonical_conditional_denominator', transitions)


def ambiguity():
    b = copy.deepcopy(BASE)
    alter(b,'gv_banking_missing_fact_b','action','ask_target')
    s = run(b)['summary']
    eq(s['ambiguity_controls']['observed_change'], score.metric(6,6))
    eq(s['ambiguity_controls']['correct_directional_change'], score.metric(5,6))
    eq(s['ambiguity_controls']['changed_but_direction_wrong'], score.metric(1,6))
    eq(s['ambiguity_by_subtype']['answer_to_missing_fact']['both_correct'], score.metric(2,3))
    eq(s['ambiguity_by_subtype']['answer_to_missing_target']['both_correct'], score.metric(3,3))
    eq(s['invariant_pairs']['both_correct'], score.metric(48,48))
    s = run([r for r in BASE if r['id'] != 'gv_banking_missing_target_b'])['summary']
    eq(s['ambiguity_controls']['invalid_or_missing'], score.metric(1,6))
    eq(s['technical']['complete_pairs_by_group']['invariant'], score.metric(48,48))
    eq(s['technical']['complete_pairs_by_group']['ambiguity_change'], score.metric(5,6))


check('ambiguity_requires_exact_direction_and_excluded_from_invariance', ambiguity)


def confidence():
    b = copy.deepcopy(BASE)
    alter(b,'gv_b1_canonical','action','ask_fact',.9)
    alter(b,'gv_b1_canonical','determination','yes',.9)
    alter(b,'gv_b1_typo','determination','no',.89996)
    alter(b,'gv_b1_compact_colloquial','action','ask_fact',.9)
    alter(b,'gv_b1_compact_colloquial','determination','no',.89)
    alter(b,'gv_b1_abbreviation','action','answer',.89996)
    alter(b,'gv_b1_abbreviation','determination','no',.9)
    s = run(b)['summary']; h = s['all_cases']['high_score']
    eq(h['selected'], score.metric(69,72))
    eq(h['wrong_and_selected'], score.metric(1,72))
    eq(h['wrong_among_selected'], score.metric(1,69))
    eq(h['fields']['action']['wrong_and_selected'], score.metric(2,72))
    eq(h['fields']['determination']['wrong_and_selected'], score.metric(1,72))
    eq(h['fields_on_case_gate']['action']['wrong_and_selected'], score.metric(1,72))
    eq(h['fields_on_case_gate']['determination']['wrong_and_selected'], score.metric(0,72))
    eq(s['by_group']['invariant']['high_score']['wrong_and_selected'], score.metric(1,60))
    eq(s['by_group']['ambiguity_change']['high_score']['wrong_and_selected'], score.metric(0,12))
    eq(s['technical']['valid'],72)


check('inclusive_raw_090_min_gate_rounded_boundary_both_field_gates', confidence)


def low_confidence():
    b = copy.deepcopy(BASE)
    for r in b:
        for f in score.FIELDS:
            alter(b,r['id'],f,X['gold'][r['id']]['expected'][f],.8)
    s = run(b)['summary']
    eq(s['all_cases']['high_score']['selected'], score.metric(0,72))
    eq(s['all_cases']['high_score']['wrong_among_selected'], score.metric(0,0))
    eq(s['all_cases']['all_fields_exact'], score.metric(72,72))


check('low_confidence_valid_and_zero_selected_na', low_confidence)


def tie(probs, choice, n, field='action'):
    b = copy.deepcopy(BASE)
    alter(b,'gv_b1_canonical',field,choice,probs=probs)
    eq(run(b)['summary']['technical']['valid'],n)


check('exact_tie_first_criteria', lambda: tie({'answer':.5,'ask_fact':.5,'ask_target':0.,'resolve_conflict':0.},'answer',72))
check('exact_tie_wrong_later_choice', lambda: tie({'answer':.5,'ask_fact':.5,'ask_target':0.,'resolve_conflict':0.},'ask_fact',71))
check('rounded_tie_uses_raw_argmax', lambda: tie({'answer':.49999,'ask_fact':.50001,'ask_target':0.,'resolve_conflict':0.},'ask_fact',72))
check('map_order_is_not_tie_order', lambda: tie({'resolve_conflict':0.,'ask_target':0.,'ask_fact':.5,'answer':.5},'answer',72))
check('determination_native_criteria_order_not_lexical', lambda: tie({'no':.5,'unresolved':0.,'yes':.5},'yes',72,'determination'))
check('determination_lexical_tie_choice_invalid', lambda: tie({'no':.5,'unresolved':0.,'yes':.5},'no',71,'determination'))
check('rounded_sum_not_exactly_one_valid', lambda: tie({'answer':1/3,'ask_fact':1/3,'ask_target':1/3,'resolve_conflict':0.},'answer',72))
check('raw_sum_inside_tolerance', lambda: tie({'answer':.9,'ask_fact':.100009,'ask_target':0.,'resolve_conflict':0.},'answer',72))
check('raw_sum_outside_tolerance', lambda: tie({'answer':.9,'ask_fact':.100011,'ask_target':0.,'resolve_conflict':0.},'answer',71))


def invalid(change, variant=False):
    b = copy.deepcopy(BASE)
    r = b[1 if variant else 0]
    change(r)
    result = run(b); s = result['summary']
    eq(s['technical']['invalid_existing'],1)
    eq(s['technical']['valid'],71)
    eq(s['all_cases']['all_fields_exact'],score.metric(71,72))
    eq(s['all_cases']['high_score']['selected'],score.metric(71,72))
    eq(s['invariant_pairs']['invalid_or_missing'],score.metric(1 if variant else 4,48))
    eq(s['invariant_pairs']['invalid_existing_endpoint'],score.metric(1 if variant else 4,48))
    eq(s['invariant_pairs']['missing_endpoint'],score.metric(0,48))
    eq(result['errors'][0]['raw_native_row'],r)
    if variant:
        eq(s['invariant_pairs']['degradation'],score.metric(1,48))


CHANGES = {
 'missing_answers': lambda r:r.pop('answers'),
 'answers_list': lambda r:r.update(answers=[]),
 'missing_field': lambda r:r['answers'].pop('determination'),
 'extra_field': lambda r:r['answers'].update(extra={}),
 'answer_list': lambda r:r['answers'].update(action=[]),
 'extra_answer_key': lambda r:r['answers']['action'].update(extra=1),
 'wrong_type': lambda r:r['answers']['action'].update(type='bad'),
 'wrong_choice': lambda r:r['answers']['action'].update(choice='bad'),
 'list_choice': lambda r:r['answers']['action'].update(choice=[]),
 'missing_raw': lambda r:r.pop('probabilities_unrounded'),
 'raw_list': lambda r:r.update(probabilities_unrounded=[]),
 'field_raw_list': lambda r:r['probabilities_unrounded'].update(action=[]),
 'missing_raw_field': lambda r:r['probabilities_unrounded'].pop('determination'),
 'missing_raw_option': lambda r:r['probabilities_unrounded']['action'].pop('ask_fact'),
 'extra_raw_option': lambda r:r['probabilities_unrounded']['action'].update(extra=0),
 'negative_probability': lambda r:r['probabilities_unrounded']['action'].update(answer=-.1),
 'over_one_probability': lambda r:r['probabilities_unrounded']['action'].update(answer=1.1),
 'boolean_probability': lambda r:r['probabilities_unrounded']['action'].update(answer=True),
 'string_probability': lambda r:r['probabilities_unrounded']['action'].update(answer='1'),
 'unnormalized': lambda r:r['probabilities_unrounded']['action'].update(answer=.7),
 'rounded_list': lambda r:r['answers']['action'].update(probabilities=[]),
 'missing_rounded': lambda r:r['answers']['action'].pop('probabilities'),
 'rounded_missing_option': lambda r:r['answers']['action']['probabilities'].pop('ask_fact'),
 'rounded_extra_option': lambda r:r['answers']['action']['probabilities'].update(extra=0),
 'rounded_boolean': lambda r:r['answers']['action']['probabilities'].update(answer=True),
 'rounded_negative': lambda r:r['answers']['action']['probabilities'].update(answer=-1),
 'rounded_near_not_exact': lambda r:r['answers']['action']['probabilities'].update(answer=.99999),
 'confidence_boolean': lambda r:r['answers']['action'].update(confidence=True),
 'confidence_near_not_exact': lambda r:r['answers']['action'].update(confidence=.99999),
 'boolean_tokens': lambda r:r.update(input_tokens=True),
 'float_tokens': lambda r:r.update(input_tokens=float(r['input_tokens'])),
 'zero_tokens': lambda r:r.update(input_tokens=0),
 'overcap_tokens': lambda r:r.update(input_tokens=2049),
 'preflight_mismatch': lambda r:r.update(input_tokens=r['input_tokens']+1),
 'truncated': lambda r:r.update(truncated=True),
 'truncated_integer_false': lambda r:r.update(truncated=0),
 'missing_telemetry': lambda r:r.pop('total_seconds'),
 'negative_telemetry': lambda r:r.update(encode_seconds=-1),
 'boolean_telemetry': lambda r:r.update(rss_bytes=True),
 'latency_mismatch': lambda r:r.update(latency_ms=1),
 'explicit_error': lambda r:r.update(error='synthetic'),
}
for name, change in CHANGES.items():
    check(name+'_invalid',lambda change=change:invalid(change))
check('invalid_variant_degradation',lambda:invalid(CHANGES['missing_raw'],True))
check('duplicate_id_global_stop',lambda:reject(lambda:run(BASE+[BASE[0]])))
check('unexpected_id_global_stop',lambda:reject(lambda:run(BASE+[dict(BASE[0],id='unexpected')])) )
check('unassignable_id_global_stop',lambda:reject(lambda:run([{}])))
check('nonobject_row_global_stop',lambda:reject(lambda:run([[]])))
check('malformed_json_global_stop',lambda:reject(lambda:run(raw='{')))
check('duplicate_json_key_global_stop',lambda:reject(lambda:run(raw='{"id":"x","id":"y"}\n')))
check('nested_duplicate_key_global_stop',lambda:reject(lambda:run(raw='{"id":"gv_b1_canonical","a":{"x":1,"x":2}}\n')))
for constant in ('NaN','Infinity','-Infinity'):
    check('bare_'+constant+'_global_stop',lambda constant=constant:reject(lambda:run(raw='{"id":"gv_b1_canonical","a":'+constant+'}\n')))


def retained_evidence():
    raw = '\r\n'.join(json.dumps(r) for r in BASE).replace('"encode_seconds": 0.1','"encode_seconds": 1e999',1)+'\r\n'
    result = run(raw=raw)
    eq(result['summary']['technical']['invalid_existing'],1)
    eq(result['raw_predictions'],raw)
    with tempfile.TemporaryDirectory() as d:
        score.write(result,d)
        eq((Path(d)/'raw_predictions.jsonl').read_bytes(),raw.encode())
        e = score.read(Path(d)/'errors.jsonl')[0]
        eq(e['raw_native_row']['encode_seconds'],{'nonfinite_parsed_number':'inf'})
        eq('1e999' in e['raw_prediction_line'],True)
        eq(e['message'],X['cases'][e['id']]['message'])
        eq(len(e['probabilities_unrounded']['action']),4)
        reject(lambda:score.write(result,d))


check('overflow_invalid_raw_bytes_error_evidence_retained_no_overwrite',retained_evidence)


def telemetry():
    d = run(BASE)['summary']['technical']['descriptive_unique_recorded_requests']
    eq(d['inference_seconds']['sum'],72.)
    eq(d['inference_seconds']['count'],72)
    eq(d['input_tokens']['count'],72)
    eq(d['input_tokens']['sum'],sum(r['input_tokens'] for r in BASE))


check('telemetry_uses_unique_main_requests_not_pairs',telemetry)


def preflight_change(change):
    with tempfile.TemporaryDirectory() as d:
        p = score.loads(PREFLIGHT.read_text());change(p)
        path = Path(d)/'preflight.json';path.write_text(json.dumps(p))
        reject(lambda:run(BASE,preflight=path))


check('preflight_wrong_request_hash',lambda:preflight_change(lambda p:p.update(requests_sha256='bad')))
check('preflight_missing_id',lambda:preflight_change(lambda p:p['cases'].pop()))
check('preflight_duplicate_id',lambda:preflight_change(lambda p:p['cases'].append(p['cases'][0])))
check('preflight_invalid_tokens',lambda:preflight_change(lambda p:p['cases'][0].update(input_tokens=True)))
check('preflight_truncated',lambda:preflight_change(lambda p:p['cases'][0].update(truncated=True)))

check('preflight_missing_root_full_cap_evidence',lambda:preflight_change(lambda p:p.pop('all_full_cap_equal')))
check('preflight_false_root_full_cap_evidence',lambda:preflight_change(lambda p:p.update(all_full_cap_equal=False)))
check('preflight_missing_case_full_cap_evidence',lambda:preflight_change(lambda p:p['cases'][0].pop('full_cap_equal')))
check('preflight_false_case_full_cap_evidence',lambda:preflight_change(lambda p:p['cases'][0].update(full_cap_equal=False)))
check('preflight_missing_truncation_evidence',lambda:preflight_change(lambda p:p['cases'][0].pop('truncated')))
check('preflight_missing_encoded_questions',lambda:preflight_change(lambda p:p['cases'][0].pop('encoded_questions')))
check('preflight_missing_encoded_option_ids',lambda:preflight_change(lambda p:p['cases'][0]['encoded_questions'][0].pop('option_ids')))
check('preflight_missing_encoded_spans',lambda:preflight_change(lambda p:p['cases'][0]['encoded_questions'][0].pop('option_spans')))
check('preflight_encoded_span_outside_tokens',lambda:preflight_change(lambda p:p['cases'][0]['encoded_questions'][0].update(question_span=[1,99999])))
check('preflight_encoded_boolean_question_type',lambda:preflight_change(lambda p:p['cases'][0]['encoded_questions'][0].update(question_type=True)))



def encoded_options():
    p = score.loads(PREFLIGHT.read_text())
    for rec in p['cases']:
        rec['encoded_questions'] = [{'question_id':f,'question_type':1,'question_span':[1,2],
                                      'option_ids':sorted(score.OPTIONS[f]),'option_spans':[[3+i*2,4+i*2] for i in range(len(score.OPTIONS[f]))]} for f in score.FIELDS]
    with tempfile.TemporaryDirectory() as d:
        path = Path(d)/'preflight.json';path.write_text(json.dumps(p))
        eq(run(BASE,preflight=path)['summary']['technical']['valid'],72)
        p['cases'][0]['encoded_questions'][1]['option_ids'] = list(score.OPTIONS['determination'])
        path.write_text(json.dumps(p))
        reject(lambda:run(BASE,preflight=path))


check('lexical_encoded_options_distinct_from_native_tie_order',encoded_options)


def corrupt_data(filename, change):
    with tempfile.TemporaryDirectory() as d:
        d=Path(d)
        for p in DATA.iterdir():
            if p.is_file():
                (d/p.name).write_bytes(p.read_bytes())
        path=d/filename;rows=score.read(path);change(rows)
        path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
        reject(lambda:run(BASE,data=d))


check('duplicate_case_id_stops',lambda:corrupt_data('cases.reconstructed.jsonl',lambda r:r.append(r[0])))
check('wrong_pair_endpoint_stops',lambda:corrupt_data('pairs.reconstructed.jsonl',lambda r:r[1].update(b_id=r[0]['b_id'])))
check('wrong_pair_domain_stops',lambda:corrupt_data('pairs.reconstructed.jsonl',lambda r:r[0].update(domain='finance')))
check('gold_disagreement_stops',lambda:corrupt_data('gold.reconstructed.jsonl',lambda r:r[0]['expected'].update(determination='no')))
check('changed_request_bytes_stops',lambda:corrupt_data('requests.jsonl',lambda r:r[0]['request'].update(state='changed')))


if __name__=='__main__':
    report={'status':'PASS_SYNTHETIC_ONLY' if all(t['passed'] for t in RESULT) else 'FAIL',
            'identity':'new recovery code and tests; no restoration of historical source hash or historical test evidence',
            'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'synthetic_only':True,'model_loaded':False,'api_called':False,'benchmark_predictions_or_results_read':False,
            'token_fixture':PREFLIGHT_KIND,'token_fixture_sha256':score.digest(PREFLIGHT),
            'passed':sum(t['passed'] for t in RESULT),'failed':sum(not t['passed'] for t in RESULT),
            'scorer_sha256':score.digest(R/'scripts/score.py'),'self_test_sha256':score.digest(__file__),'tests':RESULT}
    (R/'evidence/scorer_self_tests.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    TMP.cleanup()
    raise SystemExit(bool(report['failed']))
