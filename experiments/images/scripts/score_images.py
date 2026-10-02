"""Exact choices scored independently of inference, after the frozen run."""
from pathlib import Path
import argparse,collections,hashlib,json,math,statistics
from provenance_checks import matches
P=Path(__file__).resolve().parents[1]
def lines(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def summarize(rows):
 n=len(rows);return {'correct':sum(r['correct'] for r in rows),'total':n,'accuracy':sum(r['correct'] for r in rows)/n if n else None}
def qtiles(xs):
 xs=sorted(xs);n=len(xs)
 return {'median':statistics.median(xs),'p95_nearest_rank':xs[max(0,math.ceil(.95*n)-1)],'min':min(xs),'max':max(xs),'mean':statistics.mean(xs)} if n else None
def score(requests,gold,predictions,cases,pairs):
 req={r['id']:r for r in requests};g={r['id']:r for r in gold};pred={r['id']:r for r in predictions};cs={r['case_id']:r for r in cases}
 assert len(req)==len(requests) and len(g)==len(gold) and len(pred)==len(predictions),'Duplicate IDs'
 assert req.keys()==g.keys()==pred.keys(),'Missing/extra outputs: run is incomplete'
 fields=[];records=[];schema_invalid=[]
 for id,gr in g.items():
  pr=pred[id];expected=gr['expected'];rq=req[id]['request']['questions'];valid=set(pr.get('answers',{}))==set(expected)
  row_fields=[]
  for q,ex in expected.items():
   ans=pr.get('answers',{}).get(q,{});probs=pr.get('probabilities_unrounded',{}).get(q,{});opts=rq[q]['criteria'];choice=ans.get('choice')
   field_valid=ans.get('type')=='choice' and choice in opts and set(probs)==set(opts) and all(isinstance(v,(int,float)) and math.isfinite(v) and 0<=v<=1 for v in probs.values()) and abs(sum(probs.values())-1)<1e-5
   if field_valid:field_valid=choice==max(opts,key=probs.__getitem__)
   valid=valid and field_valid
   f={'id':id,'case_id':gr['case_id'],'kind':gr['kind'],'language':gr['language'],'condition':gr['condition'],'field':q,'expected':ex,'predicted':choice,'correct':field_valid and choice==ex,'schema_valid':field_valid,'confidence':probs.get(choice),'gold_probability':probs.get(ex),'source_id':cs[gr['case_id']]['source_id'],'strata':cs[gr['case_id']]['strata']}
   fields.append(f);row_fields.append(f)
  records.append({'id':id,'case_id':gr['case_id'],'kind':gr['kind'],'language':gr['language'],'condition':gr['condition'],'correct':all(f['correct'] for f in row_fields),'schema_valid':valid,'inference_seconds':pr['inference_seconds'],'vision_calls':len(pr['vision_forward_events']),'tokens':pr['input_tokens'],'truncated':pr['truncated']})
  if not valid:schema_invalid.append(id)
 groups={}
 for kind in ['chart','invoice']:
  for lang,cond in [('de','image'),('en','image'),('de','blank')]:
   ff=[f for f in fields if(f['kind'],f['language'],f['condition'])==(kind,lang,cond)];rr=[r for r in records if(r['kind'],r['language'],r['condition'])==(kind,lang,cond)]
   detail={q:summarize([f for f in ff if f['field']==q]) for q in sorted({f['field'] for f in ff})}
   confusions={q:dict(collections.Counter(f['expected']+' -> '+str(f['predicted']) for f in ff if f['field']==q)) for q in detail}
   macro={q:statistics.mean([statistics.mean(f['correct'] for f in ff if f['field']==q and f['expected']==ex) for ex in {f['expected'] for f in ff if f['field']==q}]) for q in detail}
   baseline={q:max(collections.Counter(f['expected'] for f in ff if f['field']==q).values())/sum(f['field']==q for f in ff) for q in detail}
   groups[kind+'_'+lang+'_'+cond]={'per_field':detail,'all_fields_per_image':summarize(rr),'field_micro':summarize(ff),'balanced_accuracy_per_field':macro,'majority_class_baseline_per_field':baseline,'confusion_counts':confusions,'latency_seconds':qtiles([r['inference_seconds'] for r in rr])}
 paired={};fm={(f['id'],f['field']):f for f in fields}
 for kind in ['chart','invoice']:
  prs=[p for p in pairs if cs[p['case_id']]['kind']==kind];rows=[]
  for p in prs:
   for q in cs[p['case_id']]['gold']:
    de=fm[p['de'],q];en=fm[p['en'],q];blank=fm[p['blank'],q]
    rows.append({'case_id':p['case_id'],'field':q,'de_correct':de['correct'],'en_correct':en['correct'],'blank_correct':blank['correct'],'de_choice':de['predicted'],'en_choice':en['predicted'],'blank_choice':blank['predicted'],'de_gold_p':de['gold_probability'],'blank_gold_p':blank['gold_probability']})
  paired[kind]={'paired_images':len(prs),'paired_fields':len(rows),'de_correct':sum(r['de_correct'] for r in rows),'en_correct':sum(r['en_correct'] for r in rows),'blank_correct':sum(r['blank_correct'] for r in rows),'de_en_same_choices':sum(r['de_choice']==r['en_choice'] for r in rows),'de_blank_changed_choices':sum(r['de_choice']!=r['blank_choice'] for r in rows),'mean_gold_probability_image_minus_blank':statistics.mean(r['de_gold_p']-r['blank_gold_p'] for r in rows),'rows':rows}
 main=[f for f in fields if f['language']=='de' and f['condition']=='image'];errors=[f for f in main if not f['correct']]
 return {'schema_valid':len(records)-len(schema_invalid),'schema_total':len(records),'schema_invalid_ids':schema_invalid,'all_expected_images_reached_vision_encoder':all(r['vision_calls']==1 for r in records),'truncated_records':sum(r['truncated'] for r in records),'groups':groups,'paired_controls':paired,'german_image_errors':errors,'german_image_errors_confidence_ge_0_9':[f for f in errors if isinstance(f['confidence'],(int,float)) and math.isfinite(f['confidence']) and f['confidence']>=.9],'records':records,'fields':fields,'interpretation_limits':['Purposive small synthetic sample, not a population estimate','Dataset synthetic English chart labels are distinct from German questions','Invoice source labels may encode synthetic generator conventions, not legal correctness','No free-form OCR, arithmetic reconstruction, advice, or production safety claim']}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--predictions',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
 if args.output.exists():raise FileExistsError(args.output)
 freeze=json.loads((P/'benchmark/freeze_manifest.json').read_text())
 for path,expected in freeze['files_sha256'].items():assert matches(P,path,expected),'Freeze mismatch: '+path
 result=score(lines(P/'benchmark/requests.jsonl'),lines(P/'benchmark/gold.jsonl'),lines(args.predictions),lines(P/'benchmark/cases.jsonl'),lines(P/'benchmark/pairs.jsonl'))
 result['provenance']={'predictions_sha256':sha(args.predictions),'freeze_manifest_sha256':sha(P/'benchmark/freeze_manifest.json'),'scorer_sha256':sha(Path(__file__))}
 args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({k:v for k,v in result.items() if k in ['schema_valid','schema_total','groups']},ensure_ascii=False,indent=2))
