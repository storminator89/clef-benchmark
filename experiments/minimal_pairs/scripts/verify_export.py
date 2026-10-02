#!/usr/bin/env python3
"""Read-only stdlib verifier for the self-contained public archive."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name):
 p=R/name;assert p.resolve().is_relative_to(R.resolve()) and p.is_file();return p
m=json.loads((R/'FILE_SHA256.json').read_text())
actual={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and p.name!='FILE_SHA256.json' and '__pycache__' not in p.parts}
assert set(m)==actual,'Unexpected or missing public files'
for n,h in m.items():assert sha(check(n))==h,n
f=json.loads((R/'freeze_manifest.json').read_text())
for n,h in f['files'].items():assert sha(check(n))==h,n
p=json.loads((R/'provenance/portable_export.json').read_text());assert p['frozen_content_changed'] is False and p['frozen_manifest_sha256']==sha(R/'freeze_manifest.json')
q=json.loads((R/'audit/independent_result_check.json').read_text());assert q['passed'] and q['mismatches']==[] and q['prediction_count']==48
assert q['predictions_sha256']==sha(R/'results/predictions.jsonl') and q['summary_sha256']==sha(R/'results/summary.json')
prose=json.loads((R/'audit/independent_prose_review.json').read_text());assert prose['passed'] and prose['report_sha256']==sha(R/'REPORT.md') and prose['errors_md_sha256']==sha(R/'ERRORS.md')
print(json.dumps({'verified':True,'public_files':len(m),'frozen_files':len(f['files']),'prediction_count':q['prediction_count']},indent=2))
