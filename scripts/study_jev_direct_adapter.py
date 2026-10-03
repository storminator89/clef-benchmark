"""Explicit post-hoc answer correctness; frozen strict adapter remains unchanged."""
import hashlib,json,math
PIN='468f87729b3a104cf183092e0d53fa9aa120212c3f817d3fc0df673becae114e'
VERSION='native-answer-correctness-v1'
def require(ok,msg):
 if not ok:raise ValueError(msg)
def apply(data,root):
 source=root/'studies/jev974-answer-correctness-v1';manifest=source/'SHA256.json'
 require(hashlib.sha256(manifest.read_bytes()).hexdigest()==PIN,'Direct analysis manifest differs')
 files=json.loads(manifest.read_text())
 for name,sha in files.items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==sha,'Direct analysis bytes differ: '+name)
 rows=[json.loads(x) for x in (source/'case_comparison.jsonl').read_text().splitlines()];summary=json.loads((source/'comparison_summary.json').read_text())
 require(summary['metric_version']==VERSION and len(rows)==974,'Direct metric version/count differs')
 by_id={r['suite']+' / '+r['id']:r for r in rows};require(len(by_id)==974,'Duplicate direct case')
 restored=0
 for row in data['cases']:
  score=by_id[row['id']];require(row['expected']==score['expected'],'Direct gold differs')
  if not row['valid'] and score['evaluable']['jev']:
   require(score['jev_answer_status']=='native_answer_sum_only_deviation' and 'native_quarantine' in row,'Unsupported restored answer')
   native=row['native_quarantine'];row['prediction']={k:a['choice'] for k,a in native['answers'].items()};row['probabilities']=native['probabilities_unrounded'];row['native_answers']=native['answers'];row['valid']=True;row['correct']=row['prediction']==row['expected'];row['sum_only_deviation']=True
   for key,v in row['probabilities'].items():require(math.fsum(v.values())==score['jev_native_probability_sums'][key],'Native sums differ')
   del row['native_quarantine'];row.pop('technical_note',None);restored+=1
  if not row['valid']:row['technical_note']='Keine vollständig erhaltene auswertbare Antwort. Keine nachgewiesene fachliche Fehlentscheidung.'
  require(row['valid']==score['evaluable']['jev'] and row['prediction']==score['choices']['jev'] and (row['correct'] if row['valid'] else None)==score['exact']['jev'],'Direct case differs from native evidence')
  baseline=row.get('baseline_result');require((baseline['prediction'] if baseline else None)==score['choices']['clef'] and (baseline['correct'] if baseline else None)==score['exact']['clef'],'Direct baseline differs')
 require(restored==35 and sum(r['valid'] for r in data['cases'])==972,'Direct eligibility differs')
 old={(r['suite'],r['split']):r for r in data['comparisons']};comparisons=[]
 for p in summary['partitions']:
  key=(p['suite'],p['split']);selected=[r for r in rows if (r['suite'],r['split'])==key]
  require(len(selected)==p['planned']==p['expected'],'Direct denominator differs')
  for model in ['clef','jev']:
   n=sum(r['exact'][model] is True for r in selected);answered=sum(r['evaluable'][model] for r in selected)
   require(p[model+'_answered']==(answered if model=='jev' or answered else None) and p[model+'_correct']==(n if answered else None),'Direct numerator differs')
  comparisons.append({'suite':p['suite'],'split':p['split'],'label':old[key]['label'],'expected':p['planned'],'clef_correct':p['clef_correct'],'jev_correct':p['jev_correct'],'jev_answered':p['jev_answered'],'jev_no_answer':p['jev_no_answer'],'baseline_ready':p['baseline_status']=='complete','primary':p['split'] in ('german_primary','german_clean_primary','diagnostic_pairs')})
 data.update(analysis=VERSION,comparisons=comparisons,metrics=[],findings=[],normalization_rule='diagnostic_only',limitations=['Die Antwort-Richtigkeitsanalyse vergleicht unveränderte native Auswahloptionen mit den Referenzlabels. Die ursprüngliche strikte Antwortvertragsauswertung bleibt separat erhalten.','Optionscores sind keine kalibrierten Fehlerwahrscheinlichkeiten. Andere Hardware und Präzision erlauben keinen gemeinsamen Geschwindigkeitsvergleich.'])
 data['audit']['analysis_manifest_sha256']=PIN
 return data
