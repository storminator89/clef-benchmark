#!/usr/bin/env python3
"""Integrity, isolation and synthetic scorer tests; no model or network access."""
import collections, datetime, hashlib, importlib.util, json, pathlib, subprocess, sys, tempfile
D=pathlib.Path(__file__).resolve().parent

def read(name):return [json.loads(x) for x in (D/name).read_text(encoding='utf-8').splitlines() if x]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
cases=read('cases.jsonl');diag=read('diagnostic_cases.jsonl');requests=read('requests.jsonl');gold=read('gold.jsonl');pairs=read('pairs.jsonl')
lookup={c['id']:c for c in cases};req={c['id']:c for c in requests};gld={c['id']:c for c in gold}
assert not diag
assert len(cases)==len(lookup)==len(req)==len(requests)==len(gld)==len(gold)==100
assert set(req)==set(lookup)==set(gld)
assert collections.Counter(c['split'] for c in cases)=={'german_primary':80,'english_control':20}
assert len({c['input'] for c in cases})==100
for c in cases:
    q=c['questions'];assert list(q)==['decision'] and q['decision']['type']=='choice'
    assert len(q['decision']['criteria'])==5 and c['expected']['decision'] in q['decision']['criteria']
    assert 'TEST' in q['decision']['instructions']
    assert req[c['id']]=={'id':c['id'],'request':{'model':'clef-flash','state':c['input'],'questions':q}}
    assert set(req[c['id']]['request'])=={'model','state','questions'}
    assert gld[c['id']]['expected']==c['expected'] and gld[c['id']]['pair_id']==c['pair_id']
    assert isinstance(c['input'],str) and c['input'].strip() and isinstance(c['tags'],list) and c['gold_rationale'].strip()
    assert c['id'] not in c['input']
    assert c['gold_rationale'] not in json.dumps(req[c['id']]['request'])
categories={c['category'] for c in cases};assert len(categories)==8
for cat in categories:
    de=[c for c in cases if c['category']==cat and c['split']=='german_primary'];assert len(de)==10
    counts=collections.Counter(c['expected']['decision'] for c in de)
    assert set(counts.values())=={2} and len(counts)==5
    assert len([p for p in pairs if p['category']==cat]) in (2,3)
assert len(pairs)==len({p['pair_id'] for p in pairs})==20
assert len({p['german_id'] for p in pairs})==len({p['english_id'] for p in pairs})==20
for p in pairs:
    a,b=(lookup[p[k]] for k in ('german_id','english_id'))
    assert a['expected']==b['expected'] and a['category']==b['category']==p['category']
    assert a['pair_id']==b['pair_id']==p['pair_id']
    assert list(a['questions']['decision']['criteria'])==list(b['questions']['decision']['criteria'])
    assert (a['language'],a['schema_language'])==('de','de')
    assert (b['language'],b['schema_language'])==('en','en')
