#!/usr/bin/env python3
"""Offline paired scoring only; never reads a credential or makes a network call."""
import argparse, collections, hashlib, json, math, statistics
from pathlib import Path
from jev_runner import rows, write, sha, payload, validate_response, ContractError
THRESHOLDS=[.5,.7,.8,.9,.95,.99]

def indexed(rs):
    if len({r['id'] for r in rs})!=len(rs):raise ContractError('Duplicate scoring IDs')
    return {r['id']:r for r in rs}

def probability_metrics(items,expected):
    n=len(items);correct=sum(x['correct'] for x in items);zero=sum(x['p_gold']==0 for x in items)
    ece=0;bins=[]
    for b in range(10):
        selected=[x for x in items if min(9,int(x['p_selected']*10))==b]
        acc=sum(x['correct'] for x in selected)/len(selected) if selected else None
        conf=sum(x['p_selected'] for x in selected)/len(selected) if selected else None
        if selected:ece+=len(selected)/n*abs(acc-conf)
        bins.append({'bin':b,'n':len(selected),'accuracy':acc,'mean_selected_probability':conf})
    return {'expected':expected,'valid':n,'invalid_or_missing':expected-n,'correct':correct,'accuracy_all_expected':correct/expected if expected else None,'accuracy_valid_only':correct/n if n else None,'brier_multiclass_sum':sum(x['brier'] for x in items)/n if n else None,'nll':None if zero or not n else -sum(math.log(x['p_gold']) for x in items)/n,'nll_is_infinite':bool(zero),'zero_gold_probability_count':zero,'ece_10_equal_width_bins':ece if n else None,'ece_bins':bins,'risk_coverage':[{'threshold':t,'selected':len(s:=[x for x in items if x['p_selected']>=t]),'errors':sum(not x['correct'] for x in s),'coverage_all_expected':len(s)/expected if expected else None,'risk':sum(not x['correct'] for x in s)/len(s) if s else None} for t in THRESHOLDS]}

def native_fields(request,pred,model):
    if not pred:return None
    qs=request['questions']
    if model=='jev':
        if pred.get('status')!='valid':return None
        n=validate_response(payload(request),{'model':pred.get('provider_model'),'answers':pred.get('answers'),'usage':pred.get('usage')});return n['answers']
    if pred.get('truncated') is not False or 'error' in pred:raise ContractError('Invalid Clef baseline')
    if set(pred.get('answers',{}))!=set(qs) or set(pred.get('probabilities_unrounded',{}))!=set(qs):raise ContractError('Clef baseline field mismatch')
    out={}
    for f,q in qs.items():
        a=pred['answers'][f];p=pred['probabilities_unrounded'][f]
        if set(p)!=set(q['criteria']) or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in p.values()) or abs(math.fsum(p.values())-1)>1e-5:raise ContractError('Invalid Clef probability vector')
        if a.get('choice') not in p or p[a['choice']]!=max(p.values()):raise ContractError('Invalid Clef native choice')
        out[f]={'choice':a['choice'],'probabilities':p,'confidence':a.get('confidence')}
    return out

def confusion(items,options):
    matrix={g:{p:0 for p in options+['__missing__']} for g in options}
    for x in items:matrix[x['gold']][x['choice'] if x['choice'] in options else '__missing__']+=1
    classes=[]
    for label in options:
        tp=matrix[label][label];support=sum(matrix[label].values());predicted=sum(matrix[g][label] for g in options);den=support+predicted
        classes.append({'label':label,'support':support,'predicted':predicted,'tp':tp,'precision':tp/predicted if predicted else 0,'recall':tp/support if support else None,'f1_zero_division_0':2*tp/den if den else 0})
    supported=[x for x in classes if x['support']]
    return {'n':len(items),'classes':classes,'confusion':matrix,'macro_f1_gold_supported':sum(x['f1_zero_division_0'] for x in supported)/len(supported) if supported else None,'gold_supported_label_count':len(supported),'macro_f1_fixed_options_zero_division_0':sum(x['f1_zero_division_0'] for x in classes)/len(classes)}

