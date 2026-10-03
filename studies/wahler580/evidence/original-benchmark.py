"""Standard-library-only offline scoring and explicit loopback collection."""
import argparse,base64,datetime,hashlib,http.client,ipaddress,json,math,os,pathlib,time,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parent
MODEL='Wahler-4B'
def dumps(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(dumps(x).encode()).hexdigest()
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok,reason):
 if not ok:raise ValueError(reason)
def verify():
 for f,h in json.loads((ROOT/'FREEZE.json').read_text()).items():check(sha(ROOT/f)==h,'Frozen file changed: '+f)
def append(path,value):
 with path.open('a') as f:f.write(dumps(value)+'\n');f.flush();os.fsync(f.fileno())
def write(path,value):
 temp=path.with_suffix('.tmp');temp.write_text(dumps(value)+'\n')
 with temp.open('r+') as f:f.flush();os.fsync(f.fileno())
 os.replace(temp,path)
 fd=os.open(path.parent,os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def payload(request):
 check(set(request)=={'model','state','questions'},'Unexpected source request keys')
 return {'state':request['state'],'questions':request['questions'],'reasoning':'off','abstain':False}
def validate(request,response,strict=True):
 check(isinstance(response,dict) and response.get('model')==MODEL,'Unexpected model')
 check(not response.get('error') and response.get('truncated',False) is False,'Error or truncation')
 answers=response.get('answers');check(isinstance(answers,dict) and set(answers)==set(request['questions']),'Answer field mismatch')
 for field,q in request['questions'].items():
  a=answers[field];check(isinstance(a,dict) and a.get('type')=='choice','Answer primitive mismatch');p=a.get('probabilities')
  check(isinstance(p,dict) and set(p)==set(q['criteria']),'Option mismatch')
  check(all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in p.values()),'Invalid probability')
  if strict:check(abs(math.fsum(p.values())-1)<=1e-5,'Probability sum outside local tolerance')
  check(a.get('choice') in p and p[a['choice']]==max(p.values()),'Choice not native maximum')
  c=a.get('confidence');check(type(c) in (float,int) and math.isfinite(c) and 0<=c<=1,'Invalid confidence')
 usage=response.get('usage');check(isinstance(usage,dict) and all(type(usage.get(k))==int and usage[k]>=0 for k in ['input_tokens','output_tokens']),'Invalid usage')
 return answers

def verify_readiness(ready):
 check(ready['threads']==8 and ready['ctx']==8192 and ready['context_margin_tokens']==512,'Unreviewed runtime configuration')
 check(ready['reasoning']=='off' and ready['abstain'] is False and ready['language']=='native_auto','Inference policy mismatch')
 check(ready['tokenizer_model_sha256']==ready['model_sha256'],'Tokenizer source mismatch')
 check(sha(ROOT/'preflight-580.json')==ready['preflight_sha256'],'Preflight evidence changed')
 check(sha(pathlib.Path(ready['calibration_path']))==ready['calibration_sha256'],'Calibration changed')
 check(sha(pathlib.Path(ready['launch_path']))==ready['launch_sha256'],'Runtime launcher changed')
 check(sha(pathlib.Path(ready['installed_source_manifest_path']))==ready['installed_source_manifest_sha256'],'Installed source evidence changed')
 pre=json.loads((ROOT/'preflight-580.json').read_text());planned=rows(ROOT/'planned.jsonl');check(len(pre)==len(planned)==580,'Preflight inventory')
 for pf,r in zip(pre,planned):
  check((pf['suite'],pf['id'],pf['request_sha256'])==(r['suite'],r['id'],digest(payload(r['request']))),'Preflight input mismatch')
  check(pf['fit'] is True and type(pf['tokens'])==int and 0<pf['tokens']+512<=8192,'Preflight context failure')

