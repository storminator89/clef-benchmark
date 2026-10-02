#!/usr/bin/env python3
"""One-way scientific freeze, before and independently of the inference gate."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'freeze_manifest.json').exists(),'Already frozen'
assert not (R/'results/predictions.jsonl').exists(),'Inference already exists'
subprocess.run([sys.executable,str(R/'scripts/validate.py')],check=True)
a=json.loads((R/'audit/freeze_approval.json').read_text());assert a['approved_for_freeze'] is True
for rel,h in a['files'].items():assert sha(R/rel)==h,rel
p=json.loads((R/'audit/encoding_preflight.json').read_text());assert p['requests_sha256']==sha(R/'data/requests.jsonl') and p['count']==48 and p['max_tokens']<=2048
assert json.loads((R/'audit/scorer_self_tests.json').read_text())['status']=='passed'
assert json.loads((R/'audit/independent_checker_self_tests.json').read_text())['passed'] is True
v=json.loads((R/'provenance/runtime_verified_before_run.json').read_text());assert v['runner_sha256']=='d06f85b922e1e4d0e905a1ddc8846aedcafa93c29f502f48b1529a36a9eb5906'
for n,ver in {'torch':'2.11.0+cpu','transformers':'5.10.2','bitsandbytes':'0.50.2'}.items():assert v['packages'][n]==ver
paths=set(p for folder in ['data','scripts','reference_runtime','licenses','audit'] for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths|={R/'PROTOCOL.md',R/'SOURCES.md',R/'LICENSE',R/'NOTICE',R/'provenance/runtime_verified_before_run.json'}
m={'suite_id':'multidocument_precedence_2026_10_02','version':'1.0','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_inference_before_freeze':False,'case_count':48,'family_count':12,'shared_template_count':16,'paired_order_intervention':False,'fields':['source','determination'],'revision':'17f0b0ad64efb65d273590632833508766b2aae6','runtime':'CPU NF4, original BF16 head/output embeddings, six threads, batch1, cap2048','files':{str(p.relative_to(R)):sha(p) for p in sorted(paths)}}
(R/'freeze_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'frozen':True,'files':len(m['files']),'manifest_sha256':sha(R/'freeze_manifest.json')},indent=2))
