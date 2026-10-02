#!/usr/bin/env python3
"""Audit all rendered tables/errors and key narrative denominators independently."""
import hashlib,json,math,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checks=0
def read(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()]
def expect(a,b,label):
    global checks
    checks+=1
    if a!=b:raise AssertionError(f'{label}: {a!r} != {b!r}')
def number(v,digits=6):return 'nicht definiert' if v is None else f'{v:.{digits}f}'
def percent(v):return 'nicht definiert' if v is None else f'{100*v:.2f}%'
def sections(name):return re.split(r'^## ',(ROOT/name).read_text(),flags=re.M)[1:]
def key(r):return (r['suite_id'],tuple(sorted(r['partition'].items())),r['field'],tuple(sorted(r['option_keys'])))
def cells(line):return [p.strip().replace('\\|','|') for p in re.split(r'(?<!\\)\|',line.strip())[1:-1]]

def main():
    independent={key(r):r for r in read('audit/independent_field_metrics.json')}
    primary=read('results/field_metrics.json')
    byid={r['group_id']:independent[key(r)] for r in primary}
    pbyid={r['group_id']:r for r in primary}
    field_sections=sections('FIELD_DETAILS.md');expect(len(field_sections),78,'all field sections')
    seen=[];local_warnings=dict(chart_field_groups=0,chart_case_groups=0,chart_error_sections=0,blank_error_sections=0)
    for section in field_sections:
        gid=re.search(r'Gruppen-ID: `([^`]+)`',section)[1];seen.append(gid);r=byid[gid];p=pbyid[gid]
        if r['suite_id']=='images90' and r['field']=='chart_type':
            before_values=section.split('Gruppen-ID:',1)[0]
            expect(all(s in before_values for s in ('bar_line/vbar2','unveränderten Quellen-Gold','nicht automatisch ein eindeutig validierter Modellfehler')),True,'local chart-type field interpretation warning')
            local_warnings['chart_field_groups']+=1
        for line in section.splitlines():
            if line.startswith('| Bin '):expect(len(cells(line)),7,'bin table header columns')
        expect(f"Erwartet {r['expected_n']}; gültig {r['valid_n']}; ungültig 0; fehlend 0. Richtig {r['correct']}/{r['valid_n']}; Genauigkeit {percent(r['accuracy'])}." in section,True,'field denominators')
        expect(f"Optionen ({len(r['option_keys'])}): "+', '.join(r['option_keys'])+'.' in section,True,'field options')
        nll='unendlich' if r['nll']=='infinite' else number(r['nll'])
        expect(f"Brier (Klassensumme, 0–2): {number(r['brier'])}; NLL (nats): {nll}; Gold-p=0: {len(r['infinite_nll_ids'])}; ECE: {number(r['ece'])}." in section,True,'field proper scores')
        expect(f"Mittlerer Auswahlscore: {number(r['mean_confidence'])}; Score−Genauigkeit: {number(r['mean_confidence']-r['accuracy'])}; exakte Maximalwert-Bindungen: {p['tie_count']}; Fehler-AUROC: {number(r['error_auroc'])} (richtig={r['correct']}, falsch={r['valid_n']-r['correct']})." in section,True,'field auxiliary scores')
        b_rows=[cells(s) for s in section.splitlines() if s.startswith('| [')]
        expect(len(b_rows),10,'all bin rows')
        for got,b in zip(b_rows,r['bins']):
            want=[f"[{b['lower']:.1f},{b['upper']:.1f}"+(']' if b['upper_inclusive'] else ')'),str(b['count']),str(b['correct']),number(b['mean_confidence']),number(b['accuracy']),number(b['mean_confidence']-b['accuracy'] if b['count'] else None),number(b['absolute_gap'])]
            expect(got,want,'all rendered bin values')
        t_rows=[cells(s) for s in section.splitlines() if re.match(r'^\| 0\.\d\d \|',s)]
        expect(len(t_rows),6,'all threshold rows')
        for got,t in zip(t_rows,r['risk_coverage']):
            want=[number(t['threshold'],2),f"{t['accepted']}/{r['expected_n']}",str(t['errors']),percent(t['expected_coverage']),percent(t['coverage']),percent(t['risk'])]
            expect(got,want,'all rendered threshold values')
            tstr=number(t['threshold'],2)
            want_ids=p['high_score_error_ids'][tstr]
            expect('- ≥'+tstr+': '+(', '.join(want_ids) if want_ids else 'keine') in section,True,'high-score error ID list')
    expect(set(seen),set(byid),'field section identities');expect(len(set(seen)),len(seen),'unique field sections')
    cases={r['case_group_id']:r for r in read('results/case_metrics.json')}
    case_sections=sections('CASE_HEURISTICS.md');expect(len(case_sections),64,'all case sections')
    for section in case_sections:
        gid=re.search(r'Gruppen-ID `([^`]+)`',section)[1];r=cases[gid]
        if r['suite_id']=='images90' and r['partition'].get('kind')=='chart':
            before_values=section.split('Gruppen-ID',1)[0]
            expect(all(s in before_values for s in ('bar_line/vbar2','gold-relativ','nicht für jede Abweichung einen eindeutig validierten Modellfehler')),True,'local chart whole-case interpretation warning')
            local_warnings['chart_case_groups']+=1
        expect(f"{r['exact_count']}/{r['valid_count']} ganze Fälle exakt; erwartet {r['expected_count']}; ungültig/fehlend 0." in section,True,'case accounting')
        table=[cells(s) for s in section.splitlines() if re.match(r'^\| 0\.\d\d \|',s)]
        expect(len(table),6,'all case thresholds')
        for got,t in zip(table,r['risk_coverage_heuristic']):
            want=[number(t['threshold'],2),f"{t['selected_count']}/{r['expected_count']}",str(t['incorrect']),percent(t['coverage']),percent(t['risk']),', '.join(t['incorrect_ids']) or 'keine']
            expect(got,want,'case rendered values')
    raw_sources={}
    for suite in read('SOURCE_INVENTORY.json')['suites']:
        sid=suite['suite_id'];raw_sources[sid]={x['id']:x for x in rows(f'sources/{sid}/predictions.jsonl')}
    errors={(x['suite_id'],x['id'],x['field']):x for x in rows('results/all_errors.jsonl')}
    error_sections=sections('ERRORS.md');expect(len(error_sections),124,'all error sections');seen=[]
    for section in error_sections:
        k=tuple(section.splitlines()[0].split(' / '));seen.append(k);r=errors[k];p=raw_sources[k[0]][k[1]]
        before_values=section.split('Gold `',1)[0]
        if k[0]=='images90' and k[2]=='chart_type':
            expect(all(s in before_values for s in ('bar_line/vbar2','unverändertes Quellen-Gold','nicht ohne Weiteres als eindeutig validierter Modellfehler')),True,'local chart-type error interpretation warning')
            local_warnings['chart_error_sections']+=1
        if k[0]=='images90' and r['partition'].get('condition')=='blank':
            expect(all(s in before_values for s in ('Blank-Diagnostikum','Originalbild ist nicht sichtbar','keine gewöhnliche beantwortbare Bildaufgabe')),True,'local blank error interpretation warning')
            local_warnings['blank_error_sections']+=1
        expect(f"Gold `{r['gold']}`, native Auswahl `{p['answers'][k[2]]['choice']}`, Auswahlscore {p['probabilities_unrounded'][k[2]][p['answers'][k[2]]['choice']]!r}" in section,True,'error choice/score')
        state=re.search(r'```text\n(.*?)\n```',section,re.S)[1]
        expect(state,str(r['request']['request'].get('state','')),'original error context')
        blocks=re.findall(r'```json\n(.*?)\n```',section,re.S);expect(len(blocks),2,'error data blocks')
        expect(json.loads(blocks[0]),p['probabilities_unrounded'][k[2]],'original full error vector')
        expect(json.loads(blocks[1]),r['case_metadata'],'original error metadata')
        expect(f"`sources/{k[0]}/predictions.jsonl`, ID `{k[1]}`" in section,True,'original output pointer')
    expect(set(seen),set(errors),'all error identities');expect(len(set(seen)),124,'unique error sections')

    report=(ROOT/'REPORT_DE.md').read_text()
    expect('Alle 124 gold-relativen Feldabweichungen (einschließlich ausdrücklich gekennzeichneter Diagramm-Annotationsunschärfen und Blank-Diagnostik)' in report,True,'summary frozen-gold qualification')
    expect(local_warnings['chart_field_groups'],3,'all local chart field warnings');expect(local_warnings['chart_case_groups'],3,'all local chart case warnings');expect(local_warnings['chart_error_sections'],13,'all local chart error warnings')
    main_table=[cells(s) for s in report.splitlines() if re.match(r'^\| (minimal_pairs48|clarification72|bank_support80) / ',s)]
    expect(len(main_table),7,'all main summary field rows')
    core={(r['suite_id']+' / '+r['field']):r for r in independent.values() if r['suite_id'] in ('minimal_pairs48','clarification72','bank_support80')}
    for got in main_table:
        r=core[got[0]];gate=r['risk_coverage'][3]
        expect(got,[got[0],f"{r['correct']}/{r['valid_n']}",str(len(r['option_keys'])),number(r['brier']),number(r['nll']),number(r['ece']),number(r['mean_confidence']),f"{gate['errors']}/{gate['accepted']}"],'main summary values')
    high=[k for k,r in errors.items() if r['metric']['confidence']>=.9]
    expect(len(high),20,'all .90 errors count')
    high_table=[cells(s) for s in report.splitlines() if re.match(r'^\| (attack_ablation14|bank_support80|finance100|images90|minimal_pairs48|original_text180) \| ',s)]
    expect(len(high_table),20,'all rendered .90 errors');gotkeys=[]
    for row in high_table:
        k=tuple(row[:3]);gotkeys.append(k);r=errors[k]
        expect(row[3],r['gold']+' → '+r['choice'],'headline high-error choice')
        expect(row[4],number(r['metric']['confidence'],9),'headline high-error score')
    expect(set(gotkeys),set(high),'all high-score errors, no selection')
    expect(sum(r['metric']['confidence']>=.95 for r in errors.values()),0,'no observed errors at .95')

    pairmeta={r['id']:r for r in rows('sources/minimal_pairs48/cases.jsonl')}
    pair_groups={f:{pairmeta[k[1]]['pair_id'] for k in high if k[0]=='minimal_pairs48' and k[2]==f} for f in ('action','determination')}
    expect(pair_groups['action'],{'pair_report_delivery_target'},'action errors one pair')
    expect(pair_groups['determination'],{'pair_report_delivery_target','pair_statement_notification','pair_limit_order_price_step'},'determination errors three pairs')
    expect(pairmeta['pair_report_delivery_target_a']['kind'],'invariant','same invariant pair')
    expect(pairmeta['pair_report_delivery_target_b']['kind'],'invariant','same invariant pair')
    expect(pairmeta['pair_report_delivery_target_a']['expected'],{'action':'ask_target','determination':'unresolved'},'report ambiguity gold')
    expect(pairmeta['pair_statement_notification_a']['expected']['determination'],'unresolved','notification gold')
    expect(pairmeta['pair_limit_order_price_step_a']['expected']['determination'],'no','price-step gold')

    clarification=raw_sources['clarification72'];cg={r['id']:r for r in rows('sources/clarification72/gold.jsonl')}
    chosen={f:[r for r in clarification.values() if r['probabilities_unrounded'][f][r['answers'][f]['choice']]>=.9] for f in ('action','determination')}
    expect(len(chosen['action']),25,'clarification field action threshold denominator');expect(len(chosen['determination']),49,'clarification field determination threshold denominator')
    all_case=[r for r in clarification.values() if min(r['probabilities_unrounded'][f][r['answers'][f]['choice']] for f in ('action','determination'))>=.9]
    concrete=[r for r in all_case if r['answers']['action']['choice']=='answer' and r['answers']['determination']['choice'] in ('yes','no')]
    expect(len(all_case),21,'all-case threshold denominator');expect(len(concrete),5,'concrete-only threshold denominator')
    expect(sum(all(r['answers'][f]['choice']==cg[r['id']]['expected'][f] for f in ('action','determination')) for r in all_case),21,'all-case threshold correctness')
    expect(sum(all(r['answers'][f]['choice']==cg[r['id']]['expected'][f] for f in ('action','determination')) for r in clarification.values()),64,'clarification whole case count')
    repeated=[]
    for k in high:
        if k[0]=='attack_ablation14':
            base=k[1].removesuffix('__attack')
            expect(raw_sources[k[0]][k[1]]['probabilities_unrounded'],raw_sources['finance100'][base]['probabilities_unrounded'],'repeated finance/attack vector')
            repeated.append(base)
    expect(len(repeated),2,'repeated high-score scenarios')
    insurance=read('sources/insurance60/benchmark.json')
    expect(len(insurance['documents']),12,'shared insurance document count');expect(len(insurance['cases']),60,'insurance case count')
    image_cases=rows('sources/images90/cases.jsonl');expect(len(image_cases),50,'original image case count')
    expect(len(raw_sources['images90']),90,'vision output count')
    expect(all(r.get('media_tensors') and r.get('vision_forward_events') for r in raw_sources['images90'].values()),True,'vision metadata for all recorded requests')
    versions={'torch':'2.11.0+cpu','transformers':'5.10.2','bitsandbytes':'0.50.2','huggingface-hub':'1.33.0','safetensors':'0.8.0'}
    for suite in read('SOURCE_INVENTORY.json')['suites']:
        sid=suite['suite_id'];m=read(f'sources/{sid}/runtime_metadata.json')
        expect(m['revision'],'17f0b0ad64efb65d273590632833508766b2aae6','model revision')
        for package,version in versions.items():expect(m['packages'][package],version,'runtime '+package)
        expect(m['threads'],6,'runtime threads');expect(m['batch_size'],1,'runtime batch')
        expect(m['max_length'],4096 if sid=='images90' else 2048,'runtime cap')
        expect(m['requests_sha256'],hashlib.sha256((ROOT/f'sources/{sid}/requests.jsonl').read_bytes()).hexdigest(),'runtime request hash')
    # Only relative scientific paths are recorded in this audit artifact.
    privacy_pattern=re.compile(r'/(?:workspace|tmp|root|home|mnt)/|\b(?:hostname|host_name|pid|ppid|process_id|realized_path|absolute_path)\b',re.I)
    privacy_hits=[]
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix in ('.json','.jsonl','.md','.txt'):
            if privacy_pattern.search(path.read_text()):privacy_hits.append(str(path.relative_to(ROOT)))
    expect(privacy_hits,[],'public text privacy markers')
    files=['REPORT_DE.md','FIELD_DETAILS.md','CASE_HEURISTICS.md','ERRORS.md','README.md']
    result=dict(status='PASS reports',report_checks=checks,field_sections=78,bin_rows=780,field_threshold_rows=468,case_sections=64,case_threshold_rows=384,errors=124,high_score_errors_at_090=20,local_interpretation_warnings=local_warnings,minimal_pair_error_clusters={k:sorted(v) for k,v in pair_groups.items()},clarification_090=dict(action_fields=25,determination_fields=49,all_cases=21,concrete_only_cases=5),privacy_marker_findings=privacy_hits,report_sha256={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files})
    (ROOT/'audit/report_review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
