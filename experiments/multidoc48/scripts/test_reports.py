#!/usr/bin/env python3
"""Synthetic-only report rendering smoke test in a disposable directory."""
from pathlib import Path
import tempfile,shutil,json,subprocess,sys,copy
from score import read,score
R=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
 t=Path(temp);(t/'scripts').mkdir();(t/'results').mkdir();shutil.copytree(R/'data',t/'data');shutil.copyfile(R/'scripts/build_reports.py',t/'scripts/build_reports.py')
 C=read(t/'data/cases.jsonl');Q={q['id']:q['request'] for q in read(t/'data/requests.jsonl')};rows=[]
 for c in C:
  p={'id':c['id'],'input_tokens':900,'truncated':False,'encode_seconds':.1,'inference_seconds':1.,'total_seconds':1.1,'latency_ms':1000.,'rss_bytes':1024,'answers':{},'probabilities_unrounded':{}}
  for f,label in c['expected'].items():
   opts=Q[c['id']]['questions'][f]['criteria'];v={k:(.9 if k==label else .1/(len(opts)-1)) for k in opts};p['probabilities_unrounded'][f]=v;p['answers'][f]={'type':'choice','choice':label,'confidence':.9,'probabilities':{k:round(z,4) for k,z in v.items()}}
  rows.append(p)
 invalid=copy.deepcopy(rows)
 for p in invalid:p['answers']['source']['confidence']=.9001
 for name,fixture,expected_exact,expected_errors in [('complete',rows,'48/48',0),('partial',rows[:24],'24/48',24),('all_missing',[],'0/48',48),('all_invalid',invalid,'0/48',48)]:
  (t/'results/predictions.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in fixture));score(t/'data',t/'results')
  (t/'results/predictions.metadata.json').write_text(json.dumps({'revision':'synthetic-only','started_at':'synthetic-only','status':'synthetic-only','load_seconds':0}))
  (t/'freeze_manifest.json').write_text(json.dumps({'frozen_at_utc':'synthetic-only'}));subprocess.run([sys.executable,str(t/'scripts/build_reports.py')],check=True)
  assert expected_exact in (t/'REPORT.md').read_text() and f'{expected_errors} cases.' in (t/'ERRORS.md').read_text(),name
  if name in ('all_missing','all_invalid'):assert 'median unavailable; interpolated p95 unavailable' in (t/'REPORT.md').read_text()
result={'passed':True,'model_loaded':False,'synthetic_only':True,'checks':['complete report rendering','partial report rendering','all-missing report rendering','all-invalid report rendering','unavailable timings safe','error-count and exactness figures','temporary-directory-only output']};(R/'audit/report_self_test.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
