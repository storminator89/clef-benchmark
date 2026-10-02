#!/usr/bin/env python3
"""Predeclared finite-set multi-document scorer; never loads a model."""
import argparse,json,math,statistics,hashlib
from pathlib import Path
from collections import Counter,defaultdict
FIELDS=('source','determination')
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def mapping(rows):
 d={r['id']:r for r in rows}
 if len(d)!=len(rows):raise ValueError('duplicate_ids')
 return d
def metric(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None}
def quantile(xs,q):
 if not xs:return None
 xs=sorted(xs);k=(len(xs)-1)*q;i=int(k);return xs[i]+(xs[min(i+1,len(xs)-1)]-xs[i])*(k-i)
def native(p,request):
 if p is None:return False,{f:None for f in FIELDS},{},['missing_prediction']
 actual={};selected={}
 try:
  assert p.get('truncated') is False and type(p['input_tokens']) is int and 0<p['input_tokens']<=2048,'invalid_tokens_or_truncation'
  assert set(p['answers'])==set(FIELDS) and set(p['probabilities_unrounded'])==set(FIELDS),'invalid_fields'
  for f in FIELDS:
   ans=p['answers'][f];probs=p['probabilities_unrounded'][f];opts=request['questions'][f]['criteria']
   assert ans['type']=='choice' and ans['choice'] in opts,'invalid_choice'
   assert set(probs)==set(opts),'invalid_probability_options'
   assert all(type(v) in (int,float) and math.isfinite(v) and 0<=v<=1 for v in probs.values()) and abs(sum(probs.values())-1)<1e-5,'invalid_probabilities'
   assert ans['choice']==max(opts,key=probs.__getitem__),'not_native_argmax'
   assert set(ans['probabilities'])==set(opts) and all(type(v) in (int,float) and math.isfinite(v) for v in ans['probabilities'].values()),'invalid_rounded_probabilities'
   assert ans['probabilities']=={k:round(probs[k],4) for k in opts},'rounded_probability_mismatch'
   assert type(ans['confidence']) in (int,float) and math.isfinite(ans['confidence']) and 0<=ans['confidence']<=1 and ans['confidence']==round(probs[ans['choice']],4),'confidence_mismatch'
   actual[f]=ans['choice'];selected[f]=probs[ans['choice']]
  assert all(type(p[k]) in (int,float) and math.isfinite(p[k]) and p[k]>=0 for k in ['inference_seconds','encode_seconds','total_seconds','latency_ms','rss_bytes']),'invalid_telemetry'
  assert abs(p['latency_ms']-p['inference_seconds']*1000)<1e-5,'latency_mismatch'
 except (AssertionError,KeyError,TypeError,ValueError,AttributeError) as e:return False,{f:None for f in FIELDS},{},[str(e) or type(e).__name__]
 return True,actual,selected,[]
