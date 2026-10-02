"""Read label-free requests; fail rather than silently truncate. No model weights loaded."""
from pathlib import Path
import argparse,sys,json,hashlib,statistics
from transformers import AutoProcessor
p=argparse.ArgumentParser();p.add_argument('--model-dir',type=Path,required=True);p.add_argument('--requests',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
source=a.model_dir/'joint_schema_model.py';assert hashlib.sha256(source.read_bytes()).hexdigest()=='0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3'
sys.path.insert(0,str(a.model_dir));from joint_schema_model import encode_record
raw=a.requests.read_bytes();rows=[json.loads(x) for x in raw.splitlines()];processor=AutoProcessor.from_pretrained(a.model_dir,local_files_only=True)
items=[]
for row in rows:
 assert set(row)=={'id','request'}
 req=row['request'];assert set(req)=={'model','state','questions'}
 full=encode_record(processor.tokenizer,req,processor=processor,max_length=1_000_000)
 bounded=encode_record(processor.tokenizer,req,processor=processor,max_length=2048)
 items.append({'id':row['id'],'tokens':len(full.input_ids),'state_characters':len(json.dumps(req['state'],ensure_ascii=False)),'request_bytes':len(json.dumps(req,ensure_ascii=False).encode()),'fits_without_truncation':full.input_ids==bounded.input_ids})
out={'requests_sha256':hashlib.sha256(raw).hexdigest(),'count':len(rows),'min_tokens':min(x['tokens'] for x in items),'median_tokens':statistics.median(x['tokens'] for x in items),'max_tokens':max(x['tokens'] for x in items),'all_fit_without_truncation':all(x['fits_without_truncation'] for x in items),'max_state_characters':max(x['state_characters'] for x in items),'max_request_bytes':max(x['request_bytes'] for x in items),'model_instantiated':False,'items':items}
a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='items'},indent=2));assert out['all_fit_without_truncation']
