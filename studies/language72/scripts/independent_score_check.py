#!/usr/bin/env python3
"""Fresh model-free recovery scorer check via CLI; never imports the primary scorer."""
import collections,copy,datetime,hashlib,json,pathlib,subprocess,sys,tempfile
R=pathlib.Path(__file__).resolve().parents[1]
C=[json.loads(x) for x in (R/'data/cases.reconstructed.jsonl').read_text().splitlines()]
P=[json.loads(x) for x in (R/'data/pairs.reconstructed.jsonl').read_text().splitlines()]
Q={x['id']:x['request'] for x in map(json.loads,(R/'data/requests.jsonl').read_text().splitlines())}
CI={x['id']:x for x in C};FIELDS=['action','determination'];GROUPS=['invariant','ambiguity_change'];STYLES=['canonical','typo','compact_colloquial','abbreviation','de_en_mix'];DOMAINS=['banking','insurance','finance'];SUBTYPES=['answer_to_missing_fact','answer_to_missing_target']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=0

def check(a,b,label):
 global checks
 checks+=1
 if a!=b:raise AssertionError((label,a,b))

def metric(n,d):return {'numerator':n,'denominator':d,'rate':n/d if d else None}

def make_preflight():
 records=[]
 for c in C:
  records.append({'id':c['id'],'input_tokens':700,'truncated':False,'full_cap_equal':True,'encoded_questions':[{'question_id':f,'question_type':1,'question_span':[1,2],'option_ids':sorted(Q[c['id']]['questions'][f]['criteria']),'option_spans':[[3+2*i,4+2*i] for i in range(len(Q[c['id']]['questions'][f]['criteria']))]} for f in FIELDS]})
 return {'status':'passed','synthetic_fixture_only':True,'requests_sha256':sha(R/'data/requests.jsonl'),'count':72,'all_full_cap_equal':True,'min_tokens':700,'max_tokens':700,'model_weights_loaded':False,'cases':records}

def make_row(c,tokens,choice=None,peak=.95):
 choice=choice or c['expected'];maps={};answers={}
 for f in FIELDS:
  opts=list(Q[c['id']]['questions'][f]['criteria']);probs={o:peak if o==choice[f] else (1-peak)/(len(opts)-1) for o in opts};maps[f]=probs;answers[f]={'type':'choice','choice':choice[f],'confidence':round(peak,4),'probabilities':{o:round(v,4) for o,v in probs.items()}}
 return {'id':c['id'],'answers':answers,'probabilities_unrounded':maps,'input_tokens':tokens[c['id']],'truncated':False,'encode_seconds':.1,'inference_seconds':1.,'total_seconds':1.1,'latency_ms':1000.,'rss_bytes':1024}

def case_counts(items):
 n=len(items);out={'count':n,'valid_outputs':metric(sum(x['valid'] for x in items),n),'all_fields_exact':metric(sum(x['exact'] for x in items),n),'field_inconsistency':metric(sum(x['inconsistent'] for x in items),n)}
 for f in FIELDS:out[f+'_exact']=metric(sum(x['correct'][f] for x in items),n)
 selected=[x for x in items if x['high']]
 def gate(xs,field=None):
  wrong=sum(not (x['exact'] if field is None else x['correct'][field]) for x in xs)
  return {'selected':metric(len(xs),n),'wrong_and_selected':metric(wrong,n),'wrong_among_selected':metric(wrong,len(xs))}
 out['high_score']={'threshold':.9,**gate(selected),'fields':{f:gate([x for x in items if x['field_high'][f]],f) for f in FIELDS},'fields_on_case_gate':{f:gate(selected,f) for f in FIELDS}}
 return out

def pair_counts(items,inv):
 names=['both_correct','observed_change','invalid_or_missing','missing_endpoint','invalid_existing_endpoint']
 names+=['stability','stable_correct','stable_wrong','failed_invariance','degradation','improvement','both_incorrect'] if inv else ['correct_directional_change','changed_but_direction_wrong']
 out={'count':len(items),**{k:metric(sum(x[k] for x in items),len(items)) for k in names},'observed_change_among_valid':metric(sum(x['observed_change'] for x in items),sum(x['valid_pair'] for x in items))}
 if inv:out['conditional_loss_given_correct_canonical']=metric(sum(x['degradation'] for x in items),sum(x['a_exact'] for x in items))
 return out

def cluster_counts(items):return {'count':len(items),**{k:metric(sum(x[k] for x in items),len(items)) for k in ['all_five_correct','all_five_valid']}}

