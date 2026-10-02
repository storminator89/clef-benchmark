#!/usr/bin/env python3
"""Model-free native-output and denominator mutations."""
from pathlib import Path
import json,copy,tempfile,math
from score import read,score,native
R=Path(__file__).resolve().parents[1];C=read(R/'data/cases.jsonl');Q={r['id']:r['request'] for r in read(R/'data/requests.jsonl')};checks=[]
def record(c,choices=None):
 choices=choices or c['expected'];p={'id':c['id'],'answers':{},'probabilities_unrounded':{},'input_tokens':1000,'truncated':False,'encode_seconds':.1,'inference_seconds':1.2,'total_seconds':1.3,'latency_ms':1200.,'rss_bytes':10000}
 for f,opts in [(f,Q[c['id']]['questions'][f]['criteria']) for f in choices]:
  probs={k:(.9 if k==choices[f] else .1/(len(opts)-1)) for k in opts};p['probabilities_unrounded'][f]=probs;p['answers'][f]={'type':'choice','choice':choices[f],'confidence':.9,'probabilities':{k:round(v,4) for k,v in probs.items()}}
 return p
P=[record(c) for c in C]
def test(name,fn):fn();checks.append(name)
def run(rows):
 with tempfile.TemporaryDirectory() as t:
  o=Path(t);(o/'predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));return score(R/'data',o)
def assert_(x):assert x
s=run(P)
test('perfect_fixed_denominators',lambda:assert_(s['case_metrics']['all_fields_exact']=={'numerator':48,'denominator':48,'rate':1.} and s['source_metrics']['unique_source_correct']['denominator']==27 and s['source_metrics']['ambiguous_source_correct']['denominator']==21 and s['clarification_metrics']['missed']['denominator']==12 and s['clarification_metrics']['excess']['denominator']==36 and s['source_metrics']['same_answer_ambiguous_source_exact']['denominator']==9))
test('same_answer_source_ambiguity_not_inconsistent',lambda:assert_(s['consistency']['field_pair_inconsistent_with_visible_rules']['numerator']==0))
s=run(P[:-1]);test('missing_counts_in_full_denominator',lambda:assert_(s['case_metrics']['all_fields_exact']['numerator']==47 and s['case_metrics']['all_fields_exact']['denominator']==48 and s['technical']['missing_predictions']==1))
s=run([]);test('all_missing_technical_explicit',lambda:assert_(s['case_metrics']['all_fields_exact']['rate']==0 and s['technical']['missing_predictions']==48 and s['clarification_metrics']['invalid_on_required']['numerator']==12 and s['clarification_metrics']['invalid_on_answerable']['numerator']==36))
p=P[0]
mutations={
 'missing_field':lambda p:p['answers'].pop('source'),
 'missing_probability_map':lambda p:p.pop('probabilities_unrounded'),
 'missing_option':lambda p:p['probabilities_unrounded']['source'].pop('D1'),
 'nan_probability':lambda p:p['probabilities_unrounded']['source'].update(D1=float('nan')),
 'bool_probability':lambda p:p['probabilities_unrounded']['source'].update(D1=True),
 'negative_probability':lambda p:p['probabilities_unrounded']['source'].update(D1=-.1),
 'bad_sum':lambda p:p['probabilities_unrounded']['source'].update(D1=.1234),
 'wrong_native_argmax':lambda p:p['answers']['source'].update(choice='not_unique' if p['answers']['source']['choice']!='not_unique' else 'D1'),
 'rounded_mismatch':lambda p:p['answers']['source']['probabilities'].update(D1=.4321),
 'rounded_missing':lambda p:p['answers']['source'].pop('probabilities'),
 'confidence_mismatch':lambda p:p['answers']['source'].update(confidence=.8),
 'near_confidence_mismatch':lambda p:p['answers']['source'].update(confidence=.9001),
 'bad_tokens':lambda p:p.update(input_tokens=2049),
 'bool_tokens':lambda p:p.update(input_tokens=True),
 'truncation':lambda p:p.update(truncated=True),
 'missing_telemetry':lambda p:p.pop('rss_bytes'),
 'negative_telemetry':lambda p:p.update(inference_seconds=-1),
 'latency_mismatch':lambda p:p.update(latency_ms=1),
 'malformed_answer':lambda p:p['answers'].update(source=None),
}
for name,fn in mutations.items():
 m=copy.deepcopy(p);fn(m);test(name,lambda m=m:assert_(not native(m,Q[m['id']])[0]));rows=copy.deepcopy(P);rows[0]=m;s=run(rows);test(name+'_denominator',lambda:assert_(s['case_metrics']['all_fields_exact']['numerator']==47 and s['technical']['invalid_existing_predictions']==1))
for name,rows in [('duplicate_ids',P+[P[0]]),('unexpected_ids',P+[dict(P[0],id='BAD')])]:
 try:run(rows)
 except (AssertionError,ValueError):checks.append(name)
 else:raise AssertionError(name)
# Native criterion-order tie behavior.
m=copy.deepcopy(p);opts=Q[m['id']]['questions']['source']['criteria'];probs={k:.25 for k in opts};m['probabilities_unrounded']['source']=probs;m['answers']['source']={'type':'choice','choice':next(iter(opts)),'confidence':.25,'probabilities':probs};test('tie_first_criterion',lambda:assert_(native(m,Q[m['id']])[0]));m['answers']['source']['choice']=list(opts)[1];test('tie_later_criterion_invalid',lambda:assert_(not native(m,Q[m['id']])[0]))
# Fixed strata rates, clarity errors, and safe same-answer controls.
for goldout,newout,metricname,den in [('unresolved','yes','missed',12),('yes','unresolved','excess',36)]:
 rows=copy.deepcopy(P);i=next(i for i,c in enumerate(C) if c['expected']['determination']==goldout);ch=dict(C[i]['expected'],determination=newout);rows[i]=record(C[i],ch);s=run(rows);test(metricname,lambda:assert_(s['clarification_metrics'][metricname]['numerator']==1 and s['clarification_metrics'][metricname]['denominator']==den))
res={'status':'passed','model_loaded':False,'count':len(checks),'checks':checks};(R/'audit/scorer_self_tests.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
