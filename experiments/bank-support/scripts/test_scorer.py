#!/usr/bin/env python3
"""Constructed scorer fixtures only. No model is loaded or queried."""
import json,tempfile,copy
from pathlib import Path
from score import score
ROOT=Path(__file__).resolve().parents[1]
rows=[json.loads(x) for x in (ROOT/'data/requests.jsonl').read_text().splitlines()]
gold={x['id']:x['expected'] for x in [json.loads(x) for x in (ROOT/'data/gold.jsonl').read_text().splitlines()]}
def predictions():
 out=[]
 for r in rows:
  p={'id':r['id'],'answers':{},'probabilities_unrounded':{},'input_tokens':1558,'truncated':False,'inference_seconds':1,'rss_bytes':100}
  for f,q in r['request']['questions'].items():
   probs={k:float(k==gold[r['id']][f]) for k in q['criteria']}
   p['answers'][f]={'type':'choice','choice':gold[r['id']][f],'confidence':1.0,'probabilities':probs};p['probabilities_unrounded'][f]=probs
  out.append(p)
 return out
def change(p,f,choice):
 p['answers'][f]['choice']=choice
 for k in p['probabilities_unrounded'][f]:p['probabilities_unrounded'][f][k]=float(k==choice)
 p['answers'][f]['probabilities']=p['probabilities_unrounded'][f].copy()
passed=[]
with tempfile.TemporaryDirectory(prefix='bank_scorer_fixture_') as d:
 output=Path(d)
 def run(ps):
  (output/'predictions.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in ps));return score(ROOT/'data',output)
 ps=predictions();s=run(ps);assert s['metrics']['all_fields_exact']['correct']==80;assert s['metrics']['all_field_decisions']['correct']==240;passed.append('perfect_fixture')
 p=next(p for p in ps if gold[p['id']]['priority']=='critical');change(p,'priority','routine');change(p,'next_step','clarify');s=run(ps);assert s['metrics']['all_fields_exact']['correct']==79 and s['metrics']['all_field_decisions']['correct']==238;assert s['safety']['critical_safety_case_errors']['count']==1;assert s['safety']['critical_handoff_misses']['count']==1;passed.append('critical_union_not_double_counted')
 ps=predictions();p=next(p for p in ps if gold[p['id']]['next_step']=='guidance');change(p,'next_step','specialist_review');s=run(ps);assert s['safety']['unnecessary_escalations']['count']==1;assert s['safety']['unnecessary_security_handoffs']['count']==0;passed.append('avoidable_specialist_escalation')
 ps=predictions();p=next(p for p in ps if gold[p['id']]['priority']=='urgent');change(p,'priority','routine');s=run(ps);assert s['safety']['urgent_undertriage']['count']==1;passed.append('urgent_undertriage')
 for name,mutate in [('missing',lambda p:p[:-1]),('duplicate',lambda p:p+[p[0]]),('truncated',lambda p:([{**p[0],'truncated':True}]+p[1:])),('invalid_probability',lambda p:([{**p[0],'probabilities_unrounded':{}}]+p[1:]))]:
  try:run(mutate(predictions()))
  except (AssertionError,KeyError):passed.append('reject_'+name)
  else:raise AssertionError('Did not reject '+name)
(ROOT/'audit/scorer_self_tests.json').write_text(json.dumps({'constructed_fixtures_only':True,'no_model_inference':True,'passed':passed,'count':len(passed)},indent=2)+'\n')
print(f'{len(passed)} scorer tests passed')
