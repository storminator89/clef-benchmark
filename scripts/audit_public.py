#!/usr/bin/env python3
"""Reject likely credential leaks, private absolute paths and generated baggage.

This narrow automated check supplements manual curation. It does not certify
that arbitrary new files contain no personal data. It never prints matched data.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = {
    'private_absolute_path': re.compile(r'/(?:wor[k]space|ho[m]e|ro[o]t|Us[e]rs)/[^\s"<>]+'),
    'github_token': re.compile(r'\bg[h][pousr]_[A-Za-z0-9_]{20,}\b|\bgit[h]ub_pat_[A-Za-z0-9_]{20,}\b'),
    'service_key': re.compile(r'\b(?:s[k]-[A-Za-z0-9_-]{20,}|h[f]_[A-Za-z0-9]{20,}|AK[I]A[A-Z0-9]{16})\b'),
    'private_key': re.compile(r'BEGIN (?:RSA |EC |OPENSSH )?PRIVATE K[E]Y'),
    'bearer_credential': re.compile(r'(?i)Bearer\s+[A-Za-z0-9._-]{24,}'),
}
BAD_PARTS = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'hf_cache', '.cache', '.aws', '.codex'}
BAD_SUFFIXES = {'.safetensors', '.bin', '.gguf', '.pyc', '.log'}
# .git is repository machinery and is never part of a published tree inventory.
EXCLUDED = {'provenance/publication_audit.json', 'provenance/package_inventory.json'}
# Reviewed immutable offline QA evidence included in the signed image package.
SAFE_QA_LOGS = {'experiments/images/qa/build_summary.log': 'd59fd141ef568221126535efd6779a233559e75d1200d9d882ea72b370bfe1b5', 'experiments/images/qa/test_scorer.log': 'b52fd2030bf92de4dd39dd804082b2d46694302b3e58cf9795e8231d2f98f7c2'}

SAFE_QA_LOGS['experiments/insurance/results/run.log'] = '2d0386f6098184ac51c78d962ecf02882c1d774a073598af36b0d175fccd9ee2'

def extracted_text(path):
    if path.suffix == '.docx':
        with zipfile.ZipFile(path) as archive:
            return '\n'.join(archive.read(name).decode('utf-8', errors='replace') for name in archive.namelist() if name.endswith('.xml'))
    if path.suffix == '.pdf':
        process = subprocess.run(['pdftotext', str(path), '-'], check=True, capture_output=True)
        return process.stdout.decode('utf-8', errors='replace')
    data = path.read_bytes()
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        # Image/binary artifacts must have been separately visually reviewed.
        return ''

def audit():
    findings = []
    inventory = []
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if '.git' in relative.parts:
            continue
        if path.is_symlink():
            findings.append({'path': str(relative), 'reason': 'symlink'})
            continue
        if not path.is_file() or str(relative) in EXCLUDED:
            continue
        data = path.read_bytes()
        inventory.append({'path': str(relative), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        safe_qa_log = SAFE_QA_LOGS.get(str(relative)) == hashlib.sha256(data).hexdigest()
        if BAD_PARTS.intersection(relative.parts) or (path.suffix in BAD_SUFFIXES and not safe_qa_log):
            findings.append({'path': str(relative), 'reason': 'excluded_baggage'})
        if len(data) > 10 * 1024**2:
            findings.append({'path': str(relative), 'reason': 'unexpected_large_file'})
        for kind, pattern in PATTERNS.items():
            if pattern.search(extracted_text(path)):
                findings.append({'path': str(relative), 'reason': kind})
    report = {'status': 'pass' if not findings else 'fail', 'files_scanned': len(inventory), 'total_bytes': sum(row['bytes'] for row in inventory), 'findings': findings, 'scope': 'Heuristic secret/private-path/baggage scan of the public tree, including DOCX XML and extracted PDF text; not a guarantee for arbitrary later additions.'}
    return report, inventory

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='Save public audit and SHA-256 inventory')
    args = parser.parse_args()
    report, inventory = audit()
    if args.write:
        (ROOT / 'provenance/publication_audit.json').write_text(json.dumps(report, indent=2) + '\n')
        (ROOT / 'provenance/package_inventory.json').write_text(json.dumps({'excluded_self_reports': sorted(EXCLUDED), 'files': inventory}, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['status'] == 'pass' else 1)
