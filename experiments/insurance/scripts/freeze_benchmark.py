"""Freeze only after independent semantic audit and no-truncation preflight pass."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parents[1]
audit=json.loads((P/'qa/pre_inference_audit.json').read_text())
assert audit['status'].upper()=='PASS',audit['status']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert audit['source']['benchmark_sha256']==sha(P/'benchmark/benchmark.json')
assert audit['source']['requests_sha256']==sha(P/'benchmark/requests.jsonl')
pre=json.loads((P/'qa/encoding_preflight.json').read_text());assert pre['all_fit_without_truncation'] and pre['count']==60 and pre['requests_sha256']==sha(P/'benchmark/requests.jsonl')
paths=sorted([p for folder in ['benchmark','scripts'] for p in (P/folder).iterdir() if p.is_file()]+[P/'qa/pre_inference_audit.json',P/'qa/pre_inference_audit.md',P/'qa/encoding_preflight.json',P/'qa/structural_validation.json',P/'qa/model_file_manifest.json',P/'METHODOLOGY.md'])
manifest={'status':'frozen_before_inference','frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{str(p.relative_to(P)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths},'model':'Cloudflare/clef-flash','model_revision':'17f0b0ad64efb65d273590632833508766b2aae6','official_source_sha256':'0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3','inference_runner_sha256':'d06f85b922e1e4d0e905a1ddc8846aedcafa93c29f502f48b1529a36a9eb5906','primary_inference_attempts_authorized':1,'no_model_predictions_seen':True}
f=P/'qa/freeze_manifest.json';assert not f.exists();f.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'frozen_at':manifest['frozen_at'],'files':len(paths),'manifest_sha256':sha(f)},indent=2))
