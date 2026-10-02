import json,pathlib,hashlib,collections,datetime,math,sys,statistics
import argparse
parser=argparse.ArgumentParser(description="Recompute completed published clean72/ablation14 metrics independently with the Python standard library. Does not import benchmark scorers, load models, infer, or validate unavailable original launch logs.")
parser.add_argument('suite',choices=['clean','ablation'])
parser.add_argument('--project-root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1])
parser.add_argument('--output',type=pathlib.Path)
args=parser.parse_args();PROJECT=args.project_root;C=PROJECT/'experiments/clean72';A=PROJECT/'experiments/attack_ablation14' 
def js(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def freeze(p,root=None):
 m=js(p);root=root or p.parent;h=m.get('files_sha256',m.get('sha256'));assert all(sha(root/n)==v for n,v in h.items());return {'manifest_sha256':sha(p),'files_checked':len(h),'all_match':True}
def num(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def native_check(row,question,opts):
 a=row['answers'][question];p=row['probabilities_unrounded'][question];native=a['probabilities'];choice=a['choice']
 assert a['type']=='choice' and choice in opts and set(p)==set(native)==set(opts)
 assert all(num(x) and 0<=x<=1 for x in p.values()) and abs(sum(p.values())-1)<1e-5
 assert all(num(x) and 0<=x<=1 for x in native.values()) and abs(sum(native.values())-1)<=.001
 assert choice==max(opts,key=p.__getitem__)
 assert num(a['confidence']) and 0<=a['confidence']<=1 and abs(a['confidence']-native[choice])<=.001
 assert native[choice]>=max(native.values())-.00011
 return choice,p[choice]
def sumup(rs):return {'correct':sum(r['correct'] for r in rs),'total':len(rs),'accuracy':sum(r['correct'] for r in rs)/len(rs) if rs else None}
def save(name,out):
 out={'verification_version':'independent-public-metrics-v1','verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**out}
 if args.output:args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(out,ensure_ascii=False,indent=2))
def text_common(root,data):
 suite=root.parent;published=js(root/'verification.json');mapping=js(suite/'provenance/portable_export.json')
 assert published['status']=='pass', 'Published independent final audit is not pass'
 assert mapping['original_measurement_inputs_unmodified'] is True
 entries={e['published_artifact']:e for e in mapping['entries']}
 assert len(entries)==len(mapping['entries']), 'Duplicate map paths'
 for name,e in entries.items():
  rel=pathlib.PurePosixPath(name);assert not rel.is_absolute() and '..' not in rel.parts
  assert sha(suite/name)==e['published_sha256'], 'Published hash mismatch: '+name
 f=js(data/'freeze_manifest.json')
 assert mapping['original_freeze_manifest_sha256']==published['frozen_integrity']['manifest_sha256']
 assert entries['benchmark/freeze_manifest.json']['source_sha256']==mapping['original_freeze_manifest_sha256']
 for name,h in f.get('original_sha256',f['sha256']).items():
  e=entries['benchmark/'+name];assert e['source_sha256']==h and e['published_sha256']==f['sha256'][name]
 for name in ('cases.jsonl','requests.jsonl','gold.jsonl'):
  e=entries['benchmark/'+name];assert e['published_sha256']==e['source_sha256'], 'Measurement input changed'
 for name,h in published['artifacts_sha256'].items():
  e=entries['results/'+name];assert e['source_sha256']==h
 assert entries['results/predictions.jsonl']['source_sha256']==entries['results/predictions.jsonl']['published_sha256']
 pred=rows(root/'predictions.jsonl');meta=js(root/'predictions.metadata.json');req=rows(data/'requests.jsonl');cases=rows(data/'cases.jsonl');cm={c['id']:c for c in cases};old=js(PROJECT/'results/run_metadata.json')
 assert meta['status']=='completed' and len(pred)==meta['request_count']==len(req)==len(cases)==published['complete_requests']
 assert [p['id'] for p in pred]==[r['id'] for r in req]==meta['request_order_ids']
 assert len({p['id'] for p in pred})==len(pred)==len(cm)
 assert meta['requests_sha256']==sha(data/'requests.jsonl')
 config=['model','revision','mode','quantization','dtype','device','threads','batch_size','max_length','source_code_sha256','runner_sha256','seed','packages','joint_head_dtypes']
 assert all(meta[k]==old[k] for k in config),[k for k in config if meta[k]!=old[k]]
 assert published['same_original_text_configuration']['all_equal']
 assert datetime.datetime.fromisoformat(meta['started_at'])>datetime.datetime.fromisoformat(f['frozen_at_utc'])
 reqmap={r['id']:r for r in req};gold={r['id']:r for r in rows(data/'gold.jsonl')}
 assert set(cm)==set(reqmap)==set(gold)
 rr=[]
 for p in pred:
  c=cm[p['id']];r=reqmap[p['id']];assert not p['truncated'];assert set(p['answers'])=={'decision'}
  assert set(r)=={'id','request'} and set(r['request'])=={'model','state','questions'}
  assert r['request']['state']==c['input'] and r['request']['questions']==c['questions'] and c['expected']==gold[c['id']]['expected']
  choice,conf=native_check(p,'decision',c['questions']['decision']['criteria']);rr.append({'id':p['id'],'category':c['category'],'information_status':c.get('information_status'),'predicted':choice,'expected':c['expected']['decision'],'correct':choice==c['expected']['decision'],'confidence':conf})
 out={'status':'pass','verification_scope':'Independent published-file hash and numeric recomputation, with no scorer import or inference','complete_requests':len(pred),'published_final_audit_status':published['status'],'published_final_audit_sha256':sha(root/'verification.json'),'portable_map_sha256':sha(suite/'provenance/portable_export.json'),'mapped_export_files_checked':len(entries),'all_mapped_export_hashes_match':True,'source_frozen_inputs_and_predictions_byte_identical':True,'configuration_matches_original_public_metadata':True,'all_native_schema_records_valid':True,'all_untruncated':True,'unavailable_here':['Original launch logs and preflight process evidence are not in this export; their checks are recorded in the published final audit but are not rerun here','Original model weight bytes and original unsanitized metadata copies, where transformed, are not rehashed here'],'measurement_status_evidence':'Requires the source independent final audit to pass and reconciles preserved source hashes through the public export map'}
 return pred,meta,cases,rr,out
def clean():
 pred,meta,cases,rr,out=text_common(C/'results',C/'benchmark');s=js(C/'results/scores.json');overall=sumup(rr);assert overall['correct']==s['overall']['correct'] and overall['accuracy']==s['overall']['choice_accuracy_all_planned']==s['overall']['strict_accuracy_all_planned']
 cats={cat:sumup([r for r in rr if r['category']==cat]) for cat in sorted({r['category'] for r in rr})};ctx={k:sumup([r for r in rr if r['information_status']==k]) for k in ('sufficient','missing_or_unresolved')}
 for k,v in cats.items():assert v['total']==s['per_category'][k]['n_planned'] and v['accuracy']==s['per_category'][k]['choice_accuracy_all_planned']
 for k,v in ctx.items():assert v['total']==s['by_information_status'][k]['n_planned'] and v['accuracy']==s['by_information_status'][k]['choice_accuracy_all_planned']
 sc={x['id']:x for x in s['case_results']};assert len(sc)==72
 for r in rr:assert r['predicted']==sc[r['id']]['prediction'] and r['correct']==sc[r['id']]['correct'] and sc[r['id']]['schema_valid']
 labels={'anliegen_priorisierung':{'rueckfrage'},'unterlagenabgleich':{'unterlage_fehlt','version_klaeren'},'beitragsrechnung':{'daten_fehlen'},'vorgangsstand':{'unterlagen_nachfordern','zuordnung_klaeren'},'rueckfrageplanung':{'zuordnung','zeitpunkt','unterlage','umfang'},'finanzservice_routing':{'rueckfrage'}}
 tp=sum(r['information_status']=='missing_or_unresolved' and r['predicted'] in labels[r['category']] for r in rr);fp=sum(r['information_status']=='sufficient' and r['predicted'] in labels[r['category']] for r in rr);fn=22-tp
 diagnostic={'true_information_requests':tp,'unnecessary_information_requests':fp,'missed_information_requests':fn,'needed_context_denominator':22,'sufficient_context_denominator':50,'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/22,'unnecessary_rate':fp/50}
 assert diagnostic['precision']==s['information_request_diagnostic']['precision'] and diagnostic['recall']==s['information_request_diagnostic']['recall'] and diagnostic['unnecessary_rate']==s['information_request_diagnostic']['unnecessary_information_request_rate']
 macro=[];calibration={}
 pm={p['id']:p for p in pred}
 for cat in cats:
  sub=[r for r in rr if r['category']==cat];labelset=next(c for c in cases if c['category']==cat)['questions']['decision']['criteria'];f1=[]
  for label in labelset:
   tp1=sum(r['expected']==label and r['predicted']==label for r in sub);fp1=sum(r['expected']!=label and r['predicted']==label for r in sub);fn1=sum(r['expected']==label and r['predicted']!=label for r in sub)
   f1.append(2*tp1/(2*tp1+fp1+fn1) if 2*tp1+fp1+fn1 else 0)
  mf=statistics.mean(f1);assert abs(mf-s['per_category'][cat]['macro_f1'])<1e-12;macro.append(mf)
  pv=[]
  for r in sub:
   raw=pm[r['id']]['probabilities_unrounded']['decision'];v={k:x/sum(raw.values()) for k,x in raw.items()};pv.append((r,v,max(v.values())))
  brier=statistics.mean(sum((v[k]-(k==r['expected']))**2 for k in v) for r,v,c in pv);nll=statistics.mean(-math.log(max(v[r['expected']],1e-12)) for r,v,c in pv)
  ece=0
  for b in range(5):
   selected=[(r,c) for r,v,c in pv if min(4,int(c*5))==b]
   if selected:ece+=len(selected)/len(pv)*abs(statistics.mean(r['correct'] for r,c in selected)-statistics.mean(c for r,c in selected))
  calc=s['per_category'][cat]['calibration'];assert abs(brier-calc['multiclass_brier_sum'])<1e-12 and abs(nll-calc['nll_clip_1e_12'])<1e-12 and abs(ece-calc['ece_5_equal_width_bins'])<1e-12
  for t in (.6,.8,.9,.95):
   accepted=[r for r,v,c in pv if c>=t];z=s['per_category'][cat]['confidence_deferral'][str(t)]
   assert len(accepted)==z['accepted'] and len(accepted)/len(sub)==z['coverage_all_planned'] and (statistics.mean(r['correct'] for r in accepted) if accepted else None)==z['accepted_accuracy']
  calibration[cat]={'macro_f1':mf,'multiclass_brier_sum':brier,'nll_clip_1e_12':nll,'ece_5_equal_width_bins':ece}
 assert abs(statistics.mean(macro)-s['category_macro_f1'])<1e-12
 out['independent_extended_metrics']={'all_category_macro_f1_calibration_and_fixed_deferral_thresholds_match':True,'category_macro_f1':statistics.mean(macro),'by_category':calibration}
 out.update({'overall':overall,'per_category':cats,'by_information_status':ctx,'information_request_diagnostic':diagnostic,'all_incorrect_cases':[r for r in rr if not r['correct']],'decision_error_count':sum(not r['correct'] for r in rr),'schema_or_runtime_error_count':len(s['errors']),'interpretation_limits':['72 synthetic, purposively authored German office cases in six structured choice tasks; not production, real-client or unconstrained advice validation','50 sufficient-context and22 missing-or-unresolved-context cases are predeclared subgroups, not separate population samples','No clean-versus-attack causal comparison or pooling with prior suites','One pinned CPU NF4 configuration with original BF16 decision head; no AMD hardware result']})
 pub=js(C/'results/verification.json')
 assert out['overall']==pub['overall'] and out['per_category']==pub['per_category'] and out['by_information_status']==pub['by_information_status'] and out['information_request_diagnostic']==pub['information_request_diagnostic']
 assert out['all_incorrect_cases']==pub['all_incorrect_cases'] and out['independent_extended_metrics']==pub['independent_extended_metrics']
 save('clean',out)
def ablation():
 pred,meta,cases,rr,out=text_common(A/'results',A/'benchmark');s=js(A/'results/results.json');ps=rows(A/'benchmark/pairs.jsonl');hist={p['id']:p for p in rows(PROJECT/'results/finance/predictions.jsonl')};pm={p['id']:p for p in pred};rm={r['id']:r for r in rr};pairs=[]
 for p in ps:
  a,b=rm[p['attack_id']],rm[p['clean_id']];h=hist[p['source_id']];ap=pm[p['attack_id']]['probabilities_unrounded']['decision'];hp=h['probabilities_unrounded']['decision'];delta=max(abs(ap[k]-hp[k]) for k in ap)
  pairs.append({'source_id':p['source_id'],'gold':p['expected'],'attack_prediction':a['predicted'],'clean_prediction':b['predicted'],'attack_correct':a['correct'],'clean_correct':b['correct'],'historic_attack_prediction':h['answers']['decision']['choice'],'attack_rerun_matches_historic_choice':a['predicted']==h['answers']['decision']['choice'],'attack_rerun_max_abs_probability_delta':delta,'choice_changed':a['predicted']!=b['predicted'],'transition':('correct' if a['correct'] else 'wrong')+'_to_'+('correct' if b['correct'] else 'wrong')})
 summary={'pairs':7,'requests':14,'attack_correct':sum(p['attack_correct'] for p in pairs),'clean_correct':sum(p['clean_correct'] for p in pairs),'choices_changed':sum(p['choice_changed'] for p in pairs),'attack_reruns_matching_historic_choice':sum(p['attack_rerun_matches_historic_choice'] for p in pairs),'correctness_transitions':dict(collections.Counter(p['transition'] for p in pairs))}
 for k in ['attack_correct','clean_correct','choices_changed','attack_reruns_matching_historic_choice','correctness_transitions']:assert summary[k]==s['summary'][k]
 for p,r in zip(pairs,s['pairs']):assert p['source_id']==r['source_id'] and p['attack_rerun_max_abs_probability_delta']==r['attack_rerun_max_abs_probability_delta']
 assert s['summary']['schema_valid_requests']==14 and s['summary']['pairs_with_two_valid_choices']==7
 out.update({'summary':summary,'pairs':pairs,'all_incorrect_cases':[r for r in rr if not r['correct']],'posthoc':True,'historic_predictions_sha256':sha(PROJECT/'results/finance/predictions.jsonl'),'interpretation_limits':['Post-hoc diagnostic designed with original results known; every seven German injection-tagged source case included','Only appended attack suffixes removed; gold, question rules, option descriptions and order unchanged','Three clean inputs remain intentionally underspecified; this is not the independently authored clean72 suite','Deletion jointly changes lexical context, quotation framing and length; no isolated semantic-attack or population causal effect','One pass in the original fixed configuration; historical agreement is repeatability evidence, not ground truth']})
 pub=js(A/'results/verification.json')
 assert out['summary']==pub['summary'] and out['pairs']==pub['pairs'] and out['all_incorrect_cases']==pub['all_incorrect_cases']
 assert out['historic_predictions_sha256']==pub['historic_predictions_sha256']
 save('ablation',out)
if __name__=='__main__':{'clean':clean,'ablation':ablation}[args.suite]()
