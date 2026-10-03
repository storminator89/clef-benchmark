#!/usr/bin/env python3
"""Rebuild descriptive SVG charts from audited case rows (stdlib only).

No inference, network, pooled accuracy, or modification of frozen study files.
Use --check in CI to detect stale assets. Percentages are display-only.
"""
import argparse
import hashlib
import importlib.util
import json
from html import escape
from pathlib import Path

GROUPS = [
    ('original_text180', 'german_primary', 'Allgemeine Entscheidungen'),
    ('finance100', 'german_primary', 'Finanzen und Makler'),
    ('clean72', 'german_clean_primary', 'Büroentscheidungen · clean72'),
    ('bank_support80', 'german_primary', 'Bank-Kundensupport'),
    ('insurance60', 'german_primary', 'Versicherungsdokumente'),
    ('clarification72', 'german_primary', 'Rückfragen statt Raten'),
    ('minimal_pairs48', 'diagnostic_pairs', 'Minimalpaare · einzelne Fälle'),
    ('multidoc48', 'german_primary', 'Mehrere Dokumente'),
]
SOURCES = ['studies/jev974-answer-correctness-v1/case_comparison.jsonl',
           'studies/jev974-answer-correctness-v1/comparison_summary.json',
           'studies/language72/scored/case_scores.jsonl',
           'studies/language72/scored/summary.json']

def load_data(root):
    rows = [json.loads(s) for s in (root / SOURCES[0]).read_text().splitlines()]
    if len({(r['suite'], r['id']) for r in rows}) != len(rows):
        raise ValueError('Duplicate comparison case IDs')
    summary = json.loads((root / SOURCES[1]).read_text())
    partitions = []
    for p in summary['partitions']:
        selected = [r for r in rows if (r['suite'], r['split']) == (p['suite'], p['split'])]
        counts = {}
        for model in ('clef', 'jev'):
            answered = sum(r['evaluable'][model] is True for r in selected)
            correct = sum(r['exact'][model] is True for r in selected)
            for r in selected:
                choice = r['choices'][model]
                recomputed = choice == r['expected'] if choice is not None else False
                if (r['exact'][model] is True) != recomputed:
                    raise ValueError(f"Native-choice correctness mismatch: {r['id']} / {model}")
            expected_correct = correct if answered else None
            if answered != (p[f'{model}_answered'] or 0) or expected_correct != p[f'{model}_correct']:
                raise ValueError(f"Case/summary mismatch: {p['suite']} / {model}")
            counts[model] = expected_correct
        if len(selected) != p['planned'] or p['expected'] != p['planned']:
            raise ValueError('Planned-case denominator mismatch')
        partitions.append(dict(suite=p['suite'], split=p['split'], expected=len(selected),
                               clef=counts['clef'], jev=counts['jev']))
    if sum(p['expected'] for p in partitions) != len(rows):
        raise ValueError('Partition coverage mismatch')
    language = [json.loads(s) for s in (root / SOURCES[2]).read_text().splitlines()]
    ls = json.loads((root / SOURCES[3]).read_text())
    if len({r['id'] for r in language}) != len(language):
        raise ValueError('Duplicate language case IDs')
    if len(language) != ls['all_cases']['count'] or sum(r['exact'] for r in language) != ls['all_cases']['all_fields_exact']['numerator']:
        raise ValueError('Language case/summary mismatch')
    diagnostics = []
    for target, label in [(True, 'Zielobjekt unklar'), (False, 'Alle übrigen Fälle')]:
        selected = [r for r in language if (r['expected']['action'] == 'ask_target') == target]
        diagnostics.append(dict(label=label, correct=sum(r['exact'] for r in selected), total=len(selected)))
    return partitions, diagnostics


def txt(x, y, text, size=16, color='#243247', weight='normal', anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(text))}</text>'

def rect(x, y, w, h, color, radius=0):
    return f'<rect x="{x}" y="{y}" width="{w:.3f}" height="{h}" rx="{radius}" fill="{color}"/>'

def start(title, desc, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="{height}" viewBox="0 0 1120 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
            '<g font-family="DejaVu Sans, Arial, sans-serif">', rect(0,0,1120,height,'#ffffff'),
            txt(32,44,title,26,weight='bold'), txt(32,74,desc,15,color='#526174')]

def axis(s, top, bottom, x=380, width=480):
    for value in [0,25,50,75,100]:
        xx=x+width*value/100
        s.append(f'<path d="M {xx} {top} V {bottom}" stroke="#dce3eb" stroke-width="1"/>')
        s.append(txt(xx,top-12,f'{value} %',13,color='#526174',anchor='middle'))

def pct(n,d):
    return f'{100*n/d:.1f}'.replace('.',',')+' %'


