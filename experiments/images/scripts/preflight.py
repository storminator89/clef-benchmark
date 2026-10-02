from pathlib import Path
import sys,json,hashlib,collections
from PIL import Image
from transformers import AutoProcessor
P=Path(__file__).resolve().parents[1];R=Path(sys.argv[1]) if len(sys.argv)>1 else P/'runtime'
sys.path.insert(0,str(R/'model'));from joint_schema_model import encode_record
proc=AutoProcessor.from_pretrained(R/'model',local_files_only=True)
rows=[json.loads(l) for l in (P/'benchmark/requests.jsonl').read_text().splitlines()]
results=[]
for r in rows:
 assert not set(r)&{'expected','gold','answer','label','labels'}
 assert set(r['request'])=={'model','state','questions'}
 p=P/r['image_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['image_sha256']
 req=dict(r['request']);im=Image.open(p).convert('RGB')
 if r['condition']=='blank':im=Image.new('RGB',im.size,'white')
 req['images']=[im];req['media_kwargs']={'min_pixels':65536,'max_pixels':786432}
 enc=encode_record(proc.tokenizer,req,processor=proc,max_length=4096);full=encode_record(proc.tokenizer,req,processor=proc,max_length=1000000)
 assert enc.input_ids==full.input_ids
 decoded=proc.tokenizer.decode(enc.input_ids)
 assert r['image_path'] not in decoded and r['id'] not in decoded
 results.append({'id':r['id'],'tokens':len(enc.input_ids),'grid':enc.media['image_grid_thw'].tolist(),'original_size':list(im.size),'no_truncation':True,'no_filename_or_case_id_in_model_text':True})
out={'requests':len(rows),'max_tokens':max(x['tokens'] for x in results),'min_tokens':min(x['tokens'] for x in results),'records':results}
(P/'qa/encoding_preflight.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='records'}))
