#!/usr/bin/env python3
"""Offline integrity and exact score recomputation for the three follow-up suites."""
from pathlib import Path
import hashlib, importlib.util, json, os, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def lines(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def run(*args,cwd=ROOT):return subprocess.run([sys.executable,*map(str,args)],cwd=cwd,env=ENV,check=True,capture_output=True,text=True)
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    protected=load(ROOT/'provenance/followup_baseline.json')
    for name,expected in protected['protected_files_sha256'].items():assert sha(ROOT/name)==expected,name
    for suite in ('clean72','attack_ablation14'):
        base=ROOT/'experiments'/suite
        export=load(base/'provenance/portable_export.json')
        for row in export['entries']:assert sha(base/row['published_artifact'])==row['published_sha256'],row['published_artifact']
        run(base/'benchmark/validate.py')
        meta=load(base/'results/predictions.metadata.json');raw=lines(base/'results/predictions.jsonl');req=lines(base/'benchmark/requests.jsonl');v=load(base/'results/verification.json')
        n=72 if suite=='clean72' else 14
        assert meta['status']=='completed' and meta['completed_at'] and meta['request_count']==len(raw)==len(req)==n
        assert [r['id'] for r in raw]==[r['id'] for r in req]==meta['request_order_ids']
        assert meta['requests_sha256']==sha(base/'benchmark/requests.jsonl')
        assert meta['runner_sha256']==sha(ROOT/'runtime/run_clef.py') and meta['source_code_sha256']==sha(ROOT/'runtime/joint_schema_model.py')
        assert meta['revision']=='17f0b0ad64efb65d273590632833508766b2aae6'
        assert v['status']=='pass' and v['complete_requests']==n and v['process_exit_code']==0
        assert sha(base/'results/predictions.jsonl') in v['artifacts_sha256'].values()
        assert sha(base/'results/predictions.metadata.json') in v['artifacts_sha256'].values()
        assert all(r['truncated'] is False for r in raw)
    for suite in ('clean','ablation'):
        run(ROOT/'qa/verify_published_followup_metrics.py',suite,'--project-root',ROOT)
    clean=module('clean_web',ROOT/'scripts/build_clean_web_data.py').build(ROOT)
    assert clean==load(ROOT/'web/data/clean72.json'),'Clean dashboard differs from verified source data'
    run(ROOT/'experiments/clean72/benchmark/independent_scorer_tests.py')
    ab=ROOT/'experiments/attack_ablation14'
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'results.json';run(ab/'benchmark/score_ablation.py','--predictions',ab/'results/predictions.jsonl','--out',out)
        assert load(out)==load(ab/'results/results.json'),'Ablation metrics differ'
    image=ROOT/'experiments/images';manifest=load(image/'package_manifest.json')
    assert len(manifest)==56
    for name,e in manifest.items():assert (image/name).stat().st_size==e['bytes'] and sha(image/name)==e['sha256'],name
    assert len([p for p in image.rglob('*') if p.is_file()])==57,'Unexpected files added to immutable image export'
    assert load(ROOT/'qa/image_export_verification.json')['status']=='pass'
    sys.path.insert(0,str(image/'scripts'))
    scorer=module('image_score',image/'scripts/score_images.py')
    fresh=scorer.score(lines(image/'benchmark/requests.jsonl'),lines(image/'benchmark/gold.jsonl'),lines(image/'results/predictions.jsonl'),lines(image/'benchmark/cases.jsonl'),lines(image/'benchmark/pairs.jsonl'))
    saved=load(image/'results/scores.json');saved.pop('provenance',None)
    assert fresh==saved,'Image metrics differ'
    run(image/'qa/test_scorer.py')
    print('PASS: original 280 text results and AMD files preserved; clean72, image90 and seven-pair ablation complete, hash-checked and scores recomputed; no model or network used')
if __name__=='__main__':main()
