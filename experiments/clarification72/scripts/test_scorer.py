#!/usr/bin/env python3
import copy,json,tempfile,math
from pathlib import Path
from score import score,read
R=Path(__file__).resolve().parents[1];C=read(R/'data/cases.jsonl');Q=json.loads((R/'data/policy.json').read_text())['questions'];checks=[]
def preds_for(choose):
 out=[]
 for c in C:
  labels=choose(c);probs={f:{o:.97 if o==labels[f] else .03/(len(Q[f]['criteria'])-1) for o in Q[f]['criteria']} for f in Q}
  out.append({'id':c['id'],'answers':{f:{'type':'choice','choice':labels[f],'confidence':.97} for f in Q},'probabilities_unrounded':probs,'input_tokens':700,'truncated':False,'inference_seconds':1.,'encode_seconds':.01,'total_seconds':1.01,'rss_bytes':1})
 return out
def run(p):
 with tempfile.TemporaryDirectory() as d:
  pth=Path(d);(pth/'predictions.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in p));return score(R/'data',pth)
def check(name,fn):fn();checks.append({'name':name,'passed':True})
def oracle():
 s=run(preds_for(lambda c:c['expected']));assert s['metrics']['all_fields_exact']['numerator']==72;assert s['events']['risky_wrong_answers']['count']==0
check('oracle 72/72 and no risky errors',oracle)
def always_answer():
 s=run(preds_for(lambda c:{'action':'answer','determination':'yes'}));assert s['events']['missed_required_clarifications']['count']==36;assert s['events']['excess_clarifications']['count']==0;assert s['events']['risky_wrong_answers']['count']==54;assert s['high_confidence']['0.9']['confident_wrong']==54;assert s['metrics']['all_fields_exact']['numerator']==18
check('always yes misses 36 clarification cases and is wrong on 54/72',always_answer)
def always_ask():
 s=run(preds_for(lambda c:{'action':'ask_fact','determination':'unresolved'}));assert s['events']['excess_clarifications']['count']==36;assert s['events']['wrong_clarification_kind']['count']==24;assert s['metrics']['all_fields_exact']['numerator']==12
check('always clarify penalized by 36 answerable controls',always_ask)
def missing():
 s=run(preds_for(lambda c:c['expected'])[:-1]);assert s['metrics']['all_fields_exact']=={'numerator':71,'denominator':72,'rate':71/72};assert s['technical']['missing_predictions']==1
check('missing row retains denominator72 and is incorrect',missing)
def malformed():
 p=preds_for(lambda c:c['expected']);p[0]['probabilities_unrounded']['action']['answer']=math.nan;s=run(p);assert s['technical']['invalid_existing_predictions']==1;assert s['metrics']['all_fields_exact']['numerator']==71
check('NaN invalidates whole case without denominator loss',malformed)
def inconsistent():
 p=preds_for(lambda c:{'action':'answer','determination':'unresolved'});s=run(p);assert s['events']['inconsistent_fields']['count']==72;assert s['events']['substantive_answer_cases']['count']==0;assert s['events']['missed_required_clarifications']['count']==36
check('inconsistent answer-unresolved visible without fake substantive answer',inconsistent)
def duplicates():
 p=preds_for(lambda c:c['expected']);p.append(p[0]);
 try:run(p)
 except AssertionError:return
 raise AssertionError('accepted duplicate')
check('duplicates rejected',duplicates)
def extra():
 p=preds_for(lambda c:c['expected']);z=copy.deepcopy(p[0]);z['id']='other';p.append(z)
 try:run(p)
 except AssertionError:return
 raise AssertionError('accepted extra ID')
check('unexpected IDs rejected',extra)
result={'purpose':'Synthetic scorer self-tests; no model outputs','tests':checks,'passed':len(checks),'failed':0};(R/'audit/scorer_self_tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
