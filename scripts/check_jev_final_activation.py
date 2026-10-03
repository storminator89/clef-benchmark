#!/usr/bin/env python3
"""Offline gate for new recovery-revision collector and manual-only activation."""
from pathlib import Path
import hashlib
import json
import re
ROOT=Path(__file__).resolve().parents[1]
REVISION='recovery-2026-10-03-v1'
BASE='80f407f08a7c4e2680c455718e117cfe7a64d96e'
SOURCE_PINS = {'scripts/run_jev_final_continuation.py': 'd330604cbc6b9745b84b20df188301d04bc6c6deaa62250205e3f29ca753b459', 'scripts/audit_jev_final_continuation.py': '891a8f62fd4635c490b5acb3539910c2632569d3c77b088739b0297d12d7b56b', 'scripts/workflows/jev-final-continuation.yml.in': 'b03cca534e285eac6d7d6bb6732fcd9b728ee6d5c4c128bdc885c270013d2bd6', 'execution/jev/final_continuation_plan.json': '7bb0133d6d8dcb4d977b19e6ab59b2eae83250be56053055fd6a905eb7cb32a9', 'execution/jev/second-run/FILE_SHA256.json': '16eba9a3e8e89bf4666567d07eb937cdd0d7c74ecec5866c937cb7c831d759b0', 'experiments/jev_comparison/FILE_SHA256.json': 'c62021bbcb33b94c653cc9649d7d06dcbdf1633d4dc7b7f19dee2db2cb8be2f4'}
INERT_SHA256='64458f1abb017e4f61c44bc34b889dc22a159b4b773eae045440febc168ec3b2'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def check(root=ROOT):
 root=Path(root)
 require(len(SOURCE_PINS)>=6,'Recovery source pins are not finalized')
 for name,digest in SOURCE_PINS.items():
  path=root/name
  require(path.is_file() and not path.is_symlink() and sha(path)==digest,'Reviewed recovery source changed: '+name)
 state=json.loads((root/'provenance/jev_final_activation.json').read_text())
 require(state['revision']==REVISION and state['base_commit']==BASE,'Wrong recovery revision')
 require(state['source_sha256']==SOURCE_PINS,'Activation pins disagree')
 require(state['remaining_initial_requests']==520 and state['prior_wire_attempts']==454
         and state['prior_valid']==452 and state['prior_failed']==2 and state['retry_prior_cases'] is False,'Continuation scope changed')
 require(state['max_total_attempts']==1024 and state['max_global_retries']==50 and state['local_api_usd_cap']=='3','Budget scope changed')
 require(state['missing_massive_baseline']=='pending_owner_final_audit' and state['frozen_bundle_changed'] is False,'Frozen baseline scope changed')
 path=root/'.github/workflows/jev-comparison.yml'
 require(path.is_file() and not path.is_symlink(),'Expected ordinary workflow')
 text=path.read_text()
 require(sha(path)==state['workflow_sha256'],'Current workflow hash mismatch')
 if state['status']=='prepared_inert_not_activated':
  require(sha(path)==INERT_SHA256 and state['reviewed_code_commit'] is None,'Inert workflow changed')
  require('JEV_API_KEY' not in text and '--execute' not in text,'Inert workflow can execute provider requests')
 elif state['status']=='activated_awaiting_one_manual_dispatch':
  commit=state['reviewed_code_commit']
  require(isinstance(commit,str) and re.fullmatch('[0-9a-f]{40}',commit),'Immutable reviewed commit required')
  template=(root/'scripts/workflows/jev-final-continuation.yml.in').read_text()
  require(text==template.replace('REVIEWED_FINAL_CONTINUATION_COMMIT',commit),'Workflow differs from pinned reviewed template')
 else:raise ValueError('Unknown recovery activation status')
 for other in (root/'.github/workflows').glob('*'):
  if other!=path:require('JEV_API_KEY' not in other.read_text() and 'jev_runner.py --execute' not in other.read_text(),'Unreviewed live workflow')
 return {'status':'offline_activation_gate_passed','revision':REVISION,'activation_state':state['status'],'remaining_cases':520,'network_calls':0,'credential_reads':0}
if __name__=='__main__':print(json.dumps(check()))
