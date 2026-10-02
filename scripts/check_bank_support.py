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


def main():
    baseline = load(ROOT/'provenance/bank_support_baseline.json')
    assert baseline['baseline_commit'] == '1b899c5900a74ad0406bd6a25ad2ab87eec2e26d'
    for name, expected in baseline['protected_files_sha256'].items():
        assert sha(ROOT/name) == expected, f'Pre-bank historical artifact changed: {name}'
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
    print('PASS: bank80 final QA/file hashes, all240 field decisions, exact-case and safety metrics, both scorers, live request limits, deterministic UI rebuild; all212 pre-bank data/runtime artifacts unchanged; no model loaded')


if __name__ == '__main__':
    main()
