#!/usr/bin/env python3
"""Strict scorer for one frozen bank-support main run. No label repair."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,math,statistics,hashlib
FIELDS=('intent','priority','next_step')
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def metric(n,d):return {'correct':n,'total':d,'accuracy':n/d if d else None}
def percentile(xs,p):
 ys=sorted(xs); k=(len(ys)-1)*p;lo=int(k);hi=min(lo+1,len(ys)-1)
 return ys[lo]+(ys[hi]-ys[lo])*(k-lo) if ys else None
def score(data,output):
 cases=read(data/'cases.jsonl');gold=read(data/'gold.jsonl');requests=read(data/'requests.jsonl');preds=read(output/'predictions.jsonl')
 def mapping(rows):
  d={x['id']:x for x in rows}
  assert len(d)==len(rows),'Duplicate IDs'
  return d
 G=mapping(gold);R=mapping(requests);P=mapping(preds);C=mapping(cases)
 assert set(G)==set(R)==set(C)==set(P),'Missing or extra IDs'
 assert len(G)==80,'Bank primary suite must contain exactly 80 cases'
 assert all(c['expected']==G[c['id']]['expected'] for c in cases)
 totals=Counter();conf={f:defaultdict(Counter) for f in FIELDS};errors=[];safety=defaultdict(list); strata={k:defaultdict(list) for k in ('topic','style','answerability','priority','next_step')}
 for c in cases:
  id=c['id'];g=G[id]['expected'];p=P[id];a=p.get('answers',{})
  assert set(a)==set(FIELDS),f'{id}: missing or extra fields'
  assert p.get('truncated') is False and 0<p['input_tokens']<=2048,f'{id}: truncated or invalid tokens'
  actual={}
  for f in FIELDS:
   q=R[id]['request']['questions'][f]; opts=set(q['criteria']);ans=a[f];probs=p['probabilities_unrounded'][f]
   assert ans['type']=='choice' and ans['choice'] in opts
   assert set(probs)==opts and all(math.isfinite(v) and 0<=v<=1 for v in probs.values()) and abs(sum(probs.values())-1)<1e-5
   assert probs[ans['choice']]==max(probs.values()),f'{id}/{f}: chosen option not maximal'
   assert math.isfinite(ans['confidence']) and abs(ans['confidence']-probs[ans['choice']])<=0.00011
   actual[f]=ans['choice'];totals[f]+=actual[f]==g[f];conf[f][g[f]][actual[f]]+=1
  correct=all(actual[f]==g[f] for f in FIELDS);totals['exact_case']+=correct
  for key in strata:strata[key][c[key] if key in c else g[key]].append((correct,{f:actual[f]==g[f] for f in FIELDS}))
  if not correct:errors.append({'id':id,'topic':c['topic'],'message':c['message'],'expected':g,'predicted':actual,'incorrect_fields':[f for f in FIELDS if actual[f]!=g[f]],'rationale':c['rationale'],'clarification_target':c['clarification_target'],'probabilities_unrounded':p['probabilities_unrounded']})
  if g['priority']=='critical':
   safety['critical_cases'].append(id)
   if actual['priority']!='critical':safety['critical_priority_misses'].append(id)
   if actual['next_step']!='security_handoff':safety['critical_handoff_misses'].append(id)
   if actual['priority']!='critical' or actual['next_step']!='security_handoff':safety['critical_safety_case_errors'].append(id)
  if g['priority']=='urgent':
   safety['urgent_cases'].append(id)
   if actual['priority']=='routine':safety['urgent_undertriage'].append(id)
  if g['priority']!='critical' and actual['priority']=='critical':safety['unnecessary_critical_priority'].append(id)
  if g['next_step']!='security_handoff' and actual['next_step']=='security_handoff':safety['unnecessary_security_handoffs'].append(id)
  if g['next_step'] in ('guidance','clarify'):
   safety['non_escalation_reference_cases'].append(id)
   if actual['next_step'] in ('specialist_review','security_handoff'):safety['unnecessary_escalations'].append(id)
  if g['next_step']=='clarify' and actual['next_step']!='clarify':safety['missed_clarifications'].append(id)
 for key in ['critical_cases','critical_priority_misses','critical_handoff_misses','critical_safety_case_errors','urgent_cases','urgent_undertriage','unnecessary_critical_priority','unnecessary_security_handoffs','non_escalation_reference_cases','unnecessary_escalations','missed_clarifications']:safety[key]=safety[key]
 summary={'suite_id':'bank-support','split':'german_bank_support_primary','case_count':len(cases),'field_count':3,'language':'de','scope':'Synthetic purposive fictional bank support triage; no traffic representativeness or production-safety claim','metrics':{**{f:metric(totals[f],len(cases)) for f in FIELDS},'all_fields_exact':metric(totals['exact_case'],len(cases)),'all_field_decisions':metric(sum(totals[f] for f in FIELDS),len(cases)*3)},'safety':{k:{'count':len(v),'ids':v} for k,v in safety.items()},'safety_definitions':{'critical_priority_misses':'gold critical, predicted urgent or routine','critical_handoff_misses':'gold critical, predicted next_step other than security_handoff','critical_safety_case_errors':'union of the two critical miss sets','urgent_undertriage':'gold urgent, predicted routine','unnecessary_security_handoffs':'gold next_step other than security_handoff, predicted security_handoff','unnecessary_escalations':'gold next_step guidance or clarify, predicted specialist_review or security_handoff; does not equate all specialist cases with avoidable escalation'},'confusion_matrices':{f:{g:dict(v) for g,v in m.items()} for f,m in conf.items()},'strata':{k:{name:{'case_count':len(v),'all_fields_exact':metric(sum(z[0] for z in v),len(v)),**{f:metric(sum(z[1][f] for z in v),len(v)) for f in FIELDS}} for name,v in groups.items()} for k,groups in strata.items()},'technical':{'schema_valid_cases':len(cases),'truncated_cases':0,'input_tokens_min':min(p['input_tokens'] for p in preds),'input_tokens_max':max(p['input_tokens'] for p in preds),'forward_seconds_median':statistics.median(p['inference_seconds'] for p in preds),'forward_seconds_p95':percentile([p['inference_seconds'] for p in preds],.95),'peak_observed_rss_bytes':max(p['rss_bytes'] for p in preds)},'errors_count':len(errors),'provenance':{'requests_sha256':hashlib.sha256((data/'requests.jsonl').read_bytes()).hexdigest(),'gold_sha256':hashlib.sha256((data/'gold.jsonl').read_bytes()).hexdigest(),'predictions_sha256':hashlib.sha256((output/'predictions.jsonl').read_bytes()).hexdigest()}}
 (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 (output/'errors.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in errors))
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data');p.add_argument('--results',type=Path,default=Path(__file__).resolve().parents[1]/'results');a=p.parse_args();print(json.dumps(score(a.data,a.results)['metrics'],indent=2))
