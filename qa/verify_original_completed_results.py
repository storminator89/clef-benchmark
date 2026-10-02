import json,pathlib,hashlib,collections,datetime,math,sys,statistics
import argparse
parser=argparse.ArgumentParser(description="Independently verify completed frozen image, clean-text or post-hoc ablation results. No model loading or inference.")
parser.add_argument('suite',choices=['image','clean','ablation'])
parser.add_argument('--image-root',type=pathlib.Path,required=True)
parser.add_argument('--clean-root',type=pathlib.Path,required=True)
parser.add_argument('--ablation-root',type=pathlib.Path,required=True)
parser.add_argument('--output-root',type=pathlib.Path,required=True)
args=parser.parse_args()
I=args.image_root;C=args.clean_root;A=args.ablation_root;Q=args.output_root
(Q/'public').mkdir(parents=True,exist_ok=True)
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
 out={'verification_version':'independent-offline-v1','verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**out}
 (Q/'public'/f'{name}_verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
def image():
 req=rows(I/'benchmark/requests.jsonl');g=rows(I/'benchmark/gold.jsonl');cases=rows(I/'benchmark/cases.jsonl');pairs=rows(I/'benchmark/pairs.jsonl');pred=rows(I/'results/predictions.jsonl');meta=js(I/'results/predictions.metadata.json');s=js(I/'results/scores.json')
 assert meta['status']=='completed' and meta['request_count']==90 and len(pred)==90
 assert [p['id'] for p in pred]==[r['id'] for r in req]==meta['request_order_ids']
 assert meta['requests_sha256']==sha(I/'benchmark/requests.jsonl') and meta['runner_sha256']==sha(I/'scripts/run_images.py')
 assert meta['max_pixels']==786432 and meta['min_pixels']==65536 and meta['threads']==6 and meta['batch_size']==1
 assert meta['vision_linear_quantized_count']==0 and meta['vision_parameter_dtypes']==meta['joint_head_dtypes']==['torch.bfloat16'] and meta['output_embedding_dtype']=='torch.bfloat16'
 assert meta['revision']=='17f0b0ad64efb65d273590632833508766b2aae6'
 assert meta['official_source_sha256']==sha(A.parent/'runtime/model/joint_schema_model.py')
 assert meta['started_at']>js(I/'benchmark/freeze_manifest.json')['frozen_at_utc']
 pm={p['id']:p for p in pred};rm={r['id']:r for r in req};gm={r['id']:r for r in g};fields=[];records=[]
 for p in pred:
  r=rm[p['id']];truth=gm[p['id']];assert not p['truncated'] and len(p['vision_forward_events'])==1
  assert p['image']['sha256']==r['image_sha256'] and p['image']['condition']==r['condition']
  mt=p['media_tensors'];ev=p['vision_forward_events'][0];assert set(mt)>={'pixel_values','image_grid_thw'}
  assert mt['pixel_values']['sha256'] and mt['image_grid_thw']['sha256'] and ev['pixel_values_shape']==mt['pixel_values']['shape']
  assert ev['dtype']=='torch.bfloat16' and len(p['image_grid_thw'])==1
  assert set(p['answers'])==set(truth['expected'])
  rf=[]
  for q,ex in truth['expected'].items():
   choice,conf=native_check(p,q,r['request']['questions'][q]['criteria'])
   f={'id':p['id'],'case_id':truth['case_id'],'kind':truth['kind'],'language':truth['language'],'condition':truth['condition'],'field':q,'expected':ex,'predicted':choice,'confidence':conf,'correct':choice==ex};fields.append(f);rf.append(f)
  records.append({'id':p['id'],'kind':truth['kind'],'language':truth['language'],'condition':truth['condition'],'correct':all(x['correct'] for x in rf)})
 groups={}
 for kind in ('chart','invoice'):
  for lang,cond in [('de','image'),('en','image'),('de','blank')]:
   key='_'.join([kind,lang,cond]);f=[x for x in fields if(x['kind'],x['language'],x['condition'])==(kind,lang,cond)];rr=[x for x in records if(x['kind'],x['language'],x['condition'])==(kind,lang,cond)]
   groups[key]={'field_micro':sumup(f),'all_fields_per_image':sumup(rr),'per_field':{q:sumup([x for x in f if x['field']==q]) for q in sorted({x['field'] for x in f})}}
   for k,v in groups[key].items():assert v==s['groups'][key][k],(key,k)
 fm={(f['id'],f['field']):f for f in fields};paired={};allmatched=[]
 for kind in ('chart','invoice'):
  pp=[p for p in pairs if gm[p['de']]['kind']==kind];ff=[]
  for p in pp:
   de,en,bl=[pm[p[k]] for k in ('de','en','blank')]
   assert de['image']['original_size']==en['image']['original_size']==bl['image']['original_size']
   assert de['image_grid_thw']==en['image_grid_thw']==bl['image_grid_thw']
   assert all(de['media_tensors'][k]==en['media_tensors'][k] for k in ('pixel_values','image_grid_thw'))
   assert de['media_tensors']['pixel_values']['sha256']!=bl['media_tensors']['pixel_values']['sha256']
   assert de['input_tokens']==bl['input_tokens']
   for q in gm[p['de']]['expected']:
    fs=[fm[p[k],q] for k in ('de','en','blank')];ff.append(fs)
  out={'paired_images':len(pp),'paired_fields':len(ff),'de_correct':sum(x[0]['correct'] for x in ff),'en_correct':sum(x[1]['correct'] for x in ff),'blank_correct':sum(x[2]['correct'] for x in ff),'de_en_same_choices':sum(x[0]['predicted']==x[1]['predicted'] for x in ff),'de_blank_changed_choices':sum(x[0]['predicted']!=x[2]['predicted'] for x in ff),'language_transitions':dict(collections.Counter(('correct' if x[0]['correct'] else 'wrong')+'_to_'+('correct' if x[1]['correct'] else 'wrong') for x in ff)),'image_to_blank_transitions':dict(collections.Counter(('correct' if x[0]['correct'] else 'wrong')+'_to_'+('correct' if x[2]['correct'] else 'wrong') for x in ff))}
  for k in ('paired_images','paired_fields','de_correct','en_correct','blank_correct','de_en_same_choices','de_blank_changed_choices'):assert out[k]==s['paired_controls'][kind][k]
  paired[kind]=out
 err=[f for f in fields if not f['correct']];main=[f for f in err if f['language']=='de' and f['condition']=='image'];reported={(x['id'],x['field']) for x in s['german_image_errors']};assert reported=={(x['id'],x['field']) for x in main}
 assert s['schema_valid']==s['schema_total']==90 and s['all_expected_images_reached_vision_encoder'] and s['truncated_records']==0
 real=[p['media_tensors']['pixel_values']['sha256'] for p in pred if gm[p['id']]['language']=='de' and gm[p['id']]['condition']=='image'];assert len(set(real))==50
 out={'status':'pass','complete_requests':90,'unique_source_images':50,'primary_fields':120,'all_fields_including_controls':len(fields),'frozen_integrity':freeze(I/'benchmark/freeze_manifest.json',I),'artifacts_sha256':{n:sha(I/n) for n in ['results/predictions.jsonl','results/predictions.metadata.json','results/scores.json','scripts/score_images.py']},'started_at':meta['started_at'],'completed_at':meta['completed_at'],'all_native_schema_records_valid':True,'real_image_tensor_verification':{'all90_have_exactly_one_vision_hook':True,'50_primary_pixel_tensor_hashes_unique':True,'20_language_pairs_identical_pixel_tensors':True,'20_blank_pairs_different_pixel_tensors_same_grid_and_dimensions':True,'all90_untruncated':True,'original_BF16_vision_head_embeddings':True,'inference_inputs_contain_only_task_schema_state_and_pixels':True},'groups':groups,'matched_controls':paired,'error_counts':{'primary_field_errors':len(main),'all_conditions_field_errors':len(err),'primary_errors_confidence_ge_0_9':sum(f['confidence']>=.9 for f in main)},'all_incorrect_fields':err,'license_and_provenance':{'charts':'Publisher-declared CC-BY-4.0 at pinned revision; no independent chain-of-title certification','invoices':'Belege dataset license permits local evaluation and publication of attributed results. Raw20-document subset and full source labels excluded from public export','chart_source_language':'English image labels with German/English task prompts','invoice_source_language':'German synthetic images; fabricated entities','gold':'All120 task fields independently rederived from pinned source annotations; separate pre-inference source-resolution visual audit passed'},'interpretation_limits':['Purposive synthetic sample; no population estimate or production/finance safety validation','120 fields are clustered within 50 images, not120 independent images','Language comparison is on the matched20-image subset only, with the same option IDs and English official wrapper','White-image comparisons retain prompt and image dimensions; they test this pixel intervention and do not isolate visual reasoning or a general causal effect','No free-form OCR, unconstrained advice, or contamination exclusion claim','One fixed CPU quantized configuration, not an AMD or hardware-general result']}
 out['status']='pass_with_interpretation_caveat'
 out['posthoc_annotation_findings']=[{'affected_ids':['chart-001-de-image','chart-002-de-image','chart-003-de-image','chart-003-en-image'],'finding':'Each image visibly combines vertical bars and a line on two y-axes. The frozen vbar2 description says vertical columns with two y-axes and does not exclude a line, so it overlaps the intended bar_line choice. Source-taxonomy labels and the frozen exact-match scores remain unchanged, but these mismatches cannot confidently be called visual-recognition failures.','scope':'Post-hoc option-wording review; no output-dependent relabeling or adjusted headline score.'},{'affected_ids':['invoice-006-de-image','invoice-009-de-image','invoice-016-de-image'],'finding':'Reviewer visually confirmed the printed section19 notice and both negative totals at source resolution. The frozen question explicitly gives the tax notice precedence over inconsistent line-item VAT. The two gross predictions match positive magnitude intervals rather than the printed negative interval.','scope':'Observed outputs and source-pixel verification only; processing-resolution or semantic cause is not isolated.'}]
 out['interpretation_limits'].append('All three primary chart-type mismatches involve overlapping option descriptions; exact frozen taxonomy accuracy is not a pure measure of visually unambiguous chart recognition')
 out['interpretation_limits'].append('Native confidence values are not calibrated probabilities of correctness')
 save('image',out)
def text_common(root,data):
 pred=rows(root/'predictions.jsonl');meta=js(root/'predictions.metadata.json');req=rows(data/'requests.jsonl');cases=rows(data/'cases.jsonl');cm={c['id']:c for c in cases};old=js(A.parent/'runtime/finance_predictions.metadata.json')
 pre=js(root/'preflight.json');outcome=js(root/'run_outcome.json');manifest=js(A.parent/'runtime/model_file_manifest.json')
 assert outcome['process_exit_code']==0 and outcome['main_pass_attempts']==1 and all(outcome['frozen_files_all_still_match'].values())
 assert all(outcome['outputs_sha256'][n]==sha(root/n) for n in ('predictions.jsonl','predictions.metadata.json','benchmark_run.log','resource_monitor.jsonl'))
 assert pre['model_manifest_sha256']==sha(A.parent/'runtime/model_file_manifest.json') and pre['packages']==old['packages']
 assert set(manifest)==set(pre['model_file_checks'])
 for n,m in manifest.items():
  recorded=pre['model_file_checks'][n];assert recorded['matches_original_verified_manifest'] and all(recorded[k]==m[k] for k in ('bytes','sha256'))
 assert all(pre['frozen_files_all_match'].values()) and pre['original_runner_sha256']==sha(A.parent/'runtime/run_clef.py')
 assert pre['release_evidence']['image_process_exit_code']==0 and pre['release_evidence']['ram_released'] is True
 assert datetime.datetime.fromisoformat(meta['started_at'])>datetime.datetime.fromisoformat(js(I/'results/predictions.metadata.json')['completed_at'])
 assert meta['status']=='completed' and len(pred)==meta['request_count']==len(req)==len(cases)
 assert [p['id'] for p in pred]==[r['id'] for r in req]==meta['request_order_ids']
 assert len({p['id'] for p in pred})==len(pred)
 assert meta['requests_sha256']==sha(data/'requests.jsonl') and meta['runner_sha256']==sha(A.parent/'runtime/run_clef.py')
 config=['model','revision','mode','quantization','dtype','device','threads','batch_size','max_length','source_code_sha256','runner_sha256','seed','packages','joint_head_dtypes']
 assert all(meta[k]==old[k] for k in config),[k for k in config if meta[k]!=old[k]]
 assert meta['started_at']>js(data/'freeze_manifest.json')['frozen_at_utc']
 rr=[]
 for p in pred:
  c=cm[p['id']];assert not p['truncated'];assert set(p['answers'])=={'decision'}
  choice,conf=native_check(p,'decision',c['questions']['decision']['criteria']);rr.append({'id':p['id'],'category':c['category'],'information_status':c.get('information_status'),'predicted':choice,'expected':c['expected']['decision'],'correct':choice==c['expected']['decision'],'confidence':conf})
 return pred,meta,cases,rr,{'status':'pass','complete_requests':len(pred),'frozen_integrity':freeze(data/'freeze_manifest.json'),'artifacts_sha256':{'predictions.jsonl':sha(root/'predictions.jsonl'),'predictions.metadata.json':sha(root/'predictions.metadata.json')},'started_at':meta['started_at'],'completed_at':meta['completed_at'],'same_original_text_configuration':{'checked_keys':config,'all_equal':True,'original_metadata_sha256':sha(A.parent/'runtime/finance_predictions.metadata.json'),'runner_sha256':meta['runner_sha256']},'all_native_schema_records_valid':True,'all_untruncated':True,'request_gold_isolation_verified':True,'process_exit_code':0,'scored_main_pass_attempts':1,'model_integrity_evidence':{'launch_rehashed_files':len(manifest),'all_launch_hashes_match_pinned_manifest':True,'manifest_sha256':sha(A.parent/'runtime/model_file_manifest.json'),'independent_reviewer_scope':'Independently checked recorded preflight hashes against pinned manifest and inspected hash-checking launcher; did not reread19GB weights during timed inference'},'execution_order':'Started after image completion and recorded exclusive RAM release'}
def clean():
 pred,meta,cases,rr,out=text_common(C/'runtime',C/'benchmark');s=js(C/'runtime/scores.json');overall=sumup(rr);assert overall['correct']==s['overall']['correct'] and overall['accuracy']==s['overall']['choice_accuracy_all_planned']==s['overall']['strict_accuracy_all_planned']
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
 save('clean',out)
def ablation():
 pred,meta,cases,rr,out=text_common(A/'results',A);s=js(A/'results/results.json');ps=rows(A/'pairs.jsonl');hist={p['id']:p for p in rows(A.parent/'runtime/finance_predictions.jsonl')};pm={p['id']:p for p in pred};rm={r['id']:r for r in rr};pairs=[]
 for p in ps:
  a,b=rm[p['attack_id']],rm[p['clean_id']];h=hist[p['source_id']];ap=pm[p['attack_id']]['probabilities_unrounded']['decision'];hp=h['probabilities_unrounded']['decision'];delta=max(abs(ap[k]-hp[k]) for k in ap)
  pairs.append({'source_id':p['source_id'],'gold':p['expected'],'attack_prediction':a['predicted'],'clean_prediction':b['predicted'],'attack_correct':a['correct'],'clean_correct':b['correct'],'historic_attack_prediction':h['answers']['decision']['choice'],'attack_rerun_matches_historic_choice':a['predicted']==h['answers']['decision']['choice'],'attack_rerun_max_abs_probability_delta':delta,'choice_changed':a['predicted']!=b['predicted'],'transition':('correct' if a['correct'] else 'wrong')+'_to_'+('correct' if b['correct'] else 'wrong')})
 summary={'pairs':7,'requests':14,'attack_correct':sum(p['attack_correct'] for p in pairs),'clean_correct':sum(p['clean_correct'] for p in pairs),'choices_changed':sum(p['choice_changed'] for p in pairs),'attack_reruns_matching_historic_choice':sum(p['attack_rerun_matches_historic_choice'] for p in pairs),'correctness_transitions':dict(collections.Counter(p['transition'] for p in pairs))}
 for k in ['attack_correct','clean_correct','choices_changed','attack_reruns_matching_historic_choice','correctness_transitions']:assert summary[k]==s['summary'][k]
 for p,r in zip(pairs,s['pairs']):assert p['source_id']==r['source_id'] and p['attack_rerun_max_abs_probability_delta']==r['attack_rerun_max_abs_probability_delta']
 assert s['summary']['schema_valid_requests']==14 and s['summary']['pairs_with_two_valid_choices']==7
 out.update({'summary':summary,'pairs':pairs,'all_incorrect_cases':[r for r in rr if not r['correct']],'posthoc':True,'historic_predictions_sha256':sha(A.parent/'runtime/finance_predictions.jsonl'),'interpretation_limits':['Post-hoc diagnostic designed with original results known; every seven German injection-tagged source case included','Only appended attack suffixes removed; gold, question rules, option descriptions and order unchanged','Three clean inputs remain intentionally underspecified; this is not the independently authored clean72 suite','Deletion jointly changes lexical context, quotation framing and length; no isolated semantic-attack or population causal effect','One pass in the original fixed configuration; historical agreement is repeatability evidence, not ground truth']})
 save('ablation',out)
if __name__=='__main__':{'image':image,'clean':clean,'ablation':ablation}[args.suite]()
