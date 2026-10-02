"""Build UI data only from a completed, independently verified benchmark.

--cases-only is explicitly labelled test-data mode, never a partial result import.
General and finance suites stay separate; their scores are never pooled.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG={
    'general':{'id':'general','label':'Allgemeine Entscheidungen','primary_split':'german_primary','directory':'benchmark','results':'results','scores':'scores_robust_v1_1.json','n':180,'primary_n':120,'categories':{'it_routing':'IT- & M365-Routing','urgency':'Priorität & Negation','tool_selection':'Werkzeugauswahl','document_classification':'Dokumentfunktion','admin_intent':'Verwaltungsabsicht','ambiguity_abstain':'Mehrdeutigkeit'}},
    'finance':{'id':'finance','label':'Finanzen & Versicherungsmakler','primary_split':'german_primary','directory':'finance_benchmark','results':'results/finance','scores':'scores.json','n':100,'primary_n':80,'categories':{'insurance_intent':'Versicherungsanliegen','claims_route':'Schadenrouting','contract_service':'Vertragsservice','broker_workflow':'Makler-Workflow','broker_document':'Maklerdokumente','finance_intent':'Finanzanliegen','synthetic_rule_check':'Synthetische Regelprüfung','advice_escalation':'Beratung & Eskalation'}}
}
def read_lines(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def build(source,cases_only=False,suite='general'):
    cfg=CONFIG[suite];base=source/cfg['directory'];resultdir=source/cfg['results'];n=cfg['n']
    manifest=json.loads((base/'freeze_manifest.json').read_text())
    for name,expected in manifest['sha256'].items():
        if digest(base/name)!=expected:raise ValueError(f'Frozen file changed: {name}')
    cases=read_lines(base/'cases.jsonl')+read_lines(base/'diagnostic_cases.jsonl')
    if len(cases)!=n or len({c['id'] for c in cases})!=n:raise ValueError(f'Expected {n} unique benchmark cases')
    if set(c['category'] for c in cases)!=set(cfg['categories']):raise ValueError('Unexpected category set')
    if Counter(c['split'] for c in cases)[cfg['primary_split']]!=cfg['primary_n']:raise ValueError('Wrong primary denominator')
    public_cfg={k:v for k,v in cfg.items() if k not in ('directory','results','scores')}
    public_cfg['random_order_seed']=json.loads((base/'design_summary.json').read_text())['random_order_seed']
    payload={'status':'test_data_only','schema_version':1,'model':'Cloudflare/clef-flash','revision':'17f0b0ad64efb65d273590632833508766b2aae6','cases':cases,'suite':public_cfg}
    if cases_only:return payload
    predictions=resultdir/'predictions.jsonl'
    meta=json.loads((resultdir/'run_metadata.json').read_text())
    verify=json.loads((resultdir/'verification.json').read_text())
    scores=json.loads((resultdir/cfg['scores']).read_text())
    if meta.get('status')!='completed' or not meta.get('completed_at'):raise ValueError('Incomplete inference run refused')
    if meta.get('model')!=payload['model'] or meta.get('revision')!=payload['revision']:raise ValueError('Model identity does not match the pinned release')
    if meta.get('source_code_sha256')!='0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3':raise ValueError('Unverified native inference source')
    if meta.get('request_count')!=n or meta.get('requests_sha256')!=manifest['sha256']['requests.jsonl']:raise ValueError('Run does not match frozen requests')
    if verify.get('status')!='pass' or not verify.get('freeze_hashes_verified') or verify.get('n_present')!=n or verify.get('source_predictions_sha256')!=digest(predictions):raise ValueError('Independent verification does not match predictions')
    if verify.get('legacy_report_fields_changed') or verify.get('rounded_probability_mismatches'):raise ValueError('Independent verification contains discrepancies')
    raw=read_lines(predictions);results=scores['case_results'];ids={c['id'] for c in cases}
    for name,rows in [('predictions',raw),('scores',results)]:
        if len(rows)!=n or {r['id'] for r in rows}!=ids:raise ValueError(f'Invalid or incomplete {name}')
    if scores['counts']!={'planned':n,'present':n}:raise ValueError('Score counts are incomplete')
    raw={r['id']:r for r in raw};results={r['id']:r for r in results}
    for c in cases:
        row=raw[c['id']];score=results[c['id']];actual=row['answers']['decision']['choice'];expected=c['expected']['decision']
        if score['prediction']!=actual or score['expected']!=expected or score['correct']!=(actual==expected):raise ValueError('Case score does not match raw output and frozen label')
        probabilities=row['probabilities_unrounded']['decision'];norm=sum(probabilities.values())
        if set(probabilities)!=set(c['questions']['decision']['criteria']):raise ValueError('Probability options mismatch')
        if not all(math.isfinite(v) and 0<=v<=1 for v in probabilities.values()) or abs(norm-1)>1e-5:raise ValueError('Invalid probability vector')
        if not all(math.isclose(score['probabilities'][k],v/norm,rel_tol=1e-10,abs_tol=1e-12) for k,v in probabilities.items()):raise ValueError('Score probabilities do not match raw probabilities')
        c['result']=score;c['latency_ms']=row['latency_ms'];c['input_tokens']=row['input_tokens']
    for split in {c['split'] for c in cases}:
        rows=[c for c in cases if c['split']==split]
        accuracy=sum(c['result']['correct'] for c in rows)/len(rows)
        if not math.isclose(scores['splits'][split]['choice_accuracy_all_planned'],accuracy):raise ValueError('Aggregate accuracy does not match case scores')
    payload.update(status='completed',scores={k:v for k,v in scores.items() if k not in ('outputs_file','case_results')},verification=verify,run={'started_at':meta['started_at'],'completed_at':meta['completed_at'],'mode':meta['mode'],'load_seconds':meta['load_seconds'],'predictions_sha256':digest(predictions)})
    return payload

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=ROOT);parser.add_argument('--out',type=Path);parser.add_argument('--suite',choices=CONFIG,default='general');parser.add_argument('--cases-only',action='store_true');args=parser.parse_args()
    payload=build(args.source,args.cases_only,args.suite)
    out=args.out or ROOT/'web/data'/('benchmark.json' if args.suite=='general' else 'finance.json')
    out.parent.mkdir(parents=True,exist_ok=True)
    temporary=out.with_suffix('.tmp');temporary.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');temporary.replace(out)
    print(json.dumps({'status':payload['status'],'suite':args.suite,'cases':len(payload['cases']),'file':str(out)}))
if __name__=='__main__':main()