def score(data,output):
 C=mapping(read(data/'cases.jsonl'));G=mapping(read(data/'gold.jsonl'));Q=mapping(read(data/'requests.jsonl'));pp=output/'predictions.jsonl';P=mapping(read(pp)) if pp.exists() else {}
 assert len(C)==48 and set(C)==set(G)==set(Q),'invalid_input_dataset'
 assert set(P)<=set(C),'unexpected_prediction_ids'
 rows=[];conf={f:defaultdict(Counter) for f in FIELDS};validrows=[]
 for id,c in C.items():
  g=G[id]['expected'];assert g==c['expected'],'gold_mismatch'
  valid,actual,selected,issues=native(P.get(id),Q[id]['request']);correct={f:actual[f]==g[f] for f in FIELDS}
  if valid:validrows.append(P[id])
  for f in FIELDS:conf[f][g[f]][actual[f] or '__invalid__']+=1
  unique=g['source']!='not_unique';answerable=g['determination']!='unresolved';present={d['id']:d for d in c['documents']}
  concrete=valid and actual['source']!='not_unique'
  # No not_unique+definite blanket inconsistency rule: nine controls permit that pair.
  inconsistent=bool(valid and ((concrete and (actual['source'] not in present or actual['determination']!=present[actual['source']]['outcome'])) or (actual['source']=='not_unique' and not unique and not answerable and actual['determination']!='unresolved')))
  rows.append({'id':id,'template_id':c['template_id'],'domain':c['domain'],'family':c['family'],'stratum':c['stratum'],'subtype':c['subtype'],'valid':valid,'expected':g,'predicted':actual,'field_correct':correct,'all_fields_exact':all(correct.values()),'selected_probabilities':selected,'technical_issues':issues,'unique_source_gold':unique,'answerable_gold':answerable,'missed_clarification':valid and not answerable and actual['determination']!='unresolved','excess_clarification':valid and answerable and actual['determination']=='unresolved','wrong_definite_answer':valid and answerable and actual['determination'] not in (g['determination'],'unresolved'),'wrong_concrete_source':valid and unique and actual['source'] not in (g['source'],'not_unique'),'unnecessary_source_uncertainty':valid and unique and actual['source']=='not_unique','invented_unique_source':valid and not unique and concrete,'source_uncertain_answer_definite':c['source_uncertain_answer_definite'],'field_pair_inconsistent_with_visible_rules':inconsistent})
 N=len(rows);unique=[r for r in rows if r['unique_source_gold']];ambig=[r for r in rows if not r['unique_source_gold']];required=[r for r in rows if not r['answerable_gold']];answerable=[r for r in rows if r['answerable_gold']];same=[r for r in rows if r['source_uncertain_answer_definite']]
 def counted(name,rr):return metric(sum(bool(r[name]) for r in rr),len(rr))
 strata={}
 for key in ['domain','stratum','family','template_id','subtype']:
  groups=defaultdict(list)
  for r in rows:groups[r[key]].append(r)
  strata[key]={k:{'count':len(rr),'all_fields_exact':counted('all_fields_exact',rr),'source_correct':metric(sum(r['field_correct']['source'] for r in rr),len(rr)),'determination_correct':metric(sum(r['field_correct']['determination'] for r in rr),len(rr)),'invalid_or_missing':sum(not r['valid'] for r in rr),'wrong_source_including_unknown':sum(r['valid'] and not r['field_correct']['source'] for r in rr)} for k,rr in groups.items()}
 summary={'suite_id':'multidocument_precedence_2026_10_02','case_count':N,'family_count':12,'paired_order_intervention':False,'case_metrics':{**{f:metric(sum(r['field_correct'][f] for r in rows),N) for f in FIELDS},'all_fields_exact':counted('all_fields_exact',rows),'all_field_decisions':metric(sum(sum(r['field_correct'].values()) for r in rows),2*N)},'source_metrics':{'unique_source_correct':metric(sum(r['field_correct']['source'] for r in unique),len(unique)),'wrong_concrete_source':counted('wrong_concrete_source',unique),'unnecessary_source_uncertainty':counted('unnecessary_source_uncertainty',unique),'ambiguous_source_correct':metric(sum(r['field_correct']['source'] for r in ambig),len(ambig)),'invented_unique_source':counted('invented_unique_source',ambig),'same_answer_ambiguous_source_exact':counted('all_fields_exact',same)},'clarification_metrics':{'missed':counted('missed_clarification',required),'excess':counted('excess_clarification',answerable),'wrong_definite_answer_on_answerable':counted('wrong_definite_answer',answerable),'invalid_on_required':metric(sum(not r['valid'] for r in required),len(required)),'invalid_on_answerable':metric(sum(not r['valid'] for r in answerable),len(answerable)),'same_answer_control_excess':counted('excess_clarification',same)},'consistency':{'field_pair_inconsistent_with_visible_rules':counted('field_pair_inconsistent_with_visible_rules',rows),'scope':'Concrete source with absent source or incompatible own complete-rule outcome; or not_unique plus definite output on a gold material-source-conflict case. not_unique plus definite answer is explicitly allowed on same-answer controls.'},'strata':strata,'technical':{'recorded_predictions':len(P),'valid_cases':len(validrows),'missing_predictions':N-len(P),'invalid_existing_predictions':len(P)-len(validrows),'invalid_or_missing_case_ids':[r['id'] for r in rows if not r['valid']],'input_tokens_min':min((p['input_tokens'] for p in validrows),default=None),'input_tokens_max':max((p['input_tokens'] for p in validrows),default=None),'forward_seconds_median':statistics.median(p['inference_seconds'] for p in validrows) if validrows else None,'forward_seconds_p95':quantile([p['inference_seconds'] for p in validrows],.95),'forward_seconds_total':sum(p['inference_seconds'] for p in validrows),'peak_observed_rss_bytes':max((p['rss_bytes'] for p in validrows),default=None)},'confusion_matrices':{f:{k:dict(v) for k,v in d.items()} for f,d in conf.items()},'error_case_ids':[r['id'] for r in rows if not r['all_fields_exact']],'limitations':['AI-authored and separately AI-reviewed, not human-expert validated','Purposive 12 related domain/stratum families with shared cross-domain templates, not representative or IID','Bounded native source/outcome choices, not generated-answer quality or multi-clause composition','No randomized matched order-swap intervention; position-balanced descriptive results are not causal order-robustness estimates','Marginal option scores are not calibrated or joint probabilities','Experimental CPU NF4; no GPU or native unquantized precision claim'],'provenance':{p.name+'_sha256':hashlib.sha256(p.read_bytes()).hexdigest() for p in [data/'requests.jsonl',data/'gold.jsonl']}}
 if pp.exists():summary['provenance']['predictions.jsonl_sha256']=hashlib.sha256(pp.read_bytes()).hexdigest()
 errors=[{**r,'case':C[r['id']],'probabilities_unrounded':P.get(r['id'],{}).get('probabilities_unrounded')} for r in rows if not r['all_fields_exact']]
 for name,rr in [('case_scores',rows),('errors',errors)]: (output/(name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
 (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data');p.add_argument('--results',type=Path,default=Path(__file__).resolve().parents[1]/'results');a=p.parse_args();s=score(a.data,a.results);print(json.dumps(s['case_metrics'],indent=2))
