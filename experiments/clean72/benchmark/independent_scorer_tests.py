import argparse,copy,importlib.util,json,math,pathlib,statistics,hashlib
here=pathlib.Path(__file__).resolve().parent
default_benchmark=here if (here/'score.py').is_file() else here.parent/'benchmark'
parser=argparse.ArgumentParser(description='Offline scorer verification with artificial fixtures only; stdout by default.')
parser.add_argument('--benchmark',type=pathlib.Path,default=default_benchmark)
parser.add_argument('--out',type=pathlib.Path,help='Optional report path; default is stdout without writing files.')
args=parser.parse_args()
b=args.benchmark.resolve()
if args.out is not None:
 target=args.out.resolve()
 if (b/'freeze_manifest.json').exists() and target.is_relative_to(b):
  raise SystemExit('Frozen benchmark: --out must be outside the benchmark directory')
spec=importlib.util.spec_from_file_location('independent_scoring_review',b/'score.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases=[json.loads(x) for x in (b/'cases.jsonl').read_text().splitlines()]
tests=[]
def check(name,condition):
 assert condition,name
 tests.append(name)
def response(c,pred=None):
 pred=pred or c['expected']['decision'];ks=list(c['questions']['decision']['criteria'])
 return {'id':c['id'],'response':{'answers':{'decision':{'type':'choice','choice':pred,'confidence':1.0,'probabilities':{k:float(k==pred) for k in ks}}}},'latency_ms':10}
c=cases[0];good=response(c);truth=c['expected']['decision'];ks=list(c['questions']['decision']['criteria']);wrong=next(k for k in ks if k!=truth)
perfect=m.score(cases,[response(c) for c in cases]);info=perfect['information_request_diagnostic']
check('complete_fixture_72_all_correct',perfect['overall']['choice_accuracy_all_planned']==perfect['overall']['strict_accuracy_all_planned']==1)
check('macro_f1_perfect',perfect['category_macro_f1']==1)
check('information_partition_and_routing_exclusion',info['n_gold_sufficient']==50 and info['n_gold_missing_or_unresolved']==22 and info['precision']==info['recall']==1 and 'fachgespraech' not in m.INFO_LABELS['finanzservice_routing'])
check('empty_output_all_planned_denominator',m.score(cases,[])['overall']['choice_accuracy_all_planned']==0)
check('partial_output_all_planned_denominator',m.score(cases,[good])['overall']['choice_accuracy_all_planned']==1/72)
for field,val in [('confidence',True),('confidence',math.nan),('probabilities',{k:0 for k in ks}),('probabilities',{k:(math.nan if k==truth else 0) for k in ks}),('probabilities',{k:(True if k==truth else 0) for k in ks})]:
 bad=copy.deepcopy(good);bad['response']['answers']['decision'][field]=val
 check('reject_'+field+'_'+repr(val),not m.inspect(c,bad)['schema_valid'])
unrounded=copy.deepcopy(good);unrounded['probabilities_unrounded']={'decision':{k:float(k==wrong) for k in ks}}
check('unrounded_argmax_conflict_invalidates_strict',m.inspect(c,unrounded)['error']=='choice_disagrees_with_unrounded_argmax' and not m.inspect(c,unrounded)['strict_correct'])
a=copy.deepcopy(good);p={k:.1 for k in ks};p[truth]=.6;a['response']['answers']['decision'].update(probabilities=p,confidence=.6)
r=m.inspect(c,a);mtr=m.metrics([r],ks)
check('known_brier_and_nll',math.isclose(r['brier'],.2) and math.isclose(r['nll'],-math.log(.6)))
check('known_ece',math.isclose(mtr['calibration']['ece_5_equal_width_bins'],.4))
check('confidence_threshold_inclusive',mtr['confidence_deferral']['0.6']['accepted']==1 and mtr['confidence_deferral']['0.8']['accepted']==0)
# Exactly one unneeded information request and one missed needed request, all remaining fixtures correct.
need=next(c for c in cases if c['information_status']=='missing_or_unresolved')
suff=next(c for c in cases if c['information_status']=='sufficient' and m.INFO_LABELS[c['category']])
raw=[]
for x in cases:
 if x['id']==need['id']:
  pred=next(k for k in x['questions']['decision']['criteria'] if k not in m.INFO_LABELS[x['category']]);raw.append(response(x,pred))
 elif x['id']==suff['id']:
  pred=next(iter(m.INFO_LABELS[x['category']]));raw.append(response(x,pred))
 else:raw.append(response(x))
i=m.score(cases,raw)['information_request_diagnostic']
check('information_diagnostic_counts',i['precision']==21/22 and i['recall']==21/22 and i['unnecessary_information_request_rate']==1/50 and i['missed_information_request_valid_choice_rate_all_needed']==1/22)
# Return one wrong information subtype: binary detection succeeds but exact subtype scoring fails.
rq=next(c for c in cases if c['category']=='rueckfrageplanung' and c['expected']['decision']=='zeitpunkt')
raw=[response(x,'umfang' if x['id']==rq['id'] else None) for x in cases]
i=m.score(cases,raw)['information_request_diagnostic']
check('binary_and_exact_information_metrics_distinct',i['recall']==1 and i['exact_choice_accuracy_on_needed']==21/22)
# Unknown labels remain incorrect even if syntactically strings.
bad=copy.deepcopy(good);bad['response']['answers']['decision']['choice']='unknown'
check('unknown_choice_is_invalid_and_wrong',not m.inspect(c,bad)['choice_valid'] and not m.inspect(c,bad)['correct'])
check('runtime_failure_wrong',not m.inspect(c,{'id':c['id'],'error':'artificial test error'})['correct'])
check('wrong_choice_brier_two',m.inspect(c,response(c,wrong))['brier']==2)
lengths=[len(x['input'].split()) for x in cases]
enc=json.loads((b/'encoding_preflight.json').read_text())
report={'test_count':len(tests),'passed_tests':tests,'scorer_sha256':hashlib.sha256((b/'score.py').read_bytes()).hexdigest(),'input_words':{'min':min(lengths),'median':statistics.median(lengths),'max':max(lengths),'sum':sum(lengths)},'encoding_preflight_existing_report':{'count':enc['count'],'model_instantiated':enc['model_instantiated'],'all_fit_without_truncation':enc['all_fit_without_truncation'],'min':min(x['tokens'] for x in enc['items']),'median':statistics.median(x['tokens'] for x in enc['items']),'max':max(x['tokens'] for x in enc['items'])},'note':'Only artificial in-memory fixtures. No target model, network, model loading or inference.'}
rendered=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
if args.out is not None:
 args.out.write_text(rendered,encoding='utf-8')
print(rendered,end='')
