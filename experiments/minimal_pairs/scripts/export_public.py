#!/usr/bin/env python3
"""Copy only hash-verified files in an explicitly reviewed public manifest."""
from pathlib import Path
import argparse,json,hashlib,shutil,re,socket
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True);p.add_argument('--manifest',type=Path,default=R/'FILE_SHA256.json');a=p.parse_args();D=a.destination.resolve()
assert not D.exists(),'Refusing to overwrite export'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert a.manifest.read_bytes()==(R/'FILE_SHA256.json').read_bytes(),'Export requires the current reviewed public allowlist'
allowed=json.loads(a.manifest.read_text());assert isinstance(allowed,dict)
frozen=json.loads((R/'freeze_manifest.json').read_text());qa=json.loads((R/'audit/independent_result_check.json').read_text());prose=json.loads((R/'audit/independent_prose_review.json').read_text())
assert qa['passed'] and qa['prediction_count']==48 and qa['mismatches']==[]
assert qa['predictions_sha256']==sha(R/'results/predictions.jsonl') and qa['summary_sha256']==sha(R/'results/summary.json')
assert prose['passed'] and prose['no_unresolved_gold_or_scoring_issue']
assert prose['report_sha256']==sha(R/'REPORT.md') and prose['errors_md_sha256']==sha(R/'ERRORS.md')
assert json.loads((R/'results/run_outcome.json').read_text())['exit_code']==0
assert json.loads((R/'results/predictions.metadata.json').read_text())['status']=='completed'
assert set(frozen['files'])<=set(allowed),'All frozen public files must be preserved'
D.mkdir(parents=True)
for rel,h in sorted(allowed.items()):
 source=R/rel;assert source.resolve().is_relative_to(R.resolve()) and source.is_file() and not source.is_symlink(),rel
 assert sha(source)==h,rel
 target=D/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
for rel,h in frozen['files'].items():assert sha(R/rel)==sha(D/rel)==h,rel
# Preserve every admitted byte, including the scope-only provenance, exactly.
private=re.compile(r'/(?:workspace|home|root|Users)/[^\s"<>]+');measurements=re.compile(r'"(?:pid|available_bytes)"\s*:\s*\d+')
for file in D.rglob('*'):
 if file.is_file():
  text=file.read_text();assert not private.search(text),str(file.relative_to(D));assert not measurements.search(text),str(file.relative_to(D));assert socket.gethostname() not in text,str(file.relative_to(D))
manifest={str(file.relative_to(D)):sha(file) for file in sorted(D.rglob('*')) if file.is_file()}
assert manifest==allowed,'Export contains a missing, extra or altered public file'
shutil.copyfile(R/'FILE_SHA256.json',D/'FILE_SHA256.json')
print(json.dumps({'public_files':len(manifest),'frozen_files':len(frozen['files']),'frozen_manifest_sha256':sha(D/'freeze_manifest.json'),'file_manifest_sha256':sha(D/'FILE_SHA256.json'),'frozen_bytes_unchanged':True},indent=2))