def oracle(native,invalid,summary,case_rows,pair_rows,cluster_rows):
 N={r['id']:r for r in native};cases=[]
 for c in C:
  id=c['id'];valid=id in N and id not in invalid;actual={f:N[id]['answers'][f]['choice'] for f in FIELDS} if valid else dict.fromkeys(FIELDS);correct={f:valid and actual[f]==c['expected'][f] for f in FIELDS};p={f:N[id]['probabilities_unrounded'][f][actual[f]] for f in FIELDS} if valid else {}
  cases.append({**{k:c[k] for k in ['id','cluster_id','domain','group','style']},'valid':valid,'recorded':id in N,'actual':actual,'correct':correct,'exact':all(correct.values()),'high':valid and min(p.values())>=.9,'field_high':{f:valid and p[f]>=.9 for f in FIELDS},'inconsistent':valid and ((actual['action']=='answer')!=(actual['determination']!='unresolved'))})
 S={x['id']:x for x in cases};pairs=[]
 for p in P:
  a,b=S[p['a_id']],S[p['b_id']];v=a['valid'] and b['valid'];equal=v and a['actual']==b['actual'];both=a['exact'] and b['exact'];e={**p,'a_exact':a['exact'],'valid_pair':v,'both_correct':both,'observed_change':v and not equal,'invalid_or_missing':not v,'missing_endpoint':not a['recorded'] or not b['recorded'],'invalid_existing_endpoint':(a['recorded'] and not a['valid']) or (b['recorded'] and not b['valid'])}
  if p['kind']=='invariant':e.update(stability=equal,stable_correct=equal and both,stable_wrong=equal and not both,failed_invariance=not equal,degradation=a['exact'] and not b['exact'],improvement=not a['exact'] and b['exact'],both_incorrect=not a['exact'] and not b['exact'])
  else:e.update(correct_directional_change=both and v and not equal,changed_but_direction_wrong=v and not equal and not both)
  pairs.append(e)
 clusters=[]
 for id in sorted({p['cluster_id'] for p in P if p['kind']=='invariant'}):
  xs=[x for x in cases if x['cluster_id']==id];clusters.append({'id':id,'domain':xs[0]['domain'],'case_ids':[x['id'] for x in xs],'correct_count':sum(x['exact'] for x in xs),'valid_count':sum(x['valid'] for x in xs),'all_five_correct':all(x['exact'] for x in xs),'all_five_valid':all(x['valid'] for x in xs)})
 def strata(cs,ps,clusters):
  inv=[p for p in ps if p['kind']=='invariant'];amb=[p for p in ps if p['kind']=='ambiguity_change']
  return {'all_cases':case_counts(cs),'by_group':{g:case_counts([x for x in cs if x['group']==g]) for g in GROUPS},'invariant_views':{s:case_counts([x for x in cs if x['group']=='invariant' and x['style']==s]) for s in STYLES},'invariant_pairs':pair_counts(inv,True),'ambiguity_controls':pair_counts(amb,False),'cluster_robustness':cluster_counts(clusters),'invariant_by_transformation':{s:pair_counts([p for p in inv if p['subtype']==s],True) for s in STYLES[1:]},'ambiguity_by_subtype':{s:pair_counts([p for p in amb if p['subtype']==s],False) for s in SUBTYPES}}
 want=strata(cases,pairs,clusters);want['by_domain']={d:strata([c for c in cases if c['domain']==d],[p for p in pairs if p['domain']==d],[c for c in clusters if c['domain']==d]) for d in DOMAINS};want['all_field_decisions']=metric(sum(sum(x['correct'].values()) for x in cases),144)
 for key,val in want.items():check(summary[key],val,'summary '+key)
 check(summary['technical']['complete_pairs'],metric(sum(p['valid_pair'] for p in pairs),54),'completepairs');check(summary['technical']['recorded'],len(native),'recorded');check(summary['technical']['missing'],72-len(native),'missing');check(summary['technical']['invalid_existing'],len(invalid),'invalid');check(summary['technical']['valid'],sum(c['valid'] for c in cases),'valid')
 check([x['id'] for x in case_rows],[c['id'] for c in C],'case order')
 for got,w in zip(case_rows,cases):
  for dest,src in [('valid','valid'),('recorded','recorded'),('predicted','actual'),('field_correct','correct'),('exact','exact'),('high_score_selected','high'),('field_high_score_selected','field_high'),('field_inconsistent','inconsistent')]:check(got[dest],w[src],'case '+w['id']+' '+dest)
 check([x['id'] for x in pair_rows],[p['id'] for p in P],'pair order')
 for got,w in zip(pair_rows,pairs):
  for k,v in w.items():check(got[k],v,'pair '+w['id']+' '+k)
 check(cluster_rows,clusters,'all cluster artifacts')
 return [c['id'] for c in cases if not c['exact']]

