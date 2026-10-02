#!/usr/bin/env python3
"""Read-only source and diagnostic validation, no model loading."""
import copy, hashlib, importlib.util, json, subprocess, sys, tempfile
from pathlib import Path
D=Path(__file__).resolve().parent;SRC=D.parents[2]/'finance_benchmark'
def read(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 design=json.loads((D/'design.json').read_text());original={c['id']:c for c in read(SRC/'cases.jsonl')};source_requests={r['id']:r for r in read(SRC/'requests.jsonl')}
 assert sha(SRC/'freeze_manifest.json')==design['original_source_manifest_sha256']
 for n,s in design['source_frozen_sha256'].items():assert sha(SRC/n)==s,n
 assert sha(D/'source_score.py')==sha(SRC/'score.py')
 assert sha(D.parents[2]/'runtime/run_clef.py')==design['runner_sha256']
 assert (D/'policies.json').read_bytes()==(SRC/'policies.json').read_bytes()
 selected={i for i,c in original.items() if c['language']=='de' and 'prompt_injection' in c['tags']}
 pairs=read(D/'pairs.jsonl');cases=read(D/'cases.jsonl');requests=read(D/'requests.jsonl');gold=read(D/'gold.jsonl')
 assert len(pairs)==7 and {p['source_id'] for p in pairs}==selected
 assert len(cases)==len(requests)==len(gold)==14
 cs={c['id']:c for c in cases};rs={r['id']:r for r in requests};gs={g['id']:g for g in gold}
 assert len(cs)==len(rs)==len(gs)==14 and set(cs)==set(rs)==set(gs)
 assert [r['id'] for r in requests]==design['request_order_ids']
 assert sum(p['within_pair_order'][0]=='attack' for p in pairs)==4
 expected_order=[]
 for p in pairs:
  src=original[p['source_id']];a=p['attack_id'];c=p['clean_id']
  assert p['attack_state']==src['input']==cs[a]['input']
  assert p['clean_state']==cs[c]['input']
  assert p['attack_state']==p['clean_state']+p['removed_suffix']
  assert p['deletion_start_character']==len(p['clean_state']) and p['deletion_end_character']==len(p['attack_state'])
  assert src['expected']['decision']==p['expected']
  assert p['within_pair_order'] in [['attack','clean'],['clean','attack']]
  expected_order.extend(p[k+'_id'] for k in p['within_pair_order'])
  for cond,cid in [('attack',a),('clean',c)]:
   case=cs[cid];req=rs[cid];g=gs[cid]
   for field in ['category','expected','gold_rationale','questions','language','schema_language','tags']:assert case[field]==src[field],(cid,field)
   assert case['source_id']==src['id'] and case['condition']==cond
   assert set(req)=={'id','request'} and set(req['request'])=={'model','state','questions'}
   assert req['request']['questions']==src['questions'] and req['request']['state']==case['input']
   assert req['request']['model']=='clef-flash' and g['expected']==src['expected']
   original_request=source_requests[src['id']]['request']
   assert {k:v for k,v in req['request'].items() if k!='state'}=={k:v for k,v in original_request.items() if k!='state'}
   if cond=='attack':assert req['request']==original_request
 assert expected_order==design['request_order_ids']
 with tempfile.TemporaryDirectory() as td:
  subprocess.run([sys.executable,str(D/'build_ablation.py'),'--out',td],check=True)
  for n in ['cases.jsonl','requests.jsonl','gold.jsonl','pairs.jsonl','policies.json','design.json']:assert (D/n).read_bytes()==(Path(td)/n).read_bytes(),n
 spec=importlib.util.spec_from_file_location('source_score',D/'source_score.py');sc=importlib.util.module_from_spec(spec);spec.loader.exec_module(sc)
 for case in cases:
  labels=list(case['questions']['decision']['criteria']);answer=case['expected']['decision'];wrong=next(x for x in labels if x!=answer)
  def fake(choice):return {'id':case['id'],'answers':{'decision':{'type':'choice','choice':choice,'confidence':1.,'probabilities':{x:float(x==choice) for x in labels}}}}
  assert sc.inspect(case,fake(answer))['strict_correct']
  assert not sc.inspect(case,fake(wrong))['correct']
  assert not sc.inspect(case,None)['correct']
  bad=fake(answer);bad['answers']['decision']['confidence']=0.
  assert not sc.inspect(case,bad)['schema_valid']
  bad=fake(answer);bad['answers']['decision']['choice']='__invalid__'
  assert not sc.inspect(case,bad)['correct']
 freeze=D/'freeze_manifest.json'
 if freeze.exists():
  for n,s in json.loads(freeze.read_text())['sha256'].items():assert sha(D/n)==s,n
 print(json.dumps({'status':'PASS','source_frozen_files_intact':True,'all_seven_selected':True,'exact_suffix_deletions':True,'unchanged_task_gold_policy_schema':True,'label_free_requests':14,'deterministic_rebuild':True,'scorer_fixtures_pass':True,'diagnostic_freeze_checked':freeze.exists()},indent=2))
if __name__=='__main__':main()
