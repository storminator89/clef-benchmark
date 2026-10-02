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
    if not isinstance(row,dict):result['error']='non_object_output_record';return result
    if row.get('error'):result['error']='runtime_error: '+str(row['error']); return result
    response=row.get('response',row.get('result',row))
    # Accept an unmodified Workers AI envelope as well as native systemone output.
    if isinstance(response,dict) and 'answers' not in response and isinstance(response.get('result'),dict):response=response['result']
    if not isinstance(response,dict):result['error']='non_object_response';return result
    answers=response.get('answers',{})
    if not isinstance(answers,dict):result['error']='non_object_answers';return result
    a=answers.get('decision',{})
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
    return {'n_planned':n,'n_present':sum(r['present'] for r in rows),'n_choice_valid':len(valid),'n_schema_valid':len(schema),'choice_accuracy_all_planned':mean([r['correct'] for r in rows]),'strict_accuracy_all_planned':mean([r['strict_correct'] for r in rows]),'accuracy_valid_choices_only':mean([r['correct'] for r in valid]),'choice_validity_all_planned':ratio(len(valid),n),'schema_validity_all_planned':ratio(len(schema),n),'schema_validity_present':ratio(len(schema),sum(r['present'] for r in rows)),'macro_f1':mean([x['f1'] for x in classes.values()]),'macro_f1_all_policy_labels':mean([x['f1'] for x in classes.values()]),'macro_f1_observed_support':mean([x['f1'] for x in classes.values() if x['support']>0]),'per_class':classes,'confusion':{label:dict(collections.Counter(r['prediction'] if r['choice_valid'] else '__invalid_or_missing__' for r in rows if r['expected']==label)) for label in labels},'calibration':{'n_probability_vectors':len(probs),'n_schema_valid_ece':len(cal),'multiclass_brier_sum':mean([r['brier'] for r in probs]),'nll_clip_1e_12':mean([r['nll'] for r in probs]),'ece_5_equal_width_bins':ece,'bins':bins},'latency_ms':{'n':len(latency),'median':percentile(latency,.5),'p95':percentile(latency,.95)},'confidence_deferral':{str(t):{'accepted':sum(r['max_probability']>=t for r in schema),'coverage_all_planned':ratio(sum(r['max_probability']>=t for r in schema),n),'accepted_accuracy':mean([r['correct'] for r in schema if r['max_probability']>=t])} for t in (.6,.8,.9,.95)}}

INFO_LABELS={
'anliegen_priorisierung':{'rueckfrage'},
'unterlagenabgleich':{'unterlage_fehlt','version_klaeren'},
'beitragsrechnung':{'daten_fehlen'},
'vorgangsstand':{'unterlagen_nachfordern','zuordnung_klaeren'},
'rueckfrageplanung':{'zuordnung','zeitpunkt','unterlage','umfang'},
'finanzservice_routing':{'rueckfrage'}}

def overall(rows):
    return {'n_planned':len(rows),'n_present':sum(r['present'] for r in rows),'n_choice_valid':sum(r['choice_valid'] for r in rows),'n_schema_valid':sum(r['schema_valid'] for r in rows),'correct':sum(r['correct'] for r in rows),'choice_accuracy_all_planned':mean([r['correct'] for r in rows]),'strict_accuracy_all_planned':mean([r['strict_correct'] for r in rows]),'accuracy_valid_choices_only':mean([r['correct'] for r in rows if r['choice_valid']])}

def score(cases,raw):
    for i,row in enumerate(raw,1):
        if not isinstance(row,dict) or not isinstance(row.get('id'),str) or not row['id']:
            raise ValueError(f'Output line {i} requires a nonempty string id')
    ids=[r['id'] for r in raw]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate output ids')
    unknown=set(ids)-{c['id'] for c in cases}
    if unknown:raise ValueError(f'Unknown output ids: {sorted(unknown)}')
    byoutput={r['id']:r for r in raw}
    rows=[inspect(c,byoutput.get(c['id'])) for c in cases]
    byid={r['id']:r for r in rows}
    categories={cat:metrics([byid[c['id']] for c in cases if c['category']==cat],list(next(c for c in cases if c['category']==cat)['questions']['decision']['criteria'])) for cat in sorted({c['category'] for c in cases})}
    infod=[]
    for c in cases:
        r=byid[c['id']]
        needed=c['information_status']=='missing_or_unresolved'
        predicted=r['choice_valid'] and r['prediction'] in INFO_LABELS[c['category']]
        infod.append((needed,predicted,r))
    goldneeded=sum(a for a,b,r in infod); predictedneeded=sum(b for a,b,r in infod)
    info={'definition':'Only asks for missing/unresolved task input. A fachgespraech label is routing, not information abstention.', 'n_gold_missing_or_unresolved':goldneeded,'n_gold_sufficient':len(rows)-goldneeded,'precision':ratio(sum(a and b for a,b,r in infod),predictedneeded),'recall':ratio(sum(a and b for a,b,r in infod),goldneeded),'unnecessary_information_request_rate':ratio(sum(not a and b for a,b,r in infod),len(rows)-goldneeded),'missed_information_request_valid_choice_rate_all_needed':ratio(sum(a and r['choice_valid'] and not b for a,b,r in infod),goldneeded),'invalid_or_missing_on_needed':sum(a and not r['choice_valid'] for a,b,r in infod),'exact_choice_accuracy_on_needed':mean([r['correct'] for a,b,r in infod if a])}
    result={'scoring_version':'clean-realistic-de-v1','counts':{'planned':len(cases),'present':len(raw)},'overall':overall(rows),'category_macro_f1':mean([r['macro_f1'] for r in categories.values()]),'per_category':categories,'by_information_status':{s:overall([byid[c['id']] for c in cases if c['information_status']==s]) for s in ('sufficient','missing_or_unresolved')},'by_complexity_tag':{t:overall([byid[c['id']] for c in cases if t in c['tags']]) for t in sorted({t for c in cases for t in c['tags']})},'information_request_diagnostic':info,'errors':[{k:r[k] for k in ('id','error','prediction','expected')} for r in rows if r['error']],'case_results':rows,'interpretation_warning':'72 independently authored synthetic, purposively selected German routing/check cases. No real customer data, production validation, free-answer evaluation, advice, eligibility or legal conclusions. Do not pool with previous benchmarks or infer manipulation robustness from this clean set.'}
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('outputs');ap.add_argument('--out',required=True);args=ap.parse_args()
    result=score(read(D/'cases.jsonl'),read(args.outputs))
    result['outputs_file']=str(pathlib.Path(args.outputs));result['request_sha256']=__import__('hashlib').sha256((D/'requests.jsonl').read_bytes()).hexdigest()
    pathlib.Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'counts':result['counts'],'overall':result['overall'],'category_macro_f1':result['category_macro_f1']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
