#!/usr/bin/env python3
"""Validate frozen public scientific sources and describe each native-score field separately."""
import argparse, hashlib, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
from metrics import field_metrics, THRESHOLDS

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read_json(path): return json.loads(path.read_text())
def read_rows(path): return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
def write_json(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def write_rows(path,rows):path.write_text(''.join(json.dumps(x,ensure_ascii=False,allow_nan=False)+'\n' for x in rows))
def index(rows):
    grouped=defaultdict(list)
    for row in rows:grouped[row.get('id')].append(row)
    return grouped

def normalized_sources(root,sid):
    src=root/'sources'/sid; requests=read_rows(src/'requests.jsonl');predictions=read_rows(src/'predictions.jsonl')
    if sid=='insurance60':
        data=read_json(src/'benchmark.json');cases={r['id']:r for r in data['cases']}
        gold=[{'id':r['id'],'expected':{k:r['expected'][k] for k in ['decision','evidence']},'document_id':r['document_id'],'area':r['area']} for r in data['cases']]
    else:
        gold=read_rows(src/'gold.jsonl'); cases={}
        for f in ['cases.jsonl','diagnostic_cases.jsonl']:
            if (src/f).exists():
                for row in read_rows(src/f):cases[row.get('id',row.get('case_id'))]=row
    return requests,gold,predictions,cases

def partition(sid,gold,case):
    if sid in ['original_text180','finance100','clean72','attack_ablation14']:
        return {k:gold.get(k,case.get(k,'unspecified')) for k in ['category','language','schema_language']} | ({'condition':gold['condition']} if sid=='attack_ablation14' else {})
    if sid=='images90':return {k:gold[k] for k in ['kind','language','condition']}
    return {}

def probability_issues(question,answer,probabilities,gold):
    errors=[]
    if question.get('type')!='choice' or not isinstance(question.get('criteria'),dict) or not question['criteria']:
        return ['invalid_request_choice_schema']
    options=question['criteria']
    if gold not in options:errors.append('gold_not_in_options')
    if not isinstance(answer,dict) or answer.get('type')!='choice':return errors+['invalid_or_missing_native_answer']
    if not isinstance(probabilities,dict) or set(probabilities)!=set(options):return errors+['invalid_or_missing_unrounded_options']
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in probabilities.values()):return errors+['invalid_probability_value']
    if abs(math.fsum(probabilities.values())-1)>1e-5:errors.append('probability_sum_outside_tolerance')
    choice=answer.get('choice')
    if choice not in options:errors.append('native_choice_not_in_options')
    elif probabilities[choice]!=max(probabilities.values()):errors.append('native_choice_not_exact_maximum')
    displayed=answer.get('probabilities')
    if not isinstance(displayed,dict) or set(displayed)!=set(options):errors.append('displayed_probability_schema_mismatch')
    elif any(isinstance(displayed[k],bool) or not isinstance(displayed[k],(int,float)) or not math.isfinite(displayed[k]) or abs(displayed[k]-probabilities[k])>5.0001e-5 for k in options):errors.append('displayed_probability_rounding_mismatch')
    confidence=answer.get('confidence')
    if choice in options and (isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not math.isfinite(confidence) or abs(confidence-probabilities[choice])>5.0001e-5):errors.append('displayed_confidence_rounding_mismatch')
    return errors

