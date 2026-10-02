#!/usr/bin/env python3
"""Independent standard-library audit. Never imports the primary scorer or a model library.

Only --self-test creates synthetic records, always in temporary directories.
--predictions audits supplied actual records; --compare checks the primary report.
"""
import argparse,collections,copy,datetime,hashlib,json,math,re,statistics,subprocess,sys,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELDS=['source','determination']

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_rows(p):
 rows=[]
 for lineno,line in enumerate(Path(p).read_text().splitlines(),1):
  if not line.strip():continue
  try:r=json.loads(line,parse_constant=lambda x:float(x))
  except Exception as e:raise ValueError(f'invalid JSON line {lineno}') from e
  rows.append(r)
 return rows

def by_id(rows):
 result={}
 for r in rows:
  if not isinstance(r,dict) or not isinstance(r.get('id'),str):raise ValueError('row_without_string_id')
  if r['id'] in result:raise ValueError('duplicate_id')
  result[r['id']]=r
 return result

def number(x):return type(x) in (float,int) and math.isfinite(x)
def tally(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None}
def pct95(xs):
 if not xs:return None
 a=sorted(xs);i=(len(a)-1)*.95;k=math.floor(i)
 return a[k]+(a[min(k+1,len(a)-1)]-a[k])*(i-k)

def validate_record(r,request):
 if r is None:return {'valid':False,'reason':'missing','values':{f:None for f in FIELDS},'selected':{}}
 reject=lambda reason:{'valid':False,'reason':reason,'values':{f:None for f in FIELDS},'selected':{}}
 if not isinstance(r,dict):return reject('not_record')
 if r.get('truncated') is not False:return reject('truncation')
 if type(r.get('input_tokens')) is not int or not 0<r['input_tokens']<=2048:return reject('token_range')
 a=r.get('answers');u=r.get('probabilities_unrounded')
 if not isinstance(a,dict) or not isinstance(u,dict) or set(a)!=set(FIELDS) or set(u)!=set(FIELDS):return reject('fields')
 result={}; selected={}
 for f in FIELDS:
  options=list(request['questions'][f]['criteria']); ans=a[f]; probs=u[f]
  if not isinstance(ans,dict) or not isinstance(probs,dict):return reject('answer_or_probability_shape')
  if ans.get('type')!='choice' or ans.get('choice') not in options:return reject('choice')
  if set(probs)!=set(options):return reject('option_set')
  if not all(number(v) and 0<=v<=1 for v in probs.values()) or abs(sum(probs.values())-1)>=1e-5:return reject('probability_values')
  maximum=max(probs.values()); winner=next(o for o in options if probs[o]==maximum)
  if ans['choice']!=winner:return reject('argmax_or_tie_order')
  rounded=ans.get('probabilities')
  if not isinstance(rounded,dict) or set(rounded)!=set(options):return reject('rounded_options')
  if not all(number(v) for v in rounded.values()):return reject('rounded_values')
  if any(rounded[o]!=round(probs[o],4) for o in options):return reject('rounded_native_mismatch')
  confidence=ans.get('confidence')
  if not number(confidence) or not 0<=confidence<=1 or confidence!=round(probs[winner],4):return reject('confidence_native_mismatch')
  result[f]=winner;selected[f]=probs[winner]
 if not all(number(r.get(k)) and r[k]>=0 for k in ['inference_seconds','encode_seconds','total_seconds','latency_ms','rss_bytes']):return reject('telemetry')
 if abs(r['latency_ms']-1000*r['inference_seconds'])>=1e-5:return reject('latency_units')
 return {'valid':True,'reason':None,'values':result,'selected':selected}

