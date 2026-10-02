#!/usr/bin/env python3
"""Pinned native Choice evaluation. Offline plan by default; live requires explicit approval.

Only request files enter the inference loop. Gold is consumed by the separate scorer.
The HTTP client has no automatic retries, redirects, proxy discovery or alternate host.
"""
from __future__ import annotations
import argparse, collections, copy, hashlib, json, math, os, ssl, sys, time
from datetime import datetime, timezone
from decimal import Decimal
from email.utils import parsedate_to_datetime
from pathlib import Path
import urllib.error, urllib.request

ENDPOINT='https://api.typesafe.ai/v1/systemone'
MODEL='jev-1.13.0'
PRICE=Decimal('0.042')
CAPACITY=65536
RESERVE=Decimal(CAPACITY)*PRICE/Decimal(1000000)
MAX_REQUESTS=974
MAX_RETRIES=50
MAX_ATTEMPTS=1024
MAX_USD=Decimal('3')
RETRYABLE={429,529}
ROOT=Path(__file__).resolve().parents[1]

class ContractError(ValueError): pass
class BudgetError(RuntimeError): pass

def stamp():return datetime.now(timezone.utc).isoformat()
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(p.read_bytes())
def dumps(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def rows(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def finite(v):return type(v) in (float,int) and math.isfinite(v)

def payload(request):
    if set(request)!={'model','state','questions'}:raise ContractError('Unexpected request fields')
    if request['model']!='clef-flash':raise ContractError('Unexpected source model')
    if not isinstance(request['state'],(str,list,dict)):raise ContractError('Invalid text state')
    # This bundle has only reviewed text JSON. Reject any media descriptor anywhere.
    def check(v):
        if isinstance(v,dict):
            if any(k.lower() in {'image','image_url','images','audio','video','input_image'} for k in v):raise ContractError('Media input is not comparable')
            for x in v.values():check(x)
        elif isinstance(v,list):
            for x in v:check(x)
    check(request['state'])
    qs=request['questions']
    if not isinstance(qs,dict) or not qs:raise ContractError('Empty questions')
    for q in qs.values():
        if not isinstance(q,dict) or set(q)!={'type','instructions','criteria'} or q['type']!='choice':raise ContractError('Native Choice only; no primitive remapping')
        if not isinstance(q['instructions'],(str,dict,list)):raise ContractError('Invalid instruction type')
        if not isinstance(q['criteria'],dict) or not 2<=len(q['criteria'])<=255:raise ContractError('Invalid option count')
        if any(not isinstance(k,str) or (v is not None and not isinstance(v,(str,dict,list))) for k,v in q['criteria'].items()):raise ContractError('Invalid criterion description type')
        check(q['instructions']);check(q['criteria'])
    # Deep copy preserves native JSON shapes, exact strings, option/field order.
    result=copy.deepcopy(request);result['model']=MODEL
    return result

def validate_response(request,response):
    if not isinstance(response,dict) or response.get('model')!=MODEL:raise ContractError('Missing or unexpected provider model version')
    answers=response.get('answers');qs=request['questions']
    if not isinstance(answers,dict) or set(answers)!=set(qs):raise ContractError('Answer fields mismatch')
    clean={}
    for field,q in qs.items():
        a=answers[field]
        if not isinstance(a,dict) or a.get('type')!='choice':raise ContractError('Response primitive mismatch')
        p=a.get('probabilities');c=a.get('choice');confidence=a.get('confidence')
        if not isinstance(p,dict) or set(p)!=set(q['criteria']):raise ContractError('Probability option keys mismatch')
        if any(not finite(x) or not 0<=x<=1 for x in p.values()):raise ContractError('Invalid native probability')
        if abs(math.fsum(p.values())-1)>1e-5:raise ContractError('Probability sum outside tolerance')
        if c not in p or p[c]!=max(p.values()):raise ContractError('Choice is not a native maximum')
        if not finite(confidence) or not 0<=confidence<=1:raise ContractError('Invalid native confidence')
        # Do not substitute p_max, normalize, round or repair a distribution.
        clean[field]={'type':'choice','choice':c,'probabilities':p,'confidence':confidence}
    usage=response.get('usage')
    if not isinstance(usage,dict) or any(type(usage.get(k))!=int or usage[k]<0 for k in ('input_tokens','output_tokens')):raise ContractError('Missing or invalid billing units')
    if usage['input_tokens']>CAPACITY:raise ContractError('Usage exceeds documented capacity reservation')
    return {'model':response['model'],'answers':clean,'usage':{k:usage[k] for k in ('input_tokens','output_tokens')}}

def load_requests(root):
    manifest=json.loads((root/'manifest.json').read_text());all_rows=[]
    for suite in manifest['suites']:
        name='inputs/'+suite['id']+'/requests.jsonl';p=root/name
        if sha(p)!=manifest['files'][name]:raise ContractError('Frozen request checksum mismatch')
        rs=rows(p)
        if len(rs)!=suite['count'] or len({r['id'] for r in rs})!=len(rs):raise ContractError('Request count/identity mismatch')
        for r in rs:
            if set(r)!={'id','request'}:raise ContractError('Unexpected request envelope fields')
            all_rows.append({'suite':suite['id'],'id':r['id'],'request':payload(r['request']),'source_request_sha256':sha_bytes(dumps(r['request']).encode())})
    if len(all_rows)>MAX_REQUESTS:raise ContractError('Request count exceeds reviewed scope')
    return manifest,all_rows

def make_plan(root):
    manifest,rs=load_requests(root);by=collections.defaultdict(list);seen=collections.defaultdict(list)
    for r in rs:by[r['suite']].append(r);seen[sha_bytes(dumps(r['request']).encode())].append([r['suite'],r['id']])
    result=[]
    for sid,group in by.items():
        size=sum(len(dumps(r['request']).encode()) for r in group)
        # Text-byte heuristic only. The provider tokenizer is not published here.
        result.append({'suite':sid,'requests':len(group),'questions':sum(len(r['request']['questions']) for r in group),'utf8_json_bytes':size,'approx_input_tokens_bytes_div_4':math.ceil(size/4),'approx_input_tokens_bytes_div_2':math.ceil(size/2),'estimated_usd_bytes_div_4':float(Decimal(math.ceil(size/4))*PRICE/1000000),'baseline':next(s['baseline'] for s in manifest['suites'] if s['id']==sid)})
    size=sum(g['utf8_json_bytes'] for g in result)
    return {'status':'offline_plan_no_network_no_credential_read','endpoint':ENDPOINT,'model':MODEL,'price_usd_per_million_input_tokens':str(PRICE),'price_verified_utc':'2026-10-02','price_source':'https://docs.typesafe.ai/models','one_pass_requests':len(rs),'question_count':sum(g['questions'] for g in result),'utf8_json_bytes':size,'approx_input_tokens_range':[math.ceil(size/4),math.ceil(size/2)],'approx_one_pass_usd_range':[float(Decimal(math.ceil(size/4))*PRICE/1000000),float(Decimal(math.ceil(size/2))*PRICE/1000000)],'estimate_caveat':'UTF-8 JSON bytes divided by 4 to 2 is an illustrative estimate, not an official tokenizer, confidence interval or billing guarantee. Structured/internal overhead can differ. Actual usage.input_tokens is logged.','max_total_attempts':MAX_ATTEMPTS,'max_global_retries':MAX_RETRIES,'max_retries_per_case':1,'capacity_tokens_reserved_per_attempt':CAPACITY,'reserved_usd_per_attempt':str(RESERVE),'all_attempts_capacity_reservation_usd':str(RESERVE*MAX_ATTEMPTS),'proposed_max_api_usd':str(MAX_USD),'cap_caveat':'Local attempt/reservation guard under dated published price/capacity. Not a provider-enforced account spend limit. No signup, top-up, subscription or paid CI authorized.','suites':result,'exact_payload_repeats':[v for v in seen.values() if len(v)>1],'pooled_accuracy':None,'excluded':manifest['excluded'],'manifest_sha256':sha(root/'manifest.json')}

class Ledger:
    def __init__(self,cap):
        self.cap=Decimal(str(cap));self.attempts=0;self.retries=0;self.known_input_tokens=0
        if not self.cap.is_finite() or not 0<self.cap<=MAX_USD:raise BudgetError('Cap must be positive and at most 3 USD')
    def reserve(self,retry=False):
        if self.attempts>=MAX_ATTEMPTS or (retry and self.retries>=MAX_RETRIES):raise BudgetError('Attempt/retry ceiling reached')
        if RESERVE*(self.attempts+1)>self.cap:raise BudgetError('Next request exceeds local reservation cap')
        self.attempts+=1;self.retries+=int(retry)
    def status(self):return {'wire_attempts_reserved':self.attempts,'retry_attempts':self.retries,'capacity_reserved_usd':str(RESERVE*self.attempts),'known_success_input_tokens':self.known_input_tokens,'known_success_cost_usd':str(Decimal(self.known_input_tokens)*PRICE/1000000),'cap_usd':str(self.cap)}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):raise ContractError('Redirect refused')

def retry_delay(value):
    if value is None:return None
    try:delay=float(value)
    except (ValueError,TypeError):
        try:
            dt=parsedate_to_datetime(value)
            if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
            delay=max(0.0,(dt-datetime.now(timezone.utc)).total_seconds())
        except (ValueError,TypeError,OverflowError):return None
    return delay if math.isfinite(delay) and delay>=0 else None

class HttpTransport:
    def __init__(self,token):
        self.token=token
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect(),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    def __call__(self,body):
        request=urllib.request.Request(ENDPOINT,data=body,headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json','Accept':'application/json'},method='POST')
        try:
            with self.opener.open(request,timeout=90) as response:
                data=response.read(2_000_001)
                if len(data)>2_000_000:raise ContractError('Response too large')
                return response.status,data,None
        except urllib.error.HTTPError as e:
            # Never save/print exception strings, error bodies, headers or echoed keys.
            delay=retry_delay(e.headers.get('Retry-After'));e.close()
            return e.code,b'',delay

def run(root,out,cap,transport,sleep=time.sleep,now=time.perf_counter):
    manifest,requests=load_requests(root);ledger=Ledger(cap)
    if out.exists():raise ContractError('New output directory required; resume needs separate review')
    out.mkdir(parents=True);summary={'status':'running','started_utc':stamp(),'endpoint':ENDPOINT,'requested_model':MODEL,'provider_immutable_weight_hash':None,'provider_revision_semantics':'Versioned service ID only; no public immutable weight checksum','manifest_sha256':sha(root/'manifest.json'),'latency_definition':'HTTP submission through complete body read; per-case total also includes validation and retries/backoff. Network-hosted service, not comparable to Clef CPU forward-only latency.','planned_cases':len(requests),'completed_cases':0,'failed_cases':0}
    attempts=(out/'attempts.jsonl').open('x');predictions=(out/'predictions.jsonl').open('x');last_start=None;halt=None
    try:
        for r in requests:
            body=dumps(r['request']).encode();case_start=now();last_error=None;case_attempts=0
            for retry in (False,True):
                if retry and ledger.retries>=MAX_RETRIES:break
                if last_start is not None:sleep(max(0,1.05-(now()-last_start)))
                ledger.reserve(retry);case_attempts+=1
                # Persist the reservation BEFORE sending: interruption never conceals an attempt.
                attempt={'suite':r['suite'],'id':r['id'],'attempt':ledger.attempts,'case_attempt':case_attempts,'retry':retry,'started_utc':stamp(),'request_body_sha256':sha_bytes(body),'reserved_usd':str(RESERVE),'event':'reserved'}
                attempts.write(dumps(attempt)+'\n');attempts.flush();os.fsync(attempts.fileno())
                last_start=now();started=last_start
                try:status,raw,retry_after=transport(body)
                except Exception:
                    elapsed=now()-started
                    # Timeouts can be billed. No blind retry of ambiguous outcomes.
                    last_error='transport_failure_unknown_billing';attempts.write(dumps({'attempt':ledger.attempts,'event':'completed','status':last_error,'request_seconds':elapsed})+'\n');attempts.flush();halt=last_error;break
                elapsed=now()-started
                event={'attempt':ledger.attempts,'event':'completed','http_status':status,'request_seconds':elapsed,'response_body_sha256':sha_bytes(raw) if raw else None}
                if status==200:
                    try:native=validate_response(r['request'],json.loads(raw))
                    except Exception:
                        event['status']='invalid_response_or_billing';last_error=event['status'];halt=last_error
                    else:
                        ledger.known_input_tokens+=native['usage']['input_tokens'];event['status']='valid'
                        prediction={'suite':r['suite'],'id':r['id'],'status':'valid','provider_model':native['model'],'answers':native['answers'],'probabilities_unrounded':{k:a['probabilities'] for k,a in native['answers'].items()},'usage':native['usage'],'input_tokens':native['usage']['input_tokens'],'request_seconds':elapsed,'case_end_to_end_seconds':now()-case_start,'attempt_count':case_attempts,'request_body_sha256':sha_bytes(body),'source_request_sha256':r['source_request_sha256'],'response_body_sha256':sha_bytes(raw),'truncation':'not_reported_by_provider; no client truncation'}
                        predictions.write(dumps(prediction)+'\n');predictions.flush();summary['completed_cases']+=1;last_error=None
                    attempts.write(dumps(event)+'\n');attempts.flush();break
                last_error='http_'+str(status);event['status']=last_error;attempts.write(dumps(event)+'\n');attempts.flush()
                if status not in RETRYABLE:halt=last_error;break
                if retry:break
                if retry_after is not None and retry_after>120:halt='retry_after_exceeds_bounded_wait';break
                sleep(max(2.0,retry_after or 0))
            if last_error:
                summary['failed_cases']+=1;predictions.write(dumps({'suite':r['suite'],'id':r['id'],'status':'failed','error_code':last_error,'attempt_count':case_attempts,'case_end_to_end_seconds':now()-case_start})+'\n');predictions.flush()
            summary.update(ledger.status());summary['remaining_cases']=len(requests)-summary['completed_cases']-summary['failed_cases'];write(out/'run_summary.json',summary)
            if halt:break
        summary['status']='halted' if halt else ('completed_with_failures' if summary['failed_cases'] else 'complete');summary['halt_reason']=halt
    except BudgetError:
        summary['status']='halted';summary['halt_reason']='local_budget_or_attempt_limit'
    finally:
        attempts.close();predictions.close();summary.update(ledger.status());summary['remaining_cases']=len(requests)-summary['completed_cases']-summary['failed_cases'];summary['ended_utc']=stamp();write(out/'run_summary.json',summary)
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path);p.add_argument('--execute',action='store_true');p.add_argument('--approved-api-usd',type=Decimal);p.add_argument('--approval',choices=['one-pass-public-text-974']);a=p.parse_args()
    if not a.execute:
        plan=make_plan(a.root)
        if a.output:write(a.output,plan)
        else:print(json.dumps(plan,indent=2))
        return 0
    if a.approval!='one-pass-public-text-974' or a.approved_api_usd is None or a.output is None:raise ContractError('Explicit bounded live approval and output directory required')
    if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='storminator89/clef-benchmark' or os.environ.get('GITHUB_EVENT_NAME')!='workflow_dispatch' or os.environ.get('GITHUB_RUN_ATTEMPT')!='1':raise ContractError('Live execution restricted to first manual run in the reviewed repository')
    token=os.environ.get('JEV_API_KEY','')
    if not token or any(c.isspace() for c in token):raise ContractError('Missing or malformed repository secret')
    outcome=run(a.root,a.output,a.approved_api_usd,HttpTransport(token));print(json.dumps({k:outcome[k] for k in ['status','completed_cases','failed_cases','remaining_cases','wire_attempts_reserved','capacity_reserved_usd','known_success_cost_usd']}))
    return 0 if outcome['status']=='complete' else 2
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        # Only our own exception class name is public. Exception text may contain external data.
        print(json.dumps({'status':'blocked','error_type':type(e).__name__,'details':'See local protocol and safe metadata; no request, header or credential emitted'}));sys.exit(2)
