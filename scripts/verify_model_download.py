#!/usr/bin/env python3
"""Read-only SHA-256 verification of the pinned complete upstream release."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
manifest = json.loads((ROOT / 'runtime/model_file_manifest.json').read_text())
model = ROOT / 'runtime/model'
for name, expected in sorted(manifest.items()):
    path = model / name
    if not path.is_file():
        raise SystemExit(f'Missing model file: {name}; run runtime/download_model.py')
    if path.stat().st_size != expected['bytes']:
        raise SystemExit(f'Size mismatch: {name}')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            digest.update(block)
    if digest.hexdigest() != expected['sha256']:
        raise SystemExit(f'SHA-256 mismatch: {name}')
    print(f'OK {name}')
print(f'Verified {len(manifest)} pinned model files')