def recompute(data,predictions):
 C=by_id(read_rows(data/'cases.jsonl'));G=by_id(read_rows(data/'gold.jsonl'));Q=by_id(read_rows(data/'requests.jsonl'));P=by_id(predictions)
 if len(C)!=48 or set(C)!=set(G) or set(C)!=set(Q):raise ValueError('dataset_ids')
 if set(P)-set(C):raise ValueError('unexpected_id')
 rr=[];conf={f:collections.defaultdict(collections.Counter) for f in FIELDS};vps=[]
 for cid,c in C.items():
  gold=G[cid]['expected']
  if gold!=c['expected']:raise ValueError('gold_disagreement')
  v=validate_record(P.get(cid),Q[cid]['request']);pred=v['values'];valid=v['valid'];unique=gold['source']!='not_unique';definite=gold['determination']!='unresolved'
  fc={f:valid and pred[f]==gold[f] for f in FIELDS}
  if valid:vps.append(P[cid])
  for f in FIELDS:conf[f][gold[f]][pred[f] if valid else '__invalid__']+=1
  # Independently parse each source's full rule rather than using authored outcome metadata.
  amount=int(re.search(r'(?:Überweisungsbetrag|Schadenbetrag|Änderungsbetrag): (\d+) EUR',c['state'])[1])
  outcomes={did:('yes' if amount<=int(threshold) else 'no') for did,threshold in re.findall(r'Dokument (D[123]) — .*?Vollständige Regel: .*?bis einschließlich (\d+) EUR',c['state'],re.S)}
  concrete=valid and pred['source'] in ['D1','D2','D3']
  inconsistent=False
  if concrete:inconsistent=pred['source'] not in outcomes or pred['determination']!=outcomes[pred['source']]
  elif valid and not unique and not definite:inconsistent=pred['determination']!='unresolved'
  row={'id':cid,'domain':c['domain'],'family':c['family'],'stratum':c['stratum'],'subtype':c['subtype'],'template_id':c['template_id'],'valid':valid,'expected':gold,'predicted':pred,'field_correct':fc,'all_fields_exact':all(fc.values()),'selected_probabilities':v['selected'],'unique_source_gold':unique,'answerable_gold':definite,'missed_clarification':valid and not definite and pred['determination'] in ['yes','no'],'excess_clarification':valid and definite and pred['determination']=='unresolved','wrong_definite_answer':valid and definite and pred['determination'] in ['yes','no'] and pred['determination']!=gold['determination'],'wrong_concrete_source':bool(concrete and unique and pred['source']!=gold['source']),'unnecessary_source_uncertainty':valid and unique and pred['source']=='not_unique','invented_unique_source':bool(concrete and not unique),'source_uncertain_answer_definite':not unique and definite,'field_pair_inconsistent_with_visible_rules':bool(inconsistent),'independent_invalid_reason':v['reason']}
  rr.append(row)
 N=len(rr);u=[r for r in rr if r['unique_source_gold']];a=[r for r in rr if not r['unique_source_gold']];req=[r for r in rr if not r['answerable_gold']];d=[r for r in rr if r['answerable_gold']];same=[r for r in rr if r['source_uncertain_answer_definite']]
 def flag(name,subset):return tally(sum(r[name] for r in subset),len(subset))
 def correct(field,subset):return tally(sum(r['field_correct'][field] for r in subset),len(subset))
 slices={}
 for axis in ['domain','stratum','family','subtype','template_id']:
  slices[axis]={}
  for label in dict.fromkeys(r[axis] for r in rr):
   subset=[r for r in rr if r[axis]==label]
   slices[axis][label]={'count':len(subset),'all_fields_exact':flag('all_fields_exact',subset),'source_correct':correct('source',subset),'determination_correct':correct('determination',subset),'invalid_or_missing':sum(not r['valid'] for r in subset),'wrong_source_including_unknown':sum(r['valid'] and not r['field_correct']['source'] for r in subset)}
 summary={'suite_id':'multidocument_precedence_2026_10_02','case_count':N,'family_count':len({r['family'] for r in rr}),'paired_order_intervention':False,'case_metrics':{**{f:correct(f,rr) for f in FIELDS},'all_fields_exact':flag('all_fields_exact',rr),'all_field_decisions':tally(sum(sum(r['field_correct'].values()) for r in rr),2*N)},'source_metrics':{'unique_source_correct':correct('source',u),'wrong_concrete_source':flag('wrong_concrete_source',u),'unnecessary_source_uncertainty':flag('unnecessary_source_uncertainty',u),'ambiguous_source_correct':correct('source',a),'invented_unique_source':flag('invented_unique_source',a),'same_answer_ambiguous_source_exact':flag('all_fields_exact',same)},'clarification_metrics':{'missed':flag('missed_clarification',req),'excess':flag('excess_clarification',d),'wrong_definite_answer_on_answerable':flag('wrong_definite_answer',d),'invalid_on_required':tally(sum(not r['valid'] for r in req),len(req)),'invalid_on_answerable':tally(sum(not r['valid'] for r in d),len(d)),'same_answer_control_excess':flag('excess_clarification',same)},'consistency':{'field_pair_inconsistent_with_visible_rules':flag('field_pair_inconsistent_with_visible_rules',rr)},'strata':slices,'technical':{'recorded_predictions':len(P),'valid_cases':len(vps),'missing_predictions':N-len(P),'invalid_existing_predictions':len(P)-len(vps),'invalid_or_missing_case_ids':[r['id'] for r in rr if not r['valid']],'input_tokens_min':min((p['input_tokens'] for p in vps),default=None),'input_tokens_max':max((p['input_tokens'] for p in vps),default=None),'forward_seconds_median':statistics.median([p['inference_seconds'] for p in vps]) if vps else None,'forward_seconds_p95':pct95([p['inference_seconds'] for p in vps]),'forward_seconds_total':sum(p['inference_seconds'] for p in vps),'peak_observed_rss_bytes':max((p['rss_bytes'] for p in vps),default=None)},'confusion_matrices':{f:{g:dict(v) for g,v in table.items()} for f,table in conf.items()},'error_case_ids':[r['id'] for r in rr if not r['all_fields_exact']]}
 return summary,rr

