#!/usr/bin/env python3
"""Fail-closed local preflight. No credential read, network access or inference."""
import hashlib,json
from pathlib import Path
from jev_runner import sha,make_plan,rows,ContractError
ROOT=Path(__file__).resolve().parents[1]
def check(root=ROOT):
    manifest=json.loads((root/'manifest.json').read_text())
    lock=json.loads((root/'CODE_SHA256.json').read_text())
    for name,digest in (manifest['files']|lock).items():
        p=root/name
        if p.is_symlink() or not p.is_file() or sha(p)!=digest:raise ContractError('Bundle checksum mismatch')
    if lock.get('manifest.json')!=sha(root/'manifest.json'):raise ContractError('Manifest not code-locked')
    for suite in manifest['suites']:
        p=root/'inputs'/suite['id'];gold={g['id']:g for g in rows(p/'gold.jsonl')};reqs=rows(p/'requests.jsonl')
        if len(gold)!=len(reqs):raise ContractError('Gold accounting mismatch')
        for r in reqs:
            if set(r['request']['questions'])!=set(gold[r['id']]['expected']):raise ContractError('Gold fields mismatch')
            for f,q in r['request']['questions'].items():
                if gold[r['id']]['expected'][f] not in q['criteria']:raise ContractError('Gold label not in options')
    plan=make_plan(root)
    if plan['one_pass_requests']!=974 or plan['question_count']!=1362:raise ContractError('Scope differs from approved request/field counts')
    return {'status':'offline_preflight_passed','requests':974,'questions':1362,'code_and_manifest_sha256_verified':len(lock),'scientific_files_sha256_verified':len(manifest['files']),'network_calls':0,'credential_reads':0}
if __name__=='__main__':print(json.dumps(check()))
