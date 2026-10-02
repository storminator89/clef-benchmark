#!/usr/bin/env python3
"""Verify public artifact bytes and locked sources without loading any model."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify():
 manifest=json.loads((ROOT/'FILE_SHA256.json').read_text());files=manifest['files']
 actual={str(f.relative_to(ROOT)) for f in ROOT.rglob('*') if f.is_file()}
 expected=set(files)|{'FILE_SHA256.json'}
 if actual!=expected:raise ValueError('Artifact file set differs: '+repr({'unexpected':sorted(actual-expected),'missing':sorted(expected-actual)}))
 for name,digest in files.items():
  if name.startswith('/') or '..' in Path(name).parts:raise ValueError('Nonportable public path')
  if sha(ROOT/name)!=digest:raise ValueError('Artifact hash mismatch: '+name)
 lock=json.loads((ROOT/'SOURCE_LOCK.json').read_text())
 for name,digest in lock['files'].items():
  if sha(ROOT/name)!=digest:raise ValueError('Source lock mismatch: '+name)
 recorded=(ROOT/'SOURCE_LOCK.sha256').read_text().split()[0]
 if sha(ROOT/'SOURCE_LOCK.json')!=recorded:raise ValueError('Source lock checksum mismatch')
 for name in actual:
  if '__pycache__' in name or name.endswith('.pyc'):raise ValueError('Python execution cache is not a public scientific file')
 print(json.dumps({'status':'PASS','public_files_verified':len(files),'locked_files_verified':len(lock['files']),'source_lock_sha256':recorded,'model_inference_performed':False}))
if __name__=='__main__':verify()
