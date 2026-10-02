#!/usr/bin/env python3
import hashlib,json,argparse,importlib.metadata,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);a=p.parse_args()
expected=json.loads((R/'reference_runtime/model_file_manifest.json').read_text());facts={}
for name,e in expected.items():
 f=a.runtime/'model'/name;h=hashlib.sha256()
 with f.open('rb') as stream:
  for b in iter(lambda:stream.read(8*1024**2),b''):h.update(b)
 assert h.hexdigest()==e['sha256'] and f.stat().st_size==e['bytes'],name
 facts[name]={'sha256':h.hexdigest(),'bytes':f.stat().st_size}
for name in ['run_clef.py','joint_schema_model.py']:
 assert hashlib.sha256((a.runtime/name).read_bytes()).digest()==hashlib.sha256((R/'reference_runtime'/name).read_bytes()).digest(),name
result={'status':'passed','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':'17f0b0ad64efb65d273590632833508766b2aae6','model_files':facts,'runner_sha256':hashlib.sha256((a.runtime/'run_clef.py').read_bytes()).hexdigest(),'packages':{n:importlib.metadata.version(n) for n in ['torch','transformers','bitsandbytes','accelerate','huggingface-hub','safetensors']},'model_not_loaded':True}
(R/'provenance/runtime_verified_before_run.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='model_files'},indent=2))
