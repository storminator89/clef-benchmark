#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'freeze_manifest.json').exists(), 'Already frozen'
assert not (R/'results/predictions.jsonl').exists(),'Inference exists'
a=json.loads((R/'audit/freeze_approval.json').read_text());assert a['approved_for_freeze'] is True
for path,h in a['files'].items():assert sha(R/path)==h,path
p=json.loads((R/'audit/encoding_preflight.json').read_text());assert p['requests_sha256']==sha(R/'data/requests.jsonl') and p['count']==72 and p['max_tokens']<=2048
assert json.loads((R/'audit/scorer_self_tests.json').read_text())['failed']==0
paths=sorted(list((R/'data').glob('*'))+list((R/'scripts').glob('*.py'))+list((R/'scripts').glob('*.sh'))+list((R/'reference_runtime').glob('*'))+list((R/'audit').glob('pre_inference*'))+[R/'audit/freeze_approval.json',R/'audit/encoding_preflight.json',R/'audit/scorer_self_tests.json',R/'PROTOCOL.md',R/'SOURCES.md',R/'provenance/runtime_verified_before_run.json'])
m={'suite_id':'clarification','version':'1.0','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_inference_before_freeze':False,'case_count':72,'fields':['action','determination'],'revision':'17f0b0ad64efb65d273590632833508766b2aae6','runtime':'CPU NF4 original6threads2048cap','files':{str(p.relative_to(R)):sha(p) for p in paths if p.is_file()}}
(R/'freeze_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'frozen':True,'files':len(m['files']),'manifest_sha256':sha(R/'freeze_manifest.json')},indent=2))