def live_identity(u,ready):
 conn=http.client.HTTPConnection(u.hostname,u.port,timeout=10)
 try:
  conn.request('GET','/benchmark-identity');resp=conn.getresponse();check(resp.status==200,'No live runtime identity');identity=json.loads(resp.read())
 finally:conn.close()
 return validate_identity(identity,ready)

def validate_identity(identity,ready):
 for k in ['runtime_commit','model_sha256','calibration_sha256','ctx','threads','preflight_sha256','planned_sha256','identity_token','tokenizer_source','context_margin_tokens','installed_source_manifest_sha256']:
  check(identity.get(k)==ready[k],'Live runtime identity mismatch: '+k)
 check(identity.get('status')=='loaded' and bool(identity.get('run_instance_uuid')),'Runtime not loaded')
 return identity

def collect(endpoint,out,readiness):
 verify();u=urllib.parse.urlparse(endpoint)
 check(u.scheme=='http' and u.hostname in ('127.0.0.1','::1') and u.path=='/v1/systemone' and not u.query and not u.fragment and not u.username,'Only literal loopback native endpoint allowed')
 check(sha(readiness)==sha(ROOT/'runtime-readiness.json'),'Readiness changed after review')
 ready=json.loads(readiness.read_text());check(ready.get('status')=='ready' and ready.get('planned_sha256')==sha(ROOT/'planned.jsonl') and ready.get('preflight_cases')==580 and ready.get('all_fit') is True and ready.get('smoke_passed') is True,'Runtime readiness/preflight required')
 source=json.loads((ROOT/'source_manifest.json').read_text())
 for k in ['model_sha256','runtime_commit']:check(ready.get(k)==source[k],'Runtime pin mismatch: '+k)
 verify_readiness(ready)
 identity=live_identity(u,ready)
 check(not out.exists(),'Fresh output required; no automatic resume/replay');out.mkdir(parents=True)
 write(out/'run_metadata.json',{'started':stamp(),'endpoint':endpoint,'freeze_sha256':sha(ROOT/'FREEZE.json'),'readiness':ready,'live_identity':identity,'latency':'HTTP connect/write/read wall time, not comparable to other hardware or provider timing','no_retries':True})
 for ordinal,r in enumerate(rows(ROOT/'planned.jsonl')):
  check(live_identity(u,ready)==identity,'Loaded runtime instance changed')
  body=dumps(payload(r['request'])).encode();key={'ordinal':ordinal,'suite':r['suite'],'id':r['id'],'request_sha256':hashlib.sha256(body).hexdigest()}
  append(out/'requests.jsonl',{**key,'body_utf8':body.decode()});append(out/'attempts.jsonl',{**key,'event':'started','utc':stamp()})
  conn=http.client.HTTPConnection(u.hostname,u.port,timeout=600);start=time.monotonic();raw=b'';status=None;response_logged=False
  try:
   conn.request('POST',u.path,body,{'Content-Type':'application/json'});resp=conn.getresponse();status=resp.status;raw=resp.read()
   append(out/'responses.jsonl',{**key,'http_status':status,'body_base64':base64.b64encode(raw).decode(),'body_sha256':hashlib.sha256(raw).hexdigest(),'seconds':time.monotonic()-start});response_logged=True
   check(status==200,'HTTP status '+str(status));native=json.loads(raw);answers=validate(r['request'],native,strict=False)
   result={**key,'status':'valid','native':native,'strict_probability_valid':all(abs(math.fsum(a['probabilities'].values())-1)<=1e-5 for a in answers.values())}
  except Exception as e:
   if not response_logged:
    raw=e.partial if isinstance(e,http.client.IncompleteRead) else raw
    append(out/'responses.jsonl',{**key,'http_status':status,'body_base64':base64.b64encode(raw).decode(),'body_sha256':hashlib.sha256(raw).hexdigest(),'seconds':time.monotonic()-start,'transport_error':str(e),'body_complete':False})
   result={**key,'status':'invalid','error':str(e),'http_status':status}
   # Fail closed: leave all later cases missing. No implicit retry or scope change.
  finally:conn.close()
  append(out/'predictions.jsonl',result);append(out/'attempts.jsonl',{**key,'event':'finished','status':result['status'],'utc':stamp()})
  write(out/'checkpoint.json',{'last_finished_ordinal':ordinal,'finished':ordinal+1,'planned':580,'state':'halted' if result['status']!='valid' else 'complete' if ordinal==579 else 'running'})
  if ordinal==579 or rows(ROOT/'planned.jsonl')[ordinal+1]['suite']!=r['suite'] or result['status']!='valid':
   append(out/'group_checkpoints.jsonl',{'suite':r['suite'],'last_ordinal':ordinal,'status':'complete' if result['status']=='valid' else 'halted','utc':stamp(),'feedback':'Completed groups may be scored now; unfinished groups are provisional, no partial accuracy headline.'})
  if result['status']!='valid':break