assert (datetime.date(2026,3,7)-datetime.date(2026,2,28)).days==7
assert (datetime.date(2026,10,9)-datetime.date(2026,10,1)).days==8
# Check deterministic assembly without touching any frozen artifact.
spec=importlib.util.spec_from_file_location('builder',D/'build_benchmark.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
with tempfile.TemporaryDirectory() as tmp:
    builder.D=pathlib.Path(tmp);builder.main()
    for name in ('cases.jsonl','diagnostic_cases.jsonl','pairs.jsonl','requests.jsonl','gold.jsonl','policies.json','design_summary.json'):
        assert (D/name).read_bytes()==(builder.D/name).read_bytes(),name
# Scorer tests use artificial answers, never model outputs.
spec=importlib.util.spec_from_file_location('scorer',D/'score.py');score=importlib.util.module_from_spec(spec);spec.loader.exec_module(score)
c=cases[0];truth=c['expected']['decision'];labels=list(c['questions']['decision']['criteria']);n=len(labels)
def answer(c,pred=None):
    pred=pred or c['expected']['decision'];labels=list(c['questions']['decision']['criteria'])
    return {'id':c['id'],'answers':{'decision':{'type':'choice','choice':pred,'confidence':1.0,'probabilities':{k:float(k==pred) for k in labels}}},'latency_ms':5}
correct=answer(c);r=score.inspect(c,correct);assert r['schema_valid'] and r['strict_correct'] and r['brier']==0 and r['nll']==0
wrong=next(k for k in labels if k!=truth);w=score.inspect(c,answer(c,wrong));assert w['schema_valid'] and not w['correct'] and w['brier']==2
missing=score.inspect(c,None);assert not missing['present'] and not missing['correct']
bad=score.inspect(c,{'answers':{'decision':{'type':'choice','choice':truth,'confidence':1,'probabilities':{truth:1}}}});assert bad['correct'] and not bad['schema_valid']
bad2=score.inspect(c,{'answers':{'decision':{'type':'choice','choice':'invented','confidence':.2,'probabilities':{k:1/n for k in labels}}}});assert not bad2['choice_valid']
for badval in (None,[],3,'bad'):
    for malformed in ({'response':badval},{'answers':badval},{'answers':{'decision':badval}}):
        inspected=score.inspect(c,malformed);assert not inspected['correct'] and not inspected['schema_valid']
for badrow in ([],7,'bad'):
    assert score.inspect(c,badrow)['error']=='non_object_output_record'
met=score.metrics([r,w,missing],labels);assert met['choice_accuracy_all_planned']==1/3 and met['n_present']==2
unrounded=dict(correct,probabilities_unrounded={'decision':{k:.9 if k==truth else .1/(n-1) for k in labels}})
u=score.inspect(c,unrounded);assert u['probability_source']=='unrounded' and abs(u['max_probability']-.9)<1e-10
with tempfile.TemporaryDirectory() as tmp:
    inp=pathlib.Path(tmp)/'synthetic_answers.jsonl';out=pathlib.Path(tmp)/'scores.json'
    inp.write_text(''.join(json.dumps(answer(c))+'\n' for c in cases))
    command=[sys.executable,str(D/'score.py'),str(inp),'--out',str(out)]
    subprocess.run(command,check=True,capture_output=True,text=True)
    report=json.loads(out.read_text());assert report['counts']=={'planned':100,'present':100}
    for split,count in [('german_primary',80),('english_control',20)]:
        assert report['splits'][split]['n_planned']==count
        assert report['splits'][split]['strict_accuracy_all_planned']==1
    assert report['splits']['english_control']['category_macro_f1']==0.5
    assert report['splits']['english_control']['category_macro_f1_observed_support']==1
    assert report['paired']['german_id_vs_english_id']['n_pairs_valid_both']==20
    assert report['paired_all_planned']['german_id_vs_english_id']['n_pairs_used']==20
    pair=pairs[0];left=lookup[pair['german_id']];right=lookup[pair['english_id']]
    incomplete={left['id']:score.inspect(left,answer(left)),right['id']:score.inspect(right,None)}
    paircheck=score.paired_all_planned([pair],incomplete,'german_id','english_id')
    assert paircheck['n_pairs_used']==1 and paircheck['n_pairs_with_invalid_or_missing']==1
    assert paircheck['left_minus_right_accuracy_all_planned']==1
    assert score.paired([pair],incomplete,'german_id','english_id')['n_pairs_valid_both']==0
    inp.write_text('');subprocess.run(command,check=True,capture_output=True,text=True)
    empty=json.loads(out.read_text());assert empty['counts']['present']==0 and empty['splits']['german_primary']['choice_accuracy_all_planned']==0
    inp.write_text(json.dumps(answer(cases[0]))+'\n'+json.dumps(answer(cases[0]))+'\n')
    assert subprocess.run(command,capture_output=True).returncode!=0
    for malformed in (None,[],42,{'id':None},{'id':[]},{'id':''}):
        inp.write_text(json.dumps(malformed)+'\n')
        assert subprocess.run(command,capture_output=True).returncode!=0
    inp.write_text(json.dumps({'id':'unknown_test_id'})+'\n')
    assert subprocess.run(command,capture_output=True).returncode!=0
preflight=D/'encoding_preflight.json'
if preflight.exists():
    enc=json.loads(preflight.read_text(encoding='utf-8'))
    assert enc['requests_sha256']==digest(D/'requests.jsonl')
    assert enc['count']==100 and not enc['model_instantiated'] and enc['all_fit_without_truncation']
    assert len(enc['items'])==100 and {x['id'] for x in enc['items']}==set(req)
    assert all(x['fits_without_truncation'] and x['tokens']<=2048 for x in enc['items'])
manifest=D/'freeze_manifest.json'
if manifest.exists():
    m=json.loads(manifest.read_text(encoding='utf-8'))
    for name,value in m['sha256'].items():assert digest(D/name)==value,name
print('PASS: 100 native payloads; 80 balanced German cases; 20 aligned pairs; no gold leakage; deterministic generation; scorer CLI/edge tests'+('; freeze hashes verified' if manifest.exists() else '; not frozen yet'))
