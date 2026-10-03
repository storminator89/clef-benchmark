#!/usr/bin/env python3
"""Offline post-hoc native-answer correctness. Never changes frozen evidence."""
import argparse, collections, hashlib, json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments/jev_comparison/scripts'))
from jev_runner import rows, sha, payload, dumps, CAPACITY, MODEL
from compare import native_fields

def require(ok, message):
    if not ok: raise ValueError(message)

def keyed(items):
    out={(r['suite'],r['id']):r for r in items}
    require(len(out)==len(items),'Duplicate case keys')
    return out

def answer_fields(request, record):
    """Check the original native answer contract except probability normalization."""
    require(record.get('provider_model')==MODEL,'Model mismatch')
    require(record.get('request_body_sha256')==hashlib.sha256(dumps(payload(request)).encode()).hexdigest(),'Request body linkage')
    require(record.get('source_request_sha256')==hashlib.sha256(dumps(request).encode()).hexdigest(),'Source request linkage')
    answers=record.get('answers'); qs=request['questions']
    require(isinstance(answers,dict) and set(answers)==set(qs),'Answer fields mismatch')
    sums={}
    for field,q in qs.items():
        a=answers[field]; require(isinstance(a,dict) and a.get('type')=='choice','Primitive mismatch')
        p=a.get('probabilities'); require(isinstance(p,dict) and set(p)==set(q['criteria']),'Option mismatch')
        require(all(type(v) in (int,float) and math.isfinite(v) and 0<=v<=1 for v in p.values()),'Invalid probability')
        require(a.get('choice') in p and p[a['choice']]==max(p.values()),'Choice is not native maximum')
        v=a.get('confidence');require(type(v) in (int,float) and math.isfinite(v) and 0<=v<=1,'Invalid confidence')
        require(record['probabilities_unrounded'][field]==p,'Stored native vector mismatch')
        sums[field]=math.fsum(p.values())
    usage=record.get('usage');require(isinstance(usage,dict) and all(type(usage.get(k))==int and usage[k]>=0 for k in ('input_tokens','output_tokens')),'Invalid usage')
    require(usage['input_tokens']<=CAPACITY,'Capacity mismatch')
    return answers,sums

