#!/usr/bin/env python3
"""Read-only, model-free verification of the curated scientific allowlist."""
from pathlib import Path, PurePosixPath
from types import ModuleType
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
FREEZE_SHA256 = '69713f59dfcd175413e7d8b07d8cd7295c39af06aa45c01e6fcbe247ee2ce32a'
ADDITIONS = frozenset({
    'freeze_manifest.json', 'README.md', 'REPORT.md', 'ERRORS.md',
    'results/predictions.jsonl', 'results/predictions.metadata.json',
    'results/case_scores.jsonl', 'results/errors.jsonl', 'results/summary.json',
    'audit/independent_actual_result_audit.json', 'audit/independent_error_review.json',
    'audit/independent_final_review.json', 'audit/INTEGRATION_METHOD.md',
    'provenance/portable_export.json', 'provenance/public_scope_evolution.json',
    'scripts/export_public.py', 'scripts/verify_export.py',
})
PORTABLE_KEYS = {'schema_version', 'suite_id', 'frozen_content_changed',
                'frozen_manifest_sha256', 'frozen_file_count', 'public_scope', 'excluded_scope'}
SCOPE_KEYS = {'schema_version', 'change_type', 'scientific_inputs_outputs_changed',
              'locked_scientific_file_count', 'retained_scope', 'documentation_change',
              'excluded_scope', 'provenance_policy'}

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe(root, name):
    assert isinstance(name, str) and name and '\\' not in name
    path = PurePosixPath(name)
    assert not path.is_absolute() and str(path) == name
    assert all(part not in ('', '.', '..') for part in name.split('/'))
    current = root
    for part in path.parts:
        current /= part
        assert not current.is_symlink(), 'Symlink public artifact'
    assert current.resolve().is_relative_to(root.resolve()) and current.is_file()
    return current

def verify(root=ROOT):
    root = Path(root)
    assert not root.is_symlink(), 'Symlink artifact root'
    assert sha(safe(root, 'freeze_manifest.json')) == FREEZE_SHA256, 'Wrong frozen manifest'
    freeze = load(root / 'freeze_manifest.json')
    assert len(freeze['files']) == 61
    allowed = set(freeze['files']) | ADDITIONS
    manifest = load(safe(root, 'FILE_SHA256.json'))
    assert set(manifest) == allowed, 'Manifest outside public scientific allowlist'
    directories = {str(p) for name in allowed for p in PurePosixPath(name).parents if str(p) != '.'}
    actual = set()
    for path in root.rglob('*'):
        assert not path.is_symlink(), 'Symlink public artifact'
        name = path.relative_to(root).as_posix()
        if path.is_file():
            if name != 'FILE_SHA256.json': actual.add(name)
        elif path.is_dir(): assert name in directories, 'Unexpected directory'
        else: raise AssertionError('Nonregular public artifact')
    assert actual == allowed, 'Missing or extra public file'
    for name, digest in manifest.items(): assert sha(safe(root, name)) == digest, name
    for name, digest in freeze['files'].items(): assert sha(safe(root, name)) == digest, name
    portable = load(root / 'provenance/portable_export.json')
    assert set(portable) == PORTABLE_KEYS and portable['schema_version'] == 2
    assert portable['frozen_content_changed'] is False
    assert portable['frozen_manifest_sha256'] == FREEZE_SHA256 and portable['frozen_file_count'] == 61
    scope = load(root / 'provenance/public_scope_evolution.json')
    assert set(scope) == SCOPE_KEYS and scope['schema_version'] == 1
    assert scope['scientific_inputs_outputs_changed'] is False and scope['locked_scientific_file_count'] == 61
    # Frozen checker is hash-verified before execution; no package/model imports.
    script = root / 'audit/independent_score_check.py'
    checker = ModuleType('multidoc_frozen_checker'); checker.__file__ = str(script)
    exec(compile(script.read_bytes(), str(script), 'exec'), checker.__dict__)
    native = checker.read_rows(root / 'results/predictions.jsonl')
    summary, rows = checker.recompute(root / 'data', native)
    assert checker.compare(root / 'results', summary, rows, root / 'data', native) == []
    context = checker.verify_actual_context(root / 'data', root / 'results/predictions.jsonl')
    assert context['status'] == 'passed' and context['native_completed'] and len(rows) == 48
    audit = load(root / 'audit/independent_actual_result_audit.json')
    assert audit['status'] == 'passed' and audit['primary_comparison_mismatches'] == []
    assert audit['primary_scorer_imported'] is False and audit['model_loaded'] is False and audit['inference_performed'] is False
    assert audit['frozen_run_verification'] == context and audit['case_count'] == 48 and audit['valid_count'] == 48
    assert audit['case_metrics'] == summary['case_metrics'] and audit['error_case_ids'] == summary['error_case_ids']
    assert audit['error_count'] == len(summary['error_case_ids']) == 24
    assert audit['independent_checker_sha256'] == sha(script)
    for name, digest in audit['input_sha256'].items(): assert sha(safe(root, name)) == digest
    review = load(root / 'audit/independent_final_review.json')
    assert review['passed'] and review['no_unresolved_gold_or_scoring_issue'] and review['all_errors_reviewed']
    assert review['report_sha256'] == sha(root / 'REPORT.md') and review['errors_md_sha256'] == sha(root / 'ERRORS.md')
    errors = load(root / 'audit/independent_error_review.json')
    assert errors['passed'] and errors['error_count'] == errors['reviewed_error_count'] == 24
    assert set(errors['error_ids']) == set(summary['error_case_ids'])
    for name, digest in errors['files'].items(): assert sha(safe(root, name)) == digest
    private = re.compile(r'/(?:workspace|home|root|Users)/[^\s"<>]+')
    identifiers = re.compile(r'"(?:pid|available_bytes)"\s*:\s*\d+')
    for name in allowed:
        body = (root / name).read_text(encoding='utf-8')
        assert not private.search(body) and not identifiers.search(body), 'Private diagnostic data'
    return {'verified': True, 'public_files': len(manifest) + 1, 'frozen_files': 61,
            'case_count': 48, 'error_count': 24, 'model_loaded': False}

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
