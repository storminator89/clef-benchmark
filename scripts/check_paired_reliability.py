#!/usr/bin/env python3
"""Model-free release gate: immutable science, exact adapters and synthetic tests."""
from __future__ import annotations
from contextlib import redirect_stdout
import io
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from paired_reliability_common import ROOT, load, require, sha, public_file, serialize, module_from_file
import build_minimal_pairs_web_data as paired
import build_reliability_web_data as reliability

BASELINE_COMMIT = '73033f97f80fc9736313e54932e92026c8e9bd54'
BASELINE_SHA256 = '3d0e1f03a266bb1f8ea72a27c5235773263884a8da39972fc80bf433f9a5e097'


def protected_rows(root=ROOT):
    """Reconstruct the fixed public scope in memory; never publish a broad inventory."""
    root = Path(root)
    paths = set()
    prefixes = ('benchmark', 'finance_benchmark', 'experiments', 'results', 'runtime',
                'schemas', 'examples', 'licenses', 'web/data')
    additions = ('experiments/minimal_pairs/', 'experiments/probability_reliability/',
                 'web/data/minimal_pairs.json', 'web/data/reliability.json',
                 # New independently gated stage only; the original 388-file digest is unchanged.
                 'experiments/multidoc48/', 'experiments/jev_comparison/', 'web/data/multidoc.json')
    for prefix in prefixes:
        for path in (root / prefix).rglob('*'):
            name = path.relative_to(root).as_posix()
            if (path.is_file() or path.is_symlink()) and '__pycache__' not in path.parts and not name.startswith(additions):
                paths.add(name)
    paths.update(load(root / 'provenance/clarification_baseline.json')['protected_files_sha256'])
    return [{'path': name, 'sha256': sha(public_file(root, name))} for name in sorted(paths)]


def verify_protected_files(root=ROOT):
    root = Path(root)
    path = public_file(root, 'provenance/paired_reliability_baseline.json')
    require(sha(path) == BASELINE_SHA256, 'Previous-science baseline manifest changed')
    baseline = load(path)
    require(baseline['baseline_commit'] == BASELINE_COMMIT and baseline['schema_version'] == 2,
            'Wrong previous-science baseline')
    rows = protected_rows(root)
    encoded = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    require(len(rows) == baseline['file_count']
            and sum((root / r['path']).stat().st_size for r in rows) == baseline['total_bytes']
            and hashlib.sha256(encoded).hexdigest() == baseline['aggregate_sha256'],
            'Previous scientific artifact set or bytes changed')
    return len(rows)


def verify_retained_source_lineage(root=ROOT):
    """Every analytical input is an exact copy of already retained public science."""
    root = Path(root)
    verify_protected_files(root)
    known = {row['sha256'] for row in protected_rows(root)}
    known.update(load(root / 'experiments/minimal_pairs/FILE_SHA256.json').values())
    count = 0
    source = root / 'experiments/probability_reliability'
    for suite in load(source / 'SOURCE_INVENTORY.json')['suites']:
        require(suite['scientific_inputs_outputs_changed'] is False, 'Scientific source copy was changed')
        for name, digest in suite['files'].items():
            require(digest in known, f'Reliability source has no retained public-byte lineage: {suite["suite_id"]}/{name}')
            require(sha(public_file(source, f'sources/{suite["suite_id"]}/{name}')) == digest,
                    'Retained reliability source changed')
            count += 1
    return count


def verify_data_files(root=ROOT):
    root = Path(root)
    for name, builder, directory in [('minimal_pairs', paired.build, 'minimal_pairs'),
                                     ('reliability', reliability.build, 'probability_reliability')]:
        derived = builder(root / 'experiments' / directory)
        require(serialize(derived) == (root / 'web/data' / (name + '.json')).read_bytes(),
                f'Deterministic {name} UI data differs from verified raw outputs')


def run_synthetic_and_scorer_checks():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='clef-paired-offline-') as td:
        paircopy = Path(td) / 'minimal_pairs'
        reliabilitycopy = Path(td) / 'probability_reliability'
        shutil.copytree(paired.SOURCE, paircopy)
        shutil.copytree(reliability.SOURCE, reliabilitycopy)
        commands = [
            [paircopy / 'scripts/validate.py'],
            [paircopy / 'scripts/test_scorer.py'],
            [paircopy / 'scripts/test_independent_result_check.py', '--root', paircopy],
            [reliabilitycopy / 'scripts/test_metrics.py'],
            [reliabilitycopy / 'audit/test_independent_metrics.py'],
        ]
        for args in commands:
            completed = subprocess.run([sys.executable, *map(str, args)], env=env, capture_output=True, text=True)
            require(completed.returncode == 0, f'Offline synthetic check failed: {Path(args[0]).name}\n{completed.stdout}\n{completed.stderr}')
        # Export is a copy of the reviewed allowlist, never a broad directory scan.
        exported = Path(td) / 'public_export'
        subprocess.run([sys.executable, str(paircopy / 'scripts/export_public.py'),
                        '--destination', str(exported)], env=env, check=True, capture_output=True)
        paired.verify_manifest(exported, paired.EXPORT_MANIFEST_SHA256, paired.PUBLIC_FILE_COUNT - 1)
        # Recompute prose assertions after scope-only editorial curation.
        subprocess.run([sys.executable, str(reliabilitycopy / 'audit/audit_reports.py')],
                       env=env, check=True, capture_output=True)
        require((reliabilitycopy / 'audit/report_review.json').read_bytes()
                == (reliability.SOURCE / 'audit/report_review.json').read_bytes(),
                'Reliability report review differs')
        subprocess.run([sys.executable, str(paircopy / 'scripts/build_reports.py')],
                       env=env, check=True, capture_output=True)
        for name in ('REPORT.md', 'ERRORS.md'):
            require((paircopy / name).read_bytes() == (paired.SOURCE / name).read_bytes(),
                    f'Paired report reproduction differs: {name}')
        scorer = module_from_file('paired_frozen_scorer', paircopy / 'scripts/score.py')
        with redirect_stdout(io.StringIO()):
            scorer.score(paircopy / 'data', paircopy / 'results')
        for name in ('summary.json', 'case_scores.jsonl', 'pair_scores.jsonl', 'errors.jsonl', 'pair_errors.jsonl'):
            require((paircopy / 'results' / name).read_bytes() == (paired.SOURCE / 'results' / name).read_bytes(),
                    f'Frozen paired scorer differs: {name}')
    return len(commands)


def main():
    protected = verify_protected_files()
    verify_data_files()
    lineage = verify_retained_source_lineage()
    synthetic = run_synthetic_and_scorer_checks()
    # Every check above must leave the archived experiment and previous science intact.
    paired.verify_manifest(paired.SOURCE, paired.EXPORT_MANIFEST_SHA256, paired.PUBLIC_FILE_COUNT - 1)
    reliability.verify_manifest(reliability.SOURCE, reliability.EXPORT_MANIFEST_SHA256, reliability.PUBLIC_FILE_COUNT - 1)
    verify_protected_files()
    print(f'PASS: {protected} prior scientific artifacts unchanged; {paired.PUBLIC_FILE_COUNT} paired and {reliability.PUBLIC_FILE_COUNT} reliability files pinned; '
          f'{lineage} retained source copies; native paired and dual reliability recomputation; '
          f'{synthetic} offline synthetic suites; deterministic UI bytes; no inference')

if __name__ == '__main__': main()
