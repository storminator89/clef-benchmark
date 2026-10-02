#!/usr/bin/env python3
"""Export this reviewed public snapshot; no model, secrets or network."""
import argparse, hashlib, json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(out):
    manifest=json.loads((ROOT/'FILE_SHA256.json').read_text())
    if out.exists():raise ValueError('Refuse to overwrite an export')
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name!='FILE_SHA256.json' and '__pycache__' not in p.parts}
    if set(manifest)!=actual:raise ValueError('Unexpected source files')
    for name,digest in manifest.items():
        p=ROOT/name
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('Public source checksum mismatch')
    out.mkdir(parents=True)
    for name in [*manifest,'FILE_SHA256.json']:
        p=out/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
    return {'status':'exported_verified_public_snapshot','file_count':len(manifest)+1}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.out)))
