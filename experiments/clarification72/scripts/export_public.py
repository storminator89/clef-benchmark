#!/usr/bin/env python3
"""Copy only an already reviewed public manifest; never auto-publish new diagnostics."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
out=a.destination.resolve();assert not out.exists(),'Refusing to overwrite export'
manifest=json.loads((ROOT/'FILE_SHA256.json').read_text())
for name,expected in manifest.items():
 path=Path(name);source=ROOT/path
 assert not path.is_absolute() and '..' not in path.parts and source.resolve().is_relative_to(ROOT.resolve())
 assert source.is_file() and not source.is_symlink()
 assert hashlib.sha256(source.read_bytes()).hexdigest()==expected,f'Unreviewed source change: {name}'
out.mkdir(parents=True)
for name in [*manifest,'FILE_SHA256.json']:
 target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
print(json.dumps({'reviewed_files_copied':len(manifest)+1,'new_files_included':False}))
