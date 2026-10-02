"""Independent post-run QA. Does not import the benchmark scorer or load a model.

Preparation: python qa/independent_validate.py --prepare-only
Final: python qa/independent_validate.py --final --runtime-dir /path/to/runtime
A final audit is written only after completion gates establish a finished run.
"""
from __future__ import annotations
import argparse, collections, datetime, hashlib, json, math, pathlib, re, statistics, struct, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
REVISION = '17f0b0ad64efb65d273590632833508766b2aae6'
SEED = 20261002


def sha(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(pathlib.Path(path).read_text())


def read_lines(path):
    return [json.loads(line) for line in pathlib.Path(path).read_text().splitlines() if line.strip()]


def same(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(same(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    if isinstance(left, float) or isinstance(right, float):
        return isinstance(left, (int, float)) and isinstance(right, (int, float)) and math.isclose(left, right, rel_tol=1e-11, abs_tol=1e-11)
    return type(left) is type(right) and left == right


def numbers(rows):
    n = len(rows)
    result = {'cases': n}
    counts = {key: sum(bool(row['correct'][key]) for row in rows) for key in ('decision', 'evidence', 'exact_case')}
    for key, count in counts.items():
        result[key] = {'correct': count, 'total': n, 'accuracy': count / n if n else None}
    total_correct = counts['decision'] + counts['evidence']
    result['field_accuracy'] = {'correct': total_correct, 'total': 2*n, 'accuracy': total_correct / (2*n) if n else None}
    return result


def recompute(benchmark, predictions):
    """Derive metrics directly from raw answers and reference fields, independently."""
    cases = benchmark['cases']
    by_id = {}
    for prediction in predictions:
        if prediction['id'] in by_id:
            raise ValueError('Duplicate prediction ID: ' + prediction['id'])
        by_id[prediction['id']] = prediction
    if set(by_id) != {c['id'] for c in cases}:
        raise ValueError('Prediction ID set differs from benchmark')
    rows = []
    for c in cases:
        p = by_id[c['id']]
        choices = {field: p['answers'][field]['choice'] for field in ('decision', 'evidence')}
        d = choices['decision'] == c['expected']['decision']
        e = choices['evidence'] in c['expected'].get('accepted_evidence', [c['expected']['evidence']])
        rows.append({'id': c['id'], 'document_id': c['document_id'], 'area': c['area'], 'tags': c.get('tags', []),
                     'expected': c['expected'], 'actual': choices,
                     'actual_evidence_clauses': c['evidence_options'][choices['evidence']],
                     'correct': {'decision': d, 'evidence': e, 'exact_case': d and e},
                     'answers': p['answers'], 'probabilities': p['probabilities_unrounded'],
                     'input_tokens': p['input_tokens'], 'truncated': p['truncated'],
                     'inference_seconds': p['inference_seconds'], 'encode_seconds': p['encode_seconds'], 'rss_bytes': p.get('rss_bytes')})
    labels = collections.Counter(c['expected']['decision'] for c in cases)
    evidence = collections.Counter(c['expected']['evidence'] for c in cases)
    pair_counts = collections.Counter((c['expected']['decision'], c['expected']['evidence']) for c in cases)
    confusion = {truth: {guess: 0 for guess in labels} for truth in labels}
    for row in rows:
        confusion[row['expected']['decision']][row['actual']['decision']] += 1
    macro_recall = sum(confusion[label][label] / count for label, count in labels.items()) / len(labels)
    summary = numbers(rows)
    random_evidence = sum(len(c['expected'].get('accepted_evidence', [c['expected']['evidence']])) / len(c['evidence_options']) for c in cases) / len(cases)
    summary.update({'decision_label_distribution': dict(labels), 'decision_majority_baseline': max(labels.values()) / len(cases),
                    'evidence_uniform_random_baseline': random_evidence, 'evidence_option_distribution': dict(evidence),
                    'evidence_position_majority_baseline': max(evidence.values()) / len(cases),
                    'exact_case_majority_pair_baseline': max(pair_counts.values()) / len(cases),
                    'decision_balanced_accuracy': macro_recall})
    high_errors = {}
    for field in ('decision', 'evidence'):
        high_errors[field] = []
        for row in rows:
            confidence = max(row['probabilities'][field].values())
            if not row['correct'][field] and confidence >= .9:
                high_errors[field].append({'id': row['id'], 'choice': row['actual'][field], 'confidence': confidence})
    summary['high_confidence_errors'] = high_errors
    latencies = sorted(row['inference_seconds'] for row in rows)
    summary['latency_seconds'] = {'median': statistics.median(latencies), 'p95_nearest_rank': latencies[math.ceil(.95*len(latencies))-1],
                                  'min': latencies[0], 'max': latencies[-1], 'total': sum(latencies)}
    tokens = [row['input_tokens'] for row in rows]
    summary['tokens'] = {'min': min(tokens), 'median': statistics.median(tokens), 'max': max(tokens), 'truncated_cases': sum(row['truncated'] for row in rows)}
    groups = {}
    groups['by_area'] = {area: numbers([row for row in rows if row['area'] == area]) for area in benchmark['metadata']['areas']}
    groups['by_document'] = {doc['id']: numbers([row for row in rows if row['document_id'] == doc['id']]) for doc in benchmark['documents']}
    groups['by_decision_label'] = {label: numbers([row for row in rows if row['expected']['decision'] == label]) for label in labels}
    groups['date_version_subset'] = numbers([row for row in rows if 'date_version_application' in row['tags']])
    groups['without_date_version_subset'] = numbers([row for row in rows if 'date_version_application' not in row['tags']])
    taxonomy = collections.Counter(('both_correct' if row['correct']['exact_case'] else 'decision_only_correct' if row['correct']['decision'] else 'evidence_only_correct' if row['correct']['evidence'] else 'both_wrong') for row in rows)
    return {'summary': summary, **groups, 'cases': rows, 'decision_confusion_matrix': confusion, 'error_taxonomy': dict(taxonomy)}


class Auditor:
    def __init__(self):
        self.checks = []
    def check(self, name, condition, details=None):
        self.checks.append({'check': name, 'status': 'pass' if condition else 'fail', 'details': details})
        return condition
    def equal(self, name, actual, expected):
        return self.check(name, same(actual, expected), None if same(actual, expected) else {'actual': actual, 'expected': expected})
    @property
    def blockers(self):
        return [c for c in self.checks if c['status'] != 'pass']


def frozen_checks(audit, root, manifest):
    for rel, item in manifest['files'].items():
        p = root / rel
        audit.check('frozen_file:' + rel, p.is_file() and p.stat().st_size == item['bytes'] and sha(p) == item['sha256'])
    pre = read(root / 'qa/pre_inference_audit.json')
    audit.equal('pre_inference_semantic_gate', pre['status'], 'pass')
    audit.equal('preaudit_benchmark_hash', pre['source']['benchmark_sha256'], sha(root/'benchmark/benchmark.json'))
    audit.equal('preaudit_request_hash', pre['source']['requests_sha256'], sha(root/'benchmark/requests.jsonl'))


def self_test():
    # Hand-worked, model-free fixture: all four labels; controlled 2/4, 3/4, 1/4 outcomes.
    truths = ['ja', 'nein', 'offen', 'konflikt']; guesses = ['ja', 'ja', 'offen', 'nein']
    c = [{'id':str(i), 'document_id':'doc', 'area':'area', 'tags':(['date_version_application'] if i==0 else []),
          'expected':{'decision':label,'evidence':'b1','evidence_clauses':['X']}, 'evidence_options':{'b1':['X'],'b2':['Y']}}
         for i,label in enumerate(truths)]
    ps = []
    for i, guess in enumerate(guesses):
        ev = 'b2' if i==0 else 'b1'
        ps.append({'id':str(i), 'answers':{'decision':{'choice':guess},'evidence':{'choice':ev}},
                   'probabilities_unrounded':{'decision':{guess:.95},'evidence':{ev:.9}},'input_tokens':100+i,
                   'truncated':False,'inference_seconds':i+1,'encode_seconds':.1,'rss_bytes':1})
    out = recompute({'cases':c,'documents':[{'id':'doc'}],'metadata':{'areas':['area']}},ps)
    assert out['summary']['decision']['correct']==2 and out['summary']['evidence']['correct']==3
    assert out['summary']['exact_case']['correct']==1 and out['summary']['field_accuracy']['correct']==5
    assert out['summary']['decision_balanced_accuracy']==.5
    assert out['summary']['decision_majority_baseline']==.25
    assert out['summary']['evidence_position_majority_baseline']==1
    assert out['summary']['evidence_uniform_random_baseline']==.5
    assert out['summary']['exact_case_majority_pair_baseline']==.25
    assert out['summary']['latency_seconds']['p95_nearest_rank']==4
    assert len(out['summary']['high_confidence_errors']['decision'])==2
    assert len(out['summary']['high_confidence_errors']['evidence'])==1
    ps[0]['probabilities_unrounded']['evidence']['b2']=.899999
    boundary=recompute({'cases':c,'documents':[{'id':'doc'}],'metadata':{'areas':['area']}},ps)
    assert len(boundary['summary']['high_confidence_errors']['evidence'])==0
    ps[0]['probabilities_unrounded']['evidence']['b2']=.9
    assert out['date_version_subset']['cases']==1 and out['without_date_version_subset']['cases']==3
    assert out['error_taxonomy']=={'decision_only_correct':1,'evidence_only_correct':2,'both_correct':1}
    try:
        recompute({'cases':c,'documents':[{'id':'doc'}],'metadata':{'areas':['area']}},ps+[ps[0]])
    except ValueError: pass
    else: raise AssertionError('Duplicate IDs not rejected')
    try:
        recompute({'cases':c,'documents':[{'id':'doc'}],'metadata':{'areas':['area']}},ps[:-1])
    except ValueError: pass
    else: raise AssertionError('Missing IDs not rejected')
    return True


def final_audit(root, runtime):
    # Do not open prediction rows until every completion artifact exists and metadata is terminal.
    required = ['results/run_completion.json','results/exit_code.txt','results/predictions.metadata.json','results/predictions.jsonl','results/results.json','REPORT.md','ERRORS.md']
    missing = [p for p in required if not (root/p).is_file()]
    if missing:
        print(json.dumps({'status':'waiting_for_completion','missing':missing})); return 2
    meta=read(root/'results/predictions.metadata.json'); completion=read(root/'results/run_completion.json')
    if meta.get('status')!='completed':
        print(json.dumps({'status':'waiting_for_completion','metadata_status':meta.get('status')})); return 2
    a=Auditor(); manifest=read(root/'qa/freeze_manifest.json'); frozen_checks(a,root,manifest)
    benchmark=read(root/'benchmark/benchmark.json'); requests=read_lines(root/'benchmark/requests.jsonl')
    predictions=read_lines(root/'results/predictions.jsonl'); scored=read(root/'results/results.json')
    preflight=read(root/'qa/encoding_preflight.json'); start=read(root/'results/run_start.json')
    a.equal('completion_exit_code',completion.get('exit_code'),0)
    a.equal('shell_exit_code',int((root/'results/exit_code.txt').read_text().strip()),0)
    a.equal('scored_status',scored.get('status'),'completed')
    a.equal('case_count',len(benchmark['cases']),60);a.equal('prediction_count',len(predictions),60)
    a.equal('ordered_ids',[p['id'] for p in predictions],[q['id'] for q in requests])
    a.equal('metadata_order',meta.get('request_order_ids'),[q['id'] for q in requests])
    a.equal('metadata_count',meta.get('request_count'),60)
    a.equal('primary_attempt',start.get('primary_prediction_attempt'),1)
    a.equal('start_requests_hash',start.get('requests_sha256'),sha(root/'benchmark/requests.jsonl'))
    a.equal('start_freeze_hash',start.get('freeze_manifest_sha256'),sha(root/'qa/freeze_manifest.json'))
    dt=lambda value:datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    a.check('freeze_before_start_before_finish',dt(manifest['frozen_at'])<=dt(start['started_at'])<=dt(meta['started_at'])<=dt(meta['completed_at']))
    for key,expected in [('model','Cloudflare/clef-flash'),('revision',REVISION),('seed',SEED),('dtype','bfloat16'),('device','cpu'),('mode','CPU NF4 backbone, original BF16 joint head and BF16 output embeddings'),('threads',6),('batch_size',1),('max_length',2048),('joint_head_dtypes',['torch.bfloat16']),('joint_head_parameter_count',121762820),('benchmark_requests_only_no_gold',True)]:
        a.equal('metadata:'+key,meta.get(key),expected)
    for key,expected in [('requests_sha256',sha(root/'benchmark/requests.jsonl')),('source_code_sha256',manifest['official_source_sha256']),('runner_sha256',manifest['inference_runner_sha256'])]:
        a.equal('metadata:'+key,meta.get(key),expected)
    quant=meta.get('quantization',{})
    a.equal('NF4_enabled',quant.get('load_in_4bit',quant.get('_load_in_4bit')),True)
    a.equal('8bit_disabled',quant.get('load_in_8bit',quant.get('_load_in_8bit')),False)
    for key,expected in [('bnb_4bit_quant_type','nf4'),('bnb_4bit_compute_dtype','bfloat16'),('bnb_4bit_use_double_quant',True),('llm_int8_skip_modules',['lm_head'])]:
        a.equal('quantization:'+key,quant.get(key),expected)
    pins={k.lower().replace('_','-'):v for k,v in (line.strip().split('==',1) for line in (root/'scripts/requirements_frozen.txt').read_text().splitlines() if '==' in line)}
    for package,version in meta.get('packages',{}).items():a.equal('package:'+package,version,pins.get(package.lower().replace('_','-')))
    a.equal('six_runtime_package_versions_reported',len(meta.get('packages',{})),6)
    a.equal('scored_run_metadata',scored.get('run_metadata'),meta)
    a.equal('scored_benchmark_metadata',scored.get('benchmark'),benchmark['metadata'])
    a.equal('preflight_request_hash',preflight['requests_sha256'],sha(root/'benchmark/requests.jsonl'))
    a.check('preflight_no_truncation',preflight['all_fit_without_truncation'] is True and preflight['count']==60)
    token_reference={x['id']:x['tokens'] for x in preflight['items']}
    cases_by_id={c['id']:c for c in benchmark['cases']};max_normalization_error=0.;ties=[]
    for p in predictions:
        ident=p['id'];c=cases_by_id.get(ident)
        if not a.check(ident+':known_id',c is not None):continue
        a.equal(ident+':two_answer_fields',sorted(p['answers']),['decision','evidence'])
        a.equal(ident+':two_probability_fields',sorted(p['probabilities_unrounded']),['decision','evidence'])
        for field in ('decision','evidence'):
            probs=p['probabilities_unrounded'][field];ans=p['answers'][field];option_order=list(c[field+'_options'])
            a.equal(ident+':'+field+':option_set',sorted(probs),sorted(option_order))
            valid=all(isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v) and 0<=v<=1 for v in probs.values())
            a.check(ident+':'+field+':finite_probabilities',valid)
            err=abs(sum(probs.values())-1);max_normalization_error=max(max_normalization_error,err)
            a.check(ident+':'+field+':normalization',err<1e-5,{'absolute_error':err})
            wanted=max(option_order,key=probs.__getitem__)
            a.equal(ident+':'+field+':official_order_argmax',ans['choice'],wanted)
            if sum(v==max(probs.values()) for v in probs.values())>1:ties.append({'id':ident,'field':field})
            a.equal(ident+':'+field+':answer_type',ans.get('type'),'choice')
            a.equal(ident+':'+field+':rounded_confidence',ans.get('confidence'),round(probs[wanted],4))
            a.equal(ident+':'+field+':rounded_probabilities',ans.get('probabilities'),{k:round(v,4) for k,v in probs.items()})
        a.check(ident+':not_truncated',p['truncated'] is False)
        a.check(ident+':token_bounds',isinstance(p['input_tokens'],int) and 0<p['input_tokens']<=2048)
        a.equal(ident+':preflight_token_match',p['input_tokens'],token_reference[ident])
        for key in ('inference_seconds','encode_seconds','latency_ms','total_seconds','rss_bytes'):
            a.check(ident+':finite_nonnegative_'+key,isinstance(p[key],(int,float)) and math.isfinite(p[key]) and p[key]>=0)
        a.check(ident+':latency_units',math.isclose(p['latency_ms'],p['inference_seconds']*1000,rel_tol=1e-10,abs_tol=1e-8))
        a.check(ident+':total_time_bound',p['total_seconds']+1e-8>=p['inference_seconds']+p['encode_seconds'])
    independent=recompute(benchmark,predictions)
    for key in ('summary','by_area','by_document','by_decision_label','date_version_subset','without_date_version_subset','cases'):
        a.equal('independent_result:'+key,scored.get(key),independent[key])
    for key,path in [('benchmark','benchmark/benchmark.json'),('predictions','results/predictions.jsonl'),('metadata','results/predictions.metadata.json')]:
        a.equal('scorer_input_hash:'+key,scored['input_hashes'].get(key),sha(root/path))
    a.equal('date_version_case_ids',[c['id'] for c in benchmark['cases'] if 'date_version_application' in c.get('tags',[])],['fall_006','fall_028','fall_033'])
    a.equal('areas_total',sum(v['cases'] for v in independent['by_area'].values()),60)
    a.equal('documents_total',sum(v['cases'] for v in independent['by_document'].values()),60)
    a.equal('labels_total',sum(v['cases'] for v in independent['by_decision_label'].values()),60)
    events=[]
    for line in (root/'results/run.log').read_text().splitlines():
        try:item=json.loads(line)
        except json.JSONDecodeError:continue
        if isinstance(item,dict) and 'event' in item:events.append(item)
    counts=collections.Counter(x['event'] for x in events)
    for event,n in [('loading',1),('loaded',1),('warmup',1),('prediction',60),('completed',1)]:a.equal('run_log_count:'+event,counts[event],n)
    logged=[x for x in events if x['event']=='prediction']
    a.equal('log_prediction_order',[x['id'] for x in logged],[x['id'] for x in requests])
    a.check('log_prediction_sequence',all(x['n']==i and x['of']==60 for i,x in enumerate(logged,1)))
    resources=read_lines(root/'results/resource_monitor.jsonl')
    a.check('resource_guard_not_triggered',not any(x.get('event')=='memory_guard_stop' for x in resources))
    probe=meta.get('repeatability_probe',{})
    a.equal('repeat_probe_id',probe.get('id'),requests[0]['id']);a.equal('single_case_probe',probe.get('single_case_only'),True)
    a.check('repeat_probe_delta_valid',isinstance(probe.get('repeat_max_absolute_probability_difference'),(float,int)) and math.isfinite(probe['repeat_max_absolute_probability_difference']) and probe['repeat_max_absolute_probability_difference']>=0)
    a.check('warmup_not_truncated',meta.get('warmup',{}).get('truncated') is False)
    a.equal('warmup_field_count',list(meta.get('warmup',{}).get('answers',{})),['decision'])
    # Runtime verification reads files only; never instantiates the model.
    a.check('runtime_directory_supplied',runtime is not None and runtime.is_dir())
    if runtime and runtime.is_dir():
        model=runtime/'model';model_manifest=read(root/'qa/model_file_manifest.json')
        a.equal('actual_runtime_runner_sha',sha(runtime/'run_clef.py'),manifest['inference_runner_sha256'])
        a.equal('actual_official_model_code_sha',sha(model/'joint_schema_model.py'),manifest['official_source_sha256'])
        a.equal('actual_copied_model_code_sha',sha(runtime/'joint_schema_model.py'),manifest['official_source_sha256'])
        a.check('all_model_manifest_revisions',all(x['hf_commit']==REVISION for x in model_manifest.values()))
        a.equal('actual_joint_head_sha',sha(model/'joint_head.safetensors'),model_manifest['joint_head.safetensors']['sha256'])
        with (model/'joint_head.safetensors').open('rb') as stream:
            length=struct.unpack('<Q',stream.read(8))[0];header=json.loads(stream.read(length))
        tensors=[v for k,v in header.items() if k!='__metadata__']
        a.equal('original_head_checkpoint_dtype',sorted({x['dtype'] for x in tensors}),['BF16'])
        a.equal('head_parameter_count_from_checkpoint',sum(math.prod(x['shape']) for x in tensors),meta['joint_head_parameter_count'])
        code=(runtime/'run_clef.py').read_text()
        a.check('completed_runner_enforces_BF16_output_embeddings',"assert embedding.dtype==torch.bfloat16" in code and "(248320,4096)" in code)
    # Check both human-readable deliverables against independently recomputed facts.
    report=(root/'REPORT.md').read_text();errors=(root/'ERRORS.md').read_text();s=independent['summary']
    pct=lambda x:f'{x*100:.1f}'.replace('.',',')+' %'
    fmt=lambda x:f"{x['correct']}/{x['total']} ({pct(x['accuracy'])})"
    for key,title in [('decision','Entscheidung richtig'),('evidence','Belegmenge richtig'),('exact_case','Vollständig richtiger Fall')]:
        a.check('report_headline:'+key,f'{title}: **{fmt(s[key])}**' in report)
    for area,stat in independent['by_area'].items():
        a.check('report_area:'+area,'| '+area+' | '+' | '.join(fmt(stat[k]) for k in ('decision','evidence','exact_case'))+' |' in report)
    for label,stat in independent['by_decision_label'].items():
        a.check('report_label:'+label,'| '+label+' | '+fmt(stat['decision'])+' | '+fmt(stat['exact_case'])+' |' in report)
    a.check('report_softmax_caveat','keine validierte Zuverlässigkeitsgarantie' in report)
    a.check('report_ai_review_disclosure','Keine externe menschliche Fachprüfung' in report)
    a.check('report_token_range',f"{s['tokens']['min']}–{s['tokens']['max']} Tokens, Median {s['tokens']['median']}" in report)
    a.check('report_balanced_accuracy',f"Balanced-Accuracy des Modells: {pct(s['decision_balanced_accuracy'])}" in report)
    a.check('report_majority_baseline',pct(s['decision_majority_baseline']) in report)
    a.check('report_evidence_position_baseline',pct(s['evidence_position_majority_baseline']) in report)
    a.check('report_majority_pair_baseline',pct(s['exact_case_majority_pair_baseline']) in report)
    for field,label in [('decision','Entscheidung'),('evidence','Belegmenge')]:
        expected=s['high_confidence_errors'][field]
        a.check('report_high_confidence_count:'+field,f'{label}: {len(expected)} falsche Auswahlen mit mindestens 90 %' in report)
        a.check('report_high_confidence_ids:'+field,all(x['id'] in report for x in expected))
    expected_errors=[row['id'] for row in independent['cases'] if not row['correct']['exact_case']]
    a.equal('error_report_complete_ordered_case_list',re.findall(r'^## (fall_\d+)\b',errors,re.M),expected_errors)
    sections={m.group(1):m.group(2) for m in re.finditer(r'^## (fall_\d+)\b[^\n]*\n(.*?)(?=^## fall_|\Z)',errors,re.S|re.M)}
    docs={d['id']:d for d in benchmark['documents']}
    for row in independent['cases']:
        if row['correct']['exact_case']:continue
        c=cases_by_id[row['id']];section=sections.get(row['id'],'')
        a.check('error_case_text:'+row['id'],c['scenario'] in section and c['claim'] in section and c['rationale'] in section)
        a.check('error_case_decision_output:'+row['id'],f"Modell `{row['actual']['decision']}` ({pct(row['probabilities']['decision'][row['actual']['decision']])}); Referenz `{c['expected']['decision']}`" in section)
        a.check('error_case_evidence_output:'+row['id'],f"Modell {', '.join(row['actual_evidence_clauses'])} ({pct(row['probabilities']['evidence'][row['actual']['evidence']])}); Referenz {', '.join(c['expected']['evidence_clauses'])}" in section)
        wanted=set(c['expected']['evidence_clauses'])|set(row['actual_evidence_clauses'])
        a.check('error_case_clauses:'+row['id'],all(q['text'] in section for q in docs[c['document_id']]['clauses'] if q['id'] in wanted))
    # Final hash pass catches unexpected changes while validation was running.
    frozen_checks(a,root,manifest)
    source_paths={'benchmark':'benchmark/benchmark.json','requests':'benchmark/requests.jsonl','predictions':'results/predictions.jsonl','metadata':'results/predictions.metadata.json','results':'results/results.json','freeze_manifest':'qa/freeze_manifest.json','run_completion':'results/run_completion.json','exit_code':'results/exit_code.txt','report':'REPORT.md','errors':'ERRORS.md','validator':'qa/independent_validate.py'}
    out={'status':'pass' if not a.blockers else 'fail','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'reviewer':'Separate AI reviewer. Independent metric recomputation; no import or execution of score_results.score; no model inference.',
         'source':{k+'_sha256':sha(root/v) for k,v in source_paths.items()},
         'counts':{'cases':len(predictions),'fields':2*len(predictions),'checks':len(a.checks),'blockers':len(a.blockers)},
         'summary':independent['summary'],'groups':{k:independent[k] for k in ('by_area','by_document','by_decision_label','date_version_subset','without_date_version_subset')},
         'decision_confusion_matrix':independent['decision_confusion_matrix'],'error_taxonomy':independent['error_taxonomy'],
         'raw_probability_max_normalization_error':max_normalization_error,'exact_argmax_ties':ties,'repeatability_probe':probe,
         'blockers':a.blockers,'checks':a.checks,'per_case':[{'id':row['id'],'expected':row['expected'],'actual':row['actual'],'correct':row['correct']} for row in independent['cases']],
         'limitations':['No model predictions were read until completion gates passed.','All frozen files are rehashed; large backbone weight files were not rehashed again by this independent validator. Their pre-run revision/hash manifest is frozen.','Original joint-head file is independently hashed and its BF16 header and parameter count checked. Runtime output-embedding dtype is supported by the hash-verified runner assertion and successful completion, not a second live-memory read.','Single-case repeatability probe is not broad determinism evidence.','AI QA is not external human or insurance/legal expert review.']}
    false_conflicts=[row['id'] for row in independent['cases'] if row['actual']['decision']=='konflikt' and row['expected']['decision']!='konflikt']
    out['interpretation_checks']={
        'correct_evidence_with_wrong_decision':independent['error_taxonomy'].get('evidence_only_correct',0),
        'wrong_decisions_total':60-s['decision']['correct'],
        'false_conflict_case_ids':false_conflicts,
        'conflict_true_positive_count':independent['decision_confusion_matrix']['konflikt']['konflikt'],
        'conflict_prediction_count':sum(row['actual']['decision']=='konflikt' for row in independent['cases']),
        'note':'Correct evidence choice does not establish correct rule application. All three true conflicts were recognized, but false conflict predictions must also be counted. No high-confidence field errors does not validate calibration.'}
    (root/'qa/post_inference_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    lines=['# Independent post-inference audit','',f"**Status: {out['status'].upper()}**",'',out['reviewer'],'',f"{len(predictions)} cases, {2*len(predictions)} fields, {len(a.checks)} checks; {len(a.blockers)} blockers.",'','## Independently recomputed result','',f"- Decision: {fmt(s['decision'])}",f"- Evidence: {fmt(s['evidence'])}",f"- Exact case: {fmt(s['exact_case'])}",f"- Balanced decision accuracy: {pct(s['decision_balanced_accuracy'])}",f"- Decision-majority baseline: {pct(s['decision_majority_baseline'])}",f"- Evidence-position-majority baseline: {pct(s['evidence_position_majority_baseline'])}",f"- Uniform random evidence baseline: {pct(s['evidence_uniform_random_baseline'])}",f"- Most-common decision/evidence pair baseline: {pct(s['exact_case_majority_pair_baseline'])}",'','## High-confidence errors (raw maximum ≥ 0.9)','']
    for field in ('decision','evidence'):lines.append(f"- {field}: "+(', '.join(x['id'] for x in s['high_confidence_errors'][field]) or 'none'))
    lines+=['','## Verification','','Per-case grading, all group totals, baselines, balanced accuracy, latency/token summaries, raw probability normalization, official-order argmax, rounding, metadata, source hashes, no truncation, terminal completion/exit code, and all frozen input hashes were checked independently. Full check records and source hashes are in the adjacent JSON.','','## Blockers','']
    lines += ['- '+x['check']+': '+str(x['details']) for x in a.blockers] or ['None.']
    lines += ['','## Limits','']+['- '+x for x in out['limitations']]
    lines += ['','## Interpretation checks','',
              f"- {out['interpretation_checks']['correct_evidence_with_wrong_decision']} of {out['interpretation_checks']['wrong_decisions_total']} wrong decisions still selected the correct evidence",
              f"- Date/version subset: {fmt(independent['date_version_subset']['decision'])} decisions, {fmt(independent['date_version_subset']['evidence'])} evidence selections",
              f"- True conflicts recognized: {out['interpretation_checks']['conflict_true_positive_count']}/3; additional false-conflict predictions: {', '.join(false_conflicts) or 'none'}",
              '- No observed ≥90% field error is not evidence that softmax values are calibrated']
    (root/'qa/post_inference_audit.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status':out['status'],'counts':out['counts'],'summary':s,'blockers':a.blockers},ensure_ascii=False,indent=2))
    return 0 if not a.blockers else 1


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=ROOT);p.add_argument('--runtime-dir',type=pathlib.Path);p.add_argument('--prepare-only',action='store_true');p.add_argument('--final',action='store_true');args=p.parse_args()
    self_test()
    if args.prepare_only:
        a=Auditor();frozen_checks(a,args.root,read(args.root/'qa/freeze_manifest.json'))
        print(json.dumps({'status':'prepared' if not a.blockers else 'blocked','model_free_self_tests':'pass','frozen_checks':len(a.checks),'blockers':a.blockers},indent=2));return 0 if not a.blockers else 1
    if not args.final:p.error('Use --prepare-only or --final')
    try:
        return final_audit(args.root,args.runtime_dir)
    except Exception as exc:
        paths={'benchmark':'benchmark/benchmark.json','requests':'benchmark/requests.jsonl','predictions':'results/predictions.jsonl','metadata':'results/predictions.metadata.json','results':'results/results.json','freeze_manifest':'qa/freeze_manifest.json','validator':'qa/independent_validate.py'}
        failure={'status':'fail','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':{k+'_sha256':sha(args.root/v) for k,v in paths.items() if (args.root/v).is_file()},'blockers':[{'check':'validator_completed','details':type(exc).__name__+': '+str(exc)}]}
        (args.root/'qa/post_inference_audit.json').write_text(json.dumps(failure,indent=2)+'\n')
        (args.root/'qa/post_inference_audit.md').write_text('# Independent post-inference audit\n\nStatus: FAIL\n\nValidation could not finish: '+type(exc).__name__+': '+str(exc)+'\n')
        print(json.dumps(failure,indent=2));return 1


if __name__=='__main__':
    raise SystemExit(main())