def indexed(rs,key):
 d={key(r):r for r in rs};check(len(d)==len(rs),'Duplicate identity');return d

def audit_run(run,planned):
 """Reject unlinked/rewritten observations; recognize incomplete write-ahead tails."""
 meta=json.loads((run/'run_metadata.json').read_text());check(meta['readiness']==json.loads((ROOT/'runtime-readiness.json').read_text()),'Run readiness mismatch');validate_identity(meta['live_identity'],meta['readiness']);check(meta['freeze_sha256']==sha(ROOT/'FREEZE.json'),'Run freeze differs')
 def rr(name):return rows(run/name) if (run/name).exists() else []
 requests=rr('requests.jsonl');responses=rr('responses.jsonl');attempts=rr('attempts.jsonl');predictions=rr('predictions.jsonl')
 starts=[x for x in attempts if x['event']=='started'];ends=[x for x in attempts if x['event']=='finished']
 check(len(starts)==len(requests),'Write-ahead request/start mismatch')
 check([x['ordinal'] for x in requests]==list(range(len(requests))),'Request ordinals not contiguous')
 check([x['ordinal'] for x in predictions]==list(range(len(predictions))),'Prediction ordinals not contiguous')
 check(len(predictions)<=len(requests)<=len(planned),'Observation counts exceed plan')
 for records in [requests,starts,ends,responses,predictions]:
  indexed(records,lambda x:x['ordinal'])
  for x in records:
   i=x['ordinal'];check(type(i)==int and 0<=i<len(planned),'Bad ordinal');r=planned[i]
   check((x['suite'],x['id'],x['request_sha256'])==(r['suite'],r['id'],digest(payload(r['request']))),'Evidence identity/input mismatch')
 for x in requests:check(x['body_utf8']==dumps(payload(planned[x['ordinal']]['request'])),'Exact request bytes mismatch')
 rb={x['ordinal']:x for x in responses};eb={x['ordinal']:x for x in ends}
 for i,x in rb.items():
  raw=base64.b64decode(x['body_base64'],validate=True);check(hashlib.sha256(raw).hexdigest()==x['body_sha256'],'Raw response hash mismatch')
 for x in predictions:
  i=x['ordinal']
  if x['status']=='valid':
   check(i in rb and rb[i]['http_status']==200 and rb[i].get('body_complete',True) is True and not rb[i].get('transport_error'),'Valid prediction lacks complete raw 200 response')
   native=json.loads(base64.b64decode(rb[i]['body_base64'],validate=True));check(native==x['native'],'Native prediction/raw response mismatch');validate(planned[i]['request'],native,strict=False)
  if i in eb:check(eb[i]['status']==x['status'],'Attempt final status mismatch')
 check(all(x['ordinal']<len(predictions) for x in ends),'Finished attempt without prediction')
 check(len(requests)-len(predictions)<=1,'More than one interrupted request')
 check(all(x['status']=='valid' for x in predictions[:-1]),'Collector continued after invalid result')
 cp=json.loads((run/'checkpoint.json').read_text()) if (run/'checkpoint.json').exists() else None
 complete=len(predictions)==len(planned) and all(x['status']=='valid' for x in predictions) and len(ends)==len(planned) and cp and cp.get('state')=='complete' and cp.get('finished')==len(planned)
 if cp and cp.get('state')=='complete':check(bool(complete),'False complete checkpoint')
 if cp:check(cp['finished']<=len(predictions) and cp['last_finished_ordinal']==cp['finished']-1,'Checkpoint ahead of evidence')
 return {'status':'complete' if complete else 'partial_provisional','publishable':True,'planned':len(planned),'started':len(starts),'observed':len(predictions),'finished':len(ends),'unobserved':len(planned)-len(predictions),'interrupted_tail':len(starts)>len(ends),'completed_groups':[sid for sid in dict.fromkeys(r['suite'] for r in planned) if all(any(x['suite']==r['suite'] and x['id']==r['id'] and x['ordinal'] in eb and cp and x['ordinal']<cp['finished'] for x in predictions) for r in planned if r['suite']==sid)]}

