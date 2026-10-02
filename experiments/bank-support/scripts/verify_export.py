#!/usr/bin/env python3
"""Verify a final self-contained export; read-only, stdlib only."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(path):
 p=R/path
 assert p.resolve().is_relative_to(R.resolve()),'Manifest escaped package'
 assert p.is_file(),f'Missing: {path}'
 return p
manifest=json.loads((R/'FILE_SHA256.json').read_text())
for path,expected in manifest.items():assert sha(check(path))==expected,f'Hash mismatch: {path}'
freeze=json.loads((R/'freeze_manifest.json').read_text())
for path,expected in freeze['files'].items():assert sha(check(path))==expected,f'Frozen hash mismatch: {path}'
mapping=json.loads((R/'provenance/portable_export.json').read_text())
assert mapping['frozen_content_changed'] is False
for m in mapping['frozen_file_mapping']:
 assert m['original_sha256']==m['published_sha256']==sha(check(m['published_path']))
 assert freeze['files'][m['original_path']]==m['original_sha256']
assert len(mapping['frozen_file_mapping'])==len(freeze['files'])
qa=json.loads((R/'audit/independent_score_check.json').read_text())
assert qa['passed'] is True and qa['prediction_count']==80 and qa['mismatches']==[]
assert qa['freeze_manifest_sha256']==sha(R/'freeze_manifest.json')
assert qa['checker_sha256']==sha(R/'scripts/independent_score_check.py')
assert qa['run_metadata_sha256']==sha(R/'results/predictions.metadata.json')
assert qa['summary_sha256']==sha(R/'results/summary.json')
assert qa['errors_sha256']==sha(R/'results/errors.jsonl')
assert qa['independently_recomputed']['provenance']['predictions_sha256']==sha(R/'results/predictions.jsonl')
print(json.dumps({'export_files_verified':len(manifest),'frozen_files_verified':len(freeze['files']),'portable_mapping_verified':True,'independent_check_file_present':True,'freeze_manifest_sha256':sha(R/'freeze_manifest.json')},indent=2))
