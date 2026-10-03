"""Portable independent native/metric and public-integrity verification."""
from pathlib import Path
import json,hashlib,math,importlib.util
R=Path(__file__).resolve().parents[1]
def need(v,msg):
    if not v:raise AssertionError(msg)

def unique(kvs):
    out={}
    for k,v in kvs:need(k not in out,'Duplicate JSON key '+k);out[k]=v
    return out

def load(s):
    def bad(v):raise ValueError('Nonstandard JSON numeric constant '+v)
    return json.loads(s,object_pairs_hook=unique,parse_constant=bad)

def obj(p):return load(p.read_bytes().decode('utf-8'))

def rows(p):return [load(l) for l in p.read_bytes().decode('utf-8').splitlines() if l.strip()]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def numbered(v):
    try:return type(v) in (int,float) and math.isfinite(v)
    except OverflowError:return False

def ids(xs):
    out={}
    for x in xs:need(isinstance(x,dict) and isinstance(x.get('id'),str) and x['id'] and x['id'] not in out,'Unassignable/duplicate ID');out[x['id']]=x
    return out

def safe(x):
    if isinstance(x,float) and not math.isfinite(x):return {'nonfinite_parsed_number':repr(x)}
    if isinstance(x,dict):return {k:safe(v) for k,v in x.items()}
    if isinstance(x,list):return [safe(v) for v in x]
    return x

def same(a,b,msg):need(json.dumps(safe(a),sort_keys=True,ensure_ascii=False)==json.dumps(safe(b),sort_keys=True,ensure_ascii=False),msg)

def metric(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None}

def native_valid(row,request,tokens):
    try:
        need(isinstance(row,dict) and 'error' not in row,'Missing/explicit-error row')
        need(type(row['input_tokens']) is int and row['input_tokens']==tokens and 0<tokens<=2048,'Token count')
        need(row['truncated'] is False,'Truncation')
        need(isinstance(row['answers'],dict) and isinstance(row['probabilities_unrounded'],dict),'Field-map type')
        need(set(row['answers'])==set(row['probabilities_unrounded'])==set(request['questions']),'Field membership')
        for f,q in request['questions'].items():
            a=row['answers'][f];p=row['probabilities_unrounded'][f];opts=list(q['criteria'])
            need(isinstance(a,dict) and set(a)=={'type','choice','confidence','probabilities'},'Native answer shape')
            need(a['type']=='choice' and isinstance(a['choice'],str) and a['choice'] in opts,'Native choice')
            need(isinstance(p,dict) and set(p)==set(opts),'Raw map membership')
            need(all(numbered(v) and 0<=v<=1 for v in p.values()) and abs(sum(p.values())-1)<1e-5,'Raw probability values/sum')
            winner=opts[0]
            for option in opts[1:]:
                if p[option]>p[winner]:winner=option
            need(a['choice']==winner,'Native criteria-order maximum')
            rounded=a['probabilities'];need(isinstance(rounded,dict) and set(rounded)==set(opts),'Rounded map membership')
            need(all(numbered(rounded[o]) and 0<=rounded[o]<=1 and rounded[o]==round(p[o],4) for o in opts),'Rounded values')
            need(numbered(a['confidence']) and a['confidence']==round(p[winner],4),'Native confidence')
        for k in ('encode_seconds','inference_seconds','total_seconds','latency_ms','rss_bytes'):need(numbered(row[k]) and row[k]>=0,'Telemetry '+k)
        need(abs(row['latency_ms']-1000*row['inference_seconds'])<1e-5,'Latency agreement')
        return True,None
    except (AssertionError,KeyError,TypeError,ValueError,OverflowError) as e:return False,str(e)

def main():
 manifest=obj(R/'PUBLIC_MANIFEST.json')
 for n,h in manifest['files'].items():need(sha(R/n)==h,'Public file hash mismatch '+n)
 frozen=obj(R/'public_scientific_freeze.json')
 for n,h in frozen['files'].items():need(sha(R/n)==h,'Scientific byte mismatch '+n)
 native=rows(R/'results/predictions.jsonl');q=ids(rows(R/'data/requests.jsonl'));t=ids(obj(R/'evidence/encoding_preflight.json')['cases'])
 need(len(native)==72 and len(ids(native))==72,'72 unique native rows')
 invalid={}
 for x in native:
  valid,issue=native_valid(x,q[x['id']]['request'],t[x['id']]['input_tokens'])
  if not valid:invalid[x['id']]=issue
 spec=importlib.util.spec_from_file_location('independent_oracle',R/'scripts/independent_score_check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 summary=obj(R/'scored/summary.json');module.oracle(native,invalid,summary,rows(R/'scored/case_scores.jsonl'),rows(R/'scored/pair_scores.jsonl'),rows(R/'scored/cluster_scores.jsonl'))
 need(not invalid,'Native validity failures')
 combined=(R/'runtime_results/segment01/predictions.jsonl').read_bytes()+(R/'runtime_results/segment02/predictions.jsonl').read_bytes()
 need(combined==(R/'results/predictions.jsonl').read_bytes(),'Byte-preserving assembly')
 print(json.dumps({'status':'passed','native_rows':72,'independent_metric_assertions':module.checks,'public_files':len(manifest['files']),'primary_scorer_imported':False}))
if __name__=='__main__':main()
