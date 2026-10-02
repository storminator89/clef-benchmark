#!/usr/bin/env python3
"""One-way pre-inference freeze; requires independent approval and exact encoding."""
import json,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'freeze_manifest.json').exists(),'Already frozen'
assert not (R/'results/predictions.jsonl').exists(),'Benchmark inference already exists'
a=json.loads((R/'audit/freeze_approval.json').read_text())
assert a['approved_for_freeze'] is True
for rel,h in a['files'].items():assert sha(R/rel)==h,rel
p=json.loads((R/'audit/encoding_preflight.json').read_text())
assert p['requests_sha256']==sha(R/'data/requests.jsonl') and p['count']==80 and p['max_tokens']<=2048
paths=sorted(list((R/'data').glob('*'))+list((R/'scripts').glob('*.py'))+list((R/'scripts').glob('*.sh'))+list((R/'reference_runtime').glob('*'))+list((R/'audit').glob('pre_inference*'))+[R/'audit/freeze_approval.json',R/'audit/encoding_preflight.json',R/'audit/scorer_self_tests.json',R/'SOURCES.md'])
manifest={'suite':'bank-support','scope':'Custom German retail-bank support pilot; synthetic, purposively stratified, not BANKING77','frozen_at_host_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'case_count':80,'fields':['intent','priority','next_step'],'model_inference_before_freeze':False,'requests_label_free':True,'order_seed':20261002,'revision':'17f0b0ad64efb65d273590632833508766b2aae6','runtime':'original CPU NF4 backbone / BF16 original joint head and output embedding / 2048 cap / six threads','files':{str(p.relative_to(R)):sha(p) for p in paths if p.is_file()}}
(R/'freeze_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(manifest,indent=2))