def main():
 scenarios=[]
 with tempfile.TemporaryDirectory(prefix='recovery_independent_scoring_') as td:
  td=pathlib.Path(td);pf=R/'evidence/encoding_preflight.json';kind='real_tokenizer_preflight'
  if not pf.exists():
   kind='explicit_synthetic_token_fixture_not_tokenizer_evidence';pf=td/'synthetic_preflight.json';pf.write_text(json.dumps(make_preflight()))
  pfd=json.loads(pf.read_text());tokens={x['id']:x['input_tokens'] for x in pfd['cases']};base={c['id']:make_row(c,tokens) for c in C}
  def run(name,rs,invalid=(),fatal=False,preflight=pf):
   folder=td/name;folder.mkdir();pred=folder/'fixture.jsonl';pred.write_bytes(('\r\n'.join(json.dumps(x).replace('Infinity','1e999') for x in rs)+'\r\n').encode());out=folder/'scored';p=subprocess.run([sys.executable,str(R/'scripts/score.py'),'--predictions',str(pred),'--preflight',str(preflight),'--output',str(out)],capture_output=True,text=True)
   if fatal:check(p.returncode!=0,True,name+' rejection')
   else:
    check(p.returncode,0,name+' CLI error '+p.stderr);j=lambda f:[json.loads(x) for x in (out/f).read_text().splitlines() if x.strip()];errors=oracle(rs,set(invalid),json.loads((out/'summary.json').read_text()),j('case_scores.jsonl'),j('pair_scores.jsonl'),j('cluster_scores.jsonl'));check([x['id'] for x in j('errors.jsonl')],errors,name+' every error');check((out/'raw_predictions.jsonl').read_bytes(),pred.read_bytes(),name+' raw bytes')
   scenarios.append(name)
  run('perfect',list(base.values()));run('empty',[]);run('missing_canonical',[v for k,v in base.items() if k!='gv_b1_canonical'])
  x=copy.deepcopy(base);x['gv_b1_typo']['answers']['action'].pop('confidence');run('invalid_variant',list(x.values()),['gv_b1_typo'])
  x=copy.deepcopy(base)
  for id in x:
   if id.startswith('gv_b1_'):x[id]=make_row(CI[id],tokens,{'action':'answer','determination':'no'})
  run('stable_wrong',list(x.values()))
  for name,id in [('degradation','gv_b1_typo'),('improvements','gv_b1_canonical')]:
   x=copy.deepcopy(base);x[id]=make_row(CI[id],tokens,{'action':'answer','determination':'no'});run(name,list(x.values()))
  x=copy.deepcopy(base)
  for p in P:
   if p['kind']=='ambiguity_change':x[p['a_id']]=make_row(CI[p['a_id']],tokens,CI[p['b_id']]['expected']);x[p['b_id']]=make_row(CI[p['b_id']],tokens,CI[p['a_id']]['expected'])
  run('reversed_controls',list(x.values()))
  x=copy.deepcopy(base);id='gv_b1_canonical';x[id]=make_row(CI[id],tokens,peak=.89996);run('raw_threshold',list(x.values()))
  x=copy.deepcopy(base);x[id]=make_row(CI[id],tokens,{'action':'ask_fact','determination':'yes'});low=make_row(CI[id],tokens,peak=.8);x[id]['answers']['determination']=low['answers']['determination'];x[id]['probabilities_unrounded']['determination']=low['probabilities_unrounded']['determination'];run('field_vs_case_gate',list(x.values()))
  x=copy.deepcopy(base)
  for f in FIELDS:
   opts=list(Q[id]['questions'][f]['criteria']);p={o:.5 if i<2 else 0. for i,o in enumerate(opts)};x[id]['probabilities_unrounded'][f]=dict(reversed(list(p.items())));x[id]['answers'][f]={'type':'choice','choice':opts[0],'confidence':.5,'probabilities':p}
  run('criteria_order_ties',list(x.values()))
  for name,mutation in [('wrong_tokens',lambda r:r.update(input_tokens=r['input_tokens']+1)),('truncation',lambda r:r.update(truncated=True)),('nonfinite_numeric_syntax',lambda r:r.update(rss_bytes=1e309)),('boolean_probability',lambda r:r['probabilities_unrounded']['action'].update(answer=True)),('missing_map',lambda r:r.pop('probabilities_unrounded')),('bad_confidence',lambda r:r['answers']['action'].update(confidence=.1234))]:
   x=copy.deepcopy(base);mutation(x[id]);run(name,list(x.values()),[id])
  run('duplicate_id',list(base.values())+[copy.deepcopy(base[id])],fatal=True);x=copy.deepcopy(base);x[id]['id']='unexpected';run('unexpected_id',list(x.values()),fatal=True)
  for name,mutation in [('missing_full_cap',lambda p:p['cases'][0].pop('full_cap_equal')),('missing_truncation_evidence',lambda p:p['cases'][0].pop('truncated')),('missing_encoded_schema',lambda p:p['cases'][0].pop('encoded_questions'))]:
   bad=copy.deepcopy(pfd);mutation(bad);badpf=td/(name+'.json');badpf.write_text(json.dumps(bad));run(name,list(base.values()),fatal=True,preflight=badpf)
  report={'status':'PASS_INDEPENDENT_SYNTHETIC_RECOVERY_SCORER_CHECK','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scenarios':scenarios,'assertions':checks,'token_fixture':kind,'token_fixture_sha256':sha(pf),'scorer_sha256':sha(R/'scripts/score.py'),'checker_sha256':sha(pathlib.Path(__file__)),'primary_scorer_imported':False,'native_predictions_read':False,'model_loaded':False,'api_called':False,'identity':'Fresh recovery checker and current checks; no restored historical source or result claim.'}
  (R/'evidence/independent_score_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
