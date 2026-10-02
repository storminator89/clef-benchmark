"""Pinned official Clef vision inference. Requests+pixels only, never gold labels."""
from __future__ import annotations
import argparse, datetime, hashlib, importlib.metadata, json, os, resource, sys, time
from pathlib import Path
P=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--runtime',type=Path,default=P/'runtime')
p.add_argument('--requests',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
p.add_argument('--threads',type=int,default=6); p.add_argument('--max-pixels',type=int,default=262144)
p.add_argument('--max-length',type=int,default=4096);p.add_argument('--limit',type=int)
p.add_argument('--visual-warmup',type=Path)
a=p.parse_args()
if a.output.exists():raise FileExistsError(a.output)
a.output.parent.mkdir(parents=True,exist_ok=True)
rows=[json.loads(x) for x in a.requests.read_text().splitlines() if x.strip()]
if a.limit: rows=rows[:a.limit]
assert len({r['id'] for r in rows})==len(rows)
for r in rows:
 assert not set(r).intersection({'gold','expected','label','labels','answer'})
 assert set(r['request']) <= {'model','state','questions'}
 assert r.get('condition','image') in {'image','blank','no_image'}
import torch, psutil
from transformers import BitsAndBytesConfig
from PIL import Image
sys.path.insert(0,str(a.runtime/'model'))
source=a.runtime/'model/joint_schema_model.py'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3'
from joint_schema_model import load_release_model, encode_record, collate_records, systemone_answer
torch.manual_seed(20261002);torch.set_num_threads(a.threads);torch.set_num_interop_threads(1)
quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_compute_dtype=torch.bfloat16,bnb_4bit_use_double_quant=True,llm_int8_skip_modules=['lm_head','model.visual'])
meta={'model':'Cloudflare/clef-flash','revision':'17f0b0ad64efb65d273590632833508766b2aae6','mode':'CPU NF4 language Linear layers; original vision encoder, joint head, and output embeddings BF16','quantization':quant.to_dict(),'batch_size':1,'threads':a.threads,'max_pixels':a.max_pixels,'min_pixels':65536,'max_length':a.max_length,'requests_sha256':hashlib.sha256(a.requests.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'official_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'request_count':len(rows),'request_order_ids':[r['id'] for r in rows],'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packages':{n:importlib.metadata.version(n) for n in ['torch','transformers','bitsandbytes','pillow','huggingface-hub','safetensors']},'no_gold_loaded':True,'wrapper_language':'English official wrapper; all task content language recorded in requests'}
mp=a.output.with_suffix('.metadata.json')
def save():mp.write_text(json.dumps(meta,indent=2))
save();print(json.dumps({'event':'loading','metadata':meta}),flush=True)
t=time.perf_counter();model,processor=load_release_model(a.runtime/'model',device='cpu',dtype=torch.bfloat16,quantization_config=quant,local_files_only=True)
meta['load_seconds']=time.perf_counter()-t
assert model.language_model.get_output_embeddings().weight.dtype==torch.bfloat16
assert tuple(model.language_model.get_output_embeddings().weight.shape)==(248320,4096)
assert all(x.dtype==torch.bfloat16 for x in model.head.parameters())
meta['joint_head_dtypes']=sorted({str(x.dtype) for x in model.head.parameters()});meta['output_embedding_dtype']=str(model.language_model.get_output_embeddings().weight.dtype)
visual=model.language_model.model.visual
vision_events=[]
def vision_hook(module,args,kwargs):
 values=args[0] if args else kwargs.get('hidden_states')
 vision_events.append({'pixel_values_shape':list(values.shape) if values is not None else None,'dtype':str(values.dtype) if values is not None else None})
hook=visual.register_forward_pre_hook(vision_hook,with_kwargs=True)
meta['visual_module_class']=type(visual).__name__;meta['vision_linear_quantized_count']=sum(type(m).__name__=='Linear4bit' for m in visual.modules())
assert meta['vision_linear_quantized_count']==0,'Vision encoder must stay BF16'
assert all(v.dtype==torch.bfloat16 for v in visual.parameters())
meta['vision_parameter_dtypes']=sorted({str(v.dtype) for v in visual.parameters()})
meta['rss_after_load_bytes']=psutil.Process().memory_info().rss
save();print(json.dumps({'event':'loaded','seconds':meta['load_seconds'],'rss_bytes':meta['rss_after_load_bytes']}),flush=True)
def infer(row):
 req=dict(row['request']); condition=row.get('condition','image');image_meta=None
 if condition!='no_image':
  path=P/row['image_path'];raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  assert sha==row['image_sha256'],f'Image changed: {path}'
  im=Image.open(path).convert('RGB')
  image_meta={'sha256':sha,'original_size':list(im.size),'condition':condition}
  if condition=='blank':im=Image.new('RGB',im.size,(255,255,255))
  req['images']=[im];req['media_kwargs']={'min_pixels':65536,'max_pixels':a.max_pixels}
 t=time.perf_counter();enc=encode_record(processor.tokenizer,req,processor=processor,max_length=a.max_length)
 full=encode_record(processor.tokenizer,req,processor=processor,max_length=1000000)
 assert enc.input_ids==full.input_ids,'Truncated input'
 del full
 batch=collate_records([enc],processor.tokenizer.pad_token_id,torch.device('cpu'))
 tensor_meta={k:{'shape':list(v.shape),'dtype':str(v.dtype),'sha256':hashlib.sha256(v.contiguous().numpy().tobytes()).hexdigest() if v.dtype!=torch.bfloat16 else None} for k,v in batch.get('media',{}).items()}
 if condition!='no_image':assert 'pixel_values' in tensor_meta and 'image_grid_thw' in tensor_meta
 encode_seconds=time.perf_counter()-t
 n_before=len(vision_events); t=time.perf_counter()
 with torch.inference_mode():logits=model(batch)[0]
 sec=time.perf_counter()-t;events=vision_events[n_before:]
 assert len(events)==(condition!='no_image'),f'Expected actual vision forward: {events}'
 probs={q.question_id:dict(zip(q.option_ids,l.float().softmax(-1).tolist())) for q,l in zip(enc.questions,logits)}
 assert all(abs(sum(v.values())-1)<1e-5 and all(__import__('math').isfinite(x) and 0<=x<=1 for x in v.values()) for v in probs.values())
 answers={qid:systemone_answer(req['questions'][qid],v) for qid,v in probs.items()}
 return {'answers':answers,'probabilities_unrounded':probs,'input_tokens':len(enc.input_ids),'truncated':False,'image':image_meta,'media_tensors':tensor_meta,'image_grid_thw':batch['media']['image_grid_thw'].tolist() if condition!='no_image' else None,'vision_forward_events':events,'encode_seconds':encode_seconds,'inference_seconds':sec,'rss_bytes':psutil.Process().memory_info().rss}
# Independent technical warmup. Not a quality observation and excluded from metrics.
warm={'id':'warmup','condition':'no_image','request':{'model':'clef-flash','state':'Eine Anwendung hat einen technischen Fehler.','questions':{'decision':{'type':'choice','instructions':'Wähle die zuständige Abteilung.','criteria':{'a':'Technischer Support','b':'Buchhaltung'}}}}}
meta['warmup']=infer(warm);save()
if a.visual_warmup:
 wr=[json.loads(x) for x in a.visual_warmup.read_text().splitlines() if x.strip()][0]
 assert not set(wr).intersection({'gold','expected','label','labels','answer'})
 assert set(wr['request']) <= {'model','state','questions'}
 assert wr.get('condition','image')=='image'
 meta['visual_warmup_requests_sha256']=hashlib.sha256(a.visual_warmup.read_bytes()).hexdigest()
 meta['visual_warmup']=infer(wr);save()
 print(json.dumps({'event':'visual_warmup','seconds':meta['visual_warmup']['inference_seconds']}),flush=True)
first=None
with a.output.open('x') as f:
 for i,row in enumerate(rows,1):
  result={'id':row['id'],**infer(row)}
  if first is None:first=result
  f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
  print(json.dumps({'event':'prediction','n':i,'of':len(rows),'id':row['id'],'seconds':result['inference_seconds'],'tokens':result['input_tokens'],'rss_bytes':result['rss_bytes'],'vision_calls':len(result['vision_forward_events'])}),flush=True)
if rows:
 rep=infer(rows[0]);deltas=[abs(v-rep['probabilities_unrounded'][q][o]) for q,p in first['probabilities_unrounded'].items() for o,v in p.items()]
 meta['repeatability_probe']={'id':rows[0]['id'],'maximum_absolute_probability_delta':max(deltas),'same_answers':first['answers']==rep['answers'],'single_case_only':True}
meta['status']='completed';meta['completed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();meta['max_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
save();print(json.dumps({'event':'completed','output':str(a.output)}),flush=True)
