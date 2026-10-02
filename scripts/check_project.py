#!/usr/bin/env python3
"""Check reproducibility without inference, downloads, or tracked-file changes."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

def run(*args, cwd=ROOT):
    subprocess.run([sys.executable, *map(str, args)], cwd=cwd, env=ENV, check=True)

def check_run_lineage(requests_path, predictions_path, metadata_path):
    metadata = json.loads(metadata_path.read_text())
    request_rows = [json.loads(line) for line in requests_path.read_text().splitlines() if line.strip()]
    prediction_rows = [json.loads(line) for line in predictions_path.read_text().splitlines() if line.strip()]
    assert metadata['status'] == 'completed', 'Run metadata is incomplete'
    assert metadata['requests_sha256'] == hashlib.sha256(requests_path.read_bytes()).hexdigest(), 'Run used different requests'
    assert metadata['runner_sha256'] == hashlib.sha256((ROOT / 'runtime/run_clef.py').read_bytes()).hexdigest(), 'Run used a different runner'
    assert metadata['source_code_sha256'] == hashlib.sha256((ROOT / 'runtime/joint_schema_model.py').read_bytes()).hexdigest(), 'Run used different official model code'
    model_manifest = json.loads((ROOT / 'runtime/model_file_manifest.json').read_text())
    assert {entry['hf_commit'] for entry in model_manifest.values()} == {metadata['revision']}, 'Model revision mismatch'
    request_ids = [row['id'] for row in request_rows]
    assert metadata['request_order_ids'] == request_ids == [row['id'] for row in prediction_rows], 'Request/prediction order mismatch'
    assert metadata['request_count'] == len(request_ids)

def compare_scores(saved, fresh):
    saved = json.loads(saved.read_text())
    fresh = json.loads(fresh.read_text())
    # This provenance field is explicitly sanitized for public portability.
    saved.pop('outputs_file', None)
    fresh.pop('outputs_file', None)
    assert saved == fresh, 'Published score report differs from recomputed metrics'

freeze = json.loads((ROOT / 'benchmark/freeze_manifest.json').read_text())
for name, digest in freeze['sha256'].items():
    assert hashlib.sha256((ROOT / 'benchmark' / name).read_bytes()).hexdigest() == digest, name
manifest = json.loads((ROOT / 'provenance/curation_manifest.json').read_text())
for entry in manifest['entries']:
    path = ROOT / entry['published_artifact']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['published_sha256'], entry['published_artifact']
run('benchmark/validate.py')
run('qa/check_benchmark_integrity.py')
run('qa/test_score_v1_1.py')
with tempfile.TemporaryDirectory(prefix='clef-rebuild-') as temporary:
    copied = Path(temporary)
    shutil.copy2(ROOT / 'benchmark/build_benchmark.py', copied / 'build_benchmark.py')
    run(copied / 'build_benchmark.py', cwd=copied)
    for name in ['cases.jsonl', 'diagnostic_cases.jsonl', 'requests.jsonl', 'gold.jsonl', 'pairs.jsonl', 'policies.json', 'design_summary.json']:
        assert hashlib.sha256((copied / name).read_bytes()).hexdigest() == freeze['sha256'][name], f'Deterministic reconstruction differs: {name}'
results = ROOT / 'results'
required = ['predictions.jsonl', 'run_metadata.json', 'scores_frozen_v1_0.json', 'scores_robust_v1_1.json', 'verification.json']
if not all((results / name).is_file() for name in required):
    raise SystemExit('Final results are incomplete; package is not ready for publication')
check_run_lineage(ROOT / 'benchmark/requests.jsonl', results / 'predictions.jsonl', results / 'run_metadata.json')
with tempfile.TemporaryDirectory(prefix='clef-verify-') as temporary:
    copied = Path(temporary)
    for name in ['benchmark', 'qa']:
        shutil.copytree(ROOT / name, copied / name, ignore=shutil.ignore_patterns('__pycache__'))
    run(copied / 'qa/verify_final_scores.py', '--predictions', results / 'predictions.jsonl', '--metadata', results / 'run_metadata.json', '--out', copied / 'verification.json')
    for name in ['scores_frozen_v1_0.json', 'scores_robust_v1_1.json']:
        compare_scores(results / name, copied / 'qa' / name)
    assert json.loads((results / 'verification.json').read_text()) == json.loads((copied / 'verification.json').read_text()), 'Independent verification differs'
finance = ROOT / 'finance_benchmark'
if (finance / 'freeze_manifest.json').is_file():
    finance_freeze = json.loads((finance / 'freeze_manifest.json').read_text())
    for name, digest in finance_freeze['sha256'].items():
        assert hashlib.sha256((finance / name).read_bytes()).hexdigest() == digest, f'finance/{name}'
    run('finance_benchmark/validate.py')
    finance_results = results / 'finance'
    required_finance = ['predictions.jsonl', 'run_metadata.json', 'scores.json', 'verification.json']
    if not all((finance_results / name).is_file() for name in required_finance):
        raise SystemExit('Finance results are incomplete; package is not ready for publication')
    check_run_lineage(finance / 'requests.jsonl', finance_results / 'predictions.jsonl', finance_results / 'run_metadata.json')
    with tempfile.TemporaryDirectory(prefix='clef-finance-verify-') as temporary:
        copied = Path(temporary)
        for name in ['finance_benchmark', 'qa']:
            shutil.copytree(ROOT / name, copied / name, ignore=shutil.ignore_patterns('__pycache__'))
        run(copied / 'qa/verify_finance_scores.py', '--predictions', finance_results / 'predictions.jsonl', '--metadata', finance_results / 'run_metadata.json', '--out', copied / 'verification.json')
        compare_scores(finance_results / 'scores.json', copied / 'qa/finance_scores.json')
        assert json.loads((finance_results / 'verification.json').read_text()) == json.loads((copied / 'verification.json').read_text()), 'Independent finance verification differs'
with tempfile.TemporaryDirectory(prefix='clef-summary-verify-') as temporary:
    copied = Path(temporary)
    for name in ['results', 'qa', 'finance_benchmark']:
        shutil.copytree(ROOT / name, copied / name, ignore=shutil.ignore_patterns('__pycache__'))
    (copied / 'scripts').mkdir()
    for script, summary in [('summarize_results.py', 'results/summary.json'), ('summarize_finance_results.py', 'results/finance/summary.json')]:
        shutil.copy2(ROOT / 'scripts' / script, copied / 'scripts' / script)
        run(copied / 'scripts' / script, cwd=copied)
        assert (ROOT / summary).read_bytes() == (copied / summary).read_bytes(), f'Post-hoc summary differs: {summary}'
print('PASS: frozen inputs, public provenance, reconstruction, scorer tests, completed runs, independent metrics and summaries for both suites')
