#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,datetime,subprocess,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'freeze_manifest.json').exists(),'Already frozen'
assert not (R/'results/predictions.jsonl').exists(),'Inference already exists'
subprocess.run([sys.executable,str(R/'scripts/validate.py')],check=True)
a=json.loads((R/'audit/freeze_approval.json').read_text());assert a['approved_for_freeze'] is True
for path,h in a['files'].items():assert sha(R/path)==h,path
p=json.loads((R/'audit/encoding_preflight.json').read_text());assert p['requests_sha256']==sha(R/'data/requests.jsonl') and p['count']==48 and p['max_tokens']<=2048
assert json.loads((R/'audit/scorer_self_tests.json').read_text())['failed']==0
assert json.loads((R/'provenance/runtime_verified_before_run.json').read_text())['runner_sha256']=='d06f85b922e1e4d0e905a1ddc8846aedcafa93c29f502f48b1529a36a9eb5906'
paths=sorted(list((R/'data').glob('*'))+list((R/'scripts').glob('*.py'))+list((R/'scripts').glob('*.sh'))+list((R/'reference_runtime').glob('*'))+list((R/'audit').glob('pre_inference*'))+list((R/'audit').glob('correction*'))+[R/'audit/freeze_approval.json',R/'audit/encoding_preflight.json',R/'audit/scorer_self_tests.json',R/'PROTOCOL.md',R/'SOURCES.md',R/'provenance/runtime_verified_before_run.json'])
paths=sorted(set(paths)|{R/path for path in a['files']})
m={'suite_id':'minimal_pairs','version':'1.0','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_inference_before_freeze':False,'case_count':48,'pair_count':24,'fields':['action','determination'],'revision':'17f0b0ad64efb65d273590632833508766b2aae6','runtime':'CPU NF4 original6threads2048cap','files':{str(p.relative_to(R)):sha(p) for p in paths if p.is_file()}}
(R/'freeze_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'frozen':True,'files':len(m['files']),'manifest_sha256':sha(R/'freeze_manifest.json')},indent=2))
