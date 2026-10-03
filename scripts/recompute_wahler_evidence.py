#!/usr/bin/env python3
"""Recompute primary native-choice results from portable public evidence, offline."""
import argparse
import hashlib
import json
import math
from pathlib import Path
GROUPS={'original_text180':120,'finance100':80,'clean72':72,'bank_support80':80,
        'insurance60':60,'clarification72':72,'minimal_pairs48':48,'multidoc48':48}
MODELS=('clef','jev','wahler')
FILES=('planned.jsonl','cases.jsonl','wahler-native-responses.jsonl','wahler-requests.jsonl',
       'original-benchmark.py','recompute.py','provenance.json','README.md')
def require(ok,why):
    if not ok: raise ValueError(why)
def records(path): return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def keyed(rows):
    d={(r['suite'],r['id']):r for r in rows}
    require(len(d)==len(rows),'Duplicate case keys'); return d

def recompute(planned,rows):
    plan=keyed(planned); cases=keyed(rows)
    require(len(plan)==580 and set(plan)==set(cases),'Expected identical 580-case plan')
    require(sum(len(p['request']['questions']) for p in plan.values())==968,'Expected 968 fields')
    groups={s:{'planned':n,'models':{m:{'correct':0,'incorrect':0,'missing':0,'sum_only_diagnostics':0} for m in MODELS}} for s,n in GROUPS.items()}
    counts={s:0 for s in GROUPS}
    for key,p in plan.items():
        s=key[0]; require(s in groups,'Unexpected suite'); counts[s]+=1
        r=cases[key]; q=p['request']['questions']; gold=r['expected']
        require(set(q)==set(gold),'Gold fields differ')
        require(set(r['models'])==set(MODELS),'Model set differs')
        for f in q:require(q[f]['type']=='choice' and gold[f] in q[f]['criteria'],'Bad gold/options')
        for m in MODELS:
            model=r['models'][m]; out=groups[s]['models'][m]
            if model['status']=='missing_or_structurally_invalid':
                require(model['answers'] is None,'Missing model carries answers');out['missing']+=1;continue
            require(model['status']=='native_answer','Unknown model status');answers=model['answers']
            require(set(answers)==set(q),'Answer fields differ');exact=True;strict=True
            for f,question in q.items():
                a=answers[f];ps=a['probabilities']
                require(a['type']=='choice' and set(ps)==set(question['criteria']),'Option fields differ')
                require(all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in ps.values()),'Bad probabilities')
                require(a['choice'] in ps and ps[a['choice']]==max(ps.values()),'Native selection differs')
                require(type(a['confidence']) in (int,float) and math.isfinite(a['confidence']) and 0<=a['confidence']<=1,'Bad confidence')
                exact &= a['choice']==gold[f];strict &= abs(math.fsum(ps.values())-1)<=1e-5
            out['correct' if exact else 'incorrect']+=1;out['sum_only_diagnostics']+=not strict
    require(counts==GROUPS,'Group denominators differ')
    return {'metric':'all_fields_native_exact_over_same_planned_cases','groups':groups}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,default=Path(__file__).resolve().parent);args=p.parse_args()
    root=args.evidence
    manifest=json.loads((root/'SHA256SUMS').read_text())
    require(isinstance(manifest,dict) and set(manifest)==set(FILES),'Incomplete or unexpected evidence manifest')
    for name,digest in manifest.items():
        require(Path(name).name==name,'Unsafe evidence filename')
        require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,'Evidence digest mismatch: '+name)
    result=recompute(records(root/'planned.jsonl'),records(root/'cases.jsonl'))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
