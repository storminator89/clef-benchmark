#!/usr/bin/env python3
"""Encode every label-free request twice; never load or run a model."""
import os,sys,json,hashlib,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();os.environ['HF_HUB_OFFLINE']='1'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(a.runtime/'model'))
from joint_schema_model import encode_record
from transformers import AutoProcessor
proc=AutoProcessor.from_pretrained(a.runtime/'model',local_files_only=True)
rows=[json.loads(x) for x in (ROOT/'data/requests.jsonl').read_text().splitlines()]
encoded=[]
for r in rows:
 full=encode_record(proc.tokenizer,r['request'],processor=proc,max_length=1000000)
 capped=encode_record(proc.tokenizer,r['request'],processor=proc,max_length=2048)
 assert full.input_ids==capped.input_ids,f'Truncation: {r["id"]} {len(full.input_ids)}'
 encoded.append({'id':r['id'],'input_tokens':len(full.input_ids),'state_characters':len(r['request']['state']),'request_bytes':len(json.dumps(r['request'],ensure_ascii=False).encode()),'truncated':False})
result={'purpose':'Tokenizer-only pre-inference shape/cap check, no model loaded or outputs generated','requests_sha256':hashlib.sha256((ROOT/'data/requests.jsonl').read_bytes()).hexdigest(),'count':len(rows),'min_tokens':min(x['input_tokens'] for x in encoded),'max_tokens':max(x['input_tokens'] for x in encoded),'max_state_characters':max(x['state_characters'] for x in encoded),'max_request_bytes':max(x['request_bytes'] for x in encoded),'cases':encoded}
(ROOT/'audit/encoding_preflight.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
