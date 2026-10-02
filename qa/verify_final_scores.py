"""Independently recompute finished-run metrics. Refuses incomplete run metadata."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

BASE=Path(__file__).resolve().parent.parent

def read(path):return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
def avg(values):return statistics.fmean(values) if values else None
def finite(value):return isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value)
def equal(a,b):
    if isinstance(a,(float,int)) and not isinstance(a,bool) and isinstance(b,(float,int)) and not isinstance(b,bool):return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12)
    return a==b

def quantile(values,fraction):
    if not values:return None
    values=sorted(values);position=(len(values)-1)*fraction;index=int(position)
    return values[index]+(values[min(index+1,len(values)-1)]-values[index])*(position-index)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--predictions',type=Path,required=True)
    parser.add_argument('--metadata',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    meta=json.loads(args.metadata.read_text())
    if meta.get('status')!='completed':raise RuntimeError('Refusing to inspect incomplete predictions')
    manifest=json.loads((BASE/'benchmark/freeze_manifest.json').read_text())
    for filename,digest in manifest['sha256'].items():assert hashlib.sha256((BASE/'benchmark'/filename).read_bytes()).hexdigest()==digest,filename
    assert meta['requests_sha256']==manifest['sha256']['requests.jsonl']
    cases=read(BASE/'benchmark/cases.jsonl')+read(BASE/'benchmark/diagnostic_cases.jsonl')
    gold={r['id']:r for r in read(BASE/'benchmark/gold.jsonl')}
    ids={c['id'] for c in cases};raw=read(args.predictions)
    assert all(isinstance(r,dict) and isinstance(r.get('id'),str) for r in raw)
    assert len({r['id'] for r in raw})==len(raw)
    assert {r['id'] for r in raw}==ids,'Completed run is missing cases or has unknown IDs'
    assert len(raw)==180 and meta['request_count']==180
    raw_by_id={r['id']:r for r in raw}
    evaluated={}
    native_coherence=[]
    for case in cases:
        identifier=case['id'];r=raw_by_id[identifier];expected=gold[identifier]['expected']['decision']
        assert expected==case['expected']['decision']
        labels=list(case['questions']['decision']['criteria'])
        answer=r.get('answers',{});answer=answer.get('decision',{}) if isinstance(answer,dict) else {}
        answer=answer if isinstance(answer,dict) else {}
        prediction=answer.get('choice');valid=isinstance(prediction,str) and prediction in labels and not r.get('error')
        native=answer.get('probabilities')
        native_valid=isinstance(native,dict) and set(native)==set(labels) and all(finite(v) and 0<=v<=1 for v in native.values()) and abs(sum(native.values())-1)<=.001
        full=r.get('probabilities_unrounded',{});full=full.get('decision') if isinstance(full,dict) else None
        full_valid=isinstance(full,dict) and set(full)==set(labels) and all(finite(v) and 0<=v<=1 for v in full.values()) and abs(sum(full.values())-1)<1e-5
        p={k:v/sum(native.values()) for k,v in native.items()} if native_valid else None
        confidence=answer.get('confidence')
        strict=bool(answer.get('type')=='choice' and valid and native_valid and p[prediction]>=max(p.values())-.00011 and finite(confidence) and 0<=confidence<=1 and abs(confidence-p[prediction])<=.001)
        if full_valid:
            if valid and full[prediction]<max(full.values())-1e-7:strict=False
            p={k:v/sum(full.values()) for k,v in full.items()}
        coherence=bool(native_valid and full_valid and all(native[k]==round(full[k],4) for k in labels) and valid and confidence==round(full[prediction],4))
        if not coherence:native_coherence.append(identifier)
        item={'id':identifier,'category':case['category'],'split':case['split'],'expected':expected,'predicted':prediction if valid else None,'choice_valid':valid,'correct':bool(valid and prediction==expected),'strict_correct':bool(valid and prediction==expected and strict),'schema_valid':strict,'probabilities':p,'latency_ms':r.get('latency_ms')}
        evaluated[identifier]=item
        assert r.get('truncated') is False,identifier
    reports=[]
    for source,filename in [(BASE/'benchmark/score.py','scores_frozen_v1_0.json'),(BASE/'qa/score_v1_1.py','scores_robust_v1_1.json')]:
        output=BASE/'qa'/filename
        completed=subprocess.run([sys.executable,str(source),str(args.predictions),'--out',str(output)],capture_output=True,text=True)
        if completed.returncode:raise RuntimeError(f'{source.name} failed: {completed.stderr}')
        reports.append(json.loads(output.read_text()))
    original,robust=reports
    legacy_differences=[key for key in original if key!='scoring_version' and original[key]!=robust.get(key)]
    independent={'status':'pass','source_predictions_sha256':hashlib.sha256(args.predictions.read_bytes()).hexdigest(),'freeze_hashes_verified':True,'n_unique_scenarios':120,'n_payloads':180,'n_present':len(raw),'legacy_report_fields_changed':legacy_differences,'rounded_probability_mismatches':native_coherence,'splits':{},'paired_all_planned':{},'timing_scope':'CPU forward-only latency_ms; encoding and total separately recorded; not API end-to-end'}
    scored={x['id']:x for x in robust['case_results']}
    for identifier,row in evaluated.items():
        for name in ['correct','strict_correct','schema_valid','choice_valid']:assert row[name]==scored[identifier][name],(identifier,name)
    for split in ['german_primary','english_control','mixed_schema_diagnostic']:
        rows=[r for r in evaluated.values() if r['split']==split]
        summary={'n':len(rows),'correct':sum(r['correct'] for r in rows),'strict_correct':sum(r['strict_correct'] for r in rows),'choice_valid':sum(r['choice_valid'] for r in rows),'schema_valid':sum(r['schema_valid'] for r in rows),'accuracy':avg([r['correct'] for r in rows]),'per_category':{}}
        for category in sorted({r['category'] for r in rows}):
            subset=[r for r in rows if r['category']==category]
            case=next(c for c in cases if c['category']==category)
            labels=list(case['questions']['decision']['criteria'])
            confusions=Counter((r['expected'],r['predicted']) for r in subset)
            f1={}
            for label in labels:
                tp=confusions[label,label]
                fp=sum(v for (truth,pred),v in confusions.items() if truth!=label and pred==label)
                fn=sum(v for (truth,pred),v in confusions.items() if truth==label and pred!=label)
                f1[label]=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0
            vectors=[r for r in subset if r['probabilities'] is not None]
            brier=avg([sum((value-int(label==r['expected']))**2 for label,value in r['probabilities'].items()) for r in vectors])
            nll=avg([-math.log(max(r['probabilities'][r['expected']],1e-12)) for r in vectors])
            bins=[[] for _ in range(5)]
            for r in subset:
                if r['schema_valid'] and r['probabilities'] is not None:
                    probability=max(r['probabilities'].values());bins[min(4,int(probability*5))].append((probability,r['correct']))
            cal_n=sum(map(len,bins))
            ece=sum(abs(sum(p for p,y in bucket)-sum(y for p,y in bucket)) for bucket in bins)/cal_n if cal_n else None
            summary['per_category'][category]={'n':len(subset),'correct':sum(r['correct'] for r in subset),'accuracy':avg([r['correct'] for r in subset]),'macro_f1':avg(list(f1.values())),'brier_sum':brier,'nll':nll,'ece_5_bins':ece,'n_probability_vectors':len(vectors),'n_ece':cal_n}
            official=robust['splits'][split]['per_category'][category]
            for key,expected in [('choice_accuracy_all_planned',summary['per_category'][category]['accuracy']),('macro_f1',avg(list(f1.values())))]:assert equal(official[key],expected),(split,category,key)
            for key,expected in [('multiclass_brier_sum',brier),('nll_clip_1e_12',nll),('ece_5_equal_width_bins',ece)]:assert equal(official['calibration'][key],expected),(split,category,key)
            for label in labels:assert equal(official['per_class'][label]['f1'],f1[label])
        summary['category_macro_f1']=avg([c['macro_f1'] for c in summary['per_category'].values()])
        assert equal(summary['accuracy'],robust['splits'][split]['choice_accuracy_all_planned'])
        assert equal(summary['category_macro_f1'],robust['splits'][split]['category_macro_f1'])
        timing={}
        for key in ['latency_ms','encode_seconds','total_seconds','input_tokens']:
            vals=[raw_by_id[r['id']][key] for r in rows if finite(raw_by_id[r['id']].get(key))]
            timing[key]={'n':len(vals),'min':min(vals) if vals else None,'median':quantile(vals,.5),'p95':quantile(vals,.95),'max':max(vals) if vals else None}
        summary['timing']=timing
        independent['splits'][split]=summary
    pairs=read(BASE/'benchmark/pairs.jsonl')
    for left,right in [('german_id','english_id'),('german_id','mixed_id'),('mixed_id','english_id')]:
        counts=Counter((evaluated[p[left]]['correct'],evaluated[p[right]]['correct']) for p in pairs)
        result={'n':len(pairs),'both_correct':counts[True,True],'left_only_correct':counts[True,False],'right_only_correct':counts[False,True],'both_wrong':counts[False,False]}
        key=f'{left}_vs_{right}'
        assert {k:v for k,v in result.items() if k!='n'}==robust['paired_all_planned'][key]['counts']
        independent['paired_all_planned'][key]=result
    assert not legacy_differences,legacy_differences
    assert not native_coherence,native_coherence
    args.out.write_text(json.dumps(independent,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'pass','counts':{s:{k:v for k,v in d.items() if k not in ['per_category','timing']} for s,d in independent['splits'].items()},'paired':independent['paired_all_planned'],'legacy_report_fields_changed':legacy_differences,'rounded_probability_mismatches':native_coherence},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
