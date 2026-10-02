#!/usr/bin/env python3
"""Data integrity checks and scorer unit tests. Does not run an ML model."""
import collections, hashlib, importlib.util, json, pathlib, sys
D=pathlib.Path(__file__).resolve().parent

def read(name):return [json.loads(x) for x in (D/name).read_text(encoding='utf-8').splitlines() if x]
cases=read('cases.jsonl');diag=read('diagnostic_cases.jsonl');requests=read('requests.jsonl');gold=read('gold.jsonl');pairs=read('pairs.jsonl')
allcases=cases+diag;lookup={c['id']:c for c in allcases};req={c['id']:c for c in requests};gld={c['id']:c for c in gold}
assert len(cases)==150 and len(diag)==30 and len(lookup)==len(allcases)==180
assert len(req)==len(requests)==180 and set(req)==set(lookup)==set(gld)
assert collections.Counter(c['split'] for c in allcases)=={'german_primary':120,'english_control':30,'mixed_schema_diagnostic':30}
for c in allcases:
    q=c['questions'];assert list(q)==['decision'] and q['decision']['type']=='choice'
    assert c['expected']['decision'] in q['decision']['criteria']
    assert req[c['id']]=={'id':c['id'],'request':{'model':'clef-flash','state':c['input'],'questions':q}}
    assert all(k not in req[c['id']]['request'] for k in ('expected','gold_rationale','tags','pair_id','category','language'))
    assert gld[c['id']]['expected']==c['expected'] and gld[c['id']]['pair_id']==c['pair_id']
    assert isinstance(c['input'],str) and c['input'].strip() and isinstance(c['tags'],list)
for cat in {c['category'] for c in cases}:
    de=[c for c in cases if c['category']==cat and c['language']=='de']
    assert len(de)==20
    counts=collections.Counter(c['expected']['decision'] for c in de)
    assert len(set(counts.values()))==1
    assert len([p for p in pairs if p['category']==cat])==5
    assert {lookup[p['german_id']]['expected']['decision'] for p in pairs if p['category']==cat}==set(counts)
assert len({p['pair_id'] for p in pairs})==30
for p in pairs:
    a,b,c=(lookup[p[k]] for k in ('german_id','english_id','mixed_id'))
    assert a['input']==c['input'] and b['questions']==c['questions']
    assert a['expected']==b['expected']==c['expected']
    assert a['pair_id']==b['pair_id']==c['pair_id']==p['pair_id']
    assert list(a['questions']['decision']['criteria'])==list(b['questions']['decision']['criteria'])
    assert (a['language'],a['schema_language'])==('de','de')
    assert (b['language'],b['schema_language'])==('en','en')
    assert (c['language'],c['schema_language'])==('de','en')
# Synthetic output objects below only test scorer code, not model performance.
spec=importlib.util.spec_from_file_location('scorer',D/'score.py');score=importlib.util.module_from_spec(spec);spec.loader.exec_module(score)
c=cases[0];truth=c['expected']['decision'];labels=list(c['questions']['decision']['criteria']);n=len(labels)
p={k:float(k==truth) for k in labels}
correct={'id':c['id'],'answers':{'decision':{'type':'choice','choice':truth,'confidence':1.0,'probabilities':p}},'latency_ms':5}
r=score.inspect(c,correct);assert r['schema_valid'] and r['strict_correct'] and r['brier']==0 and r['nll']==0
wrong=next(k for k in labels if k!=truth);pwrong={k:float(k==wrong) for k in labels}
w=score.inspect(c,{'answers':{'decision':{'type':'choice','choice':wrong,'confidence':1.,'probabilities':pwrong}}})
assert w['schema_valid'] and not w['correct'] and w['brier']==2
missing=score.inspect(c,None);assert not missing['present'] and not missing['correct']
bad=score.inspect(c,{'answers':{'decision':{'type':'choice','choice':truth,'confidence':1,'probabilities':{truth:1}}}})
assert bad['correct'] and not bad['schema_valid']
bad2=score.inspect(c,{'answers':{'decision':{'type':'choice','choice':'invented','confidence':.5,'probabilities':{k:1/n for k in labels}}}})
assert not bad2['choice_valid']
met=score.metrics([r,w,missing],labels);assert met['choice_accuracy_all_planned']==1/3 and met['n_present']==2
unrounded=dict(correct,probabilities_unrounded={'decision':{k:.9 if k==truth else .1/(n-1) for k in labels}})
u=score.inspect(c,unrounded);assert u['probability_source']=='unrounded' and abs(u['max_probability']-.9)<1e-10
# Freeze hashes can be verified later after blind review approval.
manifest=D/'freeze_manifest.json'
if manifest.exists():
    m=json.loads(manifest.read_text(encoding='utf-8'))
    for filename,digest in m['sha256'].items():assert hashlib.sha256((D/filename).read_bytes()).hexdigest()==digest,filename
print('PASS: 180 payloads, 120 balanced German cases, 30 aligned triplets, gold isolation, scorer unit tests'+(', freeze hashes' if manifest.exists() else ' (not frozen yet)'))
