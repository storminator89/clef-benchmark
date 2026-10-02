#!/usr/bin/env python3
"""Offline structural, isolation, deterministic and scorer checks. No model loading."""
import collections, hashlib, importlib.util, json, pathlib, subprocess, sys, tempfile
D=pathlib.Path(__file__).resolve().parent

def read(name):return [json.loads(x) for x in (D/name).read_text(encoding='utf-8').splitlines() if x]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
cases=read('cases.jsonl');requests=read('requests.jsonl');gold=read('gold.jsonl')
byid={c['id']:c for c in cases};req={r['id']:r for r in requests};gld={g['id']:g for g in gold}
assert len(cases)==len(byid)==len(requests)==len(req)==len(gold)==len(gld)==72
assert set(byid)==set(req)==set(gld)
assert [r['id'] for r in requests]==[g['id'] for g in gold]
assert len({c['input'] for c in cases})==72
assert len({c['category'] for c in cases})==6
assert set(collections.Counter(c['category'] for c in cases).values())=={12}
assert collections.Counter(c['information_status'] for c in cases)=={'sufficient':50,'missing_or_unresolved':22}
for c in cases:
    assert c['language']==c['schema_language']=='de' and c['split']=='german_clean_primary'
    assert c['synthetic'] is True
    assert set(c['questions'])=={'decision'}
    q=c['questions']['decision'];assert set(q)=={'type','instructions','criteria'}
    assert q['type']=='choice' and len(q['criteria']) in (4,5)
    assert c['expected']['decision'] in q['criteria']
    assert all(isinstance(k,str) and isinstance(v,str) and v for k,v in q['criteria'].items())
    assert len(c['input'].split())>=120 and len(c['tags'])>=3
    assert c['input'].startswith('Kundennachricht:\n') and '\n\nAktenauszug / Arbeitskontext:\n' in c['input']
    assert c['gold_rationale'].strip() and c['id'] not in c['input']
    assert set(req[c['id']])=={'id','request'}
    assert req[c['id']]['request']=={'model':'clef-flash','state':c['input'],'questions':c['questions']}
    assert c['gold_rationale'] not in json.dumps(req[c['id']]['request'],ensure_ascii=False)
    assert not any(k in req[c['id']]['request'] for k in ('expected','gold','gold_rationale','category','tags','information_status'))
    assert gld[c['id']]['expected']==c['expected'] and gld[c['id']]['information_status']==c['information_status']
# Every label has positive support; exact informational-abstention sets match metadata.
scorer=module('clean_score',D/'score.py')
for c in cases:
    assert (c['expected']['decision'] in scorer.INFO_LABELS[c['category']])==(c['information_status']=='missing_or_unresolved')
for cat in {c['category'] for c in cases}:
    group=[c for c in cases if c['category']==cat]
    assert set(c['expected']['decision'] for c in group)==set(group[0]['questions']['decision']['criteria'])
# Arithmetic is independently checked against hand-recorded formulae and Decimal operations.
from decimal import Decimal as N
calculated=[N(4)*N('17.50')+N(8)*N('19.20')-N('14.80'),N(4)*(N('24.15')+N('47.25'))-N(92)-N(180),N(4)*N(125),N('298.50')-N(80)-N('65.25'),N(360)*(N(1)-N('.075'))+N(12),None,N(438)*N(73)/N(365),(N(224)-N(210))+(N(94)-N(98))+(N('667.50')-N(640)),N(18+18+16)*N('2.50')-N(10),N(3)*N(80)+N(8)*N(110)+N(250),None,N('246.80')+N('109.20')-N('21.60')-N('9.40')]
for c,expected in zip([c for c in cases if c['category']=='beitragsrechnung'],calculated):
    if expected is None:assert c['expected']['decision']=='daten_fehlen'
    else:
        text=c['questions']['decision']['criteria'][c['expected']['decision']].removesuffix(' Euro')
        value=N(text.replace('.','').replace(',','.'));assert value==expected.quantize(N('.01')),(c['id'],value,expected)
# Byte-for-byte deterministic rebuild in a separate temporary directory.
builder=module('clean_builder',D/'build_benchmark.py')
with tempfile.TemporaryDirectory() as tmp:
    builder.build(tmp)
    for name in ('cases.jsonl','requests.jsonl','gold.jsonl','policies.json','design_summary.json'):
        assert (D/name).read_bytes()==(pathlib.Path(tmp)/name).read_bytes(),name
