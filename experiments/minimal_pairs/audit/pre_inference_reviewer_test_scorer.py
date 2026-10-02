#!/usr/bin/env python3
"""Separate pre-inference black-box scorer checks. Synthetic rows only; no model import."""
from pathlib import Path
import copy,hashlib,json,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
load=lambda p:[json.loads(s) for s in p.read_text().splitlines() if s.strip()]
C={x['id']:x for x in load(R/'data/cases.jsonl')};Q={x['id']:x for x in load(R/'data/requests.jsonl')};pairs=load(R/'data/pairs.jsonl')
base=[]
for id,c in C.items():
 g=c['expected']
 base.append({'id':id,'answers':{f:{'type':'choice','choice':g[f],'confidence':1.0,'probabilities':{o:float(o==g[f]) for o in Q[id]['request']['questions'][f]['criteria']}} for f in g},'probabilities_unrounded':{f:{o:float(o==g[f]) for o in Q[id]['request']['questions'][f]['criteria']} for f in g},'input_tokens':100,'truncated':False,'inference_seconds':1.0,'encode_seconds':0.1,'total_seconds':1.1,'latency_ms':1000.0,'rss_bytes':10000})
def choice(rows,id,field,value):
 row=next(r for r in rows if r['id']==id)
 row['answers'][field]={'type':'choice','choice':value,'confidence':1.0}
 row['probabilities_unrounded'][field]={o:float(o==value) for o in row['probabilities_unrounded'][field]}
 row['answers'][field]['probabilities']=dict(row['probabilities_unrounded'][field])
