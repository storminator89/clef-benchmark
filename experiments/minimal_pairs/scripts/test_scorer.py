#!/usr/bin/env python3
from pathlib import Path
import tempfile,json,copy,importlib.util
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('primary',R/'scripts/score.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
Q=m.read(R/'data/requests.jsonl');G={x['id']:x['expected'] for x in m.read(R/'data/gold.jsonl')};pairs=m.read(R/'data/pairs.jsonl');base=[]
for q in Q:
 g=G[q['id']];base.append({'id':q['id'],'answers':{f:{'type':'choice','choice':g[f],'confidence':1.0,'probabilities':{k:float(k==g[f]) for k in q['request']['questions'][f]['criteria']}} for f in g},'probabilities_unrounded':{f:{k:float(k==g[f]) for k in q['request']['questions'][f]['criteria']} for f in g},'input_tokens':100,'truncated':False,'encode_seconds':0.1,'inference_seconds':1.,'total_seconds':1.1,'latency_ms':1000.,'rss_bytes':1000})
def run(rows):
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);(p/'predictions.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));return m.score(R/'data',p)
def alter(rows,id,field,value):
 p=next(x for x in rows if x['id']==id);p['answers'][field].update(choice=value,confidence=1.);p['probabilities_unrounded'][field]={k:float(k==value) for k in p['probabilities_unrounded'][field]};p['answers'][field]['probabilities']=p['probabilities_unrounded'][field].copy()
results=[]
def check(name,fn):
 try:fn();results.append({'test':name,'passed':True})
 except Exception as e:results.append({'test':name,'passed':False,'error':repr(e)})
def eq(a,b):assert a==b,(a,b)
def perfect():
 s=run(base);eq(s['case_metrics']['all_fields_exact']['numerator'],48);eq(s['pair_metrics']['both_correct']['numerator'],24);eq(s['pair_metrics']['correct_directional_change']['numerator'],12);eq(s['pair_metrics']['unjustified_change']['numerator'],0);eq(s['pair_metrics']['stable_invariant']['numerator'],12)
check('perfect_gold',perfect)
def missing():
 s=run(base[1:]);eq(s['case_metrics']['all_fields_exact']['denominator'],48);eq(s['case_metrics']['all_fields_exact']['numerator'],47);eq(s['pair_metrics']['both_correct']['denominator'],24);eq(s['pair_metrics']['both_correct']['numerator'],23);eq(s['technical']['missing_predictions'],1)
check('missing_fixed_denominators',missing)
def inv_missing():
 id=next(p for p in pairs if p['kind']=='invariant')['case_ids'][0];s=run([x for x in base if x['id']!=id]);eq(s['pair_metrics']['stable_invariant']['numerator'],11);eq(s['pair_metrics']['failed_invariance']['numerator'],1);eq(s['pair_metrics']['unjustified_change_among_valid']['denominator'],11)
check('missing_invariant_never_stable',inv_missing)
def stable_wrong():
 p=next(p for p in pairs if p['kind']=='invariant' and p['expected_a']['determination']=='yes');b=copy.deepcopy(base)
 for id in p['case_ids']:alter(b,id,'determination','no')
 s=run(b);eq(s['pair_metrics']['stable_but_incorrect']['numerator'],1);eq(s['pair_metrics']['both_correct']['numerator'],23);eq(s['pair_metrics']['unjustified_change']['numerator'],0)
check('stable_wrong_not_correct',stable_wrong)
def unjustified():
 p=next(p for p in pairs if p['kind']=='invariant' and p['expected_a']['determination']=='yes');b=copy.deepcopy(base);alter(b,p['case_ids'][1],'determination','no');s=run(b);eq(s['pair_metrics']['unjustified_change']['numerator'],1);eq(s['pair_metrics']['failed_invariance']['numerator'],1)
check('single_field_unjustified_change',unjustified)
def reverse_flip():
 p=next(p for p in pairs if p['subtype']=='yes_to_no');b=copy.deepcopy(base);alter(b,p['case_ids'][0],'determination','no');alter(b,p['case_ids'][1],'determination','yes');s=run(b);eq(s['pair_metrics']['observed_change_on_flip']['numerator'],12);eq(s['pair_metrics']['correct_directional_change']['numerator'],11)
check('observed_change_is_not_directional_success',reverse_flip)
def wrong_action():
 p=next(p for p in pairs if p['subtype']=='clarify_to_answer');b=copy.deepcopy(base);alter(b,p['case_ids'][0],'action','answer');s=run(b);eq(s['pair_metrics']['correct_directional_change']['numerator'],11)
check('correct_determination_insufficient',wrong_action)
def reject(kind):
 b=copy.deepcopy(base)
 if kind=='duplicate':b.append(b[0])
 else:b[0]['id']='unexpected'
 try:run(b)
 except AssertionError:return
 raise AssertionError('Not rejected')
for k in ['duplicate','unexpected']:check(k+'_id_rejected',lambda k=k:reject(k))
def invalid(change):
 b=copy.deepcopy(base);change(b[0]);s=run(b);eq(s['technical']['valid_cases'],47);eq(s['case_metrics']['all_fields_exact']['numerator'],47);eq(s['pair_metrics']['both_correct']['numerator'],23)
changes={'missing_rounded_map':lambda p:p['answers']['action'].pop('probabilities'),'rounded_map_mismatch':lambda p:p['answers']['action']['probabilities'].update(answer=.345),'boolean_tokens':lambda p:p.update(input_tokens=True),'boolean_confidence':lambda p:p['answers']['action'].update(confidence=True),'boolean_telemetry':lambda p:p.update(rss_bytes=True),'truncation':lambda p:p.update(truncated=True),'over_cap':lambda p:p.update(input_tokens=2049),'missing_fields':lambda p:p['answers'].pop('action'),'bad_choice':lambda p:p['answers']['action'].update(choice='other'),'bad_option_set':lambda p:p['probabilities_unrounded']['action'].update(other=0),'nan_probability':lambda p:p['probabilities_unrounded']['action'].update(answer=float('nan')),'unnormalized':lambda p:p['probabilities_unrounded']['action'].update(answer=0.5),'confidence_mismatch':lambda p:p['answers']['action'].update(confidence=0.123),'negative_timing':lambda p:p.update(inference_seconds=-1.),'latency_mismatch':lambda p:p.update(latency_ms=15.)}
for name,change in changes.items():check(name+'_invalid',lambda change=change:invalid(change))
result={'tests':results,'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results),'uses_synthetic_predictions_only':True}
(R/'audit/scorer_self_tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['failed']==0
