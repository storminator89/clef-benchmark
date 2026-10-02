#!/usr/bin/env python3
"""Frozen paired finite-set scoring. Never load model or infer labels."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,math,statistics,hashlib
FIELDS=('action','determination')
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def metric(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None}
def mapping(xs):
 d={x['id']:x for x in xs};assert len(d)==len(xs),'Duplicate IDs';return d
def percentile(xs,q):
 if not xs:return None
 s=sorted(xs);k=(len(s)-1)*q;i=int(k);return s[i]+(s[min(i+1,len(s)-1)]-s[i])*(k-i)
def score(data,output):
 C=mapping(read(data/'cases.jsonl'));G=mapping(read(data/'gold.jsonl'));Q=mapping(read(data/'requests.jsonl'));pairs=read(data/'pairs.jsonl');P=mapping(read(output/'predictions.jsonl'))
 assert len(C)==48 and len(pairs)==24 and set(C)==set(G)==set(Q),'Invalid input dataset'
 assert set(P)<=set(C),'Unexpected prediction IDs'
 scores=[];errors=[];tot=Counter();conf={f:defaultdict(Counter) for f in FIELDS};valid_native=[]
 for id,c in C.items():
  g=G[id]['expected'];assert g==c['expected'];p=P.get(id);actual={f:None for f in FIELDS};selected={};issues=[]
  if p is None:issues=['missing_prediction']
  else:
   try:
    assert p.get('truncated') is False and type(p['input_tokens']) is int and 0<p['input_tokens']<=2048,'invalid_tokens_or_truncation'
    assert set(p['answers'])==set(FIELDS) and set(p['probabilities_unrounded'])==set(FIELDS),'invalid_fields'
    for f in FIELDS:
     ans=p['answers'][f];probs=p['probabilities_unrounded'][f];options=Q[id]['request']['questions'][f]['criteria']
     assert ans['type']=='choice' and ans['choice'] in options,'invalid_choice'
     assert set(probs)==set(options),'invalid_probability_options'
     assert all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in probs.values()) and abs(sum(probs.values())-1)<1e-5,'invalid_probabilities'
     assert ans['choice']==max(options,key=probs.__getitem__),'not_native_argmax'
     assert set(ans['probabilities'])==set(options) and all(type(v) in (int,float) and math.isfinite(v) for v in ans['probabilities'].values()),'invalid_rounded_probability_options'
     assert ans['probabilities']=={k:round(probs[k],4) for k in options},'rounded_probability_mismatch'
     assert type(ans['confidence']) in (int,float) and math.isfinite(ans['confidence']) and abs(ans['confidence']-probs[ans['choice']])<=0.00011,'confidence_mismatch'
     actual[f]=ans['choice'];selected[f]=probs[ans['choice']]
    assert all(type(p[k]) in (int,float) and math.isfinite(p[k]) and p[k]>=0 for k in ['inference_seconds','encode_seconds','total_seconds','latency_ms','rss_bytes']),'invalid_telemetry'
    assert abs(p['latency_ms']-p['inference_seconds']*1000)<1e-5,'latency_mismatch'
   except (AssertionError,KeyError,TypeError,ValueError) as e:issues.append(str(e));actual={f:None for f in FIELDS};selected={}
  valid=not issues;correct={f:actual[f]==g[f] for f in FIELDS};exact=all(correct.values())
  if valid:valid_native.append(p)
  for f in FIELDS:tot[f]+=correct[f];conf[f][g[f]][actual[f] or '__invalid__']+=1
  tot['exact']+=exact
  s={'id':id,'pair_id':c['pair_id'],'side':c['side'],'valid':valid,'expected':g,'predicted':actual,'field_correct':correct,'all_fields_exact':exact,'selected_probabilities':selected,'technical_issues':issues};scores.append(s)
  if not exact:errors.append({**s,**{k:c[k] for k in ['domain','family','kind','subtype','rule','message','question','rationale']},'probabilities_unrounded':p.get('probabilities_unrounded') if p else None})
 S=mapping(scores);ps=[]
 for pair in pairs:
  a,b=[S[i] for i in pair['case_ids']];valid=a['valid'] and b['valid'];both=a['all_fields_exact'] and b['all_fields_exact'];changed=valid and a['predicted']!=b['predicted'];flip=pair['kind']=='flip'
  ps.append({'id':pair['id'],'case_ids':pair['case_ids'],'domain':pair['domain'],'kind':pair['kind'],'subtype':pair['subtype'],'valid_pair':valid,'both_correct':both,'predicted_a':a['predicted'],'predicted_b':b['predicted'],'expected_a':a['expected'],'expected_b':b['expected'],'observed_change':changed,'correct_directional_change':both if flip else None,'unjustified_change':changed if not flip else None,'failed_invariance':(changed or not valid) if not flip else None,'stable':(valid and not changed) if not flip else None,'stable_but_incorrect':(valid and not changed and not both) if not flip else None})
 flips=[p for p in ps if p['kind']=='flip'];inv=[p for p in ps if p['kind']=='invariant'];valid_inv=sum(p['valid_pair'] for p in inv);N=len(C)
 pairmetrics={'both_correct':metric(sum(p['both_correct'] for p in ps),24),'correct_directional_change':metric(sum(p['correct_directional_change'] for p in flips),12),'wrong_valid_flip_transition':metric(sum(p['valid_pair'] and not p['both_correct'] for p in flips),12),'invalid_or_missing_flip_transition':metric(sum(not p['valid_pair'] for p in flips),12),'observed_change_on_flip':metric(sum(p['observed_change'] for p in flips),12),'unjustified_change':metric(sum(p['unjustified_change'] for p in inv),12),'unjustified_change_among_valid':metric(sum(p['unjustified_change'] for p in inv),valid_inv),'failed_invariance':metric(sum(p['failed_invariance'] for p in inv),12),'stable_invariant':metric(sum(p['stable'] for p in inv),12),'stable_but_incorrect':metric(sum(p['stable_but_incorrect'] for p in inv),12)}
 strata={}
 for key in ['domain','kind','subtype']:
  groups=defaultdict(list)
  for p in ps:groups[p[key]].append(p)
  strata[key]={k:{'pairs':len(v),'both_correct':metric(sum(x['both_correct'] for x in v),len(v)),'valid_pairs':sum(x['valid_pair'] for x in v),'observed_changes':sum(x['observed_change'] for x in v)} for k,v in groups.items()}
 summary={'suite_id':'minimal_pairs','case_count':48,'pair_count':24,'case_metrics':{**{f:metric(tot[f],N) for f in FIELDS},'all_fields_exact':metric(tot['exact'],N),'all_field_decisions':metric(sum(tot[f] for f in FIELDS),96)},'pair_metrics':pairmetrics,'pair_strata':strata,'case_domain_exact':{d:metric(sum(s['all_fields_exact'] for s in scores if C[s['id']]['domain']==d),16) for d in ['banking','insurance','finance']},'technical':{'recorded_predictions':len(P),'valid_cases':len(valid_native),'missing_predictions':N-len(P),'invalid_existing_predictions':N-len(valid_native)-(N-len(P)),'invalid_or_missing_case_ids':[s['id'] for s in scores if not s['valid']],'invalid_pair_ids':[p['id'] for p in ps if not p['valid_pair']],'valid_invariant_pairs':valid_inv,'input_tokens_min':min((p['input_tokens'] for p in valid_native),default=None),'input_tokens_max':max((p['input_tokens'] for p in valid_native),default=None),'forward_seconds_median':statistics.median(p['inference_seconds'] for p in valid_native) if valid_native else None,'forward_seconds_p95':percentile([p['inference_seconds'] for p in valid_native],.95),'forward_seconds_total':sum(p['inference_seconds'] for p in valid_native),'peak_observed_rss_bytes':max((p['rss_bytes'] for p in valid_native),default=None)},'error_case_ids':[s['id'] for s in scores if not s['all_fields_exact']],'error_pair_ids':[p['id'] for p in ps if not p['both_correct']],'confusion_matrices':{f:{k:dict(v) for k,v in m.items()} for f,m in conf.items()},'limitations':['AI-authored and separately AI-reviewed, not human-expert validated','Purposive dependent pairs, schema and generic rule templates reused, not a representative holdout','Bounded native output choices, not generated German answer/question quality','Marginal option scores are neither calibrated nor joint probabilities','Experimental CPU NF4, no stock-precision/GPU claim','No pooled prior-suite scores or independent-case statistical inference'],'provenance':{name+'_sha256':hashlib.sha256(path.read_bytes()).hexdigest() for name,path in [('requests',data/'requests.jsonl'),('gold',data/'gold.jsonl'),('pairs',data/'pairs.jsonl'),('predictions',output/'predictions.jsonl')]}}
 for name,rows in [('case_scores',scores),('pair_scores',ps),('errors',errors),('pair_errors',[p for p in ps if not p['both_correct']])]:
  (output/f'{name}.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
 (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data');p.add_argument('--results',type=Path,default=Path(__file__).resolve().parents[1]/'results');a=p.parse_args();s=score(a.data,a.results);print(json.dumps({k:s[k] for k in ['case_metrics','pair_metrics']},indent=2))