def score(run,out,synthetic_test_only=False):
 verify();planned=rows(ROOT/'planned.jsonl');audit={'status':'SYNTHETIC_TEST_ONLY','publishable':False} if synthetic_test_only else audit_run(run,planned);keys={(r['suite'],r['id']) for r in planned}
 obs=indexed(rows(run/'predictions.jsonl'),lambda r:(r['suite'],r['id']))
 check(set(obs)<=keys,'Unexpected observation');jev=indexed(rows(ROOT/'reference/predictions.jsonl'),lambda r:(r['suite'],r['id']))
 flags=indexed(rows(ROOT/'reference/flagged_native.jsonl'),lambda r:(r['suite'],r['id']))
 summary={};cases=[]
 for sid,n in json.loads((ROOT/'source_manifest.json').read_text())['groups'].items():
  gold=indexed(rows(ROOT/'frozen'/sid/'gold.jsonl'),lambda r:r['id']);clef=indexed(rows(ROOT/'frozen'/sid/'predictions.jsonl'),lambda r:r['id']);items=[]
  for r in [x for x in planned if x['suite']==sid]:
   ident=r['id'];expected=gold[ident]['expected'];models={};p=obs.get((sid,ident))
   if p and p['status']=='valid':
    check(p['request_sha256']==digest(payload(r['request'])),'Observation input mismatch');models['wahler']=validate(r['request'],p['native'],strict=False)
   cp=clef[ident]
   check(cp.get('truncated') is False and not cp.get('error'),'Invalid archived Clef')
   ca={f:{**a,'probabilities':cp['probabilities_unrounded'][f]} for f,a in cp['answers'].items()}
   # Reuse exact probability/field rules, with artificial envelope only for offline validation.
   models['clef']=validate(r['request'],{'model':MODEL,'answers':ca,'usage':{'input_tokens':0,'output_tokens':0}},strict=False)
   jp=jev[(sid,ident)]
   if jp['status']!='valid' and (sid,ident) in flags:
    jp=flags[(sid,ident)];check(jp.get('diagnostic',{}).get('sum_only_deviation') is True,'Flagged reference is not sum-only')
   if jp['status'] in ('valid','flagged_native'):
    check(jp['provider_model']=='jev-1.13.0','Jev provider mismatch')
    check(jp['source_request_sha256']==digest(r['request']),'Jev source link mismatch')
    check(jp['request_body_sha256']==digest({**r['request'],'model':'jev-1.13.0'}),'Jev body link mismatch')
    models['jev']=validate(r['request'],{'model':MODEL,'answers':jp['answers'],'usage':jp['usage']},strict=False)
   rec={'suite':sid,'id':ident,'valid':{m:m in models for m in ['wahler','clef','jev']},'exact':{},'fields':{},'strict_probability_valid':{}}
   for m,a in models.items():
    rec['strict_probability_valid'][m]=all(abs(math.fsum(q['probabilities'].values())-1)<=1e-5 for q in a.values())
    rec['exact'][m]=all(a[f]['choice']==v for f,v in expected.items());rec['fields'][m]={}
    for f,g in expected.items():
     q=a[f];ps=q['probabilities'];rec['fields'][m][f]={'correct':q['choice']==g,'choice':q['choice'],'gold':g,'p_gold':ps[g],'p_selected':ps[q['choice']],'native_confidence':q['confidence'],'brier':sum((v-int(k==g))**2 for k,v in ps.items())}
   items.append(rec);cases.append(rec)
  matched=[x for x in items if all(x['valid'].values())]
  strict_matched=[x for x in matched if all(x['strict_probability_valid'].values())]
  group={'planned':n,'three_way_matched':len(matched),'strict_three_way_matched':len(strict_matched),'models':{},'pairwise':{}}
  for m in ['wahler','clef','jev']:
   valid=[x for x in items if x['valid'][m]];correct=sum(x['exact'][m] for x in valid)
   group['models'][m]={'classifiable':len(valid),'missing_or_structurally_invalid':n-len(valid),'sum_only_diagnostics':sum(not x['strict_probability_valid'][m] for x in valid),'valid':len(valid),'coverage':len(valid)/n,'correct_observed':correct,'incorrect_observed':len(valid)-correct,'primary_exact_correct_all_planned':correct/n,'primary_numerator':correct,'primary_denominator':n,'end_to_end_success_all_planned':correct/n,'matched_correct':sum(x['exact'][m] for x in matched),'matched_accuracy':sum(x['exact'][m] for x in matched)/len(matched) if matched else None,'probabilities_by_field':{}}
   fields=list(next(r['request']['questions'] for r in planned if r['suite']==sid))
   for f in fields:
    fs=[x['fields'][m][f] for x in strict_matched];zero=sum(x['p_gold']==0 for x in fs)
    group['models'][m]['probabilities_by_field'][f]={'n':len(fs),'brier':sum(x['brier'] for x in fs)/len(fs) if fs else None,'nll':None if not fs or zero else -sum(math.log(x['p_gold']) for x in fs)/len(fs),'nll_infinite':bool(zero),'zero_gold_probability_count':zero}
  for m in ['clef','jev']:
   ms=[x for x in items if x['valid']['wahler'] and x['valid'][m]]
   group['pairwise'][m]={'matched':len(ms),'wahler_correct':sum(x['exact']['wahler'] for x in ms),'reference_correct':sum(x['exact'][m] for x in ms),'wahler_only_correct':sum(x['exact']['wahler'] and not x['exact'][m] for x in ms),'reference_only_correct':sum(not x['exact']['wahler'] and x['exact'][m] for x in ms)}
  summary[sid]=group
 check(not out.exists(),'Fresh scoring directory required');out.mkdir();write(out/'summary.json',{'run_audit':audit,'groups':summary,'pooled_model_accuracy':None,'technical_exclusions_are_not_observed_semantic_errors':True,'primary':'Native exact answers on identical planned cases; missing/structural failures counted separately; probability sum alone never excludes an answer','probability_metrics':'Secondary strict three-way intersection only; no probability repair'})
 for r in cases:append(out/'cases.jsonl',r)
if __name__=='__main__':
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True);c=s.add_parser('collect');c.add_argument('--endpoint',required=True);c.add_argument('--out',type=pathlib.Path,required=True);c.add_argument('--readiness',type=pathlib.Path,required=True);c=s.add_parser('score');c.add_argument('--run',type=pathlib.Path,required=True);c.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
 if a.command=='collect':collect(a.endpoint,a.out,a.readiness)
 else:score(a.run,a.out)
