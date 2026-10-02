#!/usr/bin/env python3
"""Independent standard-library audit, implemented without reading/importing score.py.
Reads native evidence only; never changes predictions. Duplicate/unexpected IDs or
malformed rows stop scoring. Every comparison and source line is retained.
"""
from __future__ import annotations
import argparse, collections, datetime, hashlib, json, math, random, statistics, struct, subprocess, sys
from pathlib import Path
FIELDS=('action','determination')
OPTIONS={'action':['answer','ask_fact','ask_target','resolve_conflict'],'determination':['yes','no','unresolved']}
REV='17f0b0ad64efb65d273590632833508766b2aae6'
RUNNER='d06f85b922e1e4d0e905a1ddc8846aedcafa93c29f502f48b1529a36a9eb5906'
MISSING={'__missing__':True}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def numeric(v): return type(v) in (int,float) and math.isfinite(v)
def safe(v):
    if isinstance(v,float) and not math.isfinite(v): return {'__nonfinite_float__':repr(v)}
    if isinstance(v,dict): return {str(k):safe(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [safe(x) for x in v]
    return v
def dump(p,v): Path(p).write_text(json.dumps(safe(v),ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def dump_rows(p,vs): Path(p).write_text(''.join(json.dumps(safe(v),ensure_ascii=False,allow_nan=False)+'\n' for v in vs))
def strict_object(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError('Duplicate JSON member: '+k)
        d[k]=v
    return d
def read_json(p): return json.loads(Path(p).read_text(),object_pairs_hook=strict_object)
def read_rows(p):
    evidence=[]; rows=[]; errors=[]
    if not Path(p).exists(): return [],[],[{'code':'missing_file','path':str(p)}]
    for lineno,line in enumerate(Path(p).read_text().splitlines(),1):
        try:
            row=json.loads(line,object_pairs_hook=strict_object)
            if not isinstance(row,dict): raise ValueError('JSONL row is not an object')
            rows.append(row); evidence.append({'line':lineno,'raw_line':line,'parsed':row})
        except Exception as e:
            errors.append({'code':'malformed_jsonl_line','line':lineno,'error':str(e)})
            evidence.append({'line':lineno,'raw_line':line,'parse_error':str(e)})
    return rows,evidence,errors
def equal(a,b):
    if isinstance(a,dict) and isinstance(b,dict): return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    if type(a) is bool or type(b) is bool: return type(a) is type(b) and a==b
    return a==b
class Ledger:
    def __init__(self): self.rows=[]
    def check(self,path,observed,expected,*,ok=None,note=None):
        if ok is None: ok=equal(observed,expected)
        r={'path':path,'passed':bool(ok),'observed':observed,'expected':expected}
        if note:r['note']=note
        self.rows.append(r); return bool(ok)
    @property
    def failures(self):return [r for r in self.rows if not r['passed']]
def validate_native(row,expected_tokens=None,fields=FIELDS,options=OPTIONS):
    L=Ledger(); predicted={f:None for f in fields}
    if row is None:
        L.check('prediction_present',False,True)
        return {'valid':False,'prediction':predicted,'checks':L.rows,'issues':['missing_prediction']}
    answers=row.get('answers'); probs=row.get('probabilities_unrounded')
    L.check('answers.fields',list(answers) if isinstance(answers,dict) else answers,list(fields))
    L.check('probabilities_unrounded.fields',list(probs) if isinstance(probs,dict) else probs,list(fields))
    for f in fields:
        ans=answers.get(f) if isinstance(answers,dict) else None
        pr=probs.get(f) if isinstance(probs,dict) else None
        if not isinstance(ans,dict): L.check(f+'.native_object',ans,{},ok=False); ans={}
        choice=ans.get('choice'); predicted[f]=choice
        L.check(f+'.type',ans.get('type'),'choice')
        L.check(f+'.native_fields',sorted(ans),['choice','confidence','probabilities','type'])
        L.check(f+'.choice',choice,options[f],ok=choice in options[f])
        good=isinstance(pr,dict) and set(pr)==set(options[f])
        L.check(f+'.option_set',sorted(pr) if isinstance(pr,dict) else pr,sorted(options[f]),note='Full native maps follow encoder ordering; criterion ordering is used separately for argmax tie-breaking')
        rounded=ans.get('probabilities')
        L.check(f+'.rounded_option_order',list(rounded) if isinstance(rounded,dict) else rounded,options[f])
        if isinstance(pr,dict):
            for opt,value in pr.items(): L.check(f+'.probability.'+opt,value,'finite real in [0,1]',ok=numeric(value) and 0<=value<=1)
            if good and all(numeric(v) and 0<=v<=1 for v in pr.values()):
                L.check(f+'.probability_sum',sum(pr.values()),1.0,ok=abs(sum(pr.values())-1)<=1e-5)
                L.check(f+'.native_argmax',choice,max(options[f],key=lambda k:pr[k]))
                conf=ans.get('confidence')
                in_pr=isinstance(choice,str) and choice in pr
                L.check(f+'.confidence_matches_selected',conf,pr.get(choice) if in_pr else None,ok=numeric(conf) and 0<=conf<=1 and in_pr and abs(conf-pr[choice])<=.00011)
                if isinstance(rounded,dict):
                    for opt in options[f]:
                        v=rounded.get(opt); target=round(pr[opt],4)
                        L.check(f+'.native_rounded.'+opt,v,target,ok=numeric(v) and v==target)
    tokens=row.get('input_tokens')
    L.check('input_tokens.range',tokens,'integer 1..2048',ok=type(tokens) is int and 1<=tokens<=2048)
    if expected_tokens is not None: L.check('input_tokens.preflight',tokens,expected_tokens,ok=type(tokens) is int and tokens==expected_tokens)
    L.check('truncated',row.get('truncated'),False,ok=row.get('truncated') is False)
    for key in ('encode_seconds','inference_seconds','latency_ms','total_seconds'):
        v=row.get(key); L.check(key,v,'finite nonnegative real',ok=numeric(v) and v>=0)
    inf=row.get('inference_seconds'); lat=row.get('latency_ms'); enc=row.get('encode_seconds'); total=row.get('total_seconds')
    if numeric(inf) and numeric(lat):L.check('latency_conversion',lat,inf*1000,ok=abs(lat-inf*1000)<=1e-6)
    if all(numeric(v) for v in (enc,inf,total)):L.check('total_covers_encode_plus_forward',total,enc+inf,ok=total+1e-9>=enc+inf)
    rss=row.get('rss_bytes'); L.check('rss_bytes',rss,'positive integer',ok=type(rss) is int and rss>0)
    return {'valid':not L.failures,'prediction':predicted,'checks':L.rows,'issues':[x['path'] for x in L.failures]}
def ratio(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None}
def percentile(values,q):
    s=sorted(values); k=(len(s)-1)*q; lo=math.floor(k)
    return s[lo]+(s[min(lo+1,len(s)-1)]-s[lo])*(k-lo)
def describe(v):
    if not v:return {'count':0,'sum':0,'mean':None,'median':None,'min':None,'max':None,'p95_nearest_rank':None,'p95_linear':None}
    return {'count':len(v),'sum':sum(v),'mean':statistics.mean(v),'median':statistics.median(v),'min':min(v),'max':max(v),'p95_nearest_rank':sorted(v)[math.ceil(.95*len(v))-1],'p95_linear':percentile(v,.95)}
def compute(cases,pairs,gold,requests,preflight,predictions,parse_errors=(),check_token_match=True):
    ids=[c['id'] for c in cases]; idset=set(ids); predids=[p.get('id') for p in predictions]
    counts=collections.Counter(x for x in predids if isinstance(x,str)); fatal=list(parse_errors)
    for ident,n in counts.items():
        if n>1:fatal.append({'code':'duplicate_prediction_id','id':ident,'count':n})
        if ident not in idset:fatal.append({'code':'unexpected_prediction_id','id':ident})
    for i,ident in enumerate(predids):
        if not isinstance(ident,str):fatal.append({'code':'invalid_prediction_id','index':i,'id':ident})
    if fatal:return {'scoring_stopped':True,'fatal_errors':fatal,'case_results':[],'pair_results':[],'summary':None}
    indexed={p['id']:p for p in predictions}; tokens={x['id']:x['input_tokens'] for x in preflight['cases']}; cr=[]
    for c in cases:
        ident=c['id']; raw=indexed.get(ident); v=validate_native(raw,tokens.get(ident) if check_token_match else None); g=gold[ident]['expected']
        fc={f:bool(v['valid'] and v['prediction'][f]==g[f]) for f in FIELDS}
        cr.append({'id':ident,'pair_id':c['pair_id'],'side':c['side'],'domain':c['domain'],'kind':c['kind'],'subtype':c['subtype'],'valid':v['valid'],'missing':raw is None,'prediction':v['prediction'],'gold':g,'field_correct':fc,'exact':all(fc.values()),'invalid_reasons':v['issues'],'native_checks':v['checks'],'native':raw,'case':c,'request':requests[ident]})
    byid={c['id']:c for c in cr}; pr=[]
    for p in pairs:
        a,b=(byid[x] for x in p['case_ids']); valid=a['valid'] and b['valid']; both=a['exact'] and b['exact']; flip=p['kind']=='flip'
        changed=bool(valid and a['prediction']!=b['prediction']); stable=bool(valid and a['prediction']==b['prediction'])
        pr.append({'id':p['id'],'domain':p['domain'],'kind':p['kind'],'subtype':p['subtype'],'case_ids':p['case_ids'],'gold_a':a['gold'],'gold_b':b['gold'],'prediction_a':a['prediction'],'prediction_b':b['prediction'],'a_valid':a['valid'],'b_valid':b['valid'],'valid':valid,'a_exact':a['exact'],'b_exact':b['exact'],'both_correct':both,'changed':changed,'stable':stable,'correct_directional_change':bool(flip and both),'wrong_valid_flip_transition':bool(flip and valid and not both),'invalid_flip_transition':bool(flip and not valid),'unjustified_change':bool(not flip and changed),'invalid_invariant':bool(not flip and not valid),'failed_invariance':bool(not flip and (changed or not valid)),'stable_wrong':bool(not flip and stable and not both),'pair':p})
    flips=[p for p in pr if p['kind']=='flip']; inv=[p for p in pr if p['kind']=='invariant']
    s={'case_exact':ratio(sum(c['exact'] for c in cr),48),'field_accuracy':{f:ratio(sum(c['field_correct'][f] for c in cr),48) for f in FIELDS},'all_field_decisions':ratio(sum(sum(c['field_correct'].values()) for c in cr),96),'pair_both_correct':ratio(sum(p['both_correct'] for p in pr),24),
       'flip_correct_directional_change':ratio(sum(p['correct_directional_change'] for p in flips),12),'flip_observed_change':ratio(sum(p['changed'] for p in flips),12),'flip_wrong_valid_transition':ratio(sum(p['wrong_valid_flip_transition'] for p in flips),12),'flip_invalid_transition':ratio(sum(p['invalid_flip_transition'] for p in flips),12),'flip_not_correct_transition':ratio(sum(not p['both_correct'] for p in flips),12),
       'invariant_unjustified_change':ratio(sum(p['unjustified_change'] for p in inv),12),'invariant_unjustified_change_valid_conditional':ratio(sum(p['unjustified_change'] for p in inv),sum(p['valid'] for p in inv)),'invariant_invalid':ratio(sum(p['invalid_invariant'] for p in inv),12),'invariant_failed':ratio(sum(p['failed_invariance'] for p in inv),12),'invariant_stable':ratio(sum(p['stable'] for p in inv),12),'invariant_stable_wrong':ratio(sum(p['stable_wrong'] for p in inv),12),'invariant_both_correct':ratio(sum(p['both_correct'] for p in inv),12),
       'missing_ids':[c['id'] for c in cr if c['missing']],'invalid_ids':[c['id'] for c in cr if not c['valid']],'error_case_ids':[c['id'] for c in cr if not c['exact']],'error_pair_ids':[p['id'] for p in pr if not p['both_correct']],'case_strata':{},'pair_strata':{},'confusion':{},'timing':{}}
    for key in ('domain','kind','subtype'):
        s['case_strata'][key]={}; s['pair_strata'][key]={}
        for value in sorted({c[key] for c in cr}):
            g=[c for c in cr if c[key]==value];s['case_strata'][key][value]={'case_exact':ratio(sum(c['exact'] for c in g),len(g)),'field_accuracy':{f:ratio(sum(c['field_correct'][f] for c in g),len(g)) for f in FIELDS}}
        for value in sorted({p[key] for p in pr}):
            g=[p for p in pr if p[key]==value];s['pair_strata'][key][value]={'both_correct':ratio(sum(p['both_correct'] for p in g),len(g)),'valid':sum(p['valid'] for p in g),'changed':sum(p['changed'] for p in g),'stable':sum(p['stable'] for p in g)}
    s['pair_strata']['domain_subtype']={}
    for domain,subtype in sorted({(p['domain'],p['subtype']) for p in pr}):
        g=[p for p in pr if (p['domain'],p['subtype'])==(domain,subtype)];s['pair_strata']['domain_subtype'][domain+'|'+subtype]={'both_correct':ratio(sum(p['both_correct'] for p in g),len(g)),'valid':sum(p['valid'] for p in g),'changed':sum(p['changed'] for p in g),'stable':sum(p['stable'] for p in g)}
    for f in FIELDS:
        cm={g:{p:0 for p in OPTIONS[f]+['INVALID']} for g in OPTIONS[f]}
        for c in cr:cm[c['gold'][f]][c['prediction'][f] if c['valid'] else 'INVALID']+=1
        s['confusion'][f]=cm
    valid=[c['native'] for c in cr if c['valid']]
    for k in ('encode_seconds','inference_seconds','latency_ms','total_seconds','input_tokens','rss_bytes'):s['timing'][k]=describe([p[k] for p in valid])
    return {'scoring_stopped':False,'fatal_errors':[],'case_results':cr,'pair_results':pr,'summary':s}
def dataset_checks(root,D,L):
    cases,pairs=D['cases'],D['pairs']; ids=[c['id'] for c in cases]
    L.check('dataset.case_count',len(cases),48);L.check('dataset.pair_count',len(pairs),24)
    L.check('dataset.unique_cases',len(set(ids)),48);L.check('dataset.unique_pairs',len({p['id'] for p in pairs}),24)
    for name in ('gold','metadata','requests'):L.check('dataset.order.'+name,[x['id'] for x in D[name]],ids)
    C={c['id']:c for c in cases}; G={c['id']:c for c in D['gold']};Q={c['id']:c for c in D['requests']};M={c['id']:c for c in D['metadata']}
    policy=D['policy'];L.check('dataset.field_order',list(policy),list(FIELDS))
    for f in FIELDS:L.check('dataset.options.'+f,list(policy[f]['criteria']),OPTIONS[f])
    unshuffled=[cid for p in pairs for cid in p['case_ids']];shuffled=unshuffled.copy();random.Random(2026100248).shuffle(shuffled)
    L.check('dataset.seeded_request_order',ids,shuffled); L.check('dataset.one_pair_per_case',sorted(unshuffled),sorted(ids))
    for p in pairs:
        for side,ident in zip(('a','b'),p['case_ids']):
            c=C[ident];prefix='dataset.'+ident+'.'
            L.check(prefix+'pair_id',c['pair_id'],p['id']);L.check(prefix+'side',c['side'],side)
            for field in ('rule','question','domain','family','kind','subtype'):L.check(prefix+field,c[field],p[field])
            L.check(prefix+'message',c['message'],p['unchanged_prefix']+p['span_'+side]+p['unchanged_suffix'])
            L.check(prefix+'span_offsets',p['changed_character_offsets_'+side],[len(p['unchanged_prefix']),len(p['unchanged_prefix'])+len(p['span_'+side])])
            L.check(prefix+'gold',c['expected'],G[ident]['expected']);L.check(prefix+'pair_gold',p['expected_'+side],G[ident]['expected'])
            for f in FIELDS:L.check(prefix+'allowable_gold.'+f,c['expected'].get(f),OPTIONS[f],ok=c['expected'].get(f) in OPTIONS[f])
            L.check(prefix+'metadata',M[ident],{k:c[k] for k in ('id','pair_id','side','domain','family','kind','subtype','rationale','authorship')})
            expected_state='Fiktive Testregel:\n'+c['rule']+'\n\nSynthetische Anfrage und Unterlagen:\n'+c['message']+'\n\nZu beurteilende Eigenschaft:\n'+c['question']
            L.check(prefix+'request',Q[ident],{'id':ident,'request':{'model':'clef-flash','state':expected_state,'questions':policy}})
        L.check('dataset.'+p['id']+'.different_spans',p['span_a']!=p['span_b'],True)
        L.check('dataset.'+p['id']+'.gold_relation',p['expected_a']!=p['expected_b'],p['kind']=='flip')
        for component in ('prefix','suffix'):
            L.check('dataset.'+p['id']+'.'+component+'_sha256',p['unchanged_'+component+'_sha256'],hashlib.sha256(p['unchanged_'+component].encode()).hexdigest())
    design=D['design_summary']
    for name,key,expected in [('pair_domain_counts','domain',{'banking':8,'insurance':8,'finance':8}),('pair_kind_counts','kind',{'flip':12,'invariant':12}),('pair_subtype_counts','subtype',{'yes_to_no':3,'no_to_yes':3,'clarify_to_answer':3,'answer_to_clarify':3,'irrelevant_text':6,'within_region_fact':3,'short_circuit_control':3})]:
        count=dict(collections.Counter(p[key] for p in pairs)); L.check('dataset.'+name,count,expected);L.check('design_summary.'+name,design[name],count)
    for f in FIELDS:L.check('design_summary.gold_'+f,design['gold_'+f+'_counts'],dict(collections.Counter(c['expected'][f] for c in cases)))
    pre=D['preflight'];L.check('preflight.count',pre['count'],48);L.check('preflight.order',[x['id'] for x in pre['cases']],ids)
    L.check('preflight.requests_sha256',pre['requests_sha256'],sha(root/'data/requests.jsonl'))
    tokens=[]
    for e in pre['cases']:
        r=Q[e['id']]['request'];tokens.append(e['input_tokens'])
        L.check('preflight.'+e['id']+'.truncated',e['truncated'],False)
        L.check('preflight.'+e['id']+'.tokens',e['input_tokens'],'integer 1..2048',ok=type(e['input_tokens']) is int and 1<=e['input_tokens']<=2048)
        L.check('preflight.'+e['id']+'.state_characters',e['state_characters'],len(r['state']))
        L.check('preflight.'+e['id']+'.request_bytes',e['request_bytes'],len(json.dumps(r,ensure_ascii=False).encode()))
    L.check('preflight.min_tokens',pre['min_tokens'],min(tokens));L.check('preflight.max_tokens',pre['max_tokens'],max(tokens))
    for k in ('state_characters','request_bytes'):L.check('preflight.max_'+k,pre['max_'+k],max(x[k] for x in pre['cases']))

def timestamp(value):
    t=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None:raise ValueError('Timestamp lacks timezone')
    return t

def integrity_checks(root,results,D,raw,L):
    freeze=read_json(root/'freeze_manifest.json'); approval=read_json(root/'audit/freeze_approval.json'); runtime=read_json(root/'provenance/runtime_verified_before_run.json')
    meta=read_json(results/'predictions.metadata.json');order=[x['id'] for x in D['requests']]
    for label,obj in [('freeze',freeze),('approval',approval)]:
        for rel,h in obj['files'].items():
            p=root/rel;L.check(label+'.sha256.'+rel,sha(p) if p.exists() else None,h)
    for key,v in {'case_count':48,'pair_count':24,'fields':list(FIELDS),'revision':REV,'model_inference_before_freeze':False}.items():L.check('freeze.'+key,freeze.get(key),v)
    required=['PROTOCOL.md','data/requests.jsonl','data/cases.jsonl','data/pairs.jsonl','data/gold.jsonl','data/policy.json','data/metadata.jsonl','scripts/score.py','reference_runtime/run_clef.py','reference_runtime/joint_schema_model.py','audit/freeze_approval.json','audit/encoding_preflight.json','audit/scorer_self_tests.json','provenance/runtime_verified_before_run.json']
    for rel in required:L.check('freeze.includes.'+rel,rel in freeze['files'],True)
    for key,v in {'approved_for_freeze':True,'all_cases_reviewed':48,'all_pairs_reviewed':24,'semantic_pass_count':24,'mechanical_checks_passed':True,'protocol_and_scorer_review_passed':True,'no_model_loaded_by_reviewer':True,'no_benchmark_predictions_observed':True,'prediction_files_absent_at_approval':True}.items():L.check('approval.'+key,approval.get(key),v)
    review,_,errs=read_rows(root/'audit/pre_inference_review.jsonl');L.check('review.parse_errors',errs,[])
    L.check('review.pair_ids',[r['pair_id'] for r in review],[p['id'] for p in D['pairs']])
    gold={g['id']:g['expected'] for g in D['gold']}
    for r in review:
        L.check('review.'+r['pair_id']+'.passed',r.get('pass'),True)
        L.check('review.'+r['pair_id']+'.pre_inference',r.get('pre_inference'),True)
        L.check('review.'+r['pair_id']+'.gold',r['independently_derived_gold'],{cid:gold[cid] for cid in r['case_ids']})
        for rel,h in r['dataset_file_sha256'].items():L.check('review.'+r['pair_id']+'.sha256.'+rel,sha(root/rel),h)
    corrections=read_json(root/'audit/correction_history.json')
    L.check('corrections.before_inference',corrections.get('before_inference'),True);L.check('corrections.model_outputs_seen',corrections.get('model_outputs_seen'),False)
    L.check('corrections.round1_snapshot',sha(root/'audit/round1_review_snapshot.json'),corrections.get('round1_snapshot_sha256'))
    for k,v in {'status':'passed','revision':REV,'runner_sha256':RUNNER,'model_not_loaded':True}.items():L.check('runtime_verification.'+k,runtime.get(k),v)
    expected_meta={'model':'Cloudflare/clef-flash','revision':REV,'mode':'CPU NF4 backbone, original BF16 joint head and BF16 output embeddings','dtype':'bfloat16','device':'cpu','threads':6,'batch_size':1,'max_length':2048,'requests_sha256':sha(root/'data/requests.jsonl'),'source_code_sha256':sha(root/'reference_runtime/joint_schema_model.py'),'runner_sha256':RUNNER,'seed':20261002,'packages':runtime['packages'],'request_count':48,'request_order_ids':order,'benchmark_requests_only_no_gold':True,'status':'completed','joint_head_dtypes':['torch.bfloat16']}
    for k,v in expected_meta.items():L.check('runtime_metadata.'+k,meta.get(k),v)
    for k,v in {'torch':'2.11.0+cpu','transformers':'5.10.2','bitsandbytes':'0.50.2'}.items():L.check('pinned_package.'+k,runtime['packages'].get(k),v)
    manifest=read_json(root/'reference_runtime/model_file_manifest.json');L.check('runtime.model_file_manifest',runtime['model_files'],{name:{'bytes':v['bytes'],'sha256':v['sha256']} for name,v in manifest.items()})
    for name,v in manifest.items():L.check('runtime.hf_revision.'+name,v.get('hf_commit'),REV)
    L.check('runtime.source_hash',runtime['model_files']['joint_schema_model.py']['sha256'],sha(root/'reference_runtime/joint_schema_model.py'))
    L.check('runtime.original_runner_hash',sha(root/'reference_runtime/run_clef.py'),RUNNER)
    quant=meta.get('quantization',{})
    for k,v in {'bnb_4bit_quant_type':'nf4','bnb_4bit_compute_dtype':'bfloat16','bnb_4bit_use_double_quant':True,'llm_int8_skip_modules':['lm_head']}.items():L.check('runtime.quantization.'+k,quant.get(k),v)
    L.check('runtime.quantization.load_in_4bit',quant.get('load_in_4bit',quant.get('_load_in_4bit')),True)
    for k in ('load_seconds','weight_memory_bytes','joint_head_parameter_count','rss_after_load_bytes','max_rss_bytes'):
        v=meta.get(k);L.check('runtime_metadata.'+k,v,'positive finite numeric',ok=numeric(v) and v>0)
    times={k:timestamp(v) for k,v in {'verified':runtime['checked_at_utc'],'approved':approval['approved_at_utc'],'frozen':freeze['frozen_at_utc'],'started':meta['started_at'],'completed':meta['completed_at']}.items()}
    for a,b in [('verified','frozen'),('approved','frozen'),('frozen','started'),('started','completed')]:L.check('chronology.'+a+'_before_'+b,times[a].isoformat(),times[b].isoformat(),ok=times[a]<times[b])
    L.check('request_order.predictions',[r.get('id') for r in raw],order)
    L.check('request_count.predictions',len(raw),48)
    wall=(times['completed']-times['started']).total_seconds()
    recorded_times=[r.get('total_seconds') for r in raw]+[meta.get('warmup',{}).get('total_seconds'),meta.get('load_seconds')]
    if all(numeric(t) and t>=0 for t in recorded_times):
        lower_bound=sum(recorded_times)
        L.check('runtime.wall_seconds_cover_recorded_load_and_inferences',wall,lower_bound,ok=wall+0.001>=lower_bound,note='Repeat timing is unavailable and excluded from this lower bound')
    rss_values=[r.get('rss_bytes') for r in raw]+[meta.get('rss_after_load_bytes'),meta.get('warmup',{}).get('rss_bytes')]
    if all(numeric(t) for t in rss_values) and numeric(meta.get('max_rss_bytes')):
        L.check('runtime.max_rss_covers_observed',meta['max_rss_bytes'],max(rss_values),ok=meta['max_rss_bytes']>=max(rss_values))
    warm=validate_native(meta.get('warmup'),fields=('decision',),options={'decision':['billing','technical']})
    for c in warm['checks']:L.check('warmup.'+c['path'],c['observed'],c['expected'],ok=c['passed'])
    probe=meta.get('repeatability_probe',{})
    for k,v in {'id':order[0],'single_case_only':True}.items():L.check('repeatability.'+k,probe.get(k),v)
    L.check('repeatability.same_choice_is_boolean',type(probe.get('same_choice')).__name__,'bool')
    delta=probe.get('repeat_max_absolute_probability_difference');L.check('repeatability.delta',delta,'finite real in [0,1]',ok=numeric(delta) and 0<=delta<=1)
    # The official runner exposes only this summary, never the repeated full vector.
    monitor=root/'private_resource_monitor.jsonl'
    if monitor.exists():
        mon,_,errs=read_rows(monitor);L.check('resource_monitor.parse_errors',errs,[])
        L.check('resource_monitor.nonempty',bool(mon),True)
        L.check('resource_monitor.safety_thresholds_respected',all(numeric(r.get('rss_bytes')) and r['rss_bytes']<=8.3*1024**3 and numeric(r.get('available_bytes')) and r['available_bytes']>=.4*1024**3 for r in mon),True,note='Only pass/fail retained; host available-memory values omitted')
        for i,row in enumerate(mon):
            L.check(f'resource_monitor.{i}.no_guard_stop',row.get('event'),'no memory_guard_stop',ok=row.get('event')!='memory_guard_stop')
            t=timestamp(row['at']);L.check(f'resource_monitor.{i}.after_freeze',row['at'],freeze['frozen_at_utc'],ok=t>=times['frozen'])
    return {'metadata':meta,'timestamps':{k:v.isoformat() for k,v in times.items()},'freeze_manifest_sha256':sha(root/'freeze_manifest.json'),'repeatability_evidence_limit':'Only native single-case summary retained; separate repeat vector/timing unavailable'}
def stream_sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()

def safetensor_header(path):
    with Path(path).open('rb') as f:
        length=struct.unpack('<Q',f.read(8))[0]
        if length>64*1024*1024:raise ValueError('Unexpected safetensor header size')
        return json.loads(f.read(length))

def actual_runtime_checks(root,runtime,meta,L):
    runtime=Path(runtime);manifest=read_json(root/'reference_runtime/model_file_manifest.json');verified=[]
    for name,facts in manifest.items():
        p=runtime/'model'/name
        observed={'bytes':p.stat().st_size,'sha256':stream_sha(p)}
        L.check('actual_model_file.'+name+'.bytes',observed['bytes'],facts['bytes'])
        L.check('actual_model_file.'+name+'.sha256',observed['sha256'],facts['sha256'])
        verified.append({'name':name,**observed})
    for name in ('run_clef.py','joint_schema_model.py'):
        L.check('actual_runtime_source.'+name,sha(runtime/name),sha(root/'reference_runtime'/name))
    package_names=list(meta['packages'])
    code='import importlib.metadata,json; print(json.dumps({n:importlib.metadata.version(n) for n in '+repr(package_names)+'}))'
    proc=subprocess.run([str(runtime/'venv/bin/python'),'-c',code],capture_output=True,text=True,check=True)
    packages=json.loads(proc.stdout);L.check('actual_runtime_packages',packages,meta['packages'])
    head=safetensor_header(runtime/'model/joint_head.safetensors')
    tensors=[v for k,v in head.items() if k!='__metadata__']
    parameter_count=sum(math.prod(v['shape']) for v in tensors)
    L.check('actual_joint_head.parameter_count',parameter_count,meta['joint_head_parameter_count'])
    L.check('actual_joint_head.dtypes',sorted({v['dtype'] for v in tensors}),['BF16'])
    embeddings=[]
    for p in sorted((runtime/'model').glob('model-*.safetensors')):
        for name,v in safetensor_header(p).items():
            if name.endswith('lm_head.weight'):
                embeddings.append({'name':name,'shape':v['shape'],'dtype':v['dtype']})
                L.check('actual_output_embedding.'+name+'.shape',v['shape'],[248320,4096])
                L.check('actual_output_embedding.'+name+'.dtype',v['dtype'],'BF16')
    L.check('actual_output_embedding.present',bool(embeddings),True)
    return {'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_files':verified,'source_files':['run_clef.py','joint_schema_model.py'],'packages':packages,'joint_head_parameter_count':parameter_count,'output_embeddings':embeddings,'method':'Streaming SHA256 after completed run; header inspection only, no model load'}

def compare_tree(L,path,actual,expected):
    if isinstance(expected,dict) and isinstance(actual,dict):
        L.check(path+'.keys',sorted(actual),sorted(expected))
        for k in expected:compare_tree(L,path+'.'+k,actual.get(k,MISSING),expected[k])
    elif isinstance(expected,list) and isinstance(actual,list):
        L.check(path+'.length',len(actual),len(expected))
        for i,(a,b) in enumerate(zip(actual,expected)):compare_tree(L,path+f'[{i}]',a,b)
    elif numeric(expected) and numeric(actual) and (type(expected) is float or type(actual) is float):
        L.check(path,actual,expected,ok=math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-12))
    else:L.check(path,actual,expected)

def primary_case_expected(c):
    raw=c['native']; valid=c['valid']
    return {'id':c['id'],'pair_id':c['pair_id'],'side':c['side'],'valid':valid,'expected':c['gold'],
        'predicted':c['prediction'] if valid else {f:None for f in FIELDS},'field_correct':c['field_correct'],'all_fields_exact':c['exact'],
        'selected_probabilities':{f:raw['probabilities_unrounded'][f][c['prediction'][f]] for f in FIELDS} if valid else {}}

def primary_pair_expected(p):
    flip=p['kind']=='flip'
    return {'id':p['id'],'case_ids':p['case_ids'],'domain':p['domain'],'kind':p['kind'],'subtype':p['subtype'],'valid_pair':p['valid'],'both_correct':p['both_correct'],
        'predicted_a':p['prediction_a'] if p['a_valid'] else {f:None for f in FIELDS},'predicted_b':p['prediction_b'] if p['b_valid'] else {f:None for f in FIELDS},
        'expected_a':p['gold_a'],'expected_b':p['gold_b'],'observed_change':p['changed'],'correct_directional_change':p['correct_directional_change'] if flip else None,
        'unjustified_change':None if flip else p['unjustified_change'],'failed_invariance':None if flip else p['failed_invariance'],'stable':None if flip else p['stable'],'stable_but_incorrect':None if flip else p['stable_wrong']}

def compare_primary(root,results,ind,L):
    if ind['scoring_stopped']:
        L.check('primary_scoring.not_comparable',True,False,note='Fatal input ambiguity: no primary score can be certified')
        return
    cr=ind['case_results']; pr=ind['pair_results']; s=ind['summary']; cb={c['id']:c for c in cr}; pb={p['id']:p for p in pr}
    for filename,expected_rows in [('case_scores.jsonl',cr),('pair_scores.jsonl',pr),('errors.jsonl',[c for c in cr if not c['exact']]),('pair_errors.jsonl',[p for p in pr if not p['both_correct']])]:
        rows,_,errors=read_rows(results/filename); L.check(filename+'.parse_errors',errors,[])
        L.check(filename+'.ids',[r.get('id') for r in rows],[c['id'] for c in expected_rows])
        for actual in rows:
            ident=actual.get('id'); iscase=filename in ('case_scores.jsonl','errors.jsonl');lookup=cb if iscase else pb
            if ident not in lookup:continue
            item=lookup[ident];expect=primary_case_expected(item) if iscase else primary_pair_expected(item)
            if iscase:
                issues=actual.get('technical_issues');L.check(filename+'.'+ident+'.technical_issues',issues,'nonempty list iff invalid',ok=isinstance(issues,list) and bool(issues)==(not item['valid']))
                expect['technical_issues']=issues # Names are implementation diagnostics; validity is independently checked above.
            if filename=='errors.jsonl':
                for k in ('domain','family','kind','subtype','rule','message','question','rationale'):expect[k]=item['case'][k]
                expect['probabilities_unrounded']=item['native'].get('probabilities_unrounded') if item['native'] else None
            compare_tree(L,filename+'.'+ident,actual,expect)
    actual=read_json(results/'summary.json')
    pairmap={'both_correct':'pair_both_correct','correct_directional_change':'flip_correct_directional_change','wrong_valid_flip_transition':'flip_wrong_valid_transition','invalid_or_missing_flip_transition':'flip_invalid_transition','observed_change_on_flip':'flip_observed_change','unjustified_change':'invariant_unjustified_change','unjustified_change_among_valid':'invariant_unjustified_change_valid_conditional','failed_invariance':'invariant_failed','stable_invariant':'invariant_stable','stable_but_incorrect':'invariant_stable_wrong'}
    case_metrics={f:s['field_accuracy'][f] for f in FIELDS};case_metrics.update(all_fields_exact=s['case_exact'],all_field_decisions=s['all_field_decisions'])
    strata={key:{val:{'pairs':v['both_correct']['denominator'],'both_correct':v['both_correct'],'valid_pairs':v['valid'],'observed_changes':v['changed']} for val,v in s['pair_strata'][key].items()} for key in ('domain','kind','subtype')}
    valid=[c for c in cr if c['valid']];times=s['timing']['inference_seconds'];tokens=s['timing']['input_tokens'];rss=s['timing']['rss_bytes']
    technical={'recorded_predictions':sum(not c['missing'] for c in cr),'valid_cases':len(valid),'missing_predictions':len(s['missing_ids']),'invalid_existing_predictions':sum(not c['valid'] and not c['missing'] for c in cr),'invalid_or_missing_case_ids':s['invalid_ids'],'invalid_pair_ids':[p['id'] for p in pr if not p['valid']],'valid_invariant_pairs':sum(p['valid'] for p in pr if p['kind']=='invariant'),'input_tokens_min':tokens['min'],'input_tokens_max':tokens['max'],'forward_seconds_median':times['median'],'forward_seconds_p95':times['p95_linear'],'forward_seconds_total':times['sum'],'peak_observed_rss_bytes':rss['max']}
    confusion={f:{g:{('__invalid__' if p=='INVALID' else p):n for p,n in row.items() if n} for g,row in cm.items() if sum(row.values())} for f,cm in s['confusion'].items()}
    expected={'suite_id':'minimal_pairs','case_count':48,'pair_count':24,'case_metrics':case_metrics,'pair_metrics':{k:s[v] for k,v in pairmap.items()},'pair_strata':strata,'case_domain_exact':{k:v['case_exact'] for k,v in s['case_strata']['domain'].items()},'technical':technical,'error_case_ids':s['error_case_ids'],'error_pair_ids':s['error_pair_ids'],'confusion_matrices':confusion,
        'limitations':['AI-authored and separately AI-reviewed, not human-expert validated','Purposive dependent pairs, schema and generic rule templates reused, not a representative holdout','Bounded native output choices, not generated German answer/question quality','Marginal option scores are neither calibrated nor joint probabilities','Experimental CPU NF4, no stock-precision/GPU claim','No pooled prior-suite scores or independent-case statistical inference'],
        'provenance':{'requests_sha256':sha(root/'data/requests.jsonl'),'gold_sha256':sha(root/'data/gold.jsonl'),'pairs_sha256':sha(root/'data/pairs.jsonl'),'predictions_sha256':sha(results/'predictions.jsonl')}}
    compare_tree(L,'summary',actual,expected)

def load_data(root):
    D={}
    for name in ('cases','pairs','gold','requests','metadata'):
        rows,_,errors=read_rows(root/f'data/{name}.jsonl')
        if errors:raise ValueError('Dataset parse errors in '+name+': '+json.dumps(errors))
        D[name]=rows
    for name in ('policy','design_summary'):D[name]=read_json(root/f'data/{name}.json')
    D['preflight']=read_json(root/'audit/encoding_preflight.json')
    return D

def run_audit(root,results,out,synthetic=False,runtime=None):
    root=Path(root);results=Path(results);out=Path(out)
    if out.resolve()==results.resolve():raise ValueError('Audit output must be separate from source predictions')
    out.mkdir(parents=True,exist_ok=True);L=Ledger();source=results/'predictions.jsonl';before=sha(source) if source.exists() else None
    raw,evidence,parse_errors=read_rows(source);dump_rows(out/'independent_raw_prediction_evidence.jsonl',evidence)
    ind=None;integrity={};exception=None
    try:
        D=load_data(root);dataset_checks(root,D,L)
        ind=compute(D['cases'],D['pairs'],{x['id']:x for x in D['gold']},{x['id']:x for x in D['requests']},D['preflight'],raw,parse_errors,check_token_match=not synthetic)
        L.check('scoring_stopped',ind['scoring_stopped'],False)
        for err in ind['fatal_errors']:L.check('fatal_prediction_error',err,None,ok=False)
        if not synthetic:
            integrity=integrity_checks(root,results,D,raw,L)
            if runtime is None:L.check('actual_runtime_directory_supplied',False,True)
            else:integrity['actual_runtime_verification']=actual_runtime_checks(root,runtime,integrity['metadata'],L)
        compare_primary(root,results,ind,L)
        for case in ind['case_results']:
            for check in case['native_checks']:L.check('native.'+case['id']+'.'+check['path'],check['observed'],check['expected'],ok=check['passed'])
        dump_rows(out/'independent_case_results.jsonl',ind['case_results']);dump_rows(out/'independent_pair_results.jsonl',ind['pair_results'])
        dump(out/'independent_summary.json',ind['summary'])
        dump_rows(out/'independent_error_cases.jsonl',[c for c in ind['case_results'] if not c['exact']])
        dump_rows(out/'independent_error_pairs.jsonl',[p for p in ind['pair_results'] if not p['both_correct']])
    except Exception as e:
        message=str(e).replace(str(root.resolve()),'<benchmark>').replace(str(results.resolve()),'<results>')
        if runtime:message=message.replace(str(Path(runtime).resolve()),'<runtime>')
        exception={'type':type(e).__name__,'message':message};L.check('audit_exception',exception,None,ok=False)
    after=sha(source) if source.exists() else None;L.check('source_predictions_unchanged',after,before)
    dump_rows(out/'independent_comparisons.jsonl',L.rows)
    report={'passed':not L.failures,'mismatches':L.failures,'prediction_count':len(raw),'predictions_sha256':after,'summary_sha256':sha(results/'summary.json') if (results/'summary.json').exists() else None,
        'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'synthetic_fixture_only':synthetic,'check_count':len(L.rows),'independence':'Standard-library implementation from protocol/native contract; primary scorer never read, imported or called by this checker','scoring_stopped':ind['scoring_stopped'] if ind else True,'exception':exception,
        'coverage':{'case_rows':len(ind['case_results']) if ind else 0,'pair_rows':len(ind['pair_results']) if ind else 0,'native_field_checks':'All native choice/type/options/full probabilities/rounded maps/argmax/confidence/tokens/truncation/timing/RSS','fixed_denominators':[48,24,12,12],'summary':'Every primary summary field, all strata, confusion matrices, timing and provenance compared recursively','error_records':'Exact erroneous ID sets, full input text, gold, predictions and unrounded probabilities; diagnostic issue presence independently checked, wording retained'},
        'integrity':integrity,'timing_percentile_definition':'P95 uses linear interpolation at index (n-1)*0.95 in sorted valid forward seconds, matching the frozen primary definition; nearest-rank is also retained independently','audit_script_sha256':sha(__file__),'artifacts':{p.name:sha(p) for p in sorted(out.glob('independent_*')) if p.is_file() and p.name not in ('independent_result_check.json','independent_result_review.md')}}
    dump(out/'independent_result_check.json',report)
    lines=['# Independent minimal-pair result audit','',f"Status: {'PASS' if report['passed'] else 'FAIL'}",f"Checked {report['prediction_count']} source predictions, {report['coverage']['case_rows']} case results, {report['coverage']['pair_rows']} pair results, and {report['check_count']} comparisons.",f"Prediction SHA256: {after}",'','Primary scorer was not read, imported, or invoked by this checker. Source predictions were not modified.']
    if ind and ind['summary']:
        s=ind['summary'];lines+=['','## Independently calculated main results']
        for name in ('case_exact','pair_both_correct','flip_correct_directional_change','invariant_unjustified_change','invariant_unjustified_change_valid_conditional','invariant_stable','invariant_stable_wrong','invariant_invalid'):
            v=s[name];lines.append(f"- {name}: {v['numerator']}/{v['denominator']} ({v['rate']})")
        lines+=['','## Every erroneous case']
        for c in ind['case_results']:
            if not c['exact']:lines += [f"- {c['id']}: expected {c['gold']}; native {c['prediction']}; valid={c['valid']}"]
        if not s['error_case_ids']:lines.append('None')
        lines+=['','## Every erroneous pair']
        for p in ind['pair_results']:
            if not p['both_correct']:lines.append(f"- {p['id']} ({p['kind']}/{p['subtype']}): {p['prediction_a']} → {p['prediction_b']}; expected {p['gold_a']} → {p['gold_b']}; valid={p['valid']}")
        if not s['error_pair_ids']:lines.append('None')
    lines+=['','## Mismatches']+[('- '+r['path']+': '+json.dumps(safe({'observed':r['observed'],'expected':r['expected']}),ensure_ascii=False)) for r in L.failures]
    if not L.failures:lines.append('None')
    lines+=['','## Timing definition','P95 uses linear interpolation at sorted index (n−1)×0.95 across valid benchmark forward timings. Warmup and repeated-first-case timing are excluded.','','## Evidence limits','Freeze chronology is supported by recorded UTC timestamps, approved hashes and retained run evidence, not an external trusted timestamp service. The single repeatability probe exposes only its native summary, not a second full vector or separate timing. Marginal probabilities are not calibration claims. Missing/invalid predictions cannot receive stability credit.']
    (out/'independent_result_review.md').write_text('\n'.join(lines)+'\n')
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--results',type=Path);ap.add_argument('--audit',type=Path);ap.add_argument('--runtime',type=Path,help='Real verified runtime directory, required for final all-file rehash after RAM release');ap.add_argument('--synthetic-fixture',action='store_true',help='Only for synthetic self-test fixtures: skip runtime/freeze and token preflight equality')
    a=ap.parse_args();r=run_audit(a.root,a.results or a.root/'results',a.audit or a.root/'audit',a.synthetic_fixture,a.runtime)
    print(json.dumps({k:r[k] for k in ('passed','prediction_count','check_count','predictions_sha256')},indent=2))
    if r['mismatches']:print(json.dumps(r['mismatches'][:8],ensure_ascii=False,indent=2))
    return 0 if r['passed'] else 1
if __name__=='__main__':sys.exit(main())
