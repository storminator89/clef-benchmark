#!/usr/bin/env python3
"""Local native tokenizer/encoder only; no weights, model instantiation or inference."""
from pathlib import Path
import argparse, sys, json, hashlib, statistics
from transformers import AutoProcessor
D=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,default=D.parents[2]/'runtime');ap.add_argument('--out',type=Path,default=D/'encoding_preflight.json');args=ap.parse_args()
if (D/'freeze_manifest.json').exists() and args.out.parent.resolve()==D.resolve():raise SystemExit('Frozen benchmark: use an output outside this directory')
source=args.runtime/'model/joint_schema_model.py'
expected='0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
sys.path.insert(0,str(args.runtime/'model'))
from joint_schema_model import encode_record
raw=(D/'requests.jsonl').read_bytes();rows=[json.loads(x) for x in raw.splitlines()]
processor=AutoProcessor.from_pretrained(args.runtime/'model',local_files_only=True)
lengths=[]
for row in rows:
    request=row['request'];assert set(request)=={'model','state','questions'}
    full=encode_record(processor.tokenizer,request,processor=processor,max_length=1_000_000)
    bounded=encode_record(processor.tokenizer,request,processor=processor,max_length=2048)
    lengths.append({'id':row['id'],'tokens':len(full.input_ids),'fits_without_truncation':full.input_ids==bounded.input_ids})
output={'requests_sha256':hashlib.sha256(raw).hexdigest(),'native_encoder_sha256':expected,'count':len(rows),'min_tokens':min(x['tokens'] for x in lengths),'median_tokens':statistics.median(x['tokens'] for x in lengths),'max_tokens':max(x['tokens'] for x in lengths),'all_fit_without_truncation':all(x['fits_without_truncation'] for x in lengths),'max_input_tokens':2048,'model_instantiated':False,'model_inference_performed':False,'local_files_only':True,'items':lengths}
args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k!='items'},indent=2))
