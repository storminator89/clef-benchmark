"""Strict, model-free helpers for immutable paired/reliability artifact admission."""
from __future__ import annotations
from contextlib import contextmanager
import json
from pathlib import Path
import sys
from types import ModuleType

from build_bank_web_data import load, require, sha

ROOT = Path(__file__).resolve().parents[1]
PORTABLE_KEYS = {'schema_version', 'suite_id', 'frozen_content_changed',
                 'frozen_manifest_sha256', 'frozen_file_count', 'public_scope', 'excluded_scope'}


def public_file(root, name):
    """Reject unsafe paths and symlink components, even when their target is in-tree."""
    root = Path(root)
    path = Path(name)
    require(isinstance(name, str) and name and not path.is_absolute()
            and '\\' not in name and name == path.as_posix()
            and all(p not in ('', '.', '..') for p in name.split('/')),
            'Unsafe public artifact path')
    current = root
    for part in path.parts:
        current /= part
        require(not current.is_symlink(), f'Symlink public artifact: {name}')
    require(current.resolve().is_relative_to(root.resolve()) and current.is_file(),
            f'Missing public artifact: {name}')
    return current


def verify_manifest(source, expected_sha256, expected_count):
    source = Path(source)
    require(not source.is_symlink(), 'Symlink public artifact root')
    manifest_path = public_file(source, 'FILE_SHA256.json')
    require(sha(manifest_path) == expected_sha256, 'Public export manifest changed')
    raw = load(manifest_path)
    manifest = raw.get('files', raw)
    require(len(manifest) == expected_count, 'Wrong public export file count')
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file() or p.is_symlink()}
    require(actual == set(manifest) | {'FILE_SHA256.json'}, 'Missing or extra public export files')
    for name, digest in manifest.items():
        require(sha(public_file(source, name)) == digest, f'Export hash mismatch: {name}')
    return manifest


def verify_lock(source, filename, expected_sha256, expected_count):
    path = public_file(source, filename)
    require(sha(path) == expected_sha256, 'Frozen source lock changed')
    lock = load(path)
    require(len(lock['files']) == expected_count, 'Frozen file count changed')
    for name, digest in lock['files'].items():
        require(sha(public_file(source, name)) == digest, f'Frozen input changed: {name}')
    portable = load(public_file(source, 'provenance/portable_export.json'))
    require(set(portable) == PORTABLE_KEYS and portable['schema_version'] == 2,
            'Public provenance must contain scope-only metadata')
    require(portable['frozen_content_changed'] is False
            and portable['frozen_manifest_sha256'] == expected_sha256
            and portable['frozen_file_count'] == expected_count, 'Wrong public export lineage')
    return lock


def verify_curated_scope(source, lock, manifest, public_additions):
    """Enforce the explicit retained-file allowlist, with no omitted-file lineage."""
    require(set(manifest) == set(lock['files']) | set(public_additions),
            'Public manifest is outside the reviewed curated allowlist')
    note = load(public_file(source, 'provenance/public_scope_evolution.json'))
    require(set(note) == {'schema_version', 'change_type', 'scientific_inputs_outputs_changed',
                         'locked_scientific_file_count', 'retained_scope', 'documentation_change',
                         'excluded_scope', 'provenance_policy'}, 'Public scope note contains unexpected lineage')
    require(note['schema_version'] == 1 and note['scientific_inputs_outputs_changed'] is False
            and note['locked_scientific_file_count'] == len(lock['files']), 'Invalid public curation scope')


def module_from_file(name, path):
    """Load only previously hash-verified stdlib scripts, without writing bytecode."""
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec'), module.__dict__)
    return module


@contextmanager
def module_dependency(name, path):
    missing = object()
    previous = sys.modules.get(name, missing)
    module = module_from_file(name, path)
    sys.modules[name] = module
    try:
        yield module
    finally:
        if previous is missing:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous


def serialize(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def write_data(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(serialize(data))