WAHLER_STUDY = 'studies/wahler580'
WAHLER_FILES = ('planned.jsonl','cases.jsonl','wahler-native-responses.jsonl',
                'wahler-requests.jsonl','original-benchmark.py','recompute.py','provenance.json','README.md')

def load_wahler_data(root):
    """Only a complete audited public evidence bundle can replace the legacy chart."""
    study=root/WAHLER_STUDY
    if not study.exists(): return None
    evidence=study/'evidence'
    required=[study/'comparison.json']+[evidence/n for n in (*WAHLER_FILES,'SHA256SUMS')]
    if not all(p.is_file() for p in required): raise ValueError('Incomplete Wähler evidence bundle')
    hashes=json.loads((evidence/'SHA256SUMS').read_text())
    if set(hashes)!=set(WAHLER_FILES): raise ValueError('Unexpected Wähler evidence manifest')
    for name,digest in hashes.items():
        if hashlib.sha256((evidence/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Wähler evidence digest mismatch: '+name)
    provenance=json.loads((evidence/'provenance.json').read_text())
    if provenance['provenance']['unique_completed_cases']!=580 or provenance['provenance']['choice_fields']!=968:
        raise ValueError('Wähler evidence must cover exactly 580 cases and 968 fields')
    replay_path=Path(__file__).with_name('recompute_wahler_evidence.py')
    replay_hash=hashlib.sha256(replay_path.read_bytes()).hexdigest()
    if hashes['recompute.py']!=replay_hash or provenance['recompute_sha256']!=replay_hash:
        raise ValueError('Wähler replay scorer differs from reviewed source')
    spec=importlib.util.spec_from_file_location('wahler_replay',replay_path)
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
    recomputed=replay.recompute(replay.records(evidence/'planned.jsonl'),replay.records(evidence/'cases.jsonl'))
    comparison=json.loads((study/'comparison.json').read_text())
    if comparison.get('schema_version')!=1 or comparison.get('metric')!='all_fields_native_exact_over_same_planned_cases':
        raise ValueError('Unexpected Wähler comparison schema/metric')
    if comparison['planned_sha256']!=hashes['planned.jsonl'] or comparison['score_sha256']!=provenance['final_score_sha256']:
        raise ValueError('Wähler comparison provenance differs')
    groups=comparison['groups']
    if [g['suite'] for g in groups]!=[g[0] for g in GROUPS]: raise ValueError('Wähler group inventory differs')
    for g,(_,_,label) in zip(groups,GROUPS):
        actual=recomputed['groups'][g['suite']]
        if g['planned']!=actual['planned'] or g['label']!=label or set(g['models'])!={'clef','jev','wahler'}:
            raise ValueError('Wähler group denominator/label/model mismatch')
        for model,count in actual['models'].items():
            expected={'correct':count['correct'],'planned':actual['planned'],
                      'classifiable':actual['planned']-count['missing'],
                      'missing_or_structurally_invalid':count['missing'],
                      'sum_only_diagnostics':count['sum_only_diagnostics']}
            if g['models'][model]!=expected: raise ValueError('Wähler chart counts differ from native evidence')
    return groups

def render_wahler_chart(groups):
    s=start('Vollständig richtige Fälle im direkten Vergleich',
              'Gleiche geplante Fälle · alle geforderten Felder müssen stimmen',1080)
    for x,m,label,color in [(32,'clef','Clef Flash 9B · CPU-NF4','#355fa4'),(370,'jev','Jev 1.13.0 · API','#087f78'),(680,'wahler','Wähler 4B · Q8','#9059a6')]:
        s += [rect(x,96,18,12,color),txt(x+27,107,label,14)]
    axis(s,164,954)
    s += [txt(888,142,'Richtig / Fälle',13)]
    for i,g in enumerate(groups):
        y=185+i*98; n=g['planned']
        s += [txt(32,y+10,g['label'],16,weight='bold'),txt(32,y+34,f'{n} Fälle pro Modell',14,color='#526174')]
        for dy,m,color in [(-15,'clef','#355fa4'),(12,'jev','#087f78'),(39,'wahler','#9059a6')]:
            count=g['models'][m]['correct']
            s += [rect(380,y+dy,480*count/n,19,color,2),txt(888,y+dy+15,f'{count}/{n} · {pct(count,n)}',15)]
    s += [txt(32,999,'Nicht auswertbare Antworten zählen nicht als richtig; je Gruppe bleibt der Nenner gleich.',15),
          txt(32,1025,'Synthetische, teils abhängige Fälle; unterschiedliche Quantisierung und Hardware.',14),
          txt(32,1051,'Keine allgemeine Modellrangliste oder faire Geschwindigkeitsmessung.',14)]
    return '\n'.join(s+['</g></svg>'])+'\n'

def render(root):
    partitions, diagnostic = load_data(root)
    lookup = {(p['suite'],p['split']):p for p in partitions}
    s=start('Vollständig richtige Fälle im direkten Vergleich',
            'Je Testgruppe alle geplanten Fälle · alle geforderten Felder müssen stimmen',890)
    s += [rect(32,96,18,12,'#355fa4'),txt(59,107,'Clef Flash 9B · CPU-NF4',14),
          rect(330,96,18,12,'#087f78'),txt(357,107,'Jev 1.13.0 · gehostete API',14),
          txt(890,142,'Richtig / Fälle',13),txt(32,142,'Gleicher Fallumfang',13,color='#526174')]
    axis(s,164,798)
    for i,(suite,split,label) in enumerate(GROUPS):
        p=lookup[suite,split]; y=188+i*78; n=p['expected']
        if not n or p['clef'] is None or p['jev'] is None:
            raise ValueError('Main group needs planned cases and both baselines')
        s += [txt(32,y,label,16,weight='bold'),txt(32,y+23,f"{n} Fälle pro Modell",14,color='#526174')]
        for dy,k,color in [(-15,'clef','#355fa4'),(13,'jev','#087f78')]:
            s += [rect(380,y+dy,480*p[k]/n,19,color,2),txt(888,y+dy+15,f"{p[k]}/{n}  ·  {pct(p[k],n)}",15)]
    s += [txt(32,837,'Nicht auswertbare Antworten zählen nicht als richtig. Jede Testgruppe behält ihren eigenen Nenner.',15),
          txt(32,861,'Kleine, überwiegend synthetische und teils abhängige Fälle; keine allgemeine Modellrangliste.',14,color='#526174')]
    result={'matched_accuracy.svg':'\n'.join(s+['</g></svg>'])+'\n'}
    s=start('Deutsche Sprachvarianten: Fehler konzentrieren sich auf Zielunklarheit',
            'Clef · 72 einzelne Fälle · deskriptive Aufteilung nach dem erwarteten Aktionstyp',450)
    s += [rect(32,99,18,12,'#355fa4'),txt(59,110,'Alle Felder richtig',14),
          rect(285,99,18,12,'#b36b23'),txt(313,110,'Mindestens ein Feld falsch',14),txt(885,148,'Richtig / Fälle',13)]
    axis(s,172,310)
    for i,p in enumerate(diagnostic):
        y=185+i*79; n=p['total']; correct=p['correct']
        s += [txt(32,y+17,p['label'],18,weight='bold'),txt(32,y+42,f"{n-correct} Fehler unter {n} Fällen",14,color='#526174'),
              rect(380,y,480*correct/n,30,'#355fa4'),rect(380+480*correct/n,y,480*(1-correct/n),30,'#b36b23'),
              txt(885,y+21,f"{correct}/{n} · {pct(correct,n)}",15)]
    s += [txt(32,355,'Zielunklarheit: Goldaktion ask_target; übrige Fälle: alle anderen Goldaktionen.',14),
          txt(32,381,'Post-hoc Fehlerdiagnose, kein kausaler Effekt und kein unabhängiger Holdout.',14),
          txt(32,407,'Varianten teilen Basen. Paarmetriken werden nicht mit einzelnen Fällen zusammengezählt.',14,color='#526174')]
    result['language_diagnostic.svg']='\n'.join(s+['</g></svg>'])+'\n'
    result['data.json']=json.dumps({'sources_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCES},
                                  'partitions':partitions,'language_diagnostic':diagnostic},ensure_ascii=False,indent=2)+'\n'
    wahler=load_wahler_data(root)
    if wahler is not None:
        result['matched_accuracy.svg']=render_wahler_chart(wahler)
        data=json.loads(result['data.json'])
        data['wahler580']={'groups':wahler,'evidence':WAHLER_STUDY+'/evidence/README.md'}
        for relative in (WAHLER_STUDY+'/comparison.json',WAHLER_STUDY+'/evidence/SHA256SUMS'):
            data['sources_sha256'][relative]=hashlib.sha256((root/relative).read_bytes()).hexdigest()
        result['data.json']=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args(); output=args.output or args.root/'docs/charts'
    generated=render(args.root)
    if args.check:
        stale=[name for name,content in generated.items() if not (output/name).is_file() or (output/name).read_text()!=content]
        if stale: raise SystemExit('Stale or missing charts: '+', '.join(stale))
        print('All chart assets match audited inputs.')
    else:
        output.mkdir(parents=True,exist_ok=True)
        for name,content in generated.items(): (output/name).write_text(content,encoding='utf-8')
        print(f'Wrote {len(generated)} chart assets to {output}')

if __name__ == '__main__': main()
