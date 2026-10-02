#!/usr/bin/env python3
"""Offline gate for the separate bank suite, preserving every earlier experiment."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

from build_bank_web_data import build, load, sha

ROOT = Path(__file__).resolve().parents[1]
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, env=ENV,
                          capture_output=True, text=True, check=True)


FEATURE_RUNTIME_FILES = frozenset({
    'runtime/check_backend.py', 'runtime/device_profiles.py', 'runtime/live_adapter.py',
})


def verify_protected_files(root=ROOT):
    baseline = load(root/'provenance/bank_support_baseline.json')
    assert baseline['baseline_commit'] == '1b899c5900a74ad0406bd6a25ad2ab87eec2e26d'
    evolution = load(root/'provenance/bank_feature_evolution.json')
    assert evolution['schema_version'] == 1
    assert evolution['baseline_commit'] == baseline['baseline_commit']
    assert evolution['bank_release_tree'] == '915e65b952241d028e88b29941cb2ff9440e46d9'
    changes = evolution['changes']
    assert isinstance(changes, dict) and set(changes) == FEATURE_RUNTIME_FILES, 'Unexpected feature evolution scope'
    protected = baseline['protected_files_sha256']
    for name, change in changes.items():
        assert set(change) == {'from_sha256', 'to_sha256', 'reason'}, name
        assert change['from_sha256'] == protected[name], name
        assert change['to_sha256'] != change['from_sha256'], name
        assert isinstance(change['reason'], str) and change['reason'].strip(), name
    for name, expected in protected.items():
        current = changes[name]['to_sha256'] if name in changes else expected
        assert sha(root/name) == current, f'Pre-bank historical artifact changed: {name}'
    return len(protected), len(changes)


def main():
    protected_count, evolved_count = verify_protected_files()
    bank = ROOT/'experiments/bank-support'
    fresh = build(bank)
    assert fresh == load(ROOT/'web/data/bank-support.json'), 'Bank dashboard differs from admitted raw results'
    sys.path.insert(0, str(ROOT))
    import server
    for row in load(bank/'data/requests.jsonl', True):
        native = row['request']
        assert server.validate_request({k: v for k, v in native.items() if k != 'model'}) == native
    run(bank/'scripts/validate.py')
    with tempfile.TemporaryDirectory(prefix='clef-bank-offline-') as td:
        root = Path(td)
        outputs = root/'scored'; outputs.mkdir()
        shutil.copy2(bank/'results/predictions.jsonl', outputs/'predictions.jsonl')
        run(bank/'scripts/score.py', '--data', bank/'data', '--results', outputs)
        for filename in ('summary.json', 'errors.jsonl'):
            assert (outputs/filename).read_bytes() == (bank/'results'/filename).read_bytes(), f'Deterministic scorer differs: {filename}'
        copied = root/'independent'; shutil.copytree(bank, copied)
        run(copied/'scripts/independent_score_check.py', '--root', copied, '--self-test')
        run(copied/'scripts/independent_score_check.py', '--root', copied)
        checked = load(copied/'audit/independent_score_check.json')
        saved = load(bank/'audit/independent_score_check.json')
        assert checked['passed'] is True and checked['mismatches'] == []
        for key in ('independently_recomputed', 'independently_recomputed_errors', 'prediction_count'):
            assert checked[key] == saved[key], f'Independent repeated check differs: {key}'
    print(f'PASS: bank80 final QA/file hashes, all240 field decisions, exact-case and safety metrics, both scorers, live request limits, deterministic UI rebuild; unchanged baseline protects {protected_count - evolved_count} byte-identical historical artifacts plus {evolved_count} exact bounded runtime evolutions; no model loaded')


if __name__ == '__main__':
    main()
