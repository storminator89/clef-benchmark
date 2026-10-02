#!/usr/bin/env python3
"""Model-free multidoc48 release gate: native re-scoring and deterministic display."""
from pathlib import Path
import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from build_multidoc_web_data import build, ROOT, SOURCE, FREEZE_SHA256, load, sha
from paired_reliability_common import module_from_file, serialize, public_file, require


BASELINE_COMMIT = 'ae751e09ef383d0fca7126d35f19fc8670b80b08'
BASELINE_SHA256 = '77a201e464655fa4be09485fb949ef2470c7258beb8b56f88cb30ace1c5895b8'


def protected_rows(root=ROOT):
    """Reconstruct the prior scientific scope without publishing a broad inventory."""
    root = Path(root); paths = set()
    prefixes = ('benchmark', 'finance_benchmark', 'experiments', 'results', 'runtime',
                'schemas', 'examples', 'licenses', 'web/data')
    additions = ('experiments/multidoc48/', 'experiments/jev_comparison/', 'web/data/multidoc.json')
    for prefix in prefixes:
        for path in (root / prefix).rglob('*'):
            name = path.relative_to(root).as_posix()
            if (path.is_file() or path.is_symlink()) and '__pycache__' not in path.parts and not name.startswith(additions):
                paths.add(name)
    paths.update(load(root / 'provenance/clarification_baseline.json')['protected_files_sha256'])
    return [{'path': name, 'sha256': sha(public_file(root, name))} for name in sorted(paths)]


def verify_protected_files(root=ROOT):
    root = Path(root)
    path = public_file(root, 'provenance/multidoc_baseline.json')
    require(sha(path) == BASELINE_SHA256, 'Previous-science baseline changed')
    baseline = load(path)
    require(baseline['schema_version'] == 2 and baseline['baseline_commit'] == BASELINE_COMMIT,
            'Wrong previous-science baseline')
    rows = protected_rows(root)
    encoded = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    require(len(rows) == baseline['file_count']
            and sum((root / r['path']).stat().st_size for r in rows) == baseline['total_bytes']
            and hashlib.sha256(encoded).hexdigest() == baseline['aggregate_sha256'],
            'Previous scientific artifact set or bytes changed')
    return len(rows)


def main():
    protected = verify_protected_files()
    data = build()
    assert serialize(data) == (ROOT / 'web/data/multidoc.json').read_bytes(), 'Multidoc UI differs from native evidence'
    sys.path.insert(0, str(ROOT))
    import server
    for row in load(SOURCE / 'data/requests.jsonl', True):
        request = row['request']
        assert server.validate_request({k: v for k, v in request.items() if k != 'model'}) == request
    # Archived self-tests can emit their test reports: isolate all such writes.
    with tempfile.TemporaryDirectory(prefix='clef-multidoc-offline-') as directory:
        copied = Path(directory) / 'suite'
        shutil.copytree(SOURCE, copied)
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        exported = Path(directory) / 'public_export'
        subprocess.run([sys.executable, str(SOURCE / 'scripts/export_public.py'), '--destination', str(exported)],
                       check=True, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert serialize(build(exported)) == serialize(data), 'Public export changed admitted science'
        for script in ('validate.py', 'test_scorer.py', 'test_reports.py'):
            subprocess.run([sys.executable, str(copied / 'scripts' / script)], check=True,
                           env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        report = Path(directory) / 'independent_self_test.json'
        subprocess.run([sys.executable, str(copied / 'audit/independent_score_check.py'), '--self-test',
                        '--primary-scorer', str(copied / 'scripts/score.py'), '--report', str(report)],
                       check=True, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        tests = load(report)
        assert tests['status'] == 'passed' and tests['primary_comparison_mismatches'] == []
        assert tests['model_loaded'] is False and tests['inference_performed'] is False
        scorer = module_from_file('multidoc_primary_rescore', copied / 'scripts/score.py')
        scorer.score(copied / 'data', copied / 'results')
        for name in ('summary.json', 'case_scores.jsonl', 'errors.jsonl'):
            assert (copied / 'results' / name).read_bytes() == (SOURCE / 'results' / name).read_bytes(), name
    assert sha(SOURCE / 'freeze_manifest.json') == FREEZE_SHA256
    for name, digest in load(SOURCE / 'freeze_manifest.json')['files'].items():
        assert sha(SOURCE / name) == digest, f'Frozen science changed: {name}'
    verify_protected_files()
    print(f'PASS: {protected} previous scientific files unchanged; multidoc48 {tests["check_count"]} independent synthetic scenarios; native byte-exact re-score; '
          '61 frozen files preserved; 48 complete inputs/vectors and all 24 errors; deterministic UI; no model loaded')

if __name__ == '__main__': main()
