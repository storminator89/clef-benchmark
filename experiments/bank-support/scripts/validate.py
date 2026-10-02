#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data'
def read(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
C=read(D/'cases.jsonl');R=read(D/'requests.jsonl');G=read(D/'gold.jsonl');M=read(D/'metadata.jsonl');policy=json.loads((D/'policy.json').read_text());fields=('intent','priority','next_step')
assert len(C)==len(R)==len(G)==len(M)==80
ids=[r['id'] for r in C];assert len(set(ids))==80
assert all([r['id'] for r in rows]==ids for rows in [R,G,M])
for c,r,g,m in zip(C,R,G,M):
 assert set(r)=={'id','request'} and set(r['request'])=={'model','state','questions'}
 assert set(g)=={'id','expected'} and g['expected']==c['expected']
 assert r['request']['questions']==policy['questions']
 assert r['request']['state']=='Synthetische Kundennachricht:\n'+c['message']
 assert set(c['expected'])==set(fields)
 for f in fields:
  assert r['request']['questions'][f]['type']=='choice' and c['expected'][f] in r['request']['questions'][f]['criteria']
 assert (c['expected']['next_step']=='clarify')==(c['answerability']=='clarification_needed')==bool(c['clarification_target'])
 assert (c['expected']['priority']=='critical')==(c['expected']['next_step']=='security_handoff')
 assert not re.search(r'\b[A-Z]{2}\d{2}[ A-Z0-9]{10,}\b|https?://|@',c['message'])
counts={f:dict(sorted(Counter(c['expected'][f] for c in C).items())) for f in fields}
summary={'case_count':80,'fields_per_case':3,'total_field_decisions':240,'topic_counts':dict(sorted(Counter(c['topic'] for c in C).items())),'gold_label_counts':counts,'style_counts':dict(sorted(Counter(c['style'] for c in C).items())),'answerability_counts':dict(sorted(Counter(c['answerability'] for c in C).items())),'seed':20261002,'designed_edge_cases':['bank_ambiguous_multi_07'],'not_representative_traffic_sample':True,'banking77':False}
if (ROOT/'freeze_manifest.json').exists():
 assert json.loads((D/'design_summary.json').read_text())==summary,'Design summary drift'
else:
 (D/'design_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
freeze=ROOT/'freeze_manifest.json'
if freeze.exists():
 for path,h in json.loads(freeze.read_text())['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,f'Changed frozen file: {path}'
print(json.dumps(summary,indent=2))