def derive(root=ROOT):
    snapshot=root/'experiments/jev_comparison'; run=root/'studies/jev974/run'
    manifest=json.loads((snapshot/'manifest.json').read_text())
    public=json.loads((root/'studies/jev974/PUBLIC_MANIFEST.json').read_text())
    for name,digest in public['files_sha256'].items():
        require(sha(root/'studies/jev974'/name)==digest,'Archived evidence checksum mismatch: '+name)
    sources={}
    def pin(path):sources[str(path.relative_to(root))]=sha(path)
    pin(snapshot/'manifest.json')
    for name,digest in manifest['files'].items():
        require(sha(snapshot/name)==digest,'Frozen input checksum mismatch: '+name);pin(snapshot/name)
    for path in sorted((root/'studies/jev974').rglob('*')):
        if path.is_file():pin(path)
    predictions=keyed(rows(run/'predictions.jsonl'));flags=keyed(rows(run/'flagged_native.jsonl'))
    cases=[]; parts={}; seen=set(); restored=[]
    for suite in manifest['suites']:
        sid=suite['id']; src=snapshot/'inputs'/sid
        requests=rows(src/'requests.jsonl');gold={x['id']:x for x in rows(src/'gold.jsonl')}
        cp={x['id']:x for x in rows(src/'predictions.jsonl')} if suite['baseline']=='complete' else {}
        require(len(requests)==suite['count'] and len(gold)==len(requests),'Frozen count mismatch')
        meta={}
        for name in ['cases.jsonl','diagnostic_cases.jsonl','metadata.jsonl']:
            if (src/name).exists():
                for x in rows(src/name):meta.setdefault(x.get('id',x.get('case_id')),{}).update(x)
        for request in requests:
            cid=request['id'];key=(sid,cid);require(key not in seen,'Duplicate request');seen.add(key)
            g=gold[cid];q=request['request'];expected=g['expected']
            require(set(expected)==set(q['questions']) and all(v in q['questions'][f]['criteria'] for f,v in expected.items()),'Gold mismatch')
            split=g.get('split',meta.get(cid,{}).get('split','diagnostic_pairs' if sid=='minimal_pairs48' else 'attack_removal_diagnostic' if sid=='attack_ablation14' else 'german_primary'))
            if sid=='attack_ablation14':split+='/'+g['condition']
            pk=(sid,split)
            if pk not in parts:parts[pk]={'suite':sid,'split':split,'planned':0,'expected':0,'baseline_status':suite['baseline'],'clef_correct':0 if cp else None,'clef_answered':0 if cp else None,'jev_correct':0,'jev_answered':0,'jev_sum_only_answers':0,'jev_no_answer':0}
            part=parts[pk];part['planned']+=1;part['expected']+=1
            pred=predictions[key]; native=pred if pred['status']=='valid' else flags.get(key)
            sums=None; jf=None;status='no_evaluable_native_answer'
            if native:
                jf,sums=answer_fields(q,native)
                deviation=any(abs(v-1)>1e-5 for v in sums.values())
                if key in flags:
                    require(pred['status']=='failed' and pred.get('error_code')=='probability_sum_outside_tolerance','Flag status mismatch')
                    require(deviation and native['diagnostic']['sum_only_deviation'] is True,'Not sum-only')
                    restored.append({'suite':sid,'id':cid,'native_probability_sums':sums});part['jev_sum_only_answers']+=1;status='native_answer_sum_only_deviation'
                else:require(not deviation,'Strict record has sum deviation');status='native_answer'
            cf=native_fields(q,cp.get(cid),'clef') if cp else None
            choices={model:{f:a['choice'] for f,a in fields.items()} if fields else None for model,fields in [('clef',cf),('jev',jf)]}
            exact={model:choice==expected if choice is not None else None for model,choice in choices.items()}
            for model in ['clef','jev']:
                if choices[model] is not None:part[model+'_answered']+=1;part[model+'_correct']+=int(exact[model])
            part['jev_no_answer']+=jf is None
            cases.append({'suite':sid,'id':cid,'split':split,'expected':expected,'choices':choices,'exact':exact,'evaluable':{m:choices[m] is not None for m in choices},'jev_answer_status':status,'jev_native_probability_sums':sums})
    require(seen==set(predictions),'Prediction case set mismatch');require(set(flags)<=seen,'Unknown flags')
    require(len(cases)==974 and len(restored)==35 and sum(x['jev_no_answer'] for x in parts.values())==2,'Frozen outcome counts changed')
    for part in parts.values():
        for model in ['clef','jev']:part[model+'_accuracy_all_expected']=part[model+'_correct']/part['planned'] if part[model+'_correct'] is not None else None
    summary={'metric_version':'native-answer-correctness-v1','analysis':'Post-hoc descriptive exact native-answer correctness / all planned cases, separately partitioned. No pooled accuracy or calibration claim.','metric_change':'Probability normalization is diagnostic only for this new answer-correctness analysis; original strict scoring and raw evidence are unchanged.','no_answer_note':'Two archived Jev responses have no recoverable evaluable native answer. They count as not correct in planned-case denominators, not as known semantic errors.','partitions':list(parts.values()),'case_count':974,'jev_answered':972,'jev_sum_only_answers':35,'jev_no_answer':2,'baseline_pending':['massive300'],'input_sha256':sources}
    return summary,cases,restored

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    summary,cases,restored=derive();args.output.mkdir(parents=True,exist_ok=False)
    for name,value in [('comparison_summary.json',summary),('restored_native_answers.json',restored)]: (args.output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    (args.output/'case_comparison.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n' for x in cases))
    print(json.dumps({'cases':len(cases),'restored':len(restored),'partitions':len(summary['partitions'])}))
if __name__=='__main__':main()
