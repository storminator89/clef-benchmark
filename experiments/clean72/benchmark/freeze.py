#!/usr/bin/env python3
"""Freeze the audited benchmark once; never launches model inference."""
import datetime, hashlib, json, pathlib, subprocess, sys
D=pathlib.Path(__file__).resolve().parent
manifest=D/'freeze_manifest.json'
if manifest.exists():raise SystemExit('Already frozen; use validate.py to verify, never silently refreeze.')
required=['README.md','build_benchmark.py','score.py','validate.py','check_encoding.py','freeze.py','cases.jsonl','requests.jsonl','gold.jsonl','policies.json','design_summary.json','encoding_preflight.json','pre_inference_review.jsonl','pre_inference_review.md','independent_scorer_tests.py','independent_scorer_checks.json']
for name in required:
    if not (D/name).is_file():raise SystemExit('Required artifact missing: '+name)
subprocess.run([sys.executable,str(D/'validate.py')],check=True)
enc=json.loads((D/'encoding_preflight.json').read_text())
assert enc['all_fit_without_truncation'] and not enc['model_instantiated'] and not enc['model_inference_performed']
assert not any(D.glob('*predictions*')) and not any(D.glob('*scores*.json'))
out={'benchmark_version':'clean-realistic-de-v1','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'),'status':'frozen_before_first_clean_benchmark_inference','clean_case_authoring_completed_before_any_clean_model_outputs':True,'review':'Independent AI reviewer derived every label without model predictions, checked all 72 cases for ambiguity, naturalness, complexity and absence of prompt manipulation, verified arithmetic and metadata. Not human expert adjudication. See review files for limitations.','inference_authorization':'No inference performed in preparation. The separate text run requires the image run to finish first.','counts':{'total':72,'german_clean_primary':72,'sufficient':50,'missing_or_unresolved':22,'categories':6,'cases_per_category':12,'attacks':0,'translation_controls':0},'request_order':{'method':'random.Random(seed).shuffle','seed':2026100204},'model_contract':{'model':'clef-flash','question_type':'choice','question_name':'decision','language':'de','schema_language':'de','max_input_tokens':2048,'encoder_preflight_max_tokens':enc['max_tokens'],'model_instantiated':False},'scoring':{'primary':'choice_accuracy_all_planned over all 72; missing/runtime-error/invalid-label outputs are incorrect','scorepooling':'Separate from prior benchmarks; no pooled overall metric and no causal manipulation-effect claim'},'sha256':{name:hashlib.sha256((D/name).read_bytes()).hexdigest() for name in required}}
manifest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(D/'validate.py')],check=True)
print(json.dumps({'frozen_at_utc':out['frozen_at_utc'],'files':len(required),'requests_sha256':out['sha256']['requests.jsonl'],'gold_sha256':out['sha256']['gold.jsonl']},indent=2))
