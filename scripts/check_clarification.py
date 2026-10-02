#!/usr/bin/env python3
"""Model-free clarification gate, including byte preservation of all earlier science."""
from pathlib import Path
import sys
import os
import shutil
import subprocess
import tempfile
from build_clarification_web_data import build, load, sha, ROOT, SOURCE


PUBLIC_METADATA_FILES = frozenset({
    'experiments/bank-support/provenance/portable_export.json',
    'experiments/bank-support/FILE_SHA256.json',
})


def verify_protected_files(root=ROOT):
    baseline = load(root / 'provenance/clarification_baseline.json')
    assert baseline['baseline_commit'] == 'b084dc17e8e285e0eef20e00af07fae76d371ec2'
    evolution = load(root / 'provenance/public_curation_evolution.json')
    assert evolution['schema_version'] == 1 and evolution['baseline_commit'] == baseline['baseline_commit']
    changes = evolution['changes']
    assert set(changes) == PUBLIC_METADATA_FILES, 'Unexpected public metadata evolution scope'
    protected = baseline['protected_files_sha256']
    for name, change in changes.items():
        assert set(change) == {'from_sha256', 'to_sha256', 'reason'}
        assert change['from_sha256'] == protected[name] and change['from_sha256'] != change['to_sha256']
        assert isinstance(change['reason'], str) and change['reason'].strip()
    for name, expected in protected.items():
        current = changes[name]['to_sha256'] if name in changes else expected
        assert sha(root / name) == current, f'Previous benchmark/runtime changed: {name}'
    return len(protected), len(changes)


def main():
    protected_count, evolved_count = verify_protected_files()
    assert build() == load(ROOT / 'web/data/clarification.json'), 'Clarification UI differs from verified native outputs'
    sys.path.insert(0, str(ROOT))
    import server
    for row in load(SOURCE / 'data/requests.jsonl', True):
        request = row['request']
        assert server.validate_request({k: v for k, v in request.items() if k != 'model'}) == request
    with tempfile.TemporaryDirectory(prefix='clef-clarification-offline-') as td:
        copied = Path(td) / 'suite'; shutil.copytree(SOURCE, copied)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for script in ('validate.py', 'test_scorer.py', 'test_independent_result_check.py'):
            subprocess.run([sys.executable, str(copied / 'scripts' / script)], check=True, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        spec = __import__('importlib.util', fromlist=['util']).spec_from_file_location('clarification_scorer', copied / 'scripts/score.py')
        scorer = __import__('importlib.util', fromlist=['util']).module_from_spec(spec); spec.loader.exec_module(scorer)
        scorer.score(copied / 'data', copied / 'results')
        for name in ('summary.json', 'case_scores.jsonl', 'errors.jsonl'):
            assert (copied / 'results' / name).read_bytes() == (SOURCE / 'results' / name).read_bytes(), name
    print(f'PASS: clarification72 independent recomputation, exact probability vectors, request limits, deterministic UI; {protected_count - evolved_count} previous files unchanged plus {evolved_count} explicitly bounded public-metadata redactions; no model loaded')

if __name__ == '__main__': main()
