#!/usr/bin/env python3
"""Deterministic read-only admission of separately audited study bundles.

Only explicit pinned public manifests may become displayed observations. No
inference, data repair, private recovery artifacts or historical score backfill.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
ROOT=Path(__file__).resolve().parents[1]
# Populated only after the final public bundle has passed independent review.
ADMISSIONS={'language72':{'path':'studies/language72','manifest':'PUBLIC_MANIFEST.json','sha256':'8d092cd96f86e4e5a79e2382cc81e430b96b18d7ebcf5310b45812c9f44a4427'},'jev974':{'path':'studies/jev974','manifest':'PUBLIC_MANIFEST.json','sha256':'af1055142305bc2cd2207f51e6396383ff58c54ee1af1da8b4760c661375ae35'}}

def require(value,message):
 if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text())
def rows(path):
 values=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
 require(len({r['id'] for r in values})==len(values),'Duplicate scientific ID')
 return {r['id']:r for r in values}
def verify_bundle(source,manifest_name,expected):
 require(source.is_dir() and not source.is_symlink(),'Public bundle missing')
 require(sha(source/manifest_name)==expected,'Public manifest pin differs')
 manifest=load(source/manifest_name);files=manifest.get('files',manifest.get('files_sha256'))
 require(isinstance(files,dict),'Unsupported public file inventory')
 for p in source.rglob('*'):require(not p.is_symlink(),'Public bundle contains symlink')
 actual={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
 require(actual==set(files)|{manifest_name},'Public bundle file set differs')
 for name,metadata in files.items():
  relative=Path(name);require(not relative.is_absolute() and '..' not in relative.parts,'Invalid public relative path')
  digest=metadata if isinstance(metadata,str) else metadata['sha256']
  require(sha(source/name)==digest,'Public scientific bytes changed: '+name)
 return manifest

def metric(label,n,d,unit,note=None):
 require(type(n)is int and type(d)is int and 0<=n<=d and d>0,'Invalid metric denominator')
 result={'kind':'ratio','label':label,'numerator':n,'denominator':d,'unit':unit}
 if note:result['note']=note
 return result

def language72(source,admission):
 audit=load(source/'evidence/independent_final_summary.json')
 require(audit['status']=='PASS_INDEPENDENT_COMPLETED_RESULT_AUDIT' and audit['primary_scorer_imported'] is False and audit['independent_native_rows']==72 and audit['invalid_native_rows']==0 and audit['all_error_artifacts_checked']==8,'Independent completed audit is missing')
 requests=rows(source/'data/requests.jsonl');cases=rows(source/'data/cases.reconstructed.jsonl');gold=rows(source/'data/gold.reconstructed.jsonl');native=rows(source/'results/predictions.jsonl');scored=rows(source/'scored/case_scores.jsonl');summary=load(source/'scored/summary.json')
 require(len(requests)==72 and requests.keys()==cases.keys()==gold.keys()==native.keys()==scored.keys(),'Incomplete or extra language72 evidence')
 require(summary['technical']['recorded']==summary['technical']['valid']==72 and summary['technical']['missing']==summary['technical']['invalid_existing']==0,'Language72 run is incomplete or invalid')
 output=[]
 for ident,q in requests.items():
  request=q['request'];case=cases[ident];g=gold[ident]['expected'];prediction=native[ident];score=scored[ident]
  require(case['expected']==g and score['expected']==g,'Gold differs across retained sources')
  require(set(request['questions'])==set(g)==set(prediction['answers'])==set(prediction['probabilities_unrounded'])=={'action','determination'},'Native question field set differs')
  require(type(prediction['input_tokens'])is int and 1<=prediction['input_tokens']<=2048 and prediction['truncated'] is False,'Invalid native token evidence')
  chosen={}
  for field,question in request['questions'].items():
   probabilities=prediction['probabilities_unrounded'][field];answer=prediction['answers'][field]
   require(set(probabilities)==set(question['criteria']) and all(type(v)in(int,float) and math.isfinite(v) and 0<=v<=1 for v in probabilities.values()),'Incomplete native probabilities')
   require(abs(math.fsum(probabilities.values())-1)<1e-5,'Invalid native normalization')
   require(answer['type']=='choice' and answer['choice']==max(question['criteria'],key=lambda key:probabilities[key]),'Native argmax or tie convention differs')
   require(answer['confidence']==round(probabilities[answer['choice']],4) and answer['probabilities']=={k:round(v,4) for k,v in probabilities.items()},'Rounded and unrounded native maps disagree')
   require(g[field] in question['criteria'],'Gold outside original options')
   chosen[field]=answer['choice']
  exact=chosen==g
  require(score['recorded'] is True and score['valid'] is True and score['exact']==exact and score['predicted']==chosen and score['probabilities_unrounded']==prediction['probabilities_unrounded'],'Saved per-case score differs from native recomputation')
  output.append({'id':ident,'input':request['state'],'questions':request['questions'],'expected':g,'prediction':chosen,'probabilities':prediction['probabilities_unrounded'],'native_answers':prediction['answers'],'valid':True,'correct':exact,'group':case['style'],'pair_id':case['cluster_id'],'source':{'study_group':case['group'],'domain':case['domain'],'cluster_id':case['cluster_id'],'native_case_id':ident}})
 count=sum(r['correct'] for r in output)
 require(summary['all_cases']['all_fields_exact']=={'numerator':count,'denominator':72,'rate':count/72},'Overall score differs')
 by_id={r['id']:r for r in output};pair_rows=[json.loads(x) for x in (source/'data/pairs.reconstructed.jsonl').read_text().splitlines() if x.strip()]
 invariant=[p for p in pair_rows if p['kind']=='invariant']
 require(len(invariant)==48,'Invariant-pair design differs')
 both=sum(by_id[p['a_id']]['correct'] and by_id[p['b_id']]['correct'] for p in invariant)
 require(summary['invariant_pairs']['both_correct']['numerator']==both and summary['invariant_pairs']['both_correct']['denominator']==48,'Pair score differs')
 clusters={}
 for case in cases.values():
  if case['group']=='invariant':clusters.setdefault(case['cluster_id'],[]).append(case['id'])
 require(len(clusters)==12 and all(len(ids)==5 for ids in clusters.values()),'Invariant cluster design differs')
 robust=sum(all(by_id[i]['correct'] for i in ids) for ids in clusters.values())
 require(summary['cluster_robustness']['all_five_correct']['numerator']==robust and summary['cluster_robustness']['all_five_correct']['denominator']==12,'Cluster score differs')
 ambiguity=[p for p in pair_rows if p not in invariant];require(len(ambiguity)==6,'Ambiguity control design differs')
 directional=sum(by_id[p['a_id']]['correct'] and by_id[p['b_id']]['correct'] and by_id[p['a_id']]['prediction']!=by_id[p['b_id']]['prediction'] for p in ambiguity)
 require(summary['ambiguity_controls']['correct_directional_change']['numerator']==directional and summary['ambiguity_controls']['correct_directional_change']['denominator']==6,'Ambiguity control score differs')
 changes=sum(by_id[p['a_id']]['prediction']!=by_id[p['b_id']]['prediction'] for p in invariant)
 improvements=sum(not by_id[p['a_id']]['correct'] and by_id[p['b_id']]['correct'] for p in invariant)
 losses=sum(by_id[p['a_id']]['correct'] and not by_id[p['b_id']]['correct'] for p in invariant)
 wrong_changes=sum(not by_id[p['a_id']]['correct'] and not by_id[p['b_id']]['correct'] and by_id[p['a_id']]['prediction']!=by_id[p['b_id']]['prediction'] for p in invariant)
 stable_wrong=sum(not by_id[p['a_id']]['correct'] and not by_id[p['b_id']]['correct'] and by_id[p['a_id']]['prediction']==by_id[p['b_id']]['prediction'] for p in invariant)
 for key,n in [('observed_change',changes),('improvement',improvements),('degradation',losses),('stable_wrong',stable_wrong)]:require(summary['invariant_pairs'][key]['numerator']==n and summary['invariant_pairs'][key]['denominator']==48,'Directional pair metric differs')
 targets=[r for r in output if r['expected']['action']=='ask_target'];other=[r for r in output if r not in targets]
 require(all(r['correct'] for r in other),'Non-target error contradicts admitted error focus')
 return {'format_version':1,'id':'language72','status':'completed','audit':{'status':'passed','source_manifest_sha256':admission['sha256']},'metrics':[metric('Beide Felder richtig',count,72,'Anfragen'),metric('Technisch gültig',72,72,'Anfragen'),metric('Beide Varianten richtig',both,48,'überlappende Invarianzpaare')],'secondary_metrics':[metric('Alle fünf Varianten richtig',robust,12,'Basisgruppen'),metric('Bedeutungswechsel richtig',directional,6,'Kontrollpaare'),metric('Zielmehrdeutigkeit richtig',sum(r['correct'] for r in targets),len(targets),'Anfragen'),metric('Andere Fälle richtig',len(other),len(other),'Anfragen')],'findings':[f'Alle {72-count} Fehler betreffen Zielmehrdeutigkeit.'],'directional_note':f'{changes} Invarianzpaare ändern ihre Antwort: {improvements} Verbesserungen, {wrong_changes} Wechsel zwischen falschen Antworten und {losses} Verschlechterungen. {stable_wrong} weitere Paare bleiben gleich falsch.','group_labels':{'canonical':'Standardform','typo':'Tippfehler','abbreviation':'Abkürzungen','de_en_mix':'Deutsch-Englisch-Mix','fact_status_removed':'Fakt fehlt','target_removed':'Ziel fehlt','compact_colloquial':'Knapp & umgangssprachlich'},'limitations':['Die originalen 72 Anfragebytes wurden wiederhergestellt; Scorer, Lauf und öffentliche Dokumentation sind eine neue Wiederherstellungsrevision.','Experimentelles CPU-NF4 mit originalem Joint-Head. Native Optionscores sind keine kalibrierten Wahrscheinlichkeiten.'],'cases':output}

BUILDERS={'language72':language72}
def build_all(root=ROOT):
 result={}
 for ident,admission in ADMISSIONS.items():
  source=root/admission['path'];verify_bundle(source,admission['manifest'],admission['sha256'])
  if ident=='jev974':
   namespace={'__file__':str(root/'scripts/study_jev_adapter.py'),'__name__':'study_jev_adapter'}
   exec(compile((root/'scripts/study_jev_adapter.py').read_bytes(),namespace['__file__'],'exec'),namespace)
   result[ident]=namespace['build'](source,admission,root)
   direct={'__file__':str(root/'scripts/study_jev_direct_adapter.py'),'__name__':'study_jev_direct_adapter'}
   exec(compile((root/'scripts/study_jev_direct_adapter.py').read_bytes(),direct['__file__'],'exec'),direct)
   result[ident]=direct['apply'](result[ident],root)
  else:
   require(ident in BUILDERS,'No reviewed adapter for admitted study')
   result[ident]=BUILDERS[ident](source,admission)
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();outputs=build_all();index=load(ROOT/'web/studies-data/index.json')
 require({s['id'] for s in index['studies'] if s['status']=='completed'}==set(outputs),'Index completion differs from admitted sources')
 for ident,data in outputs.items():
  content=json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n';target=ROOT/f'web/studies-data/{ident}.json'
  if args.check:require(target.read_text()==content,'Derived study data differs: '+ident)
  else:target.write_text(content)
 print(f'PASS: {len(outputs)} independently admitted study bundles; pending studies contain no invented observations')
if __name__=='__main__':main()
