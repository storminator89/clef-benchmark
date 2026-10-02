#!/usr/bin/env python3
"""Offline scorer. Never sends gold to an inference endpoint. Standard library only."""
import argparse, collections, json, math, pathlib, statistics
D=pathlib.Path(__file__).resolve().parent

def read(path):
    return [json.loads(line) for line in pathlib.Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]

def number(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)

def mean(xs):
    return sum(xs)/len(xs) if xs else None

def ratio(a,b):
    return a/b if b else None

def percentile(xs,q):
    if not xs:return None
    ys=sorted(xs); p=(len(ys)-1)*q; lo=math.floor(p); hi=math.ceil(p)
    return ys[lo]+(ys[hi]-ys[lo])*(p-lo)

def inspect(c,row):
    labels=list(c['questions']['decision']['criteria'])
    result={'id':c['id'],'category':c['category'],'split':c['split'],'expected':c['expected']['decision'],'present':row is not None,'choice_valid':False,'schema_valid':False,'probabilities_valid':False,'prediction':None,'correct':False,'strict_correct':False,'error':None}
    if row is None: result['error']='missing_output'; return result
    if row.get('error'):result['error']='runtime_error: '+str(row['error']); return result
    response=row.get('response',row.get('result',row))
    # Accept an unmodified Workers AI envelope as well as native systemone output.
    if isinstance(response,dict) and 'answers' not in response and isinstance(response.get('result'),dict):response=response['result']
    a=response.get('answers',{}).get('decision',{}) if isinstance(response,dict) else {}
    if not isinstance(a,dict):result['error']='non_object_answer'; return result
    pred=a.get('choice'); result['prediction']=pred
    result['choice_valid']=isinstance(pred,str) and pred in labels
    result['correct']=result['choice_valid'] and pred==result['expected']
    p=a.get('probabilities'); conf=a.get('confidence')
    pv=isinstance(p,dict) and set(p)==set(labels) and all(number(x) and 0<=x<=1 for x in p.values()) and abs(sum(p.values())-1)<=.001
    result['probabilities_valid']=pv
    if pv:
        norm=sum(p.values()); p={k:v/norm for k,v in p.items()}
        result['probabilities']=p
        result['brier']=sum((p[k]-(k==result['expected']))**2 for k in labels)
        result['nll']=-math.log(max(p[result['expected']],1e-12))
        result['max_probability']=max(p.values())
    valid_argmax=pv and result['choice_valid'] and p[pred]>=max(p.values())-.00011
    valid_conf=number(conf) and 0<=conf<=1 and pv and result['choice_valid'] and abs(conf-p[pred])<=.001
    result['schema_valid']=a.get('type')=='choice' and result['choice_valid'] and pv and valid_argmax and valid_conf
    result['strict_correct']=result['correct'] and result['schema_valid']
    if not result['schema_valid']:result['error']='invalid_or_incomplete_native_choice_schema'
    latency=row.get('latency_ms',row.get('elapsed_ms'))
    if number(latency) and latency>=0:result['latency_ms']=latency
    # Prefer preserved full precision for calibration; keep native rounded schema checks above.
    unrounded=row.get('probabilities_unrounded',{}).get('decision') if isinstance(row.get('probabilities_unrounded',{}),dict) else None
    if isinstance(unrounded,dict) and set(unrounded)==set(labels) and all(number(x) and 0<=x<=1 for x in unrounded.values()) and abs(sum(unrounded.values())-1)<1e-5:
        if result['choice_valid'] and unrounded[pred]<max(unrounded.values())-1e-7:
            result['schema_valid']=False;result['strict_correct']=False;result['error']='choice_disagrees_with_unrounded_argmax'
        p={k:v/sum(unrounded.values()) for k,v in unrounded.items()}
        result['probabilities_valid']=True;result['probabilities']=p;result['probability_source']='unrounded'
        result['brier']=sum((p[k]-(k==result['expected']))**2 for k in labels)
        result['nll']=-math.log(max(p[result['expected']],1e-12))
        result['max_probability']=max(p.values())
    elif pv:result['probability_source']='native_rounded'
    return result

def metrics(rows,labels):
    n=len(rows); valid=[r for r in rows if r['choice_valid']]; schema=[r for r in rows if r['schema_valid']]
    classes={}
    for label in labels:
        tp=sum(r['expected']==label and r['prediction']==label and r['choice_valid'] for r in rows)
        fp=sum(r['expected']!=label and r['prediction']==label and r['choice_valid'] for r in rows)
        fn=sum(r['expected']==label and not (r['prediction']==label and r['choice_valid']) for r in rows)
        classes[label]={'support':tp+fn,'precision':ratio(tp,tp+fp),'recall':ratio(tp,tp+fn),'f1':ratio(2*tp,2*tp+fp+fn) or 0}
    probs=[r for r in rows if r['probabilities_valid']]
    cal=[r for r in schema if r['probabilities_valid']]
    bins=[]
    for i in range(5):
        selected=[r for r in cal if min(4,int(r['max_probability']*5))==i]
        bins.append({'lower':i/5,'upper':(i+1)/5,'n':len(selected),'accuracy':mean([r['correct'] for r in selected]),'confidence':mean([r['max_probability'] for r in selected])})
    ece=sum(b['n']*abs(b['accuracy']-b['confidence']) for b in bins if b['n'])/len(cal) if cal else None
    latency=[r['latency_ms'] for r in rows if 'latency_ms' in r]
    return {'n_planned':n,'n_present':sum(r['present'] for r in rows),'n_choice_valid':len(valid),'n_schema_valid':len(schema),'choice_accuracy_all_planned':mean([r['correct'] for r in rows]),'strict_accuracy_all_planned':mean([r['strict_correct'] for r in rows]),'accuracy_valid_choices_only':mean([r['correct'] for r in valid]),'choice_validity_all_planned':ratio(len(valid),n),'schema_validity_all_planned':ratio(len(schema),n),'schema_validity_present':ratio(len(schema),sum(r['present'] for r in rows)),'macro_f1':mean([x['f1'] for x in classes.values()]),'per_class':classes,'confusion':{label:dict(collections.Counter(r['prediction'] if r['choice_valid'] else '__invalid_or_missing__' for r in rows if r['expected']==label)) for label in labels},'calibration':{'n_probability_vectors':len(probs),'n_schema_valid_ece':len(cal),'multiclass_brier_sum':mean([r['brier'] for r in probs]),'nll_clip_1e_12':mean([r['nll'] for r in probs]),'ece_5_equal_width_bins':ece,'bins':bins},'latency_ms':{'n':len(latency),'median':percentile(latency,.5),'p95':percentile(latency,.95)},'confidence_deferral':{str(t):{'accepted':sum(r['max_probability']>=t for r in schema),'coverage_all_planned':ratio(sum(r['max_probability']>=t for r in schema),n),'accepted_accuracy':mean([r['correct'] for r in schema if r['max_probability']>=t])} for t in (.6,.8,.9,.95)}}

