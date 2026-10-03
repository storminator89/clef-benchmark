"""Read-only join of independently admitted Wähler public evidence.

No model calls, score repair, rounded probability substitution, or partial data.
The caller verifies the exact public inventory and independent admission pin.
"""
import json

def require(ok,message):
 if not ok:raise ValueError(message)
def load(path):return json.loads(path.read_text())
def lines(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def index(rows):
 result={(r['suite'],r['id']):r for r in rows}
 require(len(result)==len(rows),'Duplicate Wähler evidence case')
 return result

def build(source,admission,root):
 evidence=source/'evidence';comparison=load(source/'comparison.json')
 require(comparison['metric']=='all_fields_native_exact_over_same_planned_cases','Unexpected Wähler metric')
 planned=lines(evidence/'planned.jsonl');native=lines(evidence/'cases.jsonl');plan=index(planned);cases=index(native)
 require(len(plan)==580 and set(plan)==set(cases),'Incomplete Wähler study')
 require(sum(len(p['request']['questions']) for p in planned)==968,'Wähler field count differs')
 replay={'__file__':str(evidence/'recompute.py'),'__name__':'wahler_public_replay'}
 exec(compile((evidence/'recompute.py').read_bytes(),replay['__file__'],'exec'),replay)
 measured=replay['recompute'](planned,native)
 require(len(comparison['groups'])==8 and {g['suite'] for g in comparison['groups']}==set(measured['groups']),'Wähler comparison groups differ')
 for g in comparison['groups']:
  actual=measured['groups'][g['suite']]
  require(g['planned']==actual['planned'],'Wähler planned denominator differs')
  for model in ['clef','jev','wahler']:
   require(g['models'][model]['correct']==actual['models'][model]['correct'],'Wähler model numerator differs')
   require(g['models'][model]['planned']==g['planned'] and g['models'][model]['classifiable']==g['planned']-actual['models'][model]['missing'] and g['models'][model]['missing_or_structurally_invalid']==actual['models'][model]['missing'] and g['models'][model]['sum_only_diagnostics']==actual['models'][model]['sum_only_diagnostics'],'Wähler model coverage differs')
 require(sum(g['models']['jev']['missing'] for g in measured['groups'].values())==2,'Historical missing answers differ')
 require(all(g['models'][m]['missing']==0 for g in measured['groups'].values() for m in ['clef','wahler']),'Incomplete native baseline')
 rows=[]
 for p in planned:
  c=cases[p['suite'],p['id']]
  rows.append({'suite':p['suite'],'id':p['id'],'request':p['request'],'expected':c['expected'],'models':c['models']})
 return {'format_version':2,'id':'wahler580','status':'completed','audit':{'status':'passed','source_manifest_sha256':admission['sha256']},'comparisons':comparison['groups'],'cases':rows}