def compare(primary_dir,summary,rows,data=None,predictions=None):
 p=json.loads((primary_dir/'summary.json').read_text());prows=by_id(read_rows(primary_dir/'case_scores.jsonl'));perrors=by_id(read_rows(primary_dir/'errors.jsonl'));diff=[]
 for k,v in summary.items():
  if k=='consistency':
   if p[k]['field_pair_inconsistent_with_visible_rules']!=v['field_pair_inconsistent_with_visible_rules']:diff.append('summary.consistency')
  elif p.get(k)!=v:diff.append('summary.'+k)
 if set(prows)!={r['id'] for r in rows}:diff.append('case_scores.ids')
 for r in rows:
  for k,v in r.items():
   if k!='independent_invalid_reason' and prows.get(r['id'],{}).get(k)!=v:diff.append('case_scores.'+r['id']+'.'+k)
 if set(perrors)!=set(summary['error_case_ids']):diff.append('errors.ids')
 cases=by_id(read_rows(data/'cases.jsonl')) if data else {}
 native=by_id(predictions) if predictions is not None else {}
 for r in rows:
  if r['id'] not in perrors:continue
  error=perrors[r['id']]
  for key,value in r.items():
   if key!='independent_invalid_reason' and error.get(key)!=value:diff.append('errors.'+r['id']+'.'+key)
  if error.get('technical_issues')!=prows.get(r['id'],{}).get('technical_issues'):diff.append('errors.'+r['id']+'.technical_issues')
  if data and error.get('case')!=cases[r['id']]:diff.append('errors.'+r['id']+'.full_case_evidence')
  if predictions is not None and json.dumps(error.get('probabilities_unrounded'),sort_keys=True)!=json.dumps(native.get(r['id'],{}).get('probabilities_unrounded'),sort_keys=True):diff.append('errors.'+r['id']+'.raw_probabilities')
 return diff

def fake(c,q,choices=None):
 choices=choices or c['expected'];r={'id':c['id'],'input_tokens':1100,'truncated':False,'inference_seconds':1.25,'encode_seconds':.125,'total_seconds':1.375,'latency_ms':1250.,'rss_bytes':123456,'answers':{},'probabilities_unrounded':{}}
 for f in FIELDS:
  opts=q['questions'][f]['criteria'];v={o:.85 if o==choices[f] else .15/(len(opts)-1) for o in opts}
  r['probabilities_unrounded'][f]=v;r['answers'][f]={'type':'choice','choice':choices[f],'confidence':round(v[choices[f]],4),'probabilities':{o:round(v[o],4) for o in opts}}
 return r

