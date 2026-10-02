#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
from collections import Counter
R=Path(__file__).resolve().parents[1]
def rows(n):return [json.loads(x) for x in (R/f'data/{n}.jsonl').read_text().splitlines()]
def index(xs):
 d={x['id']:x for x in xs};assert len(d)==len(xs);return d
C=index(rows('cases'));G=index(rows('gold'));Q=index(rows('requests'));M=index(rows('metadata'));P=rows('pairs');policy=json.loads((R/'data/policy.json').read_text())
assert len(C)==48 and len(P)==24 and set(C)==set(G)==set(Q)==set(M)
assert list(C)==list(G)==list(Q)==list(M)
assert Counter(p['domain'] for p in P)==dict(banking=8,insurance=8,finance=8)
assert Counter(p['kind'] for p in P)==dict(flip=12,invariant=12)
assert len({p['id'] for p in P})==24
assert Counter(p['subtype'] for p in P)==dict(yes_to_no=3,no_to_yes=3,clarify_to_answer=3,answer_to_clarify=3,irrelevant_text=6,within_region_fact=3,short_circuit_control=3)
assert list(policy)==['action','determination']
assert list(policy['action']['criteria'])==['answer','ask_fact','ask_target','resolve_conflict']
assert list(policy['determination']['criteria'])==['yes','no','unresolved']
for id,c in C.items():assert M[id]=={k:c[k] for k in ['id','pair_id','side','domain','family','kind','subtype','rationale','authorship']}
seen=[]
for p in P:
 a,b=[C[i] for i in p['case_ids']];seen+=p['case_ids'];assert a['side']=='a' and b['side']=='b'
 assert p['span_a']!=p['span_b']
 for side,c in [('a',a),('b',b)]:
  assert c['pair_id']==p['id'] and c['domain']==p['domain'] and c['kind']==p['kind']
  assert c['message']==p['unchanged_prefix']+p['span_'+side]+p['unchanged_suffix']
  assert c['expected']==G[c['id']]['expected']==p['expected_'+side]
  assert p['changed_character_offsets_'+side]==[len(p['unchanged_prefix']),len(p['unchanged_prefix'])+len(p['span_'+side])]
  assert c['rule']==p['rule'] and c['question']==p['question']
  q=Q[c['id']];assert set(q)=={'id','request'} and q['request']['questions']==policy
  assert q['request']['state']==f"Fiktive Testregel:\n{c['rule']}\n\nSynthetische Anfrage und Unterlagen:\n{c['message']}\n\nZu beurteilende Eigenschaft:\n{c['question']}"
  assert set(q['request'])=={'model','state','questions'} and q['request']['model']=='clef-flash'
 for s in ['prefix','suffix']:assert p['unchanged_'+s+'_sha256']==hashlib.sha256(p['unchanged_'+s].encode()).hexdigest()
 assert (a['expected']!=b['expected'])==(p['kind']=='flip')
assert len(seen)==len(set(seen))==48 and set(seen)==set(C)
print(json.dumps({'valid':True,'pairs':24,'cases':48,'changed_spans_verified':24,'leakage_structure_checked':True}))