def build_rows(root, inventory):
    normalized=[]; case_rows=[]; suite_audits=[]
    for info in inventory['suites']:
        sid=info['suite_id'];reqs,golds,preds,cases=normalized_sources(root,sid)
        ri=index(reqs);gi=index(golds);pi=index(preds)
        expected_ids=[r['id'] for r in reqs]
        expected_set=set(expected_ids)
        audit={'suite_id':sid,'expected_count':info['expected_request_count'],'request_rows':len(reqs),'gold_rows':len(golds),'prediction_rows':len(preds),
               'missing_prediction_ids':sorted(expected_set-set(pi)), 'extra_prediction_ids':sorted(set(pi)-expected_set),
               'duplicate_request_ids':sorted(k for k,v in ri.items() if len(v)>1),'duplicate_gold_ids':sorted(k for k,v in gi.items() if len(v)>1),
               'duplicate_prediction_ids':sorted(k for k,v in pi.items() if len(v)>1),'missing_gold_ids':sorted(expected_set-set(gi)),
               'extra_gold_ids':sorted(set(gi)-expected_set),'invalid_field_rows':0,'missing_field_rows':0,'valid_field_rows':0,
               'truncated_prediction_count':sum(p.get('truncated') is not False for p in preds),
               'max_absolute_probability_sum_deviation':0.0}
        if len(reqs)!=info['expected_request_count'] or len(ri)!=len(reqs) or set(gi)!=expected_set or any(len(v)!=1 for v in gi.values()):
            raise ValueError('Unsafe request/gold accounting: '+sid)
        for req in reqs:
            cid=req['id'];gold=gi[cid][0];case=cases.get(cid,cases.get(gold.get('case_id'),{}))
            questions=req['request']['questions'];part=partition(sid,gold,case)
            if set(gold['expected'])!=set(questions):raise ValueError('Gold/request fields mismatch: '+sid+'/'+cid)
            prediction=pi.get(cid,[]);common=[]
            if not prediction:common=['missing_prediction']
            elif len(prediction)>1:common=['duplicate_prediction']
            else:
                p=prediction[0]
                if p.get('truncated') is not False:common.append('missing_or_true_truncation_flag')
                if 'error' in p:common.append('prediction_error')
                if set(p.get('answers',{}))!=set(questions):common.append('native_answer_fields_mismatch')
                if set(p.get('probabilities_unrounded',{}))!=set(questions):common.append('unrounded_probability_fields_mismatch')
            field_rows=[]
            for field,q in questions.items():
                p=prediction[0] if len(prediction)==1 else {}
                answer=p.get('answers',{}).get(field);prob=p.get('probabilities_unrounded',{}).get(field)
                problems=common+probability_issues(q,answer,prob,gold['expected'][field])
                options=sorted(q.get('criteria',{}))
                gkey=json.dumps({'suite_id':sid,'partition':part,'field':field,'option_keys':options},sort_keys=True,ensure_ascii=False,separators=(',',':'))
                gid=sid+'__'+hashlib.sha256(gkey.encode()).hexdigest()[:16]
                row={'suite_id':sid,'id':cid,'field':field,'group_id':gid,'partition':part,'option_keys':options,
                     'status':'missing' if not prediction else 'invalid' if problems else 'valid','issues':problems,
                     'gold':gold['expected'][field],'choice':answer.get('choice') if isinstance(answer,dict) else None,
                     'probabilities':prob,'request':req,'gold_source_record':gold,'case_metadata':case}
                if row['status']=='valid':
                    audit['valid_field_rows']+=1
                    audit['max_absolute_probability_sum_deviation']=max(audit['max_absolute_probability_sum_deviation'],abs(math.fsum(prob.values())-1))
                else:audit[row['status']+'_field_rows']+=1
                normalized.append(row);field_rows.append(row)
            schema={f:sorted(q['criteria']) for f,q in questions.items()}
            casekey=json.dumps({'suite_id':sid,'partition':part,'schema':schema},sort_keys=True,ensure_ascii=False,separators=(',',':'))
            valid=all(r['status']=='valid' for r in field_rows)
            case_rows.append({'suite_id':sid,'id':cid,'case_group_id':sid+'__case__'+hashlib.sha256(casekey.encode()).hexdigest()[:16],
                              'partition':part,'schema':schema,'valid':valid,
                              'exact':all(r['choice']==r['gold'] for r in field_rows) if valid else None,
                              'minimum_selected_field_score_heuristic':min(r['probabilities'][r['choice']] for r in field_rows) if valid else None,
                              'required_fields':list(questions),'field_statuses':{r['field']:r['status'] for r in field_rows}})
        suite_audits.append(audit)
    return normalized,case_rows,suite_audits

