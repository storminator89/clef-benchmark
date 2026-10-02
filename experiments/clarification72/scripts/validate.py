#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1]
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def validate(root=R):
 data={n:rows(root/'data'/f'{n}.jsonl') for n in ['cases','gold','requests','metadata']}
 for name,rr in data.items():
  assert len(rr)==72,name
  assert len({r['id'] for r in rr})==72,name
 ids=[r['id'] for r in data['cases']]
 assert all([r['id'] for r in rr]==ids for rr in data.values())
 q=json.loads((root/'data/policy.json').read_text())['questions']
 for c,g,r,m in zip(*(data[n] for n in ['cases','gold','requests','metadata'])):
  assert c['expected']==g['expected']
  assert set(r)=={'id','request'} and set(r['request'])=={'model','state','questions'}
  assert r['request']['questions']==q
  assert all(c[k] in r['request']['state'] for k in ['rule','message','question'])
  assert not any(k in r['request'] for k in ['gold','expected','label','rationale','stratum'])
  for f in q:assert g['expected'][f] in q[f]['criteria']
  assert (g['expected']['action']=='answer')==(g['expected']['determination']!='unresolved')
 assert Counter(c['domain'] for c in data['cases'])==dict.fromkeys(['banking','finance','insurance'],24)
 assert len(set(c['family'] for c in data['cases']))==12
 assert sorted(Counter(c['stratum'] for c in data['cases']).values())==[12]*6
 assert Counter(c['expected']['action'] for c in data['cases'])=={'answer':36,'ask_fact':12,'ask_target':12,'resolve_conflict':12}
 assert Counter(c['expected']['determination'] for c in data['cases'])=={'yes':18,'no':18,'unresolved':36}
 if (root/'freeze_manifest.json').exists():
  for name,h in json.loads((root/'freeze_manifest.json').read_text())['files'].items():
   assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h, name
 return {'status':'passed','cases':72,'fields':2,'matched_ids_and_order':True,'freeze_hashes_checked':(root/'freeze_manifest.json').exists()}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
