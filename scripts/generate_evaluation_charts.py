#!/usr/bin/env python3
"""Rebuild descriptive SVG charts from audited case rows (stdlib only).

No inference, network, pooled accuracy, or modification of frozen study files.
Use --check in CI to detect stale assets. Percentages are display-only.
"""
import argparse
import hashlib
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
EXTRA = {
    ('original_text180', 'mixed_schema_diagnostic'): 'Allgemein · englisches Schema',
    ('original_text180', 'english_control'): 'Allgemein · Englischkontrolle',
    ('finance100', 'english_control'): 'Finanzen · Englischkontrolle',
    ('attack_ablation14', 'posthoc_attack/attack'): 'Angriffsentfernung · mit Angriff',
    ('attack_ablation14', 'posthoc_clean/clean'): 'Angriffsentfernung · ohne Angriff',
    ('massive300', 'german_test_primary'): 'MASSIVE de-DE',
}
SOURCES = ['studies/jev974/scoring/case_comparison.jsonl',
           'studies/jev974/scoring/comparison_summary.json',
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
        valid = [r for r in selected if r['exact']['jev'] is not None]
        matched = [r for r in valid if r['exact']['clef'] is not None]
        clef = sum(r['exact']['clef'] is True for r in matched)
        jev = sum(r['exact']['jev'] is True for r in matched)
        checks = [len(selected) == p['expected'], len(valid) == p['jev_valid'],
                  len(matched) == p['both_valid'],
                  clef == p['both_correct'] + p['clef_only_correct'],
                  jev == p['both_correct'] + p['jev_only_correct'],
                  sum(r['exact']['jev'] is True for r in valid) == p['jev_correct']]
        if not all(checks):
            raise ValueError(f"Case/summary mismatch: {p['suite']} / {p['split']}")
        partitions.append(dict(suite=p['suite'], split=p['split'], expected=len(selected),
                               valid=len(valid), matched=len(matched), clef=clef, jev=jev))
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

def render(root):
    partitions, diagnostic = load_data(root)
    lookup = {(p['suite'],p['split']):p for p in partitions}
    s=start('Vollständig richtige Fälle im direkten Vergleich',
            'Je Testgruppe dieselben Fälle für beide Modelle · alle geforderten Felder müssen stimmen',890)
    s += [rect(32,96,18,12,'#355fa4'),txt(59,107,'Clef Flash 9B · CPU-NF4',14),
          rect(330,96,18,12,'#087f78'),txt(357,107,'Jev 1.13.0 · gehostete API',14),
          txt(890,142,'Richtig / gemeinsam',13),txt(32,142,'Gemeinsam / geplant',13,color='#526174')]
    axis(s,164,798)
    for i,(suite,split,label) in enumerate(GROUPS):
        p=lookup[suite,split]; y=188+i*78; n=p['matched']
        if not n: raise ValueError('Matched group has no comparable cases')
        s += [txt(32,y,label,16,weight='bold'),txt(32,y+23,f"Abdeckung {n}/{p['expected']}",14,color='#526174')]
        for dy,k,color in [(-15,'clef','#355fa4'),(13,'jev','#087f78')]:
            s += [rect(380,y+dy,480*p[k]/n,19,color,2),txt(888,y+dy+15,f"{p[k]}/{n}  ·  {pct(p[k],n)}",15)]
    s += [txt(32,837,'Reihenfolge wie in der Ergebnistabelle. Keine Gesamtgenauigkeit über unterschiedliche Tests.',15),
          txt(32,861,'Kleine, überwiegend synthetische und teils abhängige Fälle; keine allgemeine Modellrangliste.',14,color='#526174')]
    result={'matched_accuracy.svg':'\n'.join(s+['</g></svg>'])+'\n'}
    labels={(a,b):c for a,b,c in GROUPS}; labels.update(EXTRA)
    valid=sum(p['valid'] for p in partitions); total=sum(p['expected'] for p in partitions)
    s=start('Jev: technische Abdeckung des vollständigen Laufs',
            f'{valid}/{total} strikt gültige Antworten · {total-valid} technische Ausschlüsse · keine Genauigkeitsaggregation',1020)
    s += [rect(32,98,18,12,'#087f78'),txt(59,109,'Strikt gültig',14),
          rect(224,98,18,12,'#b36b23'),txt(252,109,'Technisch ausgeschlossen',14),
          txt(885,145,'Gültig / geplant',13),txt(1080,145,'Ausg.',13,anchor='end')]
    axis(s,169,890)
    for i,p in enumerate(partitions):
        y=181+i*49; ratio=p['valid']/p['expected']; invalid=p['expected']-p['valid']
        s += [txt(32,y+15,labels[p['suite'],p['split']],15),rect(380,y,480*ratio,21,'#087f78'),
              rect(380+480*ratio,y,480*(1-ratio),21,'#b36b23'),
              txt(885,y+15,f"{p['valid']}/{p['expected']}",15),txt(1080,y+15,invalid,15,anchor='end')]
    s += [txt(32,940,'Gültigkeit folgt dem eingefrorenen Benchmark-Validator, einschließlich Summenprüfung 1e−5.',14),
          txt(32,965,'Ein technischer Ausschluss belegt keinen fachlichen Fehler. MASSIVE hat noch keine auditierte Clef-Baseline.',14),
          txt(32,990,'Sprachkontrollen und Angriffsentfernung bleiben getrennt; die Summe beschreibt nur die Abdeckung.',14,color='#526174')]
    result['jev_coverage.svg']='\n'.join(s+['</g></svg>'])+'\n'
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