# Artificial outputs are program tests, never benchmark model results.
def answer(c,pred=None):
    pred=pred or c['expected']['decision'];labels=c['questions']['decision']['criteria']
    return {'id':c['id'],'response':{'answers':{'decision':{'type':'choice','choice':pred,'confidence':1.0,'probabilities':{k:float(k==pred) for k in labels}}}},'latency_ms':5}
c=cases[0];truth=c['expected']['decision'];labels=list(c['questions']['decision']['criteria'])
a=answer(c);r=scorer.inspect(c,a);assert r['schema_valid'] and r['correct'] and r['brier']==0 and r['nll']==0
wrong=next(k for k in labels if k!=truth);rwrong=scorer.inspect(c,answer(c,wrong));assert rwrong['schema_valid'] and not rwrong['correct'] and rwrong['brier']==2
assert not scorer.inspect(c,None)['correct']
bad={'id':c['id'],'answers':{'decision':{'type':'choice','choice':truth,'confidence':1,'probabilities':{truth:1}}}}
assert scorer.inspect(c,bad)['correct'] and not scorer.inspect(c,bad)['schema_valid']
for v in (None,[],3,'bad'):
    for row in ({'response':v},{'answers':v},{'answers':{'decision':v}}):assert not scorer.inspect(c,row)['schema_valid']
for v in ([],7,'bad'):assert scorer.inspect(c,v)['error']=='non_object_output_record'
full=scorer.score(cases,[answer(c) for c in cases]);assert full['overall']['strict_accuracy_all_planned']==1 and full['category_macro_f1']==1
assert full['information_request_diagnostic']['recall']==1 and full['information_request_diagnostic']['unnecessary_information_request_rate']==0
empty=scorer.score(cases,[]);assert empty['overall']['choice_accuracy_all_planned']==0 and empty['counts']['present']==0
partial=scorer.score(cases,[answer(c)]);assert partial['overall']['choice_accuracy_all_planned']==1/72
for raw in ([a,a],[{'id':'unknown'}],[None],[[]],[42],[{'id':[]}],[{'id':''}]):
    try:scorer.score(cases,raw)
    except ValueError:pass
    else:raise AssertionError('Malformed/duplicate/unknown rows not rejected')
with tempfile.TemporaryDirectory() as tmp:
    inp=pathlib.Path(tmp)/'artificial.jsonl';out=pathlib.Path(tmp)/'result.json'
    inp.write_text(''.join(json.dumps(answer(c))+'\n' for c in cases))
    subprocess.run([sys.executable,str(D/'score.py'),str(inp),'--out',str(out)],check=True,capture_output=True)
    assert json.loads(out.read_text())['overall']['strict_accuracy_all_planned']==1
preflight=D/'encoding_preflight.json'
if preflight.exists():
    p=json.loads(preflight.read_text());assert p['requests_sha256']==digest(D/'requests.jsonl')
    assert p['count']==72 and p['all_fit_without_truncation'] and not p['model_instantiated']
    assert {i['id'] for i in p['items']}==set(req) and max(i['tokens'] for i in p['items'])<=2048
review=D/'pre_inference_review.jsonl'
if review.exists():
    rv=read('pre_inference_review.jsonl');assert len(rv)==72 and {x['id'] for x in rv}==set(byid)
    for x in rv:assert x['independent_label']==byid[x['id']]['expected']['decision'] and x['disposition']=='pass',x
independent_tests=D/'independent_scorer_checks.json'
if independent_tests.exists():
    t=json.loads(independent_tests.read_text());assert t['test_count']==len(t['passed_tests'])==19
    assert t['scorer_sha256']==digest(D/'score.py')
manifest=D/'freeze_manifest.json'
if manifest.exists():
    m=json.loads(manifest.read_text());assert m['counts']['total']==72
    for name,h in m['sha256'].items():assert digest(D/name)==h,name
print('PASS: 72 unique German clean requests; six categories; 50 sufficient/22 missing; native schema and label isolation; arithmetic; deterministic build; scorer edge/CLI tests'+('; frozen hashes checked' if manifest.exists() else '; not yet frozen'))
