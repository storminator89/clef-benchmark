#!/usr/bin/env python3
"""Verify frozen Jev preparation and any explicitly pinned manual activation, offline."""
from pathlib import Path
import hashlib,json,subprocess,sys,os,tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/jev_comparison'
EXPORT_SHA256='c62021bbcb33b94c653cc9649d7d06dcbdf1633d4dc7b7f19dee2db2cb8be2f4'
ACTIVATION_TEMPLATE_SHA256='b3805a2fd043ab68d78b8129515b6bac60c1ecd5501adc4d3d523f0fbc1858b5'
ACTIVATION_WRAPPER_SHA256='ca52c98f2b1597022c12cc6a653d1b2ebb88ba2c60cf18add35da4b710775b2f'
CONTINUATION_TEMPLATE_SHA256='d8c63b9ee0746a176082a8a9b07dd49c0e810a2b09e31bb702c7c759ef288cd2'
CONTINUATION_WRAPPER_SHA256='c8509f7886b5d95dc188a5e7fbf06fc3e0273c8b49b380fbdd6eace0eb58a048'
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
    activation_file = root/'provenance/jev_activation.json'
    approved_workflow = None
    final_activation_file = root/'provenance/jev_final_activation.json'
    if final_activation_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location('jev_final_activation_gate', root/'scripts/check_jev_final_activation.py')
        final_gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(final_gate)
        final_gate.check(root)
        approved_workflow = root/'.github/workflows/jev-comparison.yml'
    elif activation_file.exists():
        activation = json.loads(activation_file.read_text())
        import re
        require(re.fullmatch('[0-9a-f]{40}', activation['reviewed_code_commit']) is not None, 'Invalid immutable code ref')
        require(activation['workflow'] == '.github/workflows/jev-comparison.yml', 'Unexpected active workflow path')
        approved_workflow = root/activation['workflow']
        mode = activation.get('mode', 'initial974')
        require(mode in ('initial974', 'continuation793'), 'Unknown reviewed execution mode')
        if mode == 'initial974':
            template_path, template_hash = 'scripts/workflows/jev-verified-execution.yml.in', ACTIVATION_TEMPLATE_SHA256
            wrapper_path, wrapper_hash = 'scripts/run_jev_workflow.py', ACTIVATION_WRAPPER_SHA256
        else:
            template_path, template_hash = 'scripts/workflows/jev-continuation.yml.in', CONTINUATION_TEMPLATE_SHA256
            wrapper_path, wrapper_hash = 'scripts/run_jev_continuation.py', CONTINUATION_WRAPPER_SHA256
            require(activation['remaining_initial_requests'] == 793 and activation['prior_wire_attempts'] == 181 and activation['retry_failed_prior_cases'] is False, 'Continuation scope changed')
            require(activation['first_run_lock_sha256'] == '24637c98afc4c073d4fc1c9fef5aeafe24e1b76029eafd13b42211e7bca5e120', 'Continuation source lock changed')
            require(activation['continuation_plan_sha256'] == '617ccee8601d598fc623ed0722bb3a4c78f0252bfffd69e0769b670de08b3383', 'Continuation plan lock changed')
        require(sha(root/template_path) == template_hash, 'Reviewed activation template changed')
        require(sha(root/wrapper_path) == wrapper_hash, 'Reviewed activation wrapper changed')
        if mode == 'continuation793':
            with tempfile.TemporaryDirectory() as temp:
                subprocess.run([sys.executable, str(root/wrapper_path), '--output', str(Path(temp)/'plan.json')], check=True, capture_output=True, env={'PYTHONDONTWRITEBYTECODE':'1'})
        reviewed_template = (root/template_path).read_text()
        require(approved_workflow.read_text() == reviewed_template.replace('REVIEWED_CODE_COMMIT_SHA', activation['reviewed_code_commit']), 'Active workflow differs from reviewed template')
        require(sha(approved_workflow) == activation['workflow_sha256'], 'Activation workflow hash changed')
        require(sha(root/wrapper_path) == activation['wrapper_sha256'], 'Activation wrapper hash changed')
        require(activation['frozen_bundle_changed'] is False and activation['max_initial_requests'] == 974 and activation['max_wire_attempts'] == 1024 and activation['local_api_reservation_usd'] == 3, 'Activation scope changed')
    for p in (root/'.github/workflows').glob('*'):
        if p == approved_workflow: continue
        require('JEV_API_KEY' not in p.read_text() and 'jev_runner.py --execute' not in p.read_text(),'Unreviewed live Jev workflow installed')
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
