#!/usr/bin/env python3
"""Independent offline reconciliation of recovery-revision continuation evidence.

Imports only the checksum-pinned original response validator, not the new
collector. A failed audit must not be passed to scoring. No repair or inference.
"""
from pathlib import Path
from decimal import Decimal
import argparse
import hashlib
import importlib.util
import json
import math
import re
ROOT=Path(__file__).resolve().parents[1]
BUNDLE_PIN='c62021bbcb33b94c653cc9649d7d06dcbdf1633d4dc7b7f19dee2db2cb8be2f4'
RUNNER_PIN='0cbd708b644944da642c645b09b2820266259e8233c1b73de2278d27fe56f733'
PRIOR_PIN='16eba9a3e8e89bf4666567d07eb937cdd0d7c74ecec5866c937cb7c831d759b0'
PLAN_PIN='7bb0133d6d8dcb4d977b19e6ab59b2eae83250be56053055fd6a905eb7cb32a9'
FILES={'attempts.jsonl','predictions.jsonl','run_summary.json','connection_check.json','validation_diagnostics.jsonl','flagged_native.jsonl'}
def require(ok,message):
 if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def unique(pairs):
 out={}
 for key,value in pairs:
  require(key not in out,'Duplicate JSON key');out[key]=value
 return out
def parse(data):return json.loads(data,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON constant')))
def rows(data):
 if not data:return []
 require(data.endswith(b'\n') and all(data.splitlines()),'Invalid JSONL boundary')
 return [parse(line) for line in data.splitlines()]
def regular(root,name):
 path=root/name
 require(path.is_file() and not path.is_symlink() and not root.is_symlink(),'Expected ordinary artifact')
 require(path.resolve().is_relative_to(root.resolve()),'Artifact path escapes root')
 return path.read_bytes()
def finite(value):return type(value) in (float,int) and math.isfinite(value)
def identity(row):return row['suite'],row['id']
def digest(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
def sum_only(request,row):
 """Independent contract validation with only the sum restriction relaxed."""
 require(row['provider_model']=='jev-1.13.0','Flagged model differs')
 answers=row['answers'];questions=request['questions']
 require(isinstance(answers,dict) and set(answers)==set(questions),'Flagged fields differ')
 sums={}
 for field,q in questions.items():
  a=answers[field];require(set(a)=={'type','choice','probabilities','confidence'} and a['type']=='choice','Flagged answer shape differs')
  probabilities=a['probabilities'];require(isinstance(probabilities,dict) and set(probabilities)==set(q['criteria']),'Flagged options differ')
  require(all(finite(v) and 0<=v<=1 for v in probabilities.values()),'Invalid flagged numeric value')
  choice=a['choice'];require(isinstance(choice,str) and choice in probabilities and probabilities[choice]==max(probabilities.values()),'Flagged choice is not native maximum')
  require(finite(a['confidence']) and 0<=a['confidence']<=1,'Invalid flagged confidence')
  total=math.fsum(probabilities.values());sums[field]={'native_sum':total,'absolute_deviation':abs(total-1),'normalization_within_tolerance':abs(total-1)<=1e-5}
 require(any(not x['normalization_within_tolerance'] for x in sums.values()),'Strict-valid vector improperly flagged')
 usage=row['usage'];require(set(usage)=={'input_tokens','output_tokens'} and all(type(v)is int and v>=0 for v in usage.values()) and usage['input_tokens']<=65536,'Flagged billing invalid')
 require(row['input_tokens']==usage['input_tokens'],'Flagged token copy differs')
 require(row['probabilities_unrounded']=={f:a['probabilities'] for f,a in answers.items()},'Flagged native vector differs')
 diagnostic=row['diagnostic'];require(diagnostic['contract_code']=='probability_sum_outside_tolerance' and diagnostic['sum_only_deviation'] is True and diagnostic['strict_scoring_eligible'] is False and diagnostic['probability_sums']==sums,'Flagged deviation diagnostic differs')
 return usage['input_tokens']
def audit(run,root=ROOT):
 root=Path(root);run=Path(run);bundle=root/'experiments/jev_comparison';prior=root/'execution/jev/second-run'
 lock=regular(bundle,'FILE_SHA256.json');require(sha(lock)==BUNDLE_PIN,'Frozen file manifest changed')
 locked=parse(lock)
 actual={str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 require(actual==set(locked)|{'FILE_SHA256.json'},'Frozen bundle scope changed')
 for name,value in locked.items():require(sha(regular(bundle,name))==value,'Frozen bundle file changed')
 runner_path=bundle/'scripts/jev_runner.py';require(sha(runner_path.read_bytes())==RUNNER_PIN,'Frozen validator changed')
 spec=importlib.util.spec_from_file_location('audit_frozen_runner',runner_path);runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
 _,requests=runner.load_requests(bundle);require(len(requests)==974,'Frozen denominator changed')
 plock=regular(prior,'FILE_SHA256.json');require(sha(plock)==PRIOR_PIN,'Prior lock changed')
 prior_files={name:regular(prior,name) for name in parse(plock)}
 for name,data in prior_files.items():require(sha(data)==parse(plock)[name],'Prior bytes changed')
 plan_bytes=regular(root,'execution/jev/final_continuation_plan.json');require(sha(plan_bytes)==PLAN_PIN,'Continuation plan changed');plan=parse(plan_bytes)
 require({p.name for p in run.iterdir()}==FILES,'Output must have exactly six collector artifacts')
 data={name:regular(run,name) for name in FILES}
 for name in ('predictions.jsonl','attempts.jsonl','validation_diagnostics.jsonl'):require(data[name].startswith(prior_files[name]),'Historical byte prefix changed')
 predictions=rows(data['predictions.jsonl']);events=rows(data['attempts.jsonl']);diagnostics=rows(data['validation_diagnostics.jsonl']);flags=rows(data['flagged_native.jsonl']);summary=parse(data['run_summary.json']);gate=parse(data['connection_check.json'])
 require(454<=len(predictions)<=974 and len(events)%2==0,'Incomplete output or unsettled reservation')
 require(len({identity(p) for p in predictions})==len(predictions),'Duplicate prediction')
 new_predictions=predictions[454:];new_events=events[908:]
 require(len(events)>=908 and len(new_events)%2==0,'Prior ledger truncated')
 require(all(identity(p)==identity(r) for p,r in zip(predictions,requests)),'Prediction order differs from frozen prefix')
 # Revalidate all eligible historical successes without assuming their count.
 strict_tokens=0;strict_count=0
 for p,r in zip(predictions[:454],requests[:454]):
  if p['status']=='valid':
   native=runner.validate_response(r['request'],{'model':p['provider_model'],'answers':p['answers'],'usage':p['usage']});strict_tokens+=native['usage']['input_tokens'];strict_count+=1
 require((strict_count,strict_tokens)==(452,437597),'Prior strict metrics differ')
 new_diags=diagnostics[len(rows(prior_files['validation_diagnostics.jsonl'])):]
 diag_by={d['attempt']:d for d in new_diags};flag_by={d['attempt']:d for d in flags}
 require(len(diag_by)==len(new_diags) and len(flag_by)==len(flags),'Duplicate diagnostic or flag')
 offset=0;retries=0;flag_tokens=0;flag_count=0;seen_diags=set();seen_flags=set();terminal=[];fatal_cases=[]
 for index,p in enumerate(new_predictions):
  request=requests[454+index];count=p['attempt_count'];require(type(count)is int and count in (1,2) and (index>0 or count==1),'Invalid retry count')
  require(offset+2*count<=len(new_events),'Prediction has missing reservation')
  case_pairs=[]
  for case_index in range(count):
   reservation,event=new_events[offset:offset+2];attempt=455+offset//2;offset+=2
   require(reservation['event']=='reserved' and event['event']=='completed' and reservation['attempt']==event['attempt']==attempt,'Ledger sequence differs')
   require(identity(reservation)==identity(request) and reservation['case_attempt']==case_index+1 and reservation['retry'] is bool(case_index),'Reservation identity/retry differs')
   body=sha(runner.dumps(request['request']).encode());require(reservation['request_body_sha256']==body and reservation['reserved_usd']=='0.002752512','Reservation payload/capacity differs')
   require(finite(event['request_seconds']) and event['request_seconds']>=0,'Invalid observed timing')
   if case_index:require(case_pairs[-1][1].get('http_status') in (429,529) and case_pairs[-1][1]['status'] in ('http_429','http_529'),'Retry not eligible')
   retries+=case_index;case_pairs.append((reservation,event))
  reservation,event=case_pairs[-1];attempt=event['attempt'];status=event['status'];terminal.append(status)
  require(finite(p['case_end_to_end_seconds']) and p['case_end_to_end_seconds']>=0,'Invalid case timing')
  if status in ('valid','flagged_native'):
   require(event.get('http_status')==200 and digest(event.get('response_body_sha256')),'Missing successful response provenance')
   native_row=p if status=='valid' else flag_by.get(attempt)
   require(native_row is not None,'Mandatory flagged native data missing')
   require(identity(native_row)==identity(request) and native_row['attempt_count']==count,'Native row identity differs')
   require(native_row['request_body_sha256']==body and native_row['source_request_sha256']==request['source_request_sha256'] and native_row['response_body_sha256']==event['response_body_sha256'],'Native row hashes differ')
   require(finite(native_row['request_seconds']) and native_row['request_seconds']==event['request_seconds'],'Native request timing differs')
   if status=='valid':
    require(p['status']=='valid','Strict success status differs')
    native=runner.validate_response(request['request'],{'model':p['provider_model'],'answers':p['answers'],'usage':p['usage']})
    require(p['probabilities_unrounded']=={k:v['probabilities'] for k,v in native['answers'].items()} and p['input_tokens']==native['usage']['input_tokens'],'Strict native copies differ')
    strict_tokens+=native['usage']['input_tokens'];strict_count+=1
   else:
    require(p['status']=='failed' and p['error_code']=='probability_sum_outside_tolerance' and p['strict_scoring_eligible'] is False and event['strict_scoring_eligible'] is False and native_row['strict_scoring_eligible'] is False and native_row['status']=='flagged_native','Flag promoted to scored success')
    require(native_row['attempt']==attempt and native_row['diagnostic']==event['diagnostic']==p['diagnostic'],'Flag diagnostic link differs')
    flag_tokens+=sum_only(request['request'],native_row);flag_count+=1;seen_flags.add(attempt)
  else:
   require(p['status']=='failed' and p['error_code']==status and not ({'answers','probabilities_unrounded','usage','input_tokens'}&set(p)),'Failed case contains scored values')
   require(status in ('invalid_response_or_billing','transport_failure_unknown_billing') or re.fullmatch('http_[1-5][0-9][0-9]',status),'Unknown event failure')
   if status.startswith('http_'):require(event.get('http_status')==int(status[5:]),'HTTP failure mismatch')
  if 'diagnostic' in event:
   record=diag_by.get(attempt);require(record is not None and identity(record)==identity(request) and record['diagnostic']==event['diagnostic']==p.get('diagnostic'),'Missing diagnostic reconciliation');seen_diags.add(attempt)
  elif status=='invalid_response_or_billing':raise ValueError('Mandatory structural failure diagnostic missing')
  fatal = status not in ('valid','flagged_native','http_429','http_529')
  if status in ('http_429','http_529') and (index==0 or (count==1 and retries<50)):
   fatal = True  # An available permitted retry was not exhausted: gate, time/budget or excessive-wait stop.
  if fatal:
   fatal_cases.append(index)
   require(index==len(new_predictions)-1,'Collection continued after fatal event')
 require(offset==len(new_events),'Reservations without a prediction')
 require(seen_diags==set(diag_by) and seen_flags==set(flag_by),'Extra diagnostics or flagged native records')
 attempts=len(events)//2;require(attempts<=1024 and retries<=50,'Shared attempt/retry cap exceeded')
 cap=Decimal(summary['cap_usd']);require(cap.is_finite() and 0<cap<=3 and Decimal('0.002752512')*attempts<=cap,'Shared reservation cap exceeded')
 failed=len(predictions)-strict_count;current_valid=strict_count-452
 expected={'collector_revision':'newrevision-rebuilt-2026-10-03','validation_version':'v2-strict-scoring-quarantine-sum-only','flagged_vectors_are_strict_scoring_failures':True,'renormalization_permitted':False,'planned_cases':974,'continuation_planned_cases':520,'prior_completed_cases':452,'prior_failed_cases':2,'prior_wire_attempts_reserved':454,'prior_failed_cases_retried':0,'completed_cases':strict_count,'failed_cases':failed,'remaining_cases':974-len(predictions),'current_completed_cases':current_valid,'current_failed_cases':len(new_predictions)-current_valid,'wire_attempts_reserved':attempts,'current_wire_attempts_reserved':attempts-454,'retry_attempts':retries,'current_retry_attempts':retries,'current_transport_calls_started':attempts-454,'known_success_input_tokens':strict_tokens,'current_known_success_input_tokens':strict_tokens-437597,'current_flagged_native_cases':flag_count,'flagged_native_input_tokens':flag_tokens,'attempt_reservations_without_valid_billing':attempts-strict_count-flag_count,'continuation_plan_sha256':PLAN_PIN,'first_run_file_lock_sha256':PRIOR_PIN}
 for key,value in expected.items():require(summary.get(key)==value,'Summary counter/provenance differs: '+key)
 for key,value in {'capacity_reserved_usd':Decimal('0.002752512')*attempts,'current_capacity_reserved_usd':Decimal('0.002752512')*(attempts-454),'known_success_cost_usd':Decimal(strict_tokens)*Decimal('.042')/1000000,'current_known_success_cost_usd':Decimal(strict_tokens-437597)*Decimal('.042')/1000000,'flagged_native_cost_usd':Decimal(flag_tokens)*Decimal('.042')/1000000}.items():require(Decimal(summary[key])==value,'Summary cost differs: '+key)
 require(gate['probe_is_first_unattempted_case'] is True and gate['extra_requests']==0 and gate['original_case_number']==455,'Connection gate scope differs')
 if terminal:
  first=terminal[0];require(gate['connection_valid'] is (first in ('valid','flagged_native')),'Connection gate validity differs')
  require(gate['status']==({'valid':'valid','flagged_native':'flagged_native','invalid_response_or_billing':'first_request_contract_failure','transport_failure_unknown_billing':'first_request_transport_failure'}.get(first,'first_request_http_failure')),'Connection gate outcome differs')
  if first not in ('valid','flagged_native'):require(len(new_predictions)==1,'Collection continued after failed first gate')
 else:require(gate['connection_valid'] is False and gate['status']=='not_attempted','Unattempted gate differs')
 if summary['status']=='completed_with_failures':require(len(predictions)==974 and summary['halt_reason'] is None and not fatal_cases,'False completion after incomplete coverage or fatal event')
 else:
  require(summary['status']=='halted' and summary['halt_reason'] in ('local_budget_or_attempt_limit','total_time_limit','retry_after_exceeds_bounded_wait','unexpected_local_failure','transport_failure_unknown_billing','invalid_response_or_billing') or (summary['status']=='halted' and re.fullmatch('http_[1-5][0-9][0-9]',str(summary['halt_reason']))),'Unknown terminal status')
  reason=summary['halt_reason']
  if reason in ('transport_failure_unknown_billing','invalid_response_or_billing') or reason.startswith('http_'):require(bool(terminal) and terminal[-1]==reason,'Halt reason differs from terminal event')
  if reason=='retry_after_exceeds_bounded_wait':require(bool(terminal) and terminal[-1] in ('http_429','http_529'),'Retry wait halt has no eligible event')
 return {'status':'passed','audit_revision':'independent-recovery-2026-10-03-v1','cases_observed':len(predictions),'strict_valid':strict_count,'technical_failed':failed,'missing':974-len(predictions),'quarantined_new_cases':flag_count,'wire_attempts':attempts,'retries':retries,'frozen_expected_cases':974,'massive_baseline':'pending_owner_final_audit','historical_prefix_bytes_preserved':True,'scorer_imported':False,'collector_imported':False,'network_calls':0,'credential_reads':0,'raw_http_body_hashes':'linkage only; discarded bodies cannot be rehashed','files_sha256':{name:sha(data[name]) for name in sorted(FILES)}}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--output',type=Path);args=parser.parse_args()
 try:report=audit(args.run)
 except Exception as error:parser.exit(2,'Audit rejected: '+str(error)+'\n')
 text=json.dumps(report,indent=2)+'\n'
 if args.output:
  require(not args.output.resolve().is_relative_to(args.run.resolve()),'Audit output must be outside collector inputs')
  with args.output.open('x') as f:f.write(text)
 print(text,end='')
if __name__=='__main__':main()
