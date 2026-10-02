#!/usr/bin/env python3
"""Independent read-only audit of a completed frozen bank-support run.

Does not import or call score.py. Aggregate computations use independently
constructed truth/prediction vectors and set predicates. --self-test constructs
probabilities in memory from frozen gold; it never opens inference output files.
"""
from __future__ import annotations
import argparse
import collections
import copy
import datetime
import hashlib
import json
import math
from pathlib import Path

FIELDS = ('intent', 'priority', 'next_step')
STRATA = ('topic', 'style', 'answerability', 'priority', 'next_step')
MANIFEST_SHA256 = '11e895f000ada7286dc8ae5fabd00b63a862f81e57de1692ff86990e72a895d3'

class CheckFailed(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise CheckFailed(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def object_json(path):
    def reject_constant(value):
        raise CheckFailed(f'Nonstandard JSON numeric constant {value} in {path}')
    return json.loads(Path(path).read_text(), parse_constant=reject_constant)

def jsonl(path):
    # Reject blank records and duplicate JSON object keys, not only duplicate IDs.
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, f'Duplicate JSON key {key} in {path}')
            out[key] = value
        return out
    def constant(value):
        raise CheckFailed(f'Invalid JSON numeric constant {value} in {path}')
    lines = Path(path).read_text().splitlines()
    require(all(line.strip() for line in lines), f'Blank record in {path}')
    return [json.loads(line, object_pairs_hook=pairs, parse_constant=constant) for line in lines]

def indexed(rows, title):
    ids = [row.get('id') for row in rows]
    require(all(isinstance(i, str) and i for i in ids), f'{title}: invalid IDs')
    require(len(set(ids)) == len(ids), f'{title}: duplicate IDs')
    return dict(zip(ids, rows))

def finite_number(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)

def verify_frozen_inputs(root):
    manifest_path = root / 'freeze_manifest.json'
    require(sha(manifest_path) == MANIFEST_SHA256, 'Final freeze manifest SHA mismatch')
    manifest = object_json(manifest_path)
    require(manifest['case_count'] == 80 and manifest['fields'] == list(FIELDS), 'Unexpected frozen suite')
    for relative, expected in manifest['files'].items():
        path = root / relative
        require(path.is_file() and sha(path) == expected, f'Frozen file changed or missing: {relative}')
    approval = object_json(root / 'audit/freeze_approval.json')
    require(approval['approved_for_freeze'] is True, 'No affirmative independent freeze approval')
    for relative, expected in {**approval['files'], **approval['additional_sha256']}.items():
        require(sha(root / relative) == expected, f'Approved file changed: {relative}')
    cases = jsonl(root / 'data/cases.jsonl')
    gold_rows = jsonl(root / 'data/gold.jsonl')
    requests = jsonl(root / 'data/requests.jsonl')
    metadata = jsonl(root / 'data/metadata.jsonl')
    require(len(cases) == 80, 'Expected exactly 80 cases')
    cm, gm, rm, mm = (indexed(rows, title) for rows, title in
                       ((cases,'cases'),(gold_rows,'gold'),(requests,'requests'),(metadata,'metadata')))
    require(set(cm) == set(gm) == set(rm) == set(mm), 'Frozen data IDs do not match')
    ids = list(cm)
    require(ids == list(gm) == list(rm) == list(mm), 'Frozen data order differs')
    policy = object_json(root / 'data/policy.json')
    for identity in ids:
        c, g, r, m = cm[identity], gm[identity], rm[identity], mm[identity]
        require(c['expected'] == g['expected'], f'{identity}: case/gold mismatch')
        require(r['request']['state'] == 'Synthetische Kundennachricht:\n' + c['message'], f'{identity}: state mismatch')
        require(r['request']['questions'] == policy['questions'], f'{identity}: policy mismatch')
        require(m == {k:v for k,v in c.items() if k not in ('message','expected')}, f'{identity}: metadata mismatch')
    preflight = object_json(root / 'audit/encoding_preflight.json')
    token_map = indexed(preflight['cases'], 'encoding preflight')
    require(set(token_map) == set(cm) and preflight['count'] == 80, 'Preflight ID mismatch')
    require(preflight['requests_sha256'] == sha(root / 'data/requests.jsonl'), 'Preflight request hash mismatch')
    return manifest, cases, rm, token_map

def validate_predictions(cases, requests, tokens, predictions):
    pred_map = indexed(predictions, 'predictions')
    ids = [c['id'] for c in cases]
    require(set(pred_map) == set(ids), 'Prediction IDs are missing or extra')
    require(list(pred_map) == ids, 'Prediction ordering differs from frozen requests')
    for identity in ids:
        p = pred_map[identity]
        require(set(p['answers']) == set(FIELDS), f'{identity}: wrong answer fields')
        require(set(p['probabilities_unrounded']) == set(FIELDS), f'{identity}: wrong probability fields')
        require(p['truncated'] is False, f'{identity}: truncation flag')
        require(type(p['input_tokens']) is int and 0 < p['input_tokens'] <= 2048, f'{identity}: invalid tokens')
        require(p['input_tokens'] == tokens[identity]['input_tokens'], f'{identity}: tokens differ from frozen preflight')
        require(finite_number(p['inference_seconds']) and p['inference_seconds'] > 0, f'{identity}: invalid timing')
        require(type(p['rss_bytes']) is int and p['rss_bytes'] > 0, f'{identity}: invalid RSS')
        for field in FIELDS:
            opts = list(requests[identity]['request']['questions'][field]['criteria'])
            a = p['answers'][field]
            values = p['probabilities_unrounded'][field]
            require(set(a) == {'type','choice','confidence','probabilities'}, f'{identity}/{field}: answer shape')
            require(a['type'] == 'choice' and a['choice'] in opts, f'{identity}/{field}: invalid choice')
            require(set(values) == set(opts), f'{identity}/{field}: probability option IDs')
            require(all(finite_number(x) and 0 <= x <= 1 for x in values.values()), f'{identity}/{field}: invalid probability')
            require(abs(math.fsum(values.values()) - 1.0) < 1e-5, f'{identity}/{field}: probabilities do not sum to one')
            # The public official converter uses criteria-order tie breaking.
            selected = sorted(enumerate(opts), key=lambda z: (-values[z[1]], z[0]))[0][1]
            require(a['choice'] == selected, f'{identity}/{field}: incorrect argmax or tie break')
            require(finite_number(a['confidence']) and a['confidence'] == round(values[selected], 4), f'{identity}/{field}: rounded confidence mismatch')
            require(set(a['probabilities']) == set(opts), f'{identity}/{field}: rounded option IDs')
            require(all(finite_number(a['probabilities'][o]) and a['probabilities'][o] == round(values[o],4) for o in opts), f'{identity}/{field}: rounded probabilities mismatch')
    return pred_map

def fraction(flags):
    flags = list(flags)
    return {'correct': sum(flags), 'total': len(flags), 'accuracy': sum(flags) / len(flags) if flags else None}

def recompute(cases, pred_map):
    ids = [c['id'] for c in cases]
    truth = {c['id']: c['expected'] for c in cases}
    choices = {i: {f: pred_map[i]['answers'][f]['choice'] for f in FIELDS} for i in ids}
    correct = {i: tuple(choices[i][f] == truth[i][f] for f in FIELDS) for i in ids}
    metrics = {f: fraction(correct[i][j] for i in ids) for j, f in enumerate(FIELDS)}
    metrics['all_fields_exact'] = fraction(all(correct[i]) for i in ids)
    metrics['all_field_decisions'] = fraction(v for i in ids for v in correct[i])
    predicates = {
      'critical_cases': lambda g,p: g['priority'] == 'critical',
      'critical_priority_misses': lambda g,p: g['priority'] == 'critical' and p['priority'] != 'critical',
      'critical_handoff_misses': lambda g,p: g['priority'] == 'critical' and p['next_step'] != 'security_handoff',
      'critical_safety_case_errors': lambda g,p: g['priority'] == 'critical' and (p['priority'] != 'critical' or p['next_step'] != 'security_handoff'),
      'urgent_cases': lambda g,p: g['priority'] == 'urgent',
      'urgent_undertriage': lambda g,p: g['priority'] == 'urgent' and p['priority'] == 'routine',
      'unnecessary_critical_priority': lambda g,p: g['priority'] != 'critical' and p['priority'] == 'critical',
      'unnecessary_security_handoffs': lambda g,p: g['next_step'] != 'security_handoff' and p['next_step'] == 'security_handoff',
      'non_escalation_reference_cases': lambda g,p: g['next_step'] in {'guidance','clarify'},
      'unnecessary_escalations': lambda g,p: g['next_step'] in {'guidance','clarify'} and p['next_step'] in {'specialist_review','security_handoff'},
      'missed_clarifications': lambda g,p: g['next_step'] == 'clarify' and p['next_step'] != 'clarify',
    }
    safety_ids = {name:[i for i in ids if test(truth[i],choices[i])] for name,test in predicates.items()}
    safety = {name:{'count':len(members),'ids':members} for name,members in safety_ids.items()}
    confusion = {}
    for field in FIELDS:
        pairs = collections.Counter((truth[i][field], choices[i][field]) for i in ids)
        confusion[field] = {g: {p:n for (gg,p),n in pairs.items() if gg==g}
                            for g in sorted({truth[i][field] for i in ids})}
    strata = {}
    for key in STRATA:
        memberships = {c['id']: c[key] if key in c else truth[c['id']][key] for c in cases}
        strata[key] = {}
        for group in sorted(set(memberships.values())):
            members = [i for i in ids if memberships[i] == group]
            strata[key][group] = {'case_count':len(members),'all_fields_exact':fraction(all(correct[i]) for i in members),
                                  **{f:fraction(correct[i][j] for i in members) for j,f in enumerate(FIELDS)}}
    errors = [{'id':c['id'],'topic':c['topic'],'message':c['message'],'expected':truth[c['id']],
               'predicted':choices[c['id']], 'incorrect_fields':[f for f in FIELDS if choices[c['id']][f]!=truth[c['id']][f]],
               'rationale':c['rationale'],'clarification_target':c['clarification_target'],
               'probabilities_unrounded':pred_map[c['id']]['probabilities_unrounded']}
              for c in cases if not all(correct[c['id']])]
    timing = sorted(pred_map[i]['inference_seconds'] for i in ids)
    n = len(timing)
    median = timing[n//2] if n%2 else (timing[n//2-1]+timing[n//2])/2
    position = (n-1)*0.95
    low, high = math.floor(position), math.ceil(position)
    p95 = timing[low] * (high-position) + timing[high] * (position-low) if high!=low else timing[low]
    technical = {'schema_valid_cases':len(ids),'truncated_cases':0,
                 'input_tokens_min':min(pred_map[i]['input_tokens'] for i in ids),
                 'input_tokens_max':max(pred_map[i]['input_tokens'] for i in ids),
                 'forward_seconds_median':median,'forward_seconds_p95':p95,
                 'peak_observed_rss_bytes':max(pred_map[i]['rss_bytes'] for i in ids)}
    return {'metrics':metrics,'safety':safety,'confusion_matrices':confusion,'strata':strata,
            'technical':technical,'errors_count':len(errors)}, errors

def differences(want, got, path='root'):
    if isinstance(want,dict):
        if not isinstance(got,dict) or set(want)!=set(got):
            return [f'{path}: different dictionary keys']
        return [item for key in want for item in differences(want[key],got[key],f'{path}.{key}')]
    if isinstance(want,list):
        if not isinstance(got,list) or len(want)!=len(got):
            return [f'{path}: different list length/type']
        return [item for index,(a,b) in enumerate(zip(want,got)) for item in differences(a,b,f'{path}[{index}]')]
    if isinstance(want,float):
        return [] if finite_number(got) and math.isclose(want,got,rel_tol=1e-12,abs_tol=1e-12) else [f'{path}: {want!r} != {got!r}']
    return [] if want==got and type(want)==type(got) else [f'{path}: {want!r} != {got!r}']

def completed_audit(root, results):
    manifest, cases, requests, tokens = verify_frozen_inputs(root)
    # Refuse before reading predictions when a run is incomplete.
    meta_path = results / 'predictions.metadata.json'
    metadata = object_json(meta_path)
    require(metadata.get('status') == 'completed' and metadata.get('completed_at'), 'Run is not completed; predictions were not read')
    require(metadata['request_count'] == 80, 'Metadata request count mismatch')
    require(metadata['request_order_ids'] == [c['id'] for c in cases], 'Metadata order mismatch')
    require(metadata['requests_sha256'] == sha(root/'data/requests.jsonl'), 'Metadata request hash mismatch')
    require(metadata['revision'] == manifest['revision'], 'Model revision mismatch')
    require(metadata['runner_sha256'] == manifest['files']['reference_runtime/run_clef.py'], 'Runner hash mismatch')
    require(metadata['source_code_sha256'] == manifest['files']['reference_runtime/joint_schema_model.py'], 'Model source hash mismatch')
    require(metadata['benchmark_requests_only_no_gold'] is True, 'Metadata label-free-input assertion missing')
    require(metadata['max_length'] == 2048 and metadata['threads'] == 6 and metadata['batch_size'] == 1, 'Metadata runtime shape mismatch')
    started = datetime.datetime.fromisoformat(metadata['started_at'])
    frozen = datetime.datetime.fromisoformat(manifest['frozen_at_host_utc'])
    completed = datetime.datetime.fromisoformat(metadata['completed_at'])
    require(frozen <= started < completed, 'Run timestamps do not follow final freeze')
    predictions = jsonl(results/'predictions.jsonl')
    pred_map = validate_predictions(cases,requests,tokens,predictions)
    expected, errors = recompute(cases,pred_map)
    expected['provenance'] = {'requests_sha256':sha(root/'data/requests.jsonl'),'gold_sha256':sha(root/'data/gold.jsonl'),
                              'predictions_sha256':sha(results/'predictions.jsonl')}
    summary = object_json(results/'summary.json')
    require(summary['suite_id']=='bank-support' and summary['split']=='german_bank_support_primary' and
            summary['case_count']==80 and summary['field_count']==3 and summary['language']=='de', 'Summary suite identity mismatch')
    mismatches = [item for section in expected for item in differences(expected[section],summary.get(section),section)]
    mismatches.extend(differences(errors,jsonl(results/'errors.jsonl'),'errors.jsonl'))
    report = {'passed':not mismatches,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'checker_sha256':sha(Path(__file__)),'freeze_manifest_sha256':sha(root/'freeze_manifest.json'),
              'verified_frozen_file_count':len(manifest['files']),'prediction_count':len(predictions),
              'run_metadata_sha256':sha(meta_path),'summary_sha256':sha(results/'summary.json'),
              'errors_sha256':sha(results/'errors.jsonl'),'mismatches':mismatches,
              'method':'Independent computations; no import or invocation of score.py; only completed outputs read',
              'independently_recomputed':expected,'independently_recomputed_errors':errors}
    (root/'audit/independent_score_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    require(not mismatches, f'{len(mismatches)} differences; see audit/independent_score_check.json')
    return report

def self_test(root):
    _, cases, requests, tokens = verify_frozen_inputs(root)
    truth = {c['id']:c['expected'] for c in cases}
    def fixture():
        out=[]
        for c in cases:
            identity=c['id']; answers={}; raw={}
            for f in FIELDS:
                raw[f]={o:float(o==truth[identity][f]) for o in requests[identity]['request']['questions'][f]['criteria']}
                answers[f]={'type':'choice','choice':truth[identity][f],'confidence':1.0,'probabilities':raw[f].copy()}
            out.append({'id':identity,'answers':answers,'probabilities_unrounded':raw,'input_tokens':tokens[identity]['input_tokens'],
                        'truncated':False,'inference_seconds':1.0,'rss_bytes':100})
        return out
    def change(rows,identity,field,choice):
        p=next(p for p in rows if p['id']==identity)
        values={o:float(o==choice) for o in p['probabilities_unrounded'][field]}
        p['probabilities_unrounded'][field]=values
        p['answers'][field]={'type':'choice','choice':choice,'confidence':1.0,'probabilities':values.copy()}
    passed=[]
    perfect=fixture(); summary,errors=recompute(cases,validate_predictions(cases,requests,tokens,perfect))
    require(summary['metrics']['all_fields_exact']['correct']==80 and summary['metrics']['all_field_decisions']['correct']==240 and not errors,'Perfect fixture failed')
    require(summary['safety']['critical_cases']['count']==10 and summary['safety']['urgent_cases']['count']==6 and summary['safety']['non_escalation_reference_cases']['count']==45,'Reference denominator fixture failed')
    passed.append('perfect_predictions_and_reference_denominators')
    changed=fixture()
    for identity,field,choice in [('bank_cards_03','priority','routine'),('bank_cards_03','next_step','guidance'),
                                  ('bank_transfers_02','priority','routine'),('bank_fees_01','priority','critical'),
                                  ('bank_fees_01','next_step','security_handoff'),('bank_cards_07','next_step','specialist_review')]:
        change(changed,identity,field,choice)
    summary,errors=recompute(cases,validate_predictions(cases,requests,tokens,changed))
    require(summary['metrics']['all_fields_exact']['correct']==76 and summary['metrics']['all_field_decisions']['correct']==234 and len(errors)==4,'Mutation totals failed')
    counts={k:v['count'] for k,v in summary['safety'].items()}
    for key in ('critical_priority_misses','critical_handoff_misses','critical_safety_case_errors','urgent_undertriage','unnecessary_critical_priority','unnecessary_security_handoffs','missed_clarifications'):
        require(counts[key]==1, f'Mutation safety {key} failed')
    require(counts['unnecessary_escalations']==2,'Escalation denominator fixture failed')
    require(summary['confusion_matrices']['priority']['critical']['routine']==1,'Critical confusion fixture failed')
    require(summary['strata']['topic']['cards']['all_fields_exact']['correct']==6,'Topic strata fixture failed')
    require(summary['strata']['next_step']['clarify']['next_step']['correct']==13,'Clarify strata fixture failed')
    require(summary['strata']['priority']['urgent']['priority']['correct']==5,'Urgency strata fixture failed')
    require(summary['strata']['answerability']['clarification_needed']['all_fields_exact']['correct']==13,'Answerability strata fixture failed')
    passed.append('combined_errors_all_safety_sets_confusions_and_strata')
    def reject(name,mutate):
        rows=fixture(); mutate(rows)
        try: validate_predictions(cases,requests,tokens,rows)
        except (CheckFailed,KeyError,TypeError): passed.append('reject_'+name)
        else: raise CheckFailed('Accepted invalid fixture '+name)
    reject('missing_id',lambda rows:rows.pop())
    reject('duplicate_id',lambda rows:rows.append(copy.deepcopy(rows[0])))
    reject('extra_id',lambda rows:rows[0].update(id='bank_fake_99'))
    reject('changed_order',lambda rows:rows.reverse())
    reject('truncation',lambda rows:rows[0].update(truncated=True))
    reject('wrong_token_count',lambda rows:rows[0].update(input_tokens=1))
    reject('boolean_token_count',lambda rows:rows[0].update(input_tokens=True))
    reject('extra_probability_field',lambda rows:rows[0]['probabilities_unrounded'].update(extra={}))
    reject('missing_option',lambda rows:rows[0]['probabilities_unrounded']['priority'].pop('routine'))
    reject('nan_probability',lambda rows:rows[0]['probabilities_unrounded']['priority'].update(routine=float('nan')))
    reject('bad_probability_sum',lambda rows:rows[0]['probabilities_unrounded']['priority'].update(routine=0.3))
    reject('wrong_rounded_probability',lambda rows:rows[0]['answers']['priority']['probabilities'].update(routine=0.1))
    reject('wrong_confidence',lambda rows:rows[0]['answers']['priority'].update(confidence=0.5))
    reject('nonmaximal_choice',lambda rows:rows[0]['answers']['priority'].update(choice='routine'))
    # Verify comparison catches substantive changes rather than merely accepting identical dictionaries.
    require(not differences(summary,copy.deepcopy(summary)), 'Equal-result comparator failed')
    wrong=copy.deepcopy(summary); wrong['safety']['critical_safety_case_errors']['count']=2
    require(bool(differences(summary,wrong)), 'Comparator failed to reject altered safety union')
    passed.append('comparison_detects_safety_count_mismatch')
    report={'passed':True,'constructed_fixtures_only':True,'model_outputs_read':False,'model_inference':False,
            'test_count':len(passed),'tests':passed,'checker_sha256':sha(Path(__file__))}
    (root/'audit/independent_score_self_tests.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--results',type=Path)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        report=self_test(args.root)
        print(json.dumps({'passed':report['passed'],'constructed_tests':report['test_count'],'model_outputs_read':False}))
    else:
        report=completed_audit(args.root,args.results or args.root/'results')
        print(json.dumps({'passed':report['passed'],'prediction_count':report['prediction_count'],'metrics':report['independently_recomputed']['metrics']},indent=2))
