"""Deterministic scorer; separately grades decision, supplied-clause evidence, and whole case."""
from pathlib import Path
import argparse,json,hashlib,statistics,collections,math

def score(benchmark,predictions,run_metadata=None):
 cases=benchmark['cases']; gold={c['id']:c for c in cases};byid={}
 for p in predictions:
  assert p['id'] in gold, f"Unknown id {p['id']}"
  assert p['id'] not in byid, f"Duplicate id {p['id']}"
  byid[p['id']]=p
 assert set(byid)==set(gold),'Missing predictions'
 rows=[]
 for c in cases:
  p=byid[c['id']];assert set(p['answers'])=={'decision','evidence'}
  assert set(p['probabilities_unrounded'])=={'decision','evidence'}
  for field in ('decision','evidence'):
   options=set(c[f'{field}_options']);probs=p['probabilities_unrounded'][field];ans=p['answers'][field]
   assert set(probs)==options
   assert all(math.isfinite(v) and 0<=v<=1 for v in probs.values())
   assert abs(sum(probs.values())-1)<1e-5
   assert ans['choice'] in options
   assert probs[ans['choice']]>=max(probs.values())-1e-8
  actual={k:p['answers'][k]['choice'] for k in ('decision','evidence')}
  accepted=c['expected'].get('accepted_evidence',[c['expected']['evidence']])
  correct={'decision':actual['decision']==c['expected']['decision'],'evidence':actual['evidence'] in accepted}
  correct['exact_case']=all(correct.values())
  rows.append({'id':c['id'],'document_id':c['document_id'],'area':c['area'],'tags':c.get('tags',[]),'expected':c['expected'],'actual':actual,'actual_evidence_clauses':c['evidence_options'][actual['evidence']],'correct':correct,'answers':p['answers'],'probabilities':p['probabilities_unrounded'],'input_tokens':p['input_tokens'],'truncated':p['truncated'],'inference_seconds':p['inference_seconds'],'encode_seconds':p['encode_seconds'],'rss_bytes':p.get('rss_bytes')})
 def aggregate(rs):
  n=len(rs);out={'cases':n}
  for field in ('decision','evidence','exact_case'):
   count=sum(r['correct'][field] for r in rs);out[field]={'correct':count,'total':n,'accuracy':count/n if n else None}
  out['field_accuracy']={'correct':sum(r['correct']['decision']+r['correct']['evidence'] for r in rs),'total':n*2,'accuracy':sum(r['correct']['decision']+r['correct']['evidence'] for r in rs)/(n*2) if n else None}
  return out
 summary=aggregate(rows)
 summary['decision_label_distribution']=dict(collections.Counter(c['expected']['decision'] for c in cases))
 summary['decision_majority_baseline']=max(summary['decision_label_distribution'].values())/len(cases)
 summary['evidence_uniform_random_baseline']=1/5
 summary['evidence_option_distribution']=dict(collections.Counter(c['expected']['evidence'] for c in cases))
 summary['evidence_position_majority_baseline']=max(summary['evidence_option_distribution'].values())/len(cases)
 summary['exact_case_majority_pair_baseline']=max(collections.Counter((c['expected']['decision'],c['expected']['evidence']) for c in cases).values())/len(cases)
 summary['decision_balanced_accuracy']=statistics.mean(sum(r['correct']['decision'] for r in rows if r['expected']['decision']==label)/sum(r['expected']['decision']==label for r in rows) for label in summary['decision_label_distribution'])
 summary['high_confidence_errors']={field:[{'id':r['id'],'choice':r['actual'][field],'confidence':max(r['probabilities'][field].values())} for r in rows if not r['correct'][field] and max(r['probabilities'][field].values())>=.9] for field in ('decision','evidence')}
 times=sorted(r['inference_seconds'] for r in rows)
 summary['latency_seconds']={'median':statistics.median(times),'p95_nearest_rank':times[math.ceil(len(times)*.95)-1],'min':min(times),'max':max(times),'total':sum(times)}
 summary['tokens']={'min':min(r['input_tokens'] for r in rows),'median':statistics.median(r['input_tokens'] for r in rows),'max':max(r['input_tokens'] for r in rows),'truncated_cases':sum(r['truncated'] for r in rows)}
 assert summary['tokens']['truncated_cases']==0
 return {'status':'completed','schema_version':'1.0.0','benchmark':benchmark['metadata'],'run_metadata':run_metadata or {},'summary':summary,'by_area':{area:aggregate([r for r in rows if r['area']==area]) for area in benchmark['metadata']['areas']},'by_document':{d['id']:aggregate([r for r in rows if r['document_id']==d['id']]) for d in benchmark['documents']},'by_decision_label':{label:aggregate([r for r in rows if r['expected']['decision']==label]) for label in summary['decision_label_distribution']},'date_version_subset':aggregate([r for r in rows if 'date_version_application' in r['tags']]),'without_date_version_subset':aggregate([r for r in rows if 'date_version_application' not in r['tags']]),'cases':rows}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--benchmark',type=Path,required=True);p.add_argument('--predictions',type=Path,required=True);p.add_argument('--metadata',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result=score(json.loads(a.benchmark.read_text()),[json.loads(x) for x in a.predictions.read_text().splitlines()],json.loads(a.metadata.read_text()))
 result['input_hashes']={k:hashlib.sha256(getattr(a,k).read_bytes()).hexdigest() for k in ('benchmark','predictions','metadata')}
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['summary'],ensure_ascii=False,indent=2))
