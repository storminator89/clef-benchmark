#!/usr/bin/env python3
"""Independent raw-source recomputation; never imports a primary script/output parser."""
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from independent_metrics import compute, validate_record, THRESHOLDS

ROOT = Path(__file__).resolve().parents[1]
LOCK_SHA256 = 'c02c5378121b67c91706c3f2edcff45b50224f2b752bbb6188849ec9f329bff4'

def read(path): return json.loads(path.read_text())
def lines(path): return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(x): return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',',':'))
def output(path, obj): path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n')

checks = 0
def equal(a,b,label):
    global checks
    checks += 1
    if isinstance(a, (int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):
        if not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12): raise AssertionError(f'{label}: {a!r} != {b!r}')
    elif a != b: raise AssertionError(f'{label}: {a!r} != {b!r}')

def unique_index(rows, name):
    ids=[r['id'] for r in rows]
    equal(len(ids),len(set(ids)),name+' unique IDs')
    return {r['id']:r for r in rows}

def fieldkey(suite,part,field,options): return (suite,stable(part),field,tuple(sorted(options)))
def casekey(suite,part,schema): return (suite,stable(part),stable(schema))

def main():
    equal(digest(ROOT/'SOURCE_LOCK.json'),LOCK_SHA256,'announced source lock')
    lock=read(ROOT/'SOURCE_LOCK.json')
    for name,h in lock['files'].items(): equal(digest(ROOT/name),h,'locked '+name)
    inventory=read(ROOT/'SOURCE_INVENTORY.json')
    independent_groups=defaultdict(list); independent_cases=defaultdict(list)
    contexts={}; suite_audits=[];case_lookup={}
    for info in inventory['suites']:
        sid=info['suite_id'];src=ROOT/'sources'/sid
        for name,h in info['files'].items(): equal(digest(src/name),h,'inventory '+sid+'/'+name)
        requests=lines(src/'requests.jsonl'); predictions=lines(src/'predictions.jsonl')
        if sid=='insurance60':
            benchmark=read(src/'benchmark.json'); metadata={r['id']:r for r in benchmark['cases']}
            golds=[dict(id=r['id'],expected={k:r['expected'][k] for k in ('decision','evidence')},document_id=r['document_id'],area=r['area']) for r in benchmark['cases']]
        else:
            golds=lines(src/'gold.jsonl');metadata={}
            for filename in ('cases.jsonl','diagnostic_cases.jsonl'):
                if (src/filename).is_file():
                    for r in lines(src/filename):metadata[r.get('id',r.get('case_id'))]=r
        ri=unique_index(requests,sid+' request');gi=unique_index(golds,sid+' gold');pi=unique_index(predictions,sid+' predictions')
        equal(len(requests),info['expected_request_count'],sid+' inventory expected count')
        equal(set(ri),set(gi),sid+' request/gold IDs');equal(set(ri),set(pi),sid+' request/prediction IDs')
        invalid=[];all_deviation=[];fieldcount=0;ties=0
        for rid,req in ri.items():
            gold=gi[rid];pred=pi[rid];meta=metadata.get(rid,metadata.get(gold.get('case_id'),{}))
            if sid in ('original_text180','finance100','clean72','attack_ablation14'):
                part={k:gold[k] if k in gold else meta.get(k,'unspecified') for k in ('category','language','schema_language')}
                if sid=='attack_ablation14':part['condition']=gold['condition']
            elif sid=='images90':part={k:gold[k] for k in ('kind','language','condition')}
            else:part={}
            qs=req['request']['questions'];schema={f:sorted(q['criteria']) for f,q in qs.items()}
            equal(set(qs),set(gold['expected']),sid+'/'+rid+' gold fields')
            equal(set(qs),set(pred['answers']),sid+'/'+rid+' native fields')
            equal(set(qs),set(pred['probabilities_unrounded']),sid+'/'+rid+' probability fields')
            equal(pred.get('truncated'),False,sid+'/'+rid+' nontruncation')
            equal('error' in pred,False,sid+'/'+rid+' no prediction error')
            equal('expected' in req['request'],False,sid+'/'+rid+' separate labels')
            selected_scores=[];case_correct=[]
            for f,q in qs.items():
                fieldcount+=1;ans=pred['answers'][f];prob=pred['probabilities_unrounded'][f]
                equal(q['type'],'choice',sid+'/'+rid+'/'+f+' request type')
                equal(ans['type'],'choice',sid+'/'+rid+'/'+f+' answer type')
                equal(set(prob),set(q['criteria']),sid+'/'+rid+'/'+f+' option identities')
                opts=list(q['criteria'])
                record=dict(id=rid, options=opts, probabilities=[prob[k] for k in opts], gold=gold['expected'][f],choice=ans['choice'])
                issues=validate_record(record)
                if issues: invalid.append(dict(id=rid,field=f,issues=issues))
                equal(issues,[],sid+'/'+rid+'/'+f+' vector validation')
                equal(set(ans['probabilities']),set(prob),sid+'/'+rid+'/'+f+' displayed identities')
                for k in prob:
                    shown=ans['probabilities'][k]
                    equal(isinstance(shown,(int,float)) and not isinstance(shown,bool) and math.isfinite(shown) and abs(shown-prob[k])<=5.0001e-5,True,sid+'/'+rid+'/'+f+' display rounding')
                equal(abs(ans['confidence']-prob[ans['choice']])<=5.0001e-5,True,sid+'/'+rid+'/'+f+' confidence rounding')
                gkey=fieldkey(sid,part,f,opts)
                independent_groups[gkey].append(record)
                contexts[(sid,rid,f)]=dict(request=req,gold_source_record=gold,case_metadata=meta,prediction=pred,probabilities=prob,partition=part)
                selected_scores.append(prob[ans['choice']]);case_correct.append(ans['choice']==gold['expected'][f])
                all_deviation.append(abs(math.fsum(prob.values())-1))
                ties+=sum(p==max(prob.values()) for p in prob.values())>1
            ck=casekey(sid,part,schema)
            independent_cases[ck].append(dict(id=rid,correct=all(case_correct),score=min(selected_scores)))
            case_lookup[(sid,rid)]=dict(key=ck,partition=part,schema=schema,fields=list(qs),exact=all(case_correct),score=min(selected_scores))
        suite_audits.append(dict(suite_id=sid,expected_count=len(requests),raw_predictions=len(predictions),valid_fields=fieldcount,invalid_fields=len(invalid),missing_predictions=0,extra_predictions=0,duplicate_ids=0,truncated_predictions=0,maximum_sum_deviation=max(all_deviation),native_tied_maximum_fields=ties))

    # Primary reports are only opened after independent raw parsing and groups exist.
    primary_fields=read(ROOT/'results/field_metrics.json')
    pg={fieldkey(r['suite_id'],r['partition'],r['field'],r['option_keys']):r for r in primary_fields}
    equal(len(primary_fields),len(pg),'unique primary field groups')
    equal(set(pg),set(independent_groups),'field groups and partitions')
    independently_scored={};error_keys=set();saved_fields=[]
    for key,records in independent_groups.items():
        result=compute(records,expected_ids=[r['id'] for r in records]);p=pg[key]
        independently_scored[key]=result
        for mine,theirs in [('expected_n','expected_count'),('valid_n','valid_count'),('correct','correct'),('accuracy','accuracy'),('brier','brier_mean'),('mean_confidence','mean_selected_score'),('ece','ece_10_equal_width'),('error_auroc','error_detection_auroc')]:
            equal(result[mine],p[theirs],p['group_id']+'/'+theirs)
        equal(p['invalid_count'],0,p['group_id']+' invalid count');equal(p['missing_count'],0,p['group_id']+' missing count')
        equal(p['correct_over_expected'],result['correct']/result['expected_n'],p['group_id']+' expected accuracy')
        equal(p['incorrect'],result['valid_n']-result['correct'],p['group_id']+' incorrect count')
        equal(p['nll_is_infinite'],bool(result['infinite_nll_ids']),p['group_id']+' NLL infinity')
        equal(p['zero_gold_probability_ids'],result['infinite_nll_ids'],p['group_id']+' NLL zero IDs')
        equal(p['zero_gold_probability_count'],len(result['infinite_nll_ids']),p['group_id']+' NLL zero count')
        equal(p['nll_mean'],None if math.isinf(result['nll']) else result['nll'],p['group_id']+' NLL mean')
        finite=[r['nll'] for r in result['rows'] if not math.isinf(r['nll'])]
        equal(p['finite_nll_count'],len(finite),p['group_id']+' finite NLL count')
        equal(p['finite_nll_mean'],math.fsum(finite)/len(finite) if finite else None,p['group_id']+' finite NLL mean')
        equal(p['tie_count'],sum(len(r['max_tie_options'])>1 for r in result['rows']),p['group_id']+' ties')
        equal(p['option_count'],len(key[3]),p['group_id']+' option count')
        equal(p['signed_score_minus_accuracy_gap'],result['mean_confidence']-result['accuracy'],p['group_id']+' gap')
        equal(p['gold_class_counts'],dict(Counter(r['gold'] for r in records)),p['group_id']+' gold class counts')
        equal(p['expected_gold_class_counts'],dict(Counter(r['gold'] for r in records)),p['group_id']+' expected gold class counts')
        equal(p['saved_choice_class_counts'],dict(Counter(r['choice'] for r in records)),p['group_id']+' choice class counts')
        equal(p['error_auroc_correct_count'],result['correct'],p['group_id']+' AUROC correct denominator')
        equal(p['error_auroc_incorrect_count'],len(result['errors']),p['group_id']+' AUROC incorrect denominator')
        for a,b in zip(result['bins'],p['bins']):
            for mine,theirs in [('lower','lower'),('upper','upper'),('upper_inclusive','upper_inclusive'),('count','count'),('correct','correct'),('mean_confidence','mean_score'),('accuracy','accuracy'),('absolute_gap','absolute_gap')]:
                equal(a[mine],b[theirs],p['group_id']+'/bin/'+str(a['index'])+'/'+theirs)
            equal(b['signed_score_minus_accuracy_gap'],a['mean_confidence']-a['accuracy'] if a['count'] else None,p['group_id']+' bin gap')
        equal(len(p['bins']),10,p['group_id']+' bin count')
        for a,b in zip(result['risk_coverage'],p['risk_coverage']):
            for mine,theirs in [('threshold','threshold'),('accepted','selected_count'),('errors','incorrect'),('expected_coverage','coverage'),('coverage','valid_coverage'),('risk','risk')]:
                equal(a[mine],b[theirs],p['group_id']+'/risk/'+str(a['threshold'])+'/'+theirs)
            equal(b['correct'],a['accepted']-a['errors'],p['group_id']+' risk correct')
            equal(b['expected_count'],result['expected_n'],p['group_id']+' risk expected denominator')
            equal(b['valid_count'],result['valid_n'],p['group_id']+' risk valid denominator')
            threshold=format(a['threshold'],'.2f')
            equal(p['high_score_error_ids'][threshold],[r['id'] for r in result['errors'] if r['confidence']>=a['threshold']],p['group_id']+' high score errors '+threshold)
        equal(len(p['risk_coverage']),6,p['group_id']+' threshold count')
        for r in result['errors']:error_keys.add((key[0],r['id'],key[2]))
        stored={k:v for k,v in result.items() if k not in ('rows','errors','high_score_errors')}
        stored.update(suite_id=key[0],partition=json.loads(key[1]),field=key[2],option_keys=key[3],all_error_ids=[r['id'] for r in result['errors']])
        if isinstance(stored['nll'],float) and math.isinf(stored['nll']):stored['nll']='infinite'
        saved_fields.append(stored)

    primary_cases=read(ROOT/'results/case_metrics.json')
    pc={casekey(r['suite_id'],r['partition'],r['schema']):r for r in primary_cases}
    equal(len(pc),len(primary_cases),'unique primary case groups');equal(set(pc),set(independent_cases),'case grouping')
    for key,rs in independent_cases.items():
        p=pc[key];equal(p['expected_count'],len(rs),'case expected count');equal(p['valid_count'],len(rs),'case valid count')
        equal(p['invalid_or_missing_count'],0,'case invalid count');equal(p['exact_count'],sum(r['correct'] for r in rs),'case exact count')
        equal(p['exact_rate'],sum(r['correct'] for r in rs)/len(rs),'case exact rate')
        for threshold,gate in zip(THRESHOLDS,p['risk_coverage_heuristic']):
            take=[r for r in rs if r['score']>=threshold];wrong=[r['id'] for r in take if not r['correct']]
            equal(gate['threshold'],threshold,'case threshold');equal(gate['selected_count'],len(take),'case gate count')
            equal(gate['correct'],len(take)-len(wrong),'case gate correct');equal(gate['incorrect'],len(wrong),'case gate incorrect')
            equal(gate['incorrect_ids'],wrong,'case gate error IDs');equal(gate['coverage'],len(take)/len(rs),'case coverage')
            equal(gate['valid_coverage'],len(take)/len(rs),'case valid coverage');equal(gate['risk'],len(wrong)/len(take) if take else None,'case risk')
        equal(len(p['risk_coverage_heuristic']),6,'case threshold count')

    derived_rows=lines(ROOT/'results/normalized_fields.jsonl')
    equal(len(derived_rows),len(contexts),'derived field count')
    equal(len(set((r['suite_id'],r['id'],r['field']) for r in derived_rows)),len(contexts),'derived field unique IDs')
    for row in derived_rows:
        ctx=contexts[(row['suite_id'],row['id'],row['field'])]
        for name in ('request','gold_source_record','case_metadata','probabilities','partition'):
            equal(row[name],ctx[name],'derived original context '+name)
        equal(row['status'],'valid','derived field status');equal(row['issues'],[],'derived field issues')
        expected_group=pg[fieldkey(row['suite_id'],ctx['partition'],row['field'],ctx['probabilities'])]
        equal(row['group_id'],expected_group['group_id'],'derived group ID')
        equal(row['option_keys'],expected_group['option_keys'],'derived option keys')
    errors=lines(ROOT/'results/all_errors.jsonl')
    equal(len(errors),len(error_keys),'full error count')
    equal(set((r['suite_id'],r['id'],r['field']) for r in errors),error_keys,'all error identities')
    for row in errors:
        k=(row['suite_id'],row['id'],row['field']);ctx=contexts[k]
        for name in ('request','gold_source_record','case_metadata','probabilities','partition'):
            equal(row[name],ctx[name],'error context '+name)
        equal(row['choice'],ctx['prediction']['answers'][row['field']]['choice'],'error original native choice')
        equal(row['gold'],ctx['gold_source_record']['expected'][row['field']],'error original gold')
        equal(row['choice']==row['gold'],False,'error is wrong')
    items=lines(ROOT/'results/field_items.jsonl')
    equal(len(items),len(contexts),'item count')
    computed_items={(key[0],r['id'],key[2]):r for key,m in independently_scored.items() for r in m['rows']}
    equal(len(set((r['suite_id'],r['id'],r['field']) for r in items)),len(items),'item uniqueness')
    for row in items:
        ref=computed_items[(row['suite_id'],row['id'],row['field'])]
        ctx=contexts[(row['suite_id'],row['id'],row['field'])]
        equal(row['group_id'],pg[fieldkey(row['suite_id'],ctx['partition'],row['field'],ctx['probabilities'])]['group_id'],'item group ID')
        for name in ('gold','choice','confidence','correct','brier','gold_probability'):
            equal(row[name],ref[name],'item '+name)
        equal(row['nll'],None if math.isinf(ref['nll']) else ref['nll'],'item nll')
        equal(row['nll_is_infinite'],math.isinf(ref['nll']),'item infinite')
        equal(row['tied_maximum_count'],len(ref['max_tie_options']),'item tied maximum')
    for row in errors:
        ref=computed_items[(row['suite_id'],row['id'],row['field'])]
        for name in ('gold','choice','confidence','correct','brier','gold_probability'):
            equal(row['metric'][name],ref[name],'error item '+name)
    case_items=lines(ROOT/'results/case_items.jsonl')
    equal(len(case_items),len(case_lookup),'case item count')
    equal(len(set((r['suite_id'],r['id']) for r in case_items)),len(case_items),'case item uniqueness')
    for row in case_items:
        ref=case_lookup[(row['suite_id'],row['id'])]
        equal(row['partition'],ref['partition'],'case item partition');equal(row['schema'],ref['schema'],'case item schema')
        equal(row['required_fields'],ref['fields'],'case item required fields');equal(row['valid'],True,'case item valid')
        equal(row['exact'],ref['exact'],'case item exact')
        equal(row['minimum_selected_field_score_heuristic'],ref['score'],'case item minimum heuristic')
        equal(row['case_group_id'],pc[ref['key']]['case_group_id'],'case item group ID')
        equal(row['field_statuses'],{f:'valid' for f in ref['fields']},'case item statuses')
    integrity=read(ROOT/'results/integrity.json')
    equal(integrity['source_lock_sha256'],LOCK_SHA256,'integrity source lock')
    equal(integrity['metric_group_count'],len(independent_groups),'integrity field group count')
    equal(integrity['case_group_count'],len(independent_cases),'integrity case group count')
    ia={r['suite_id']:r for r in integrity['suites']}
    for r in suite_audits:
        p=ia[r['suite_id']]
        for target in ('expected_count','request_rows','gold_rows','prediction_rows'):equal(p[target],r['expected_count'],'integrity '+target)
        equal(p['valid_field_rows'],r['valid_fields'],'integrity valid fields')
        for target in ('invalid_field_rows','missing_field_rows','truncated_prediction_count'):equal(p[target],0,'integrity '+target)
        for target in ('missing_prediction_ids','extra_prediction_ids','duplicate_request_ids','duplicate_gold_ids','duplicate_prediction_ids','missing_gold_ids','extra_gold_ids'):equal(p[target],[],'integrity '+target)
        equal(p['max_absolute_probability_sum_deviation'],r['maximum_sum_deviation'],'integrity maximum sum deviation')
    for name,h in lock['files'].items():equal(digest(ROOT/name),h,'post-analysis lock '+name)
    output(ROOT/'audit/independent_field_metrics.json',saved_fields)
    output(ROOT/'audit/independent_recomputation.json',dict(status='PASS metrics and source integrity',source_lock_sha256=LOCK_SHA256,source_lock_file_count=len(lock['files']),independent_comparisons=checks,suite_count=len(suite_audits),request_count=sum(r['expected_count'] for r in suite_audits),field_count=len(contexts),field_groups=len(independent_groups),case_groups=len(independent_cases),incorrect_fields=len(error_keys),suites=suite_audits,primary_imports_used=False,real_model_inference_performed=False))
    print(json.dumps(read(ROOT/'audit/independent_recomputation.json'),indent=2))

if __name__=='__main__':main()
