from pathlib import Path
import json,collections,hashlib
P=Path(__file__).resolve().parents[1]
b=json.loads((P/'benchmark/benchmark.json').read_text());rs=[json.loads(x) for x in (P/'benchmark/requests.jsonl').read_text().splitlines()];rm={r['id']:r['request'] for r in rs}
assert len(rm)==len(rs)==len(b['cases'])==60;assert len(b['documents'])==12
assert all(v==10 for v in collections.Counter(c['area'] for c in b['cases']).values())
assert all(v==5 for v in collections.Counter(c['document_id'] for c in b['cases']).values())
for c in b['cases']:
 d=next(d for d in b['documents'] if d['id']==c['document_id']);ids={x['id'] for x in d['clauses']};r=rm[c['id']]
 assert d['synthetic'] is True
 assert set(r)=={'model','state','questions'}
 assert set(r['questions'])=={'decision','evidence'}
 assert r['state']['unterlagen']==[{'klausel':x['id'],'text':x['text']} for x in d['clauses']]
 assert r['state']['sachverhalt']==c['scenario'];assert r['state']['zu_pruefende_aussage']==c['claim']
 assert set(r['state'])=={'hinweis','unterlagen','sachverhalt','zu_pruefende_aussage'}
 assert set(c['decision_options'])=={'ja','nein','offen','konflikt'}
 assert len(c['evidence_options'])==5
 assert len({tuple(v) for v in c['evidence_options'].values()})==5
 assert len({len(v) for v in c['evidence_options'].values()})==1
 assert all(set(v)<=ids for v in c['evidence_options'].values())
 assert c['expected']['decision'] in c['decision_options']
 assert set(c['evidence_options'][c['expected']['evidence']])==set(c['expected']['evidence_clauses'])
 assert r['questions']['decision']['criteria']==c['decision_options']
 assert r['questions']['evidence']['criteria']=={k:', '.join(v) for k,v in c['evidence_options'].items()}
 assert c['rationale'] not in json.dumps(r,ensure_ascii=False)
assert sum('date_version_application' in c['tags'] for c in b['cases'])==3
out={'status':'pass','cases':60,'documents':12,'native_choice_fields':2,'no_gold_in_requests':True,'matching_docs_and_requests':True,'unique_equal_cardinality_evidence_options':True,'version_date_subset_count':3,'benchmark_sha256':hashlib.sha256((P/'benchmark/benchmark.json').read_bytes()).hexdigest(),'requests_sha256':hashlib.sha256((P/'benchmark/requests.jsonl').read_bytes()).hexdigest()}
(P/'qa/structural_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