def compare(root,run_dir,out):
    manifest=json.loads((root/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        if sha(root/name)!=digest:raise ContractError('Scoring source checksum mismatch')
    observed=rows(run_dir/'predictions.jsonl');by_suite=collections.defaultdict(list)
    for r in observed:by_suite[r['suite']].append(r)
    expected_suites={s['id'] for s in manifest['suites']}
    if set(by_suite)-expected_suites:raise ContractError('Unexpected result suite')
    groups=collections.defaultdict(lambda:{'expected':0,'clef':[],'jev':[]});partitions={};case_records=[];special={};latencies={}
    for suite in manifest['suites']:
        sid=suite['id'];src=root/'inputs'/sid;requests=rows(src/'requests.jsonl');gold=indexed(rows(src/'gold.jsonl'));jp=indexed(by_suite[sid]);cp=indexed(rows(src/'predictions.jsonl')) if suite['baseline']=='complete' else {}
        ids={r['id'] for r in requests}
        if set(jp)-ids or (suite['baseline']=='complete' and set(cp)!=ids):raise ContractError('Prediction IDs do not match frozen suite')
        meta={}
        for f in ['cases.jsonl','diagnostic_cases.jsonl','metadata.jsonl']:
            if (src/f).exists():
                for r in rows(src/f):meta.setdefault(r.get('id',r.get('case_id')),{}).update(r)
        local_cases=[];intent_items={'jev':[],'clef':[]}
        for r in requests:
            cid=r['id'];g=gold[cid];m=meta.get(cid,{});split=g.get('split',m.get('split','diagnostic_pairs' if sid=='minimal_pairs48' else 'attack_removal_diagnostic' if sid=='attack_ablation14' else 'german_primary'))
            if sid=='attack_ablation14': split+='/'+g['condition']
            partkey=sid+'|'+split
            partitions.setdefault(partkey,{'suite':sid,'split':split,'expected':0,'clef_valid':0,'jev_valid':0,'clef_correct':0,'jev_correct':0,'both_valid':0,'both_correct':0,'clef_only_correct':0,'jev_only_correct':0,'both_wrong':0,'prediction_agreement':0,'baseline_status':suite['baseline']})
            part=partitions[partkey];part['expected']+=1
            if jp.get(cid,{}).get('status')=='valid':
                exact_body=json.dumps(payload(r['request']),ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
                if jp[cid].get('request_body_sha256')!=hashlib.sha256(exact_body).hexdigest():raise ContractError('Jev result input hash mismatch')
            model_fields={'clef':native_fields(r['request'],cp.get(cid),'clef'),'jev':native_fields(r['request'],jp.get(cid),'jev')};case={'suite':sid,'id':cid,'split':split,'expected':g['expected'],'choices':{},'exact':{}}
            if set(g['expected'])!=set(r['request']['questions']):raise ContractError('Gold/question fields mismatch')
            for f,q in r['request']['questions'].items():
                if g['expected'][f] not in q['criteria']:raise ContractError('Gold option not in frozen schema')
                groupkey=json.dumps({'suite':sid,'split':split,'category':g.get('category',m.get('category',m.get('domain',g.get('area')))),'field':f,'option_keys':sorted(q['criteria'])},sort_keys=True)
                group=groups[groupkey];group['expected']+=1
                for model,fs in model_fields.items():
                    if fs:
                        a=fs[f];p=a['probabilities'];label=g['expected'][f];choice=a['choice']
                        group[model].append({'id':cid,'correct':choice==label,'gold':label,'choice':choice,'p_selected':p[choice],'p_gold':p[label],'brier':sum((v-int(k==label))**2 for k,v in p.items()),'native_confidence':a.get('confidence')})
            for model,fs in model_fields.items():
                case['choices'][model]={f:a['choice'] for f,a in fs.items()} if fs else None;case['exact'][model]=case['choices'][model]==g['expected'] if fs else None
                if fs:part[model+'_valid']+=1;part[model+'_correct']+=int(case['exact'][model])
                if sid=='massive300':intent_items[model].append({'id':cid,'source_id':g['source_id'],'gold':g['expected']['intent'],'choice':fs['intent']['choice'] if fs else None})
            if all(model_fields.values()):
                part['both_valid']+=1;c,j=case['exact']['clef'],case['exact']['jev'];part['both_correct' if c and j else 'clef_only_correct' if c else 'jev_only_correct' if j else 'both_wrong']+=1;part['prediction_agreement']+=int(case['choices']['clef']==case['choices']['jev'])
            local_cases.append(case);case_records.append(case)
        if sid=='massive300':
            design=json.loads((src/'design_summary.json').read_text());ov=design['exact_normalized_overlap'];train=set(ov['selected_with_train']);both=train|set(ov['selected_with_dev']);options=list(requests[0]['request']['questions']['intent']['criteria']);special[sid]={}
            for model,items in intent_items.items():
                if model=='clef' and not cp:special[sid][model]={'status':'awaiting_final_audited_baseline'};continue
                special[sid][model]={name:confusion([x for x in items if x['source_id'] not in exclude],options) for name,exclude in [('primary300',set()),('no_exact_train_overlap285',train),('no_exact_train_or_dev_overlap284',both)]}
        if sid=='minimal_pairs48':
            ci=indexed(local_cases);special[sid]=[]
            for pair in rows(src/'pairs.jsonl'):
                a,b=[ci[x] for x in pair['case_ids']];pr={'pair_id':pair['id'],'kind':pair['kind'],'models':{}}
                for model in ['clef','jev']:
                    valid=a['choices'][model] is not None and b['choices'][model] is not None;stable=valid and a['choices'][model]==b['choices'][model]
                    pr['models'][model]={'valid':valid,'both_correct':valid and bool(a['exact'][model]) and bool(b['exact'][model]),'stable':stable if valid else None,'stable_wrong':stable and not(a['exact'][model] and b['exact'][model]),'correct_transition':valid and bool(a['exact'][model]) and bool(b['exact'][model])}
                special[sid].append(pr)
        if sid=='attack_ablation14':
            ci=indexed(local_cases);special[sid]=[]
            for pair in rows(src/'pairs.jsonl'):
                attack,clean=ci[pair['attack_id']],ci[pair['clean_id']];pr={'source_id':pair['source_id'],'models':{}}
                for model in ['clef','jev']:
                    valid=attack['choices'][model] is not None and clean['choices'][model] is not None
                    pr['models'][model]={'valid':valid,'attack_correct':attack['exact'][model],'clean_correct':clean['exact'][model],'unchanged_choice':attack['choices'][model]==clean['choices'][model] if valid else None,'recovered_after_removal':bool(not attack['exact'][model] and clean['exact'][model]) if valid else None,'regressed_after_removal':bool(attack['exact'][model] and not clean['exact'][model]) if valid else None}
                special[sid].append(pr)
        if sid in ['original_text180','finance100']:
            ci=indexed(local_cases);special[sid]={'language_control_pairs':[]}
            for pair in rows(src/'pairs.jsonl'):
                pr={'pair_id':pair['pair_id'],'members':{k:pair[k] for k in ['german_id','english_id','mixed_id'] if k in pair},'models':{}}
                members=[ci[cid] for cid in pr['members'].values()]
                for model in ['clef','jev']:
                    valid=all(c['choices'][model] is not None for c in members)
                    pr['models'][model]={'valid':valid,'all_correct':all(c['exact'][model] for c in members) if valid else None,'all_agree':all(c['choices'][model]==members[0]['choices'][model] for c in members) if valid else None}
                special[sid]['language_control_pairs'].append(pr)
        latency={}
        for model,predictions,key in [('clef',list(cp.values()),'inference_seconds'),('jev',list(jp.values()),'request_seconds')]:
            values=sorted(p[key] for p in predictions if key in p and isinstance(p[key],(int,float)))
            latency[model]={'definition':'local CPU-NF4 forward only' if model=='clef' else 'hosted HTTP request through body read; network and provider queue included','n':len(values),'median_seconds':statistics.median(values) if values else None,'p95_nearest_rank_seconds':values[max(0,math.ceil(.95*len(values))-1)] if values else None}
        latencies[sid]=latency
    for part in partitions.values():
        for model in ['clef','jev']:
            part[model+'_accuracy_all_expected']=part[model+'_correct']/part['expected'] if model!='clef' or part['baseline_status']=='complete' else None
            part[model+'_accuracy_valid_only']=part[model+'_correct']/part[model+'_valid'] if part[model+'_valid'] else None
    out.mkdir(parents=True,exist_ok=False)
    write(out/'comparison_summary.json',{'analysis':'paired, descriptive, separately partitioned; no pooled score or significance claims','manifest_sha256':sha(root/'manifest.json'),'latency_comparability':'Different hardware, precision, service and timing boundary. No model-speed ratio or apples-to-apples latency claim.','confidence_definition':'Thresholds use selected-option native probability for both models. Jev confidence is retained separately; Clef confidence in historical data is rounded selected probability.','partitions':list(partitions.values()),'excluded':manifest['excluded'],'baseline_pending':[s['id'] for s in manifest['suites'] if s['baseline']!='complete']})
    write(out/'field_metrics.json',[{'group':json.loads(k),'clef':({'status':'awaiting_final_audited_baseline'} if json.loads(k)['suite']=='massive300' and not v['clef'] else probability_metrics(v['clef'],v['expected'])),'jev':probability_metrics(v['jev'],v['expected'])} for k,v in sorted(groups.items())]);write(out/'special_diagnostics.json',special);write(out/'latency.json',latencies)
    (out/'case_comparison.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in case_records))
    return {'scored_expected_cases':len(case_records),'partitions':len(partitions),'field_groups':len(groups),'baseline_pending':[s['id'] for s in manifest['suites'] if s['baseline']!='complete']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(compare(a.root,a.run,a.output)))
