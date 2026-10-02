#!/usr/bin/env python3
"""Verify the inactive Jev comparison preparation without credentials or network."""
from pathlib import Path
import hashlib,json,subprocess,sys,os,tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/jev_comparison'
EXPORT_SHA256='c62021bbcb33b94c653cc9649d7d06dcbdf1633d4dc7b7f19dee2db2cb8be2f4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)
def check(source=SOURCE,root=ROOT):
    require(sha(source/'FILE_SHA256.json')==EXPORT_SHA256,'Unexpected curated Jev export')
    files=json.loads((source/'FILE_SHA256.json').read_text())
    actual={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file() and p.name!='FILE_SHA256.json' and '__pycache__' not in p.parts}
    require(set(files)==actual,'Unexpected missing or extra Jev files')
    for name,digest in files.items():
        p=source/name
        require(not p.is_symlink() and sha(p)==digest,'Jev public artifact changed')
    manifest=json.loads((source/'manifest.json').read_text())
    require(manifest['status']=='prepared_not_executed','Jev status must remain prepared')
    require(sum(x['count'] for x in manifest['suites'])==974,'Jev scope changed')
    require([s['id'] for s in manifest['suites'] if s['baseline']!='complete']==['massive300'],'Unexpected baseline state')
    require(not (source/'inputs/massive300/predictions.jsonl').exists(),'Pending baseline was silently filled')
    for sid in [s['id'] for s in manifest['suites'] if s['id'] not in ('multidoc48','massive300')]:
        for name in ('requests.jsonl','predictions.jsonl'):
            require((source/'inputs'/sid/name).read_bytes()==(root/'experiments/probability_reliability/sources'/sid/name).read_bytes(),'Existing scientific source changed')
    for name,folder in [('requests.jsonl','data'),('gold.jsonl','data'),('cases.jsonl','data'),('predictions.jsonl','results')]:
        require((source/'inputs/multidoc48'/name).read_bytes()==(root/'experiments/multidoc48'/folder/name).read_bytes(),'Multidoc scientific source changed')
    template=(source/'workflow/jev-comparison.yml.in').read_text()
    require('ref: REVIEWED_CODE_COMMIT_SHA' in template,'Inactive template code placeholder changed')
    require('default: false' in template and 'github.run_attempt == 1' in template,'Bounded template guards missing')
    for p in (root/'.github/workflows').glob('*'):
        require('JEV_API_KEY' not in p.read_text() and 'jev_runner.py --execute' not in p.read_text(),'Live Jev workflow unexpectedly installed')
    require(not (source/'runs').exists(),'Live Jev output unexpectedly present')
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
    r=subprocess.run([sys.executable,str(source/'scripts/check_bundle.py')],check=True,capture_output=True,text=True,env=env)
    verified=json.loads(r.stdout);require(verified['network_calls']==0 and verified['credential_reads']==0,'Offline preflight changed')
    with tempfile.TemporaryDirectory() as temp:
        exported=Path(temp)/'snapshot'
        subprocess.run([sys.executable,str(source/'scripts/prepare_snapshot.py'),'--out',str(exported)],check=True,capture_output=True,text=True,env=env)
        require(all((source/n).read_bytes()==(exported/n).read_bytes() for n in [*files,'FILE_SHA256.json']),'Public export not byte-identical')
    return verified
if __name__=='__main__':print(json.dumps(check()))
