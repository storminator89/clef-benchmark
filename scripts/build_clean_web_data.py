#!/usr/bin/env python3
"""Build the clean72 dashboard only from a complete independently checked run."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {'anliegen_priorisierung':'Anliegen priorisieren','unterlagenabgleich':'Unterlagen abgleichen','beitragsrechnung':'Beiträge berechnen','vorgangsstand':'Vorgangsstand','rueckfrageplanung':'Nächste Rückfrage','finanzservice_routing':'Finanzservice routen'}
REVISION = '17f0b0ad64efb65d273590632833508766b2aae6'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def lines(path): return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
def require(condition, message):
    if not condition: raise ValueError(message)
def build(source=ROOT):
    base=source/'experiments/clean72';bench=base/'benchmark';results=base/'results'
    freeze=json.loads((bench/'freeze_manifest.json').read_text())
    for name,expected in freeze['sha256'].items():
        require(digest(bench/name)==expected, f'Frozen public file changed: {name}')
    cases=lines(bench/'cases.jsonl');requests=lines(bench/'requests.jsonl');raw=lines(results/'predictions.jsonl')
    meta=json.loads((results/'predictions.metadata.json').read_text());verify=json.loads((results/'verification.json').read_text())
    scores=json.loads((results/'scores.json').read_text())
    require(meta.get('status')=='completed' and meta.get('completed_at'), 'Incomplete inference run refused')
    require(meta.get('model')=='Cloudflare/clef-flash' and meta.get('revision')==REVISION, 'Unexpected model identity')
    require(meta.get('source_code_sha256')==digest(source/'runtime/joint_schema_model.py') and meta.get('runner_sha256')==digest(source/'runtime/run_clef.py'), 'Native model code or runner mismatch')
    require(meta.get('request_count')==72 and meta.get('requests_sha256')==digest(bench/'requests.jsonl'), 'Run does not match frozen requests')
    require(len(cases)==72 and len({c['id'] for c in cases})==72 and set(c['category'] for c in cases)==set(CATEGORIES), 'Wrong clean case set')
    require(len(raw)==72 and [r['id'] for r in raw]==[r['id'] for r in requests]==meta['request_order_ids'], 'Missing, duplicate, unknown, or reordered outputs')
    require(verify.get('status')=='pass' and verify.get('complete_requests')==72 and verify.get('process_exit_code')==0, 'Independent final verification missing')
    require(digest(results/'predictions.jsonl') in verify.get('artifacts_sha256',{}).values(), 'Independent QA predictions hash mismatch')
    require(digest(results/'predictions.metadata.json') in verify.get('artifacts_sha256',{}).values(), 'Independent QA metadata hash mismatch')
    spec=importlib.util.spec_from_file_location('clean_scorer',bench/'score.py');scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)
    fresh=scorer.score(cases,raw);saved={k:v for k,v in scores.items() if k not in ('outputs_file','request_sha256')}
    require(fresh==saved, 'Saved metrics differ from recomputed scores')
    require(scores.get('request_sha256')==digest(bench/'requests.jsonl'), 'Score request hash mismatch')
    byraw={r['id']:r for r in raw};byscore={r['id']:r for r in scores['case_results']}
    for c in cases:
        r=byraw[c['id']];c['result']=byscore[c['id']];c['latency_ms']=r['latency_ms'];c['input_tokens']=r['input_tokens']
        require(r.get('truncated') is False, 'Truncated output refused')
    split='german_clean_primary'
    adapted={**scores['overall'],'category_macro_f1':scores['category_macro_f1'],'per_category':scores['per_category']}
    return {'status':'completed','schema_version':1,'model':meta['model'],'revision':meta['revision'],'cases':cases,
        'suite':{'id':'clean72','label':'Alltagsnah · ohne Manipulation','primary_split':split,'splits':{split:'Deutsch · ohne Manipulation'},'categories':CATEGORIES,'n':72,'primary_n':72,'random_order_seed':freeze['request_order']['seed']},
        'scores':{'scoring_version':scores['scoring_version'],'counts':scores['counts'],'splits':{split:adapted},'paired_all_planned':{},'information_request_diagnostic':scores['information_request_diagnostic'],'by_information_status':scores['by_information_status']},
        'verification':{'status':'pass','n_present':72,'source_predictions_sha256':digest(results/'predictions.jsonl'),'independent_report_sha256':digest(results/'verification.json'),'splits':{split:{'timing':{'latency_ms':{'median':statistics.median(r['latency_ms'] for r in raw)}}}}},
        'run':{'started_at':meta['started_at'],'completed_at':meta['completed_at'],'mode':meta['mode'],'load_seconds':meta['load_seconds'],'predictions_sha256':digest(results/'predictions.jsonl')}}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=ROOT);p.add_argument('--out',type=Path,default=ROOT/'web/data/clean72.json');a=p.parse_args()
    value=build(a.source);a.out.parent.mkdir(parents=True,exist_ok=True);temporary=a.out.with_suffix('.tmp');temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temporary.replace(a.out)
    print(json.dumps({'status':value['status'],'suite':'clean72','cases':len(value['cases'])}))
if __name__=='__main__':main()
