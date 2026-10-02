"""Pinned public release download and verification. No vendor code is executed."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

from runtime.hardware_probe import existing_parent
from runtime.model_registry import DEFAULT_MODEL, MODEL_KEYS, get_model, model_manifest

MANIFEST = Path(__file__).with_name('model_file_manifest.json')


def load_manifest(model_key=DEFAULT_MODEL):
    model = get_model(model_key)
    manifest = model_manifest(model_key)
    if not manifest or any(item['hf_commit'] != model['revision'] for item in manifest.values()):
        raise ValueError('Model manifest revision differs from the pinned adapter')
    for name, item in manifest.items():
        if Path(name).name != name or name in ('.', '..') or '\\' in name:
            raise ValueError('Unsafe model manifest filename')
        if len(item['sha256']) != 64 or not isinstance(item['bytes'], int) or item['bytes'] < 0:
            raise ValueError('Invalid model manifest entry')
    return manifest


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 ** 2), b''):
            result.update(chunk)
    return result.hexdigest()


def inspect_files(model_dir, manifest=None, hashes=True):
    """Hash reuse candidates; a same-size file is not trusted without its hash."""
    manifest = load_manifest() if manifest is None else manifest
    result = {'verified': [], 'present_unverified': [], 'missing': [], 'invalid': []}
    for name, expected in manifest.items():
        path = Path(model_dir) / name
        if not path.exists():
            result['missing'].append(name)
        elif not path.is_file() or path.stat().st_size != expected['bytes']:
            result['invalid'].append(name)
        elif hashes:
            result['verified' if digest(path) == expected['sha256'] else 'invalid'].append(name)
        else:
            result['present_unverified'].append(name)
    result['verified_complete'] = len(result['verified']) == len(manifest)
    result['missing_bytes'] = sum(manifest[name]['bytes'] for name in result['missing'])
    return result


def prepare_model(model_dir, download=False, offline=False, model_key=DEFAULT_MODEL):
    model_dir = Path(model_dir).expanduser().resolve()
    model = get_model(model_key)
    manifest = load_manifest(model_key)
    result = inspect_files(model_dir, manifest)
    if result['invalid']:
        raise ValueError('Existing model files failed verification; nothing overwritten: '
                         + ', '.join(result['invalid']) + '. Choose a fresh --model-dir or investigate these files.')
    if result['verified_complete']:
        return {'status': 'verified', 'model_dir': str(model_dir), 'revision': model['revision'], 'model_key': model_key, 'model_id': model['repo_id'],
                'downloaded_files': 0, 'reused_files': len(result['verified'])}
    if offline or not download:
        raise FileNotFoundError('Pinned model files missing: ' + ', '.join(result['missing'])
                                + '. Download explicitly without --offline, or supply a verified --model-dir.')
    if os.environ.get('HF_ENDPOINT', 'https://huggingface.co').rstrip('/') != 'https://huggingface.co':
        raise ValueError('Custom HF_ENDPOINT is not permitted by this official-source setup')
    required = result['missing_bytes'] + 3 * 1024 ** 3
    if shutil.disk_usage(existing_parent(model_dir)).free < required:
        raise OSError(f'Insufficient model filesystem space: need {required} free bytes including reserve')
    # Lazy import: plans and offline verification need only the standard library.
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
    from huggingface_hub import hf_hub_download
    model_dir.mkdir(parents=True, exist_ok=True)
    for name in result['missing']:
        print(f'Downloading pinned release file: {name}', file=sys.stderr, flush=True)
        path = Path(hf_hub_download(repo_id=model['repo_id'], revision=model['revision'], filename=name,
                                   local_dir=model_dir, token=False))
        expected = manifest[name]
        if path.stat().st_size != expected['bytes'] or digest(path) != expected['sha256']:
            raise ValueError(f'Downloaded file failed pinned SHA-256 verification: {name}; no model code executed')
    final = inspect_files(model_dir, manifest)
    if not final['verified_complete']:
        raise ValueError('Model verification was incomplete after download')
    return {'status': 'verified', 'model_dir': str(model_dir), 'revision': model['revision'], 'model_key': model_key, 'model_id': model['repo_id'],
            'downloaded_files': len(result['missing']), 'reused_files': len(result['verified'])}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=MODEL_KEYS, default=DEFAULT_MODEL)
    parser.add_argument('--model-dir', type=Path)
    parser.add_argument('--download', action='store_true', help='Explicitly allow missing official files to be downloaded')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args(argv)
    if args.model_dir is None:
        args.model_dir = Path(get_model(args.model)['default_model_dir'])
    try:
        result = prepare_model(args.model_dir, args.download, args.offline, args.model)
    except Exception as error:
        print(json.dumps({'status': 'blocked', 'error': str(error), 'model_loaded': False}), file=sys.stderr)
        return 4
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
