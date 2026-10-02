#!/usr/bin/env python3
import json,collections,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(name):return [json.loads(x) for x in (R/'data'/name).read_text().splitlines()]
C=read('cases.jsonl');G=read('gold.jsonl');Q=read('requests.jsonl');M=read('metadata.jsonl');policy=json.loads((R/'data/policy.json').read_text())
assert len(C)==len(G)==len(Q)==len(M)==48
assert len({c['id'] for c in C})==48
assert [c['id'] for c in C]==[g['id'] for g in G]==[q['id'] for q in Q]==[m['id'] for m in M]
assert collections.Counter(c['domain'] for c in C)==dict(banking=16,insurance=16,finance=16)
assert sorted(collections.Counter(c['template_id'] for c in C).values())==[3]*16
assert sorted(collections.Counter(c['family'] for c in C).values())==[4]*12
assert sorted(collections.Counter(c['stratum'] for c in C).values())==[12]*4
assert collections.Counter(c['expected']['determination'] for c in C)==dict(yes=18,no=18,unresolved=12)
assert collections.Counter(c['expected']['source'] for c in C)==dict(D1=9,D2=9,D3=9,not_unique=21)
for c,g,q,m in zip(C,G,Q,M):
 assert set(q)=={'id','request'} and set(q['request'])=={'model','state','questions'}
 assert c['expected']==g['expected'] and c['state']==q['request']['state'] and q['request']['questions']==policy
 assert len(c['documents'])==3 and {d['id'] for d in c['documents']}=={'D1','D2','D3'}
 assert set(c['expected'])=={'source','determination'}
 for f in c['expected']:assert c['expected'][f] in policy[f]['criteria']
 assert all(d['outcome']==('yes' if 400<=d['threshold'] else 'no') for d in c['documents'])
 assert all(i in {'D1','D2','D3'} for i in c['plausible_source_ids'])
 outcomes={d['outcome'] for d in c['documents'] if d['id'] in c['plausible_source_ids']}
 assert (len(c['plausible_source_ids'])==1)==(c['expected']['source']!='not_unique')
 assert c['expected']['determination']==(next(iter(outcomes)) if len(outcomes)==1 else 'unresolved')
 if c['expected']['source']!='not_unique':assert c['documents'][c['source_position']-1]['id']==c['expected']['source']
 assert m=={k:c[k] for k in m}
for outcome,n in [('yes',4),('no',5)]:
 eligible=[c for c in C if c['expected']['source']!='not_unique' and c['expected']['determination']==outcome]
 assert collections.Counter(c['source_position'] for c in eligible)=={1:n,2:n,3:n}
 assert collections.Counter(c['expected']['source'] for c in eligible)=={'D1':n,'D2':n,'D3':n}
assert sum(c['source_uncertain_answer_definite'] for c in C)==9
print('PASS: 48 aligned label-free requests, gold/plausible-source truth checks, 3-document inputs, 12 families, 16 templates, fixed balanced labels and positions')
