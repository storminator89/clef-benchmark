#!/usr/bin/env python3
"""Synthetic-only tests of the independent checker. No primary scorer or model calls."""
import argparse,copy,json,math,tempfile,sys
from pathlib import Path
import independent_result_check as audit

def synthetic(D):
    token={x['id']:x['input_tokens'] for x in D['preflight']['cases']}; rows=[]
    for i,c in enumerate(D['cases']):
        raw={'id':c['id'],'answers':{},'probabilities_unrounded':{},'input_tokens':token[c['id']],'truncated':False,'encode_seconds':.125,'inference_seconds':i+1.,'latency_ms':(i+1.)*1000,'total_seconds':i+1.25,'rss_bytes':100000+i}
        for f in audit.FIELDS:
            p={o:float(o==c['expected'][f]) for o in audit.OPTIONS[f]}
            raw['probabilities_unrounded'][f]=p;raw['answers'][f]={'type':'choice','choice':c['expected'][f],'confidence':1.,'probabilities':p.copy()}
        rows.append(raw)
    return rows

def assign(row,field,choice):
    p={o:float(o==choice) for o in audit.OPTIONS[field]}; row['probabilities_unrounded'][field]=p
    row['answers'][field]={'type':'choice','choice':choice,'confidence':1.,'probabilities':p.copy()}

