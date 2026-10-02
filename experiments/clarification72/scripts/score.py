#!/usr/bin/env python3
"""Frozen scoring rules. Marginal option scores are not calibrated probabilities."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,math,statistics,hashlib
FIELDS=('action','determination');THRESHOLDS=(0.8,0.9,0.95)
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def metric(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None}
def pct(xs,p):
 if not xs:return None
 ys=sorted(xs);k=(len(ys)-1)*p;i=int(k);return ys[i]+(ys[min(i+1,len(ys)-1)]-ys[i])*(k-i)
def mapping(rows):
 d={x['id']:x for x in rows};assert len(d)==len(rows),'Duplicate IDs';return d
def score(data,output):
 C=mapping(read(data/'cases.jsonl'));G=mapping(read(data/'gold.jsonl'));R=mapping(read(data/'requests.jsonl'));P=mapping(read(output/'predictions.jsonl'))
 assert len(C)==72 and set(C)==set(G)==set(R),'Invalid input dataset'
 assert set(P)<=set(C),'Unexpected prediction IDs'
 totals=Counter();conf={f:defaultdict(Counter) for f in FIELDS};errors=[];case_scores=[];events=defaultdict(list);strata={k:defaultdict(list) for k in ['domain','stratum','family']}
 valid_preds=[]
 for id,c in C.items():
  g=G[id]['expected'];assert g==c['expected'];p=P.get(id);actual={f:None for f in FIELDS};issues=[];selected={}
  if p is None:issues.append('missing_prediction')
  else:
   try:
    assert p.get('truncated') is False and 0<p['input_tokens']<=2048,'invalid_tokens_or_truncation'
    assert set(p['answers'])==set(FIELDS) and set(p['probabilities_unrounded'])==set(FIELDS),'invalid_fields'
    for f in FIELDS:
     ans=p['answers'][f];probs=p['probabilities_unrounded'][f];options=R[id]['request']['questions'][f]['criteria']
     assert ans['type']=='choice' and ans['choice'] in options,'invalid_choice'
     assert set(probs)==set(options),'invalid_probability_options'
     assert all(isinstance(v,(float,int)) and math.isfinite(v) and 0<=v<=1 for v in probs.values()) and abs(sum(probs.values())-1)<1e-5,'invalid_probabilities'
     assert probs[ans['choice']]==max(probs.values()),'not_argmax'
     assert math.isfinite(ans['confidence']) and abs(ans['confidence']-probs[ans['choice']])<=0.00011,'confidence_mismatch'
     actual[f]=ans['choice'];selected[f]=probs[ans['choice']]
    assert all(math.isfinite(p[k]) and p[k]>=0 for k in ['inference_seconds','encode_seconds','total_seconds','rss_bytes']),'invalid_telemetry'
   except (AssertionError,KeyError,TypeError,ValueError) as e:
    issues.append(str(e));actual={f:None for f in FIELDS};selected={}
  valid=not issues
  if valid:valid_preds.append(p)
  else:events['invalid_or_missing'].append(id)
  correct={f:actual[f]==g[f] for f in FIELDS};exact=all(correct.values())
  for f in FIELDS:totals[f]+=correct[f];conf[f][g[f]][actual[f] or '__invalid__']+=1
  totals['exact']+=exact
  needs=g['action']!='answer';asks=valid and actual['action']!='answer';answers=valid and actual['action']=='answer'
  if needs and answers:events['missed_required_clarifications'].append(id)
  if needs and not asks:events['required_clarifications_not_successfully_requested'].append(id)
  if not needs and asks:events['excess_clarifications'].append(id)
  if needs and asks and actual['action']!=g['action']:events['wrong_clarification_kind'].append(id)
  if valid and ((actual['action']=='answer')!=(actual['determination']!='unresolved')):events['inconsistent_fields'].append(id)
  substantive=answers and actual['determination'] in ['yes','no']
  risky=substantive and (needs or actual['determination']!=g['determination'])
  if substantive:events['substantive_answer_cases'].append(id)
  if risky:events['risky_wrong_answers'].append(id)
  for threshold in THRESHOLDS:
   if substantive and min(selected.values())>=threshold:
    events[f'confident_answers_{threshold}'].append(id)
    if risky:events[f'confident_wrong_answers_{threshold}'].append(id)
  s={'id':id,'valid':valid,'expected':g,'predicted':actual,'field_correct':correct,'all_fields_exact':exact,'selected_probabilities':selected,'required_clarification':needs,'model_requested_clarification':asks,'risky_wrong_answer':risky,'technical_issues':issues}
  case_scores.append(s)
  for k in strata:strata[k][c[k]].append(s)
  if not exact:errors.append({**s,'domain':c['domain'],'family':c['family'],'stratum':c['stratum'],'rule':c['rule'],'message':c['message'],'question':c['question'],'rationale':c['rationale'],'clarification_target':c['clarification_target'],'probabilities_unrounded':p.get('probabilities_unrounded') if p else None})
 N=len(C);required=sum(c['expected']['action']!='answer' for c in C.values());answerable=N-required
 names=['invalid_or_missing','missed_required_clarifications','required_clarifications_not_successfully_requested','excess_clarifications','wrong_clarification_kind','inconsistent_fields','substantive_answer_cases','risky_wrong_answers']+[f'{prefix}_{t}' for t in THRESHOLDS for prefix in ['confident_answers','confident_wrong_answers']]
 for name in names:events[name]=events[name]
 summary={'suite_id':'clarification','case_count':N,'field_count':2,'metrics':{**{f:metric(totals[f],N) for f in FIELDS},'all_fields_exact':metric(totals['exact'],N),'all_field_decisions':metric(sum(totals[f] for f in FIELDS),N*2)},'denominators':{'clarification_required':required,'answerable':answerable,'valid_cases':len(valid_preds),'substantive_answers':len(events['substantive_answer_cases'])},'behavior_rates':{'missed_required_clarifications':metric(len(events['missed_required_clarifications']),required),'required_clarifications_not_successfully_requested':metric(len(events['required_clarifications_not_successfully_requested']),required),'excess_clarifications':metric(len(events['excess_clarifications']),answerable),'wrong_clarification_kind':metric(len(events['wrong_clarification_kind']),required),'risky_wrong_answers_all_cases':metric(len(events['risky_wrong_answers']),N),'risky_wrong_answers_among_substantive':metric(len(events['risky_wrong_answers']),len(events['substantive_answer_cases']))},'high_confidence':{str(t):{'confident_answers':len(events[f'confident_answers_{t}']),'confident_wrong':len(events[f'confident_wrong_answers_{t}']),'wrong_rate_among_confident':metric(len(events[f'confident_wrong_answers_{t}']),len(events[f'confident_answers_{t}']))} for t in THRESHOLDS},'events':{k:{'count':len(v),'ids':v} for k,v in events.items()},'confusion_matrices':{f:{k:dict(v) for k,v in m.items()} for f,m in conf.items()},'strata':{key:{name:{'cases':len(v),'all_fields_exact':metric(sum(z['all_fields_exact'] for z in v),len(v)),**{f:metric(sum(z['field_correct'][f] for z in v),len(v)) for f in FIELDS}} for name,v in groups.items()} for key,groups in strata.items()},'technical':{'recorded_predictions':len(P),'valid_cases':len(valid_preds),'missing_predictions':N-len(P),'invalid_existing_predictions':len(events['invalid_or_missing'])-(N-len(P)),'input_tokens_min':min([p['input_tokens'] for p in valid_preds],default=None),'input_tokens_max':max([p['input_tokens'] for p in valid_preds],default=None),'forward_seconds_median':statistics.median(p['inference_seconds'] for p in valid_preds) if valid_preds else None,'forward_seconds_p95':pct([p['inference_seconds'] for p in valid_preds],.95),'forward_seconds_total':sum(p['inference_seconds'] for p in valid_preds),'peak_observed_rss_bytes':max([p['rss_bytes'] for p in valid_preds],default=None)},'limitations':['AI authored and AI reviewed, not human-expert validated','Purposeful related scenario families, not a representative or independent population sample','Native bounded choices, not generated German clarification questions','Marginal choice probabilities are not validated calibration or a joint probability','Experimental CPU NF4, not stock vendor BF16/GPU behavior'],'provenance':{f'{name}_sha256':hashlib.sha256(path.read_bytes()).hexdigest() for name,path in [('requests',data/'requests.jsonl'),('gold',data/'gold.jsonl'),('predictions',output/'predictions.jsonl')]}}
 (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 for name,rows in [('errors',errors),('case_scores',case_scores)]:
  (output/f'{name}.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data');p.add_argument('--results',type=Path,default=Path(__file__).resolve().parents[1]/'results');a=p.parse_args();print(json.dumps(score(a.data,a.results)['metrics'],indent=2))