def paired(pairs,by_id,left,right):
    usable=[(by_id[p[left]],by_id[p[right]]) for p in pairs if by_id[p[left]]['choice_valid'] and by_id[p[right]]['choice_valid']]
    counts=collections.Counter(('both_correct' if a['correct'] and b['correct'] else 'left_only_correct' if a['correct'] else 'right_only_correct' if b['correct'] else 'both_wrong') for a,b in usable)
    b=counts['left_only_correct']; c=counts['right_only_correct']; dis=b+c
    pvalue=min(1,2*sum(math.comb(dis,k) for k in range(min(b,c)+1))/2**dis) if dis else 1.0
    return {'left':left,'right':right,'n_pairs_planned':len(pairs),'n_pairs_valid_both':len(usable),'left_accuracy':mean([a['correct'] for a,b in usable]),'right_accuracy':mean([b['correct'] for a,b in usable]),'left_minus_right_accuracy':mean([int(a['correct'])-int(b['correct']) for a,b in usable]),'counts':{k:counts[k] for k in ('both_correct','left_only_correct','right_only_correct','both_wrong')},'exact_mcnemar_two_sided_p':pvalue if usable else None,'warning':'Small deliberately selected paired subset; missing/invalid pairs excluded and counted explicitly. Do not generalize or claim statistical power.'}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('outputs');parser.add_argument('--out',required=True);args=parser.parse_args()
    cases=read(D/'cases.jsonl')+read(D/'diagnostic_cases.jsonl');raw=read(args.outputs)
    ids=[r.get('id') for r in raw]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate output ids: refusing silent overwrite')
    known={c['id'] for c in cases};unknown=set(ids)-known
    if unknown:raise ValueError(f'Unknown output ids: {unknown}')
    output={r['id']:r for r in raw};evaluated=[inspect(c,output.get(c['id'])) for c in cases];by_id={r['id']:r for r in evaluated}
    report={'scoring_version':'1.0','outputs_file':str(pathlib.Path(args.outputs)),'counts':{'planned':len(cases),'present':len(raw)},'splits':{},'paired':{},'abstention':{},'errors':[{k:r[k] for k in ('id','error','prediction','expected')} for r in evaluated if r['error']]}
    for split in ('german_primary','english_control','mixed_schema_diagnostic'):
        cats={}
        for cat in sorted({c['category'] for c in cases}):
            matching=[c for c in cases if c['category']==cat and c['split']==split];labels=list(matching[0]['questions']['decision']['criteria'])
            cats[cat]=metrics([by_id[c['id']] for c in matching],labels)
        rows=[r for r in evaluated if r['split']==split]
        report['splits'][split]={'n_planned':len(rows),'n_present':sum(r['present'] for r in rows),'choice_accuracy_all_planned':mean([r['correct'] for r in rows]),'strict_accuracy_all_planned':mean([r['strict_correct'] for r in rows]),'category_macro_f1':mean([v['macro_f1'] for v in cats.values()]),'per_category':cats}
    pairs=read(D/'pairs.jsonl')
    for left,right in (('german_id','english_id'),('german_id','mixed_id'),('mixed_id','english_id')):
        report['paired'][f'{left}_vs_{right}']=paired(pairs,by_id,left,right)
    for cat,abstain in [('it_routing',{'clarify'}),('ambiguity_abstain',{'missing','conflict','unsupported'})]:
        rows=[r for r in evaluated if r['category']==cat and r['split']=='german_primary']
        tp=sum(r['choice_valid'] and r['prediction'] in abstain and r['expected'] in abstain for r in rows)
        fp=sum(r['choice_valid'] and r['prediction'] in abstain and r['expected'] not in abstain for r in rows)
        fn=sum(r['expected'] in abstain and not(r['choice_valid'] and r['prediction'] in abstain) for r in rows)
        report['abstention'][cat]={'labels':sorted(abstain),'precision':ratio(tp,tp+fp),'recall':ratio(tp,tp+fn),'unnecessary_abstention_rate':ratio(fp,sum(r['expected'] not in abstain for r in rows)),'unsafe_commitment_rate':ratio(sum(r['choice_valid'] and r['expected'] in abstain and r['prediction'] not in abstain for r in rows),sum(r['expected'] in abstain for r in rows)),'invalid_or_missing':sum(not r['choice_valid'] for r in rows)}
    report['case_results']=evaluated
    pathlib.Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'counts':report['counts'],'splits':{k:{a:b for a,b in v.items() if a!='per_category'} for k,v in report['splits'].items()}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
