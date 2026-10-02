from pathlib import Path
import hashlib,json,time
P=Path(__file__).resolve().parent; model=P/'model';out={}
for f in sorted(model.iterdir()):
 if not f.is_file():continue
 h=hashlib.sha256()
 with f.open('rb') as stream:
  for chunk in iter(lambda:stream.read(8*1024**2),b''):h.update(chunk)
 metadata=model/'.cache'/'huggingface'/'download'/(f.name+'.metadata')
 cache=metadata.read_text().splitlines() if metadata.exists() else []
 item={'bytes':f.stat().st_size,'sha256':h.hexdigest(),'hf_commit':cache[0] if cache else None,'hf_etag':cache[1] if len(cache)>1 else None}
 if len(cache)>1 and len(cache[1])==64:
  item['lfs_sha256_match']=h.hexdigest()==cache[1]
  assert item['lfs_sha256_match'],f'LFS hash mismatch {f}'
 assert item['hf_commit']=='17f0b0ad64efb65d273590632833508766b2aae6',f'Revision mismatch {f}'
 out[f.name]=item
 print(f.name,item['bytes'],item.get('lfs_sha256_match','git_blob_etag'),flush=True)
(P/'model_file_manifest.json').write_text(json.dumps(out,indent=2))
print('ALL VERIFIED',flush=True)