def compute(root,out):
    lock=read_json(root/'SOURCE_LOCK.json')
    for path,digest in lock['files'].items():
        if sha(root/path)!=digest:raise ValueError('Source/protocol lock mismatch: '+path)
    inv=read_json(root/'SOURCE_INVENTORY.json')
    rows,cases,audits=build_rows(root,inv)
    groups=defaultdict(list)
    for row in rows:groups[row['group_id']].append(row)
    results=[];errors=[];field_items=[]
    for gid,rs in sorted(groups.items()):
        valid=[r for r in rs if r['status']=='valid'];m=field_metrics(valid,len(rs));items=m.pop('items')
        for r,item in zip(valid,items):
            field_items.append({k:r[k] for k in ['group_id','suite_id','id','field']}|item)
            if not item['correct']:errors.append(r|{'metric':item})
        results.append({k:rs[0][k] for k in ['group_id','suite_id','field','partition','option_keys']}|
                       {'option_count':len(rs[0]['option_keys']),'invalid_count':sum(r['status']=='invalid' for r in rs),
                        'missing_count':sum(r['status']=='missing' for r in rs),'expected_gold_class_counts':dict(sorted(Counter(r['gold'] for r in rs).items())),
                        'invalid_ids':[r['id'] for r in rs if r['status']=='invalid'],'missing_ids':[r['id'] for r in rs if r['status']=='missing']}|m)
    case_groups=defaultdict(list)
    for row in cases:case_groups[row['case_group_id']].append(row)
    case_results=[]
    for gid,rs in sorted(case_groups.items()):
        valid=[r for r in rs if r['valid']];correct=sum(r['exact'] for r in valid);thresholds=[]
        for t in THRESHOLDS:
            keep=[r for r in valid if r['minimum_selected_field_score_heuristic']>=t];k=sum(r['exact'] for r in keep)
            thresholds.append({'threshold':t,'selected_count':len(keep),'correct':k,'incorrect':len(keep)-k,'coverage':len(keep)/len(rs),
                               'valid_coverage':len(keep)/len(valid) if valid else None,'risk':(len(keep)-k)/len(keep) if keep else None,
                               'incorrect_ids':[r['id'] for r in keep if not r['exact']]})
        case_results.append({k:rs[0][k] for k in ['suite_id','case_group_id','partition','schema']}|{
            'score_definition':'minimum selected field score; heuristic, not calibrated joint probability','expected_count':len(rs),'valid_count':len(valid),
            'invalid_or_missing_count':len(rs)-len(valid),'exact_count':correct,'exact_rate':correct/len(valid) if valid else None,
            'risk_coverage_heuristic':thresholds})
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/'field_metrics.json',results);write_json(out/'case_metrics.json',case_results)
    write_json(out/'integrity.json',{'source_lock_sha256':sha(root/'SOURCE_LOCK.json'),'suites':audits,
                                   'metric_group_count':len(results),'case_group_count':len(case_results)})
    write_rows(out/'normalized_fields.jsonl',rows);write_rows(out/'field_items.jsonl',field_items)
    write_rows(out/'case_items.jsonl',cases);write_rows(out/'all_errors.jsonl',errors)
    write_json(out/'execution.json',{'analysis_type':'post-hoc descriptive','model_inference_performed':False,
               'source_lock_sha256':sha(root/'SOURCE_LOCK.json'),'implementation_sha256':{'scripts/analyze.py':sha(root/'scripts/analyze.py'),'scripts/metrics.py':sha(root/'scripts/metrics.py')},
               'runtime':'Python standard library; no model or third-party packages loaded','python_version':sys.version.split()[0]})
    print(json.dumps({'suites':len(audits),'field_groups':len(results),'case_groups':len(case_results),'field_rows':len(rows),'incorrect_fields':len(errors),'status':'computed'},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output',type=Path)
    args=parser.parse_args();compute(args.root,args.output or args.root/'results')
