"""Run pinned official Clef-flash with CPU NF4, preserving its original head.

Only read label-free requests. Accuracy scoring belongs in a separate process.
Official loader and encoder are not modified. No generated-text approximation.
"""
from __future__ import annotations
import argparse,datetime,hashlib,importlib.metadata,json,os,platform,resource,sys,time,traceback
from pathlib import Path
P=Path(__file__).resolve().parent
REV='17f0b0ad64efb65d273590632833508766b2aae6'
p=argparse.ArgumentParser();p.add_argument('--requests',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--limit',type=int);p.add_argument('--threads',type=int,default=6);p.add_argument('--max-length',type=int,default=2048);args=p.parse_args()
if args.output.exists(): raise FileExistsError(f'Refusing to overwrite {args.output}')
args.output.parent.mkdir(parents=True,exist_ok=True)
rows=[json.loads(line) for line in args.requests.read_text().splitlines() if line.strip()]
if args.limit:rows=rows[:args.limit]
requests=[]
seen_ids=set()
for i,row in enumerate(rows):
 if any(key in row for key in ['expected','gold','answer','label','labels']):raise ValueError('Inference file contains labels')
 request=row.get('request',row)
 request={k:request[k] for k in ('model','state','questions') if k in request}
 if 'model' not in request:request['model']='clef-flash'
 if 'state' not in request or 'questions' not in request:raise ValueError(f'Missing state/questions line {i}')
 id=row.get('id',str(i))
 if id in seen_ids:raise ValueError(f'Duplicate request id {id}')
 seen_ids.add(id)
 requests.append((id,request))
import torch,psutil
from transformers import BitsAndBytesConfig, AutoProcessor
from safetensors import safe_open
source=P/'model'/'joint_schema_model.py'
if hashlib.sha256(source.read_bytes()).digest()!=hashlib.sha256((P/'joint_schema_model.py').read_bytes()).digest(): raise ValueError('Pinned source code mismatch')
sys.path.insert(0,str(P/'model'))
from joint_schema_model import load_release_model,encode_record,collate_records,systemone_answer

torch.manual_seed(20261002);torch.set_num_threads(args.threads);torch.set_num_interop_threads(1)
quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_compute_dtype=torch.bfloat16,bnb_4bit_use_double_quant=True,llm_int8_skip_modules=['lm_head'])
meta={'model':'Cloudflare/clef-flash','revision':REV,'mode':'CPU NF4 backbone, original BF16 joint head and BF16 output embeddings','quantization':quant.to_dict(),'dtype':'bfloat16','device':'cpu','threads':args.threads,'batch_size':1,'max_length':args.max_length,'requests_sha256':hashlib.sha256(args.requests.read_bytes()).hexdigest(),'source_code_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seed':20261002,'packages':{n:importlib.metadata.version(n) for n in ['torch','transformers','bitsandbytes','accelerate','huggingface-hub','safetensors']},'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_count':len(requests),'request_order_ids':[id for id,_ in requests],'wrapper_prompt_language':'English (official release); user state and schema may be German','benchmark_requests_only_no_gold':True}
meta_path=args.output.with_suffix('.metadata.json');meta_path.write_text(json.dumps(meta,indent=2))
print(json.dumps({'event':'loading','metadata':meta}),flush=True)
processor_preflight=AutoProcessor.from_pretrained(P/'model',local_files_only=True)
del processor_preflight
t0=time.perf_counter()
model,processor=load_release_model(P/'model',device='cpu',dtype=torch.bfloat16,quantization_config=quant,local_files_only=True)
meta['load_seconds']=time.perf_counter()-t0
embedding=model.language_model.get_output_embeddings().weight
assert embedding.dtype==torch.bfloat16 and tuple(embedding.shape)==(248320,4096),f'Unexpected lexical embedding {embedding.dtype}, {embedding.shape}'
meta['weight_memory_bytes']=model.language_model.get_memory_footprint()
meta['joint_head_parameter_count']=sum(x.numel() for x in model.head.parameters())
meta['joint_head_dtypes']=sorted(set(str(x.dtype) for x in model.head.parameters()))
meta['rss_after_load_bytes']=psutil.Process().memory_info().rss
meta_path.write_text(json.dumps(meta,indent=2))
print(json.dumps({'event':'loaded','seconds':meta['load_seconds'],'rss_bytes':meta['rss_after_load_bytes']}),flush=True)

def infer(request):
 t=time.perf_counter()
 encoded=encode_record(processor.tokenizer,request,processor=processor,max_length=args.max_length)
 full=encode_record(processor.tokenizer,request,processor=processor,max_length=1_000_000)
 assert full.input_ids==encoded.input_ids,'Input would be silently truncated'
 batch=collate_records([encoded],processor.tokenizer.pad_token_id,torch.device('cpu'))
 encoded_seconds=time.perf_counter()-t
 t=time.perf_counter()
 with torch.inference_mode():logits=model(batch)[0]
 inference_seconds=time.perf_counter()-t
 probs={q.question_id:dict(zip(q.option_ids,l.float().softmax(-1).tolist())) for q,l in zip(encoded.questions,logits)}
 for qid,v in probs.items():
  assert all(0<=n<=1 for n in v.values()) and abs(sum(v.values())-1)<1e-5,f'Bad probabilities {qid}'
 answers={qid:systemone_answer(request['questions'][qid],v) for qid,v in probs.items()}
 return {'answers':answers,'probabilities_unrounded':probs,'input_tokens':len(encoded.input_ids),'truncated':False,'encode_seconds':encoded_seconds,'inference_seconds':inference_seconds,'latency_ms':inference_seconds*1000,'total_seconds':time.perf_counter()-t+encoded_seconds,'rss_bytes':psutil.Process().memory_info().rss}

warmup={'model':'clef-flash','state':'Beim Starten der Anwendung erscheint eine Fehlermeldung.','questions':{'decision':{'type':'choice','instructions':'Welche Abteilung passt zum Anliegen?','criteria':{'billing':'Rechnungen und Zahlungen','technical':'Technische Fehler'}}}}
meta['warmup']=infer(warmup);meta_path.write_text(json.dumps(meta,indent=2));print(json.dumps({'event':'warmup','result':meta['warmup']},ensure_ascii=False),flush=True)
first_prediction=None
with args.output.open('x') as out:
 for n,(id,request) in enumerate(requests,1):
  result={'id':id,**infer(request)}
  if first_prediction is None:first_prediction=result
  out.write(json.dumps(result,ensure_ascii=False)+'\n');out.flush();os.fsync(out.fileno())
  print(json.dumps({'event':'prediction','n':n,'of':len(requests),'id':id,'seconds':result['inference_seconds'],'rss_bytes':result['rss_bytes']}),flush=True)
if requests:
 repeated=infer(requests[0][1])
 deltas=[abs(v-repeated['probabilities_unrounded'][qid][option]) for qid,probs in first_prediction['probabilities_unrounded'].items() for option,v in probs.items()]
 meta['repeatability_probe']={'id':requests[0][0],'repeat_max_absolute_probability_difference':max(deltas),'same_choice':first_prediction['answers']==repeated['answers'],'single_case_only':True}
meta['completed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();meta['max_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;meta['status']='completed';meta_path.write_text(json.dumps(meta,indent=2))
print(json.dumps({'event':'completed','output':str(args.output)}),flush=True)