def selftest(data,primary):
 cases=read_rows(data/'cases.jsonl');qs={r['id']:r['request'] for r in read_rows(data/'requests.jsonl')};perfect=[fake(c,qs[c['id']]) for c in cases];checks=[];disagreements=[]
 def scenario(name,rows,expect=None,fail=False):
  try:s,r=recompute(data,rows)
  except ValueError:
   if not fail:raise
   checks.append(name+':independent_rejects')
   if primary:
    with tempfile.TemporaryDirectory(prefix='multidoc_synthetic_reject_') as td:
     out=Path(td);(out/'predictions.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));p=subprocess.run([sys.executable,str(primary),'--data',str(data),'--results',str(out)],capture_output=True,text=True)
     if p.returncode==0:disagreements.append(name+':primary_accepted')
   return
  if fail:raise AssertionError(name+' not rejected')
  if expect:expect(s,r)
  if primary:
   with tempfile.TemporaryDirectory(prefix='multidoc_synthetic_') as td:
    out=Path(td);(out/'predictions.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));p=subprocess.run([sys.executable,str(primary),'--data',str(data),'--results',str(out)],capture_output=True,text=True)
    if p.returncode:disagreements.append(name+':primary_crash:'+p.stderr[-300:])
    else:disagreements.extend(name+':'+d for d in compare(out,s,r,data,rows))
  checks.append(name)
 def eq(a,b):
  if a!=b:raise AssertionError((a,b))
 scenario('perfect',perfect,lambda s,r:(eq(s['case_metrics']['all_fields_exact'],tally(48,48)),eq(s['case_metrics']['all_field_decisions'],tally(96,96)),eq(s['source_metrics']['unique_source_correct'],tally(27,27)),eq(s['source_metrics']['ambiguous_source_correct'],tally(21,21)),eq(s['source_metrics']['same_answer_ambiguous_source_exact'],tally(9,9)),eq(s['clarification_metrics']['missed'],tally(0,12)),eq(s['clarification_metrics']['excess'],tally(0,36)),eq(s['consistency']['field_pair_inconsistent_with_visible_rules'],tally(0,48))))
 scenario('all_missing',[],lambda s,r:(eq(s['case_metrics']['all_field_decisions'],tally(0,96)),eq(s['technical']['missing_predictions'],48),eq(s['clarification_metrics']['invalid_on_required'],tally(12,12)),eq(s['clarification_metrics']['invalid_on_answerable'],tally(36,36))))
 for predicate,label in [(lambda c:c['expected']['determination']=='unresolved','required'),(lambda c:c['source_uncertain_answer_definite'],'same_answer'),(lambda c:c['expected']['source']!='not_unique','unique')]:
  k=next(i for i,c in enumerate(cases) if predicate(c));scenario('one_missing_'+label,perfect[:k]+perfect[k+1:],lambda s,r:eq(s['case_metrics']['all_fields_exact'],tally(47,48)))
 mutations={
  'missing_answer_field':lambda p:p['answers'].pop('source'),
  'missing_raw_map':lambda p:p.pop('probabilities_unrounded'),
  'raw_map_list':lambda p:p.update(probabilities_unrounded=[]),
  'answer_list':lambda p:p['answers'].update(source=[]),
  'answer_null':lambda p:p['answers'].update(source=None),
  'probability_option_missing':lambda p:p['probabilities_unrounded']['source'].pop('D1'),
  'probability_extra_option':lambda p:p['probabilities_unrounded']['source'].update(BAD=0),
  'probability_nan':lambda p:p['probabilities_unrounded']['source'].update(D1=float('nan')),
  'probability_infinity':lambda p:p['probabilities_unrounded']['source'].update(D1=float('inf')),
  'probability_bool':lambda p:p['probabilities_unrounded']['source'].update(D1=True),
  'probability_negative':lambda p:p['probabilities_unrounded']['source'].update(D1=-.5),
  'probability_above_one':lambda p:p['probabilities_unrounded']['source'].update(D1=1.5),
  'probability_wrong_sum':lambda p:p['probabilities_unrounded']['source'].update(D1=.23456),
  'choice_unknown':lambda p:p['answers']['source'].update(choice='bogus'),
  'choice_nonargmax':lambda p:p['answers']['source'].update(choice='D1' if p['answers']['source']['choice']!='D1' else 'D2'),
  'rounded_missing':lambda p:p['answers']['source'].pop('probabilities'),
  'rounded_bool':lambda p:p['answers']['source']['probabilities'].update(D1=True),
  'rounded_wrong':lambda p:p['answers']['source']['probabilities'].update(D1=.2345),
  'confidence_rounding_drift':lambda p:p['answers']['source'].update(confidence=.8501),
  'confidence_bool':lambda p:p['answers']['source'].update(confidence=True),
  'confidence_nan':lambda p:p['answers']['source'].update(confidence=float('nan')),
  'input_tokens_zero':lambda p:p.update(input_tokens=0),
  'input_tokens_bool':lambda p:p.update(input_tokens=True),
  'input_tokens_over_cap':lambda p:p.update(input_tokens=2049),
  'truncated':lambda p:p.update(truncated=True),
  'truncation_flag_missing':lambda p:p.pop('truncated'),
  'telemetry_missing':lambda p:p.pop('rss_bytes'),
  'telemetry_negative':lambda p:p.update(encode_seconds=-1),
  'telemetry_bool':lambda p:p.update(rss_bytes=True),
  'telemetry_nonfinite':lambda p:p.update(inference_seconds=float('inf')),
  'latency_mismatch':lambda p:p.update(latency_ms=1251),
 }
 for label,fn in mutations.items():
  rows=copy.deepcopy(perfect);fn(rows[0]);scenario('malformed_'+label,rows,lambda s,r:(eq(s['case_metrics']['all_fields_exact'],tally(47,48)),eq(s['case_metrics']['all_field_decisions'],tally(94,96)),eq(s['technical']['invalid_existing_predictions'],1)))
 scenario('duplicate_id',perfect+[perfect[0]],fail=True);scenario('unexpected_id',perfect+[dict(perfect[0],id='NOT_IN_DATA')],fail=True)
 scenario('row_not_object',[None],fail=True);scenario('row_id_missing',[{'answers':{}}],fail=True)
 # Exhaustively exercise each allowed source×determination pair for every gold case.
 # This catches each diagnostic flag and all nine same-answer controls without importing primary code.
 for source in ['D1','D2','D3','not_unique']:
  for determination in ['yes','no','unresolved']:
   rows=[fake(c,qs[c['id']],{'source':source,'determination':determination}) for c in cases]
   scenario('constant_pair_'+source+'_'+determination,rows)
 # Tie handling is criterion insertion order, independent of raw probability-map insertion order.
 for later in [False,True]:
  rows=copy.deepcopy(perfect);r=rows[0];opts=list(qs[r['id']]['questions']['source']['criteria']);probs={o:.25 for o in reversed(opts)};r['probabilities_unrounded']['source']=probs;r['answers']['source']={'type':'choice','choice':opts[int(later)],'confidence':.25,'probabilities':probs}
  scenario('tie_'+('later_invalid' if later else 'first_valid'),rows,lambda s,rr: eq(rr[0]['valid'],not later))
 # Synthetic provenance fixtures exercise the frozen actual-run checker without model loads.
 with tempfile.TemporaryDirectory(prefix='multidoc_provenance_') as td:
  base=Path(td);dd=base/'data';dd.mkdir();(base/'results').mkdir();(base/'reference_runtime').mkdir();(base/'provenance').mkdir();(base/'audit').mkdir()
  for name in ['cases.jsonl','gold.jsonl','requests.jsonl']:shutil.copyfile(data/name,dd/name)
  for name in ['run_clef.py','joint_schema_model.py']:(base/'reference_runtime'/name).write_text('synthetic source only')
  (base/'provenance/runtime_verified_before_run.json').write_text(json.dumps({'packages':{'fixture':'1'}}))
  ep={'requests_sha256':digest(dd/'requests.jsonl'),'cases':[{'id':r['id'],'input_tokens':r['input_tokens']} for r in perfect]}
  (base/'audit/encoding_preflight.json').write_text(json.dumps(ep))
  freeze={'frozen_at_utc':'2026-01-01T00:00:00+00:00','files':{'data/requests.jsonl':digest(dd/'requests.jsonl')}}
  (base/'freeze_manifest.json').write_text(json.dumps(freeze))
  pred=base/'results/predictions.jsonl'
  pred.write_text(''.join(json.dumps(r)+'\n' for r in perfect))
  metadata={'model':'Cloudflare/clef-flash','revision':'17f0b0ad64efb65d273590632833508766b2aae6','dtype':'bfloat16','device':'cpu','threads':6,'batch_size':1,'max_length':2048,'seed':20261002,'benchmark_requests_only_no_gold':True,'request_order_ids':[r['id'] for r in perfect],'request_count':48,'requests_sha256':digest(dd/'requests.jsonl'),'runner_sha256':digest(base/'reference_runtime/run_clef.py'),'source_code_sha256':digest(base/'reference_runtime/joint_schema_model.py'),'packages':{'fixture':'1'},'quantization':{'load_in_4bit':True,'bnb_4bit_quant_type':'nf4','bnb_4bit_use_double_quant':True},'started_at':'2026-01-01T00:01:00+00:00','completed_at':'2026-01-01T00:02:00+00:00','status':'completed'}
  def provenance_scenario(name,metadata_value=None,prediction_rows=None,expect_pass=False):
   pred.with_suffix('.metadata.json').write_text(json.dumps(metadata if metadata_value is None else metadata_value))
   pred.write_text(''.join(json.dumps(r)+'\n' for r in (perfect if prediction_rows is None else prediction_rows)))
   result=verify_actual_context(dd,pred)
   eq(result['status']=='passed',expect_pass);checks.append('provenance_'+name)
  provenance_scenario('complete',expect_pass=True)
  partial=dict(metadata,status='interrupted');partial.pop('completed_at')
  provenance_scenario('transparent_partial',partial,perfect[:20],True)
  for label,change in [('request_hash',{'requests_sha256':'wrong'}),('runner_hash',{'runner_sha256':'wrong'}),('encoder_hash',{'source_code_sha256':'wrong'}),('packages',{'packages':{}}),('before_freeze',{'started_at':'2025-01-01T00:01:00+00:00'}),('completion_before_start',{'completed_at':'2025-01-01T00:02:00+00:00'}),('configuration',{'threads':7}),('request_order',{'request_order_ids':list(reversed(metadata['request_order_ids']))})]:
   provenance_scenario(label,dict(metadata,**change))
  provenance_scenario('false_completion',prediction_rows=perfect[:20])
  changed=copy.deepcopy(perfect);changed[0]['input_tokens']+=1;provenance_scenario('token_mismatch',prediction_rows=changed)
  provenance_scenario('output_order',prediction_rows=list(reversed(perfect)))
  freeze['files']['data/requests.jsonl']='wrong';(base/'freeze_manifest.json').write_text(json.dumps(freeze));provenance_scenario('frozen_byte_change')
 return {'status':'passed' if not disagreements else 'disagreements','model_loaded':False,'inference_performed':False,'synthetic_only':True,'primary_scorer_imported':False,'check_count':len(checks),'checks':checks,'primary_comparison_mismatches':disagreements,'input_sha256':{p.name:digest(p) for p in [data/'cases.jsonl',data/'gold.jsonl',data/'requests.jsonl']},'primary_scorer_sha256':digest(primary) if primary else None,'independent_checker_sha256':digest(__file__)}

def verify_actual_context(data,predictions):
 """Verify current public scientific bytes and native run chronology without runtime imports."""
 root=data.parent
 freeze=json.loads((root/'freeze_manifest.json').read_text())
 failures=[]
 for rel,expected in freeze['files'].items():
  rp=Path(rel)
  if rp.is_absolute() or '..' in rp.parts:failures.append('unsafe_manifest_key');continue
  target=root/rp
  if not target.is_file() or digest(target)!=expected:failures.append('frozen_file_changed:'+rel)
 meta=json.loads(predictions.with_suffix('.metadata.json').read_text())
 requests=read_rows(data/'requests.jsonl');outputs=read_rows(predictions)
 expected_order=[x['id'] for x in requests]
 if [x.get('id') for x in outputs]!=expected_order[:len(outputs)]:failures.append('prediction_order_not_frozen_prefix')
 if meta.get('request_order_ids')!=expected_order or meta.get('request_count')!=48:failures.append('metadata_request_order_or_count')
 if meta.get('requests_sha256')!=digest(data/'requests.jsonl'):failures.append('metadata_request_hash')
 if meta.get('runner_sha256')!=digest(root/'reference_runtime/run_clef.py'):failures.append('metadata_runner_hash')
 if meta.get('source_code_sha256')!=digest(root/'reference_runtime/joint_schema_model.py'):failures.append('metadata_encoder_hash')
 configuration={'model':'Cloudflare/clef-flash','revision':'17f0b0ad64efb65d273590632833508766b2aae6','dtype':'bfloat16','device':'cpu','threads':6,'batch_size':1,'max_length':2048,'seed':20261002,'benchmark_requests_only_no_gold':True}
 for k,v in configuration.items():
  if meta.get(k)!=v:failures.append('metadata_configuration:'+k)
 verified=json.loads((root/'provenance/runtime_verified_before_run.json').read_text())
 if meta.get('packages')!=verified['packages']:failures.append('runtime_package_mismatch')
 for key,expected in [('load_in_4bit',True),('bnb_4bit_quant_type','nf4'),('bnb_4bit_use_double_quant',True)]:
  if meta.get('quantization',{}).get(key)!=expected:failures.append('quantization:'+key)
 try:
  frozen_at=datetime.datetime.fromisoformat(freeze['frozen_at_utc']);started=datetime.datetime.fromisoformat(meta['started_at'])
  if started<frozen_at:failures.append('inference_before_freeze')
  if meta.get('completed_at') and datetime.datetime.fromisoformat(meta['completed_at'])<started:failures.append('completion_before_start')
 except (KeyError,ValueError,TypeError):failures.append('invalid_chronology')
 if meta.get('status')=='completed' and (len(outputs)!=48 or not meta.get('completed_at')):failures.append('false_completion')
 preflight=json.loads((root/'audit/encoding_preflight.json').read_text())
 tokens={x['id']:x['input_tokens'] for x in preflight['cases']}
 if preflight['requests_sha256']!=digest(data/'requests.jsonl'):failures.append('stale_preflight')
 for row in outputs:
  if row.get('input_tokens')!=tokens.get(row.get('id')):failures.append('preflight_token_mismatch:'+str(row.get('id')))
 return {'status':'passed' if not failures else 'failed','failures':failures,'frozen_files_checked':len(freeze['files']),'native_completed':meta.get('status')=='completed','recorded_predictions':len(outputs),'full_benchmark_count':48,'inference_started_after_freeze':not any('chronology' in f or f=='inference_before_freeze' for f in failures),'warmup_and_repeat_probe_excluded_from_scores':True,'completion_chronology':{k:meta.get(k) for k in ['started_at','completed_at','status']},'freeze_timestamp':freeze['frozen_at_utc']}

def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=ROOT/'data');p.add_argument('--predictions',type=Path);p.add_argument('--compare',type=Path);p.add_argument('--report',type=Path);p.add_argument('--self-test',action='store_true');p.add_argument('--primary-scorer',type=Path);p.add_argument('--verify-frozen-run',action='store_true');args=p.parse_args()
 if args.self_test:report=selftest(args.data,args.primary_scorer)
 else:
  if not args.predictions:p.error('--predictions required unless --self-test')
  summary,rows=recompute(args.data,read_rows(args.predictions));mismatches=compare(args.compare,summary,rows,args.data,read_rows(args.predictions)) if args.compare else []
  provenance=verify_actual_context(args.data,args.predictions) if args.verify_frozen_run else None
  if provenance and provenance['status']!='passed':mismatches.extend('provenance:'+f for f in provenance['failures'])
  report={'status':'passed' if not mismatches else 'mismatch','frozen_run_verification':provenance,'actual_result_recomputation':True,'primary_scorer_imported':False,'primary_comparison_mismatches':mismatches,'summary':summary,'case_rows':rows,'input_sha256':{label:digest(x) for label,x in [('data/cases.jsonl',args.data/'cases.jsonl'),('data/gold.jsonl',args.data/'gold.jsonl'),('data/requests.jsonl',args.data/'requests.jsonl'),('results/predictions.jsonl',args.predictions)]},'independent_checker_sha256':digest(__file__)}
 if args.report:args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ['summary','case_rows','checks']},indent=2))
 if report['status']!='passed':sys.exit(1)
if __name__=='__main__':main()