def run(root):
    D=audit.load_data(root);base=synthetic(D);gold={x['id']:x for x in D['gold']};q={x['id']:x for x in D['requests']};tests=[]
    def compute(rows):return audit.compute(D['cases'],D['pairs'],gold,q,D['preflight'],rows)
    def test(name,fn):
        try:fn();tests.append({'name':name,'passed':True})
        except Exception as exc:tests.append({'name':name,'passed':False,'error':repr(exc)})
    def ck(condition):
        if not condition:raise AssertionError('Assertion failed')
    perfect=compute(base)
    test('perfect_native_all_48',lambda:ck(all(c['valid'] and c['exact'] for c in perfect['case_results'])))
    test('perfect_pairs_all_24',lambda:ck(perfect['summary']['pair_both_correct']==audit.ratio(24,24)))
    test('perfect_direction_12',lambda:ck(perfect['summary']['flip_correct_directional_change']==audit.ratio(12,12)))
    test('fixed_48_case_denominator',lambda:ck(compute(base[:-1])['summary']['case_exact']==audit.ratio(47,48)))
    empty=compute([])
    test('all_missing_retains_denominators',lambda:ck(empty['summary']['case_exact']==audit.ratio(0,48) and empty['summary']['pair_both_correct']==audit.ratio(0,24)))
    test('all_missing_invariants_not_stable',lambda:ck(empty['summary']['invariant_stable']==audit.ratio(0,12) and empty['summary']['invariant_failed']==audit.ratio(12,12)))
    test('zero_valid_conditional_is_null',lambda:ck(empty['summary']['invariant_unjustified_change_valid_conditional']==audit.ratio(0,0)))
    firstinv=next(p for p in D['pairs'] if p['kind']=='invariant');inv_ids=firstinv['case_ids'];firstflip=next(p for p in D['pairs'] if p['kind']=='flip');flip_ids=firstflip['case_ids']
    def stable_wrong():
        rows=copy.deepcopy(base)
        for r in rows:
            if r['id'] in inv_ids:assign(r,'action','ask_fact' if gold[r['id']]['expected']['action']!='ask_fact' else 'answer')
        s=compute(rows)['summary'];ck(s['invariant_stable_wrong']['numerator']==1 and s['invariant_stable']['numerator']==12 and s['pair_both_correct']['numerator']==23)
    test('stable_wrong_never_both_correct',stable_wrong)
    def unjustified():
        rows=copy.deepcopy(base);r=next(x for x in rows if x['id']==inv_ids[1]);assign(r,'action','ask_fact' if gold[r['id']]['expected']['action']!='ask_fact' else 'answer')
        s=compute(rows)['summary'];ck(s['invariant_unjustified_change']==audit.ratio(1,12) and s['invariant_failed']==audit.ratio(1,12))
    test('one_field_change_is_unjustified',unjustified)
    def wrong_direction():
        rows=copy.deepcopy(base)
        for r in rows:
            if r['id'] in flip_ids:
                other=flip_ids[1-flip_ids.index(r['id'])]
                for f in audit.FIELDS:assign(r,f,gold[other]['expected'][f])
        s=compute(rows)['summary'];ck(s['flip_observed_change']['numerator']==12 and s['flip_correct_directional_change']['numerator']==11)
    test('changed_reversed_endpoints_not_directional_success',wrong_direction)
    def invalid_invariant():
        rows=copy.deepcopy(base);next(x for x in rows if x['id']==inv_ids[1])['truncated']=True
        s=compute(rows)['summary'];ck(s['invariant_stable']['numerator']==11 and s['invariant_invalid']==audit.ratio(1,12) and s['invariant_unjustified_change_valid_conditional']==audit.ratio(0,11))
    test('invalid_invariant_not_stable',invalid_invariant)
    mutations={
        'boolean_tokens':lambda r:r.update(input_tokens=True),
        'zero_tokens':lambda r:r.update(input_tokens=0),
        'over_cap_tokens':lambda r:r.update(input_tokens=2049),
        'wrong_preflight_tokens':lambda r:r.update(input_tokens=r['input_tokens']+1),
        'missing_tokens':lambda r:r.pop('input_tokens'),
        'truncated_true':lambda r:r.update(truncated=True),
        'truncated_zero':lambda r:r.update(truncated=0),
        'missing_field':lambda r:r['answers'].pop('action'),
        'extra_field':lambda r:r['answers'].update(extra={}),
        'native_type':lambda r:r['answers']['action'].update(type='score'),
        'invalid_choice':lambda r:r['answers']['action'].update(choice='maybe'),
        'unhashable_choice':lambda r:r['answers']['action'].update(choice=[]),
        'boolean_confidence':lambda r:r['answers']['action'].update(confidence=True),
        'mismatched_confidence':lambda r:r['answers']['action'].update(confidence=.8),
        'missing_rounded_map':lambda r:r['answers']['action'].pop('probabilities'),
        'mismatched_rounded_map':lambda r:r['answers']['action']['probabilities'].update(answer=.1234),
        'boolean_rounded_map':lambda r:r['answers']['action']['probabilities'].update(answer=True),
        'extra_full_option':lambda r:r['probabilities_unrounded']['action'].update(extra=.0),
        'missing_full_option':lambda r:r['probabilities_unrounded']['action'].pop('ask_fact'),
        'nan_full_probability':lambda r:r['probabilities_unrounded']['action'].update(answer=float('nan')),
        'infinite_full_probability':lambda r:r['probabilities_unrounded']['action'].update(answer=float('inf')),
        'negative_full_probability':lambda r:r['probabilities_unrounded']['action'].update(answer=-.01),
        'unnormalized_full_probability':lambda r:r['probabilities_unrounded']['action'].update(answer=.5),
        'boolean_full_probability':lambda r:r['probabilities_unrounded']['action'].update(answer=True),
        'negative_encode_time':lambda r:r.update(encode_seconds=-1),
        'nan_forward_time':lambda r:r.update(inference_seconds=float('nan')),
        'boolean_forward_time':lambda r:r.update(inference_seconds=True),
        'wrong_latency_ms':lambda r:r.update(latency_ms=r['latency_ms']+1),
        'insufficient_total_time':lambda r:r.update(total_seconds=r['inference_seconds']),
        'boolean_rss':lambda r:r.update(rss_bytes=True),
        'zero_rss':lambda r:r.update(rss_bytes=0),
        'missing_timing':lambda r:r.pop('encode_seconds'),
    }
    for name,mutate in mutations.items():
        def attempt(mutate=mutate):
            rows=copy.deepcopy(base);mutate(rows[0]);r=compute(rows)
            ck(not r['scoring_stopped'] and not r['case_results'][0]['valid'] and r['summary']['case_exact']['numerator']==47)
        test(name,attempt)
    def tie_test(correct):
        r=copy.deepcopy(base[0]);p={'answer':.5,'ask_fact':.5,'ask_target':0.,'resolve_conflict':0.};r['probabilities_unrounded']['action']=p;r['answers']['action']={'type':'choice','choice':'answer' if correct else 'ask_fact','confidence':.5,'probabilities':p.copy()}
        ck(audit.validate_native(r)['valid']==correct)
    test('tie_first_criterion_accepted',lambda:tie_test(True));test('tie_later_criterion_rejected',lambda:tie_test(False))
    def reordered_full_map():
        r=copy.deepcopy(base[0]);r['probabilities_unrounded']['determination']={k:r['probabilities_unrounded']['determination'][k] for k in sorted(r['probabilities_unrounded']['determination'])}
        ck(audit.validate_native(r)['valid'])
    test('encoder_sorted_full_map_is_valid',reordered_full_map)
    test('manifest_hash_byte_projection',lambda:ck(audit.equal({'file':{'bytes':10,'sha256':'a'}},{k:{'bytes':v['bytes'],'sha256':v['sha256']} for k,v in {'file':{'bytes':10,'sha256':'a','hf_commit':'revision','hf_etag':'etag'}}.items()})))
    test('duplicate_id_stops_scores',lambda:ck(compute(base+[base[0]])['scoring_stopped']))
    test('unexpected_id_stops_scores',lambda:ck(compute(base+[dict(base[0],id='unexpected')])['scoring_stopped']))
    test('list_id_stops_without_exception',lambda:ck(compute(base+[dict(base[0],id=[])])['scoring_stopped']))
    test('null_id_stops_without_exception',lambda:ck(compute(base+[dict(base[0],id=None)])['scoring_stopped']))
    test('linear_p95_definition',lambda:ck(audit.percentile(list(range(1,49)),.95)==45.65))
    test('all_48_timing_rows',lambda:ck(perfect['summary']['timing']['inference_seconds']['sum']==1176.))
    test('all_24_pair_strata',lambda:ck(sum(v['both_correct']['denominator'] for v in perfect['summary']['pair_strata']['domain_subtype'].values())==24))
    test('all_48_confusion_rows',lambda:ck(all(sum(sum(row.values()) for row in cm.values())==48 for cm in perfect['summary']['confusion'].values())))
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'rows.jsonl'
        for name,text in [('duplicate_json_member','{"id":"a","id":"b"}\n'),('malformed_json','{broken\n'),('non_object_json','[]\n'),('blank_jsonl','\n')]:
            p.write_text(text);test(name,lambda p=p:ck(bool(audit.read_rows(p)[2])))
        p.write_text('{"id":"x","probability":NaN}\n');raw,ev,errors=audit.read_rows(p);out=Path(td)/'out.json';audit.dump(out,ev)
        test('nonfinite_preserved_in_audit_evidence',lambda:ck('__nonfinite_float__' in out.read_text()))
    return {'synthetic_only':True,'model_calls':0,'primary_scorer_imports_or_calls':0,'passed':sum(t['passed'] for t in tests),'failed':sum(not t['passed'] for t in tests),'tests':tests}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args();r=run(a.root)
    if a.output:audit.dump(a.output,r)
    print(json.dumps(r,indent=2));sys.exit(bool(r['failed']))