def blackbox(rows):
 with tempfile.TemporaryDirectory(prefix='minimal_pair_reviewer_') as folder:
  out=Path(folder);(out/'predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
  process=subprocess.run([sys.executable,str(R/'scripts/score.py'),'--data',str(R/'data'),'--results',str(out)],capture_output=True,text=True)
  if process.returncode:return {'failed':True,'stderr':process.stderr}
  return json.loads((out/'summary.json').read_text())
def get(row,id):return next(r for r in row if r['id']==id)
def oracle(rows,invalid=()):
 mapping={r['id']:r for r in rows};bad=set(invalid)
 pred={id:{f:p['answers'][f]['choice'] for f in ('action','determination')} for id,p in mapping.items() if id not in bad}
 exact={id:pred.get(id)==c['expected'] for id,c in C.items()}
 n={'case_exact':sum(exact.values()),'both_correct':0,'directional':0,'observed_flip':0,'unjustified':0,'valid_inv':0,'failed_inv':0,'stable':0,'stable_wrong':0}
 for p in pairs:
  a,b=p['case_ids'];valid=a in pred and b in pred;both=exact[a] and exact[b];changed=valid and pred[a]!=pred[b];n['both_correct']+=both
  if p['kind']=='flip':n['directional']+=both;n['observed_flip']+=changed
  else:
   n['valid_inv']+=valid;n['unjustified']+=changed;n['failed_inv']+=(not valid or changed);n['stable']+=(valid and not changed);n['stable_wrong']+=(valid and not changed and not both)
 return n
checks=[]
def check(name,rows,invalid=(),must_reject=False):
 result=blackbox(rows)
 try:
  if must_reject:assert result.get('failed') is True,'must reject duplicate/unexpected';expected={'scoring_aborted':True}
  else:
   assert not result.get('failed'),result.get('stderr')
   expected=oracle(rows,invalid)
   observed={'case_exact':result['case_metrics']['all_fields_exact']['numerator']}
   keys={'both_correct':'both_correct','directional':'correct_directional_change','observed_flip':'observed_change_on_flip','unjustified':'unjustified_change','failed_inv':'failed_invariance','stable':'stable_invariant','stable_wrong':'stable_but_incorrect'}
   observed.update({k:result['pair_metrics'][metric]['numerator'] for k,metric in keys.items()});observed['valid_inv']=result['pair_metrics']['unjustified_change_among_valid']['denominator'];assert observed==expected,(observed,expected)
   assert result['case_metrics']['all_fields_exact']['denominator']==48
   assert result['pair_metrics']['both_correct']['denominator']==24
   for key in ('correct_directional_change','unjustified_change','failed_invariance','stable_invariant','stable_but_incorrect'):assert result['pair_metrics'][key]['denominator']==12,key
   if not expected['valid_inv']:assert result['pair_metrics']['unjustified_change_among_valid']['rate'] is None
  checks.append({'name':name,'passed':True,'expected':expected})
 except Exception as e:checks.append({'name':name,'passed':False,'error':repr(e)})
check('gold_fixture',copy.deepcopy(base))
check('no_predictions',[])
flips=[p for p in pairs if p['kind']=='flip'];invariants=[p for p in pairs if p['kind']=='invariant']
b=copy.deepcopy(base)
for pair in flips:
 a,c=pair['case_ids']
 for f in ('action','determination'):
  choice(b,a,f,C[c]['expected'][f]);choice(b,c,f,C[a]['expected'][f])
check('all_flip_directions_reversed',b)
b=copy.deepcopy(base)
for r in b:
 choice(b,r['id'],'action','answer');choice(b,r['id'],'determination','no')
check('constant_answer_no',b)
a,c=invariants[0]['case_ids'];b=copy.deepcopy(base)
for id in (a,c):choice(b,id,'determination','unresolved' if C[id]['expected']['determination']!='unresolved' else 'yes')
check('stable_wrong_invariant',b)
b=copy.deepcopy(base);choice(b,c,'determination','unresolved' if C[c]['expected']['determination']!='unresolved' else 'yes');check('one_field_unjustified_change',b)
a,c=flips[0]['case_ids'];b=copy.deepcopy(base);choice(b,a,'action','ask_fact' if C[a]['expected']['action']!='ask_fact' else 'answer');check('flip_one_field_wrong',b)
a,c=invariants[0]['case_ids']
check('missing_invariant_b',[r for r in base if r['id']!=c])
check('both_invariant_missing',[r for r in base if r['id'] not in (a,c)])
mutations={
 'missing_rounded_map':lambda r:r['answers']['action'].pop('probabilities'),
 'boolean_rounded_probability':lambda r:r['answers']['action']['probabilities'].update(answer=True),
 'wrong_rounded_probability':lambda r:r['answers']['action']['probabilities'].update(answer=0.3),
 'boolean_token':lambda r:r.update(input_tokens=True),
 'float_token':lambda r:r.update(input_tokens=100.0),
 'boolean_confidence':lambda r:r['answers']['action'].update(confidence=True),
 'boolean_timing':lambda r:r.update(encode_seconds=True),
 'boolean_rss':lambda r:r.update(rss_bytes=True),
 'probability_nan':lambda r:r['probabilities_unrounded']['action'].update(answer=float('nan')),
 'probability_boolean':lambda r:r['probabilities_unrounded']['action'].update(answer=True),
 'missing_action_field':lambda r:r['answers'].pop('action'),
 'not_argmax':lambda r:r['answers']['action'].update(choice='answer' if r['answers']['action']['choice']!='answer' else 'ask_fact'),
 'truncated':lambda r:r.update(truncated=True),
 'negative_latency':lambda r:r.update(latency_ms=-1.0),
 'bad_confidence':lambda r:r['answers']['action'].update(confidence=0.13),
}
for name,mutate in mutations.items():
 b=copy.deepcopy(base);mutate(get(b,c));check(name,b,invalid=(c,))
b=copy.deepcopy(base);get(b,a)['answers']={};get(b,c)['answers']={};check('identically_invalid_pair_not_stable',b,invalid=(a,c))
b=copy.deepcopy(base);get(b,c)['answers']['action']['confidence']=0.99999;check('confidence_within_declared_tolerance_valid',b)
b=copy.deepcopy(base);t=get(b,c);t['probabilities_unrounded']['action']={'answer':0.5,'ask_fact':0.5,'ask_target':0.0,'resolve_conflict':0.0};t['answers']['action']={'type':'choice','choice':'answer','confidence':0.5,'probabilities':dict(t['probabilities_unrounded']['action'])};check('argmax_tie_first_option_valid',b)
b=copy.deepcopy(b);get(b,c)['answers']['action']['choice']='ask_fact';check('argmax_tie_later_option_invalid',b,invalid=(c,))
b=copy.deepcopy(base);b.append(copy.deepcopy(b[0]));check('duplicate_id',b,must_reject=True)
b=copy.deepcopy(base);b[0]['id']='unknown_case';check('unexpected_id',b,must_reject=True)
report={'reviewer_type':'separate AI pre-inference reviewer','no_model_loaded':True,'synthetic_predictions_only':True,'primary_scorer_not_imported':True,'test_method':'CLI black-box executions compared to a separate direct counting oracle','count':len(checks),'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'checks':checks,'reviewed_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'scripts/score.py',R/'data/requests.jsonl',R/'data/cases.jsonl',R/'data/gold.jsonl',R/'data/pairs.jsonl']}}
(R/'audit/pre_inference_reviewer_scorer_tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('checks','reviewed_sha256')},indent=2))
for c in checks:
 if not c['passed']:print(c)
raise SystemExit(bool(report['failed']))
