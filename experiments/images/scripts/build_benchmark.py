"""Build only from pinned dataset labels; no model predictions are read."""
from pathlib import Path
import json, hashlib, shutil, collections, datetime
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadlines(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def write(name,rows):
 (P/'benchmark'/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
charts=loadlines(P/'source/chart_selected60/manifest.jsonl')
groups=collections.defaultdict(list)
for r in charts:groups[r['type'],r['difficulty']].append(r)
charts=[min(rs,key=lambda r:r['image_sha256']) for k,rs in sorted(groups.items())]
assert len(charts)==30
invoices=loadlines(P/'source/belege-de-invoices-sample/acquired-manifest.jsonl')
regular=collections.defaultdict(list)
for r in invoices:
 if r['vat_scheme']=='regelbesteuert':regular[r['variant'],r['layout']].append(r)
for rs in regular.values():rs.sort(key=lambda r:r['image_sha256'])
regular_selected=[]
while len(regular_selected)<8:
 for k,rs in sorted(regular.items()):
  if rs and len(regular_selected)<8:regular_selected.append(rs.pop(0))
invoice_selected=sorted([r for r in invoices if r['vat_scheme']!='regelbesteuert']+regular_selected,key=lambda r:r['image_sha256'])
assert len(invoice_selected)==20
classes_de={'bar_line':'Kombination aus Säulen und Linie','bar_pie':'Kreisdiagramm neben einer gestapelten Säule','hbar':'Gruppierte waagerechte Balken','hbar2':'Waagerechte Balken mit einer Reihe und Positiv-/Negativ-Legende','line':'Liniendiagramm ohne Balken','pie':'Kreisdiagramm ohne Balken','stack_hbar':'Gestapelte waagerechte Balken','stack_vbar':'Gestapelte senkrechte Säulen','vbar':'Gruppierte senkrechte Säulen mit einer y-Achse','vbar2':'Senkrechte Säulen mit zwei y-Achsen'}
classes_en={'bar_line':'Combination of columns and a line','bar_pie':'Pie chart next to a stacked vertical column','hbar':'Grouped horizontal bars','hbar2':'Single-series horizontal bars with a positive/negative legend','line':'Line chart without bars','pie':'Pie chart without bars','stack_hbar':'Stacked horizontal bars','stack_vbar':'Stacked vertical columns','vbar':'Grouped vertical columns with one y-axis','vbar2':'Vertical columns with two y-axes'}
def chart_questions(lang):
 return {'chart_type':{'type':'choice','instructions':'Welche Diagrammart ist dargestellt?' if lang=='de' else 'Which chart type is shown?','criteria':classes_de if lang=='de' else classes_en},'legend_count':{'type':'choice','instructions':'Wie viele beschriftete Einträge hat die Legende insgesamt? Zähle die Legendenüberschrift und Beschriftungen direkt an Datenpunkten nicht mit.' if lang=='de' else 'How many labeled entries are in the legend in total? Do not count the legend title or direct data-point labels.','criteria':{str(i):str(i)+(' Einträge' if lang=='de' else ' entries') for i in range(0,11)}}}
def invoice_questions(lang):
 if lang=='de':return {'document_type':{'type':'choice','instructions':'Welche Dokumentart steht auf dem Beleg?','criteria':{'rechnung':'Rechnung','gutschrift':'Gutschrift'}},'tax_note':{'type':'choice','instructions':'Welcher Steuerhinweis ist ausdrücklich auf dem Beleg erkennbar? Bei einem ausdrücklichen §19- oder Reverse-Charge-Hinweis hat dieser Vorrang vor Steuersätzen in einzelnen Positionszeilen.','criteria':{'regular':'Reguläre Umsatzsteuer mit ausgewiesenem Steuerbetrag; kein §19- oder Reverse-Charge-Hinweis','small_business':'Kleinunternehmer-Hinweis gemäß §19 UStG','reverse_charge':'Hinweis auf Reverse Charge oder Steuerschuldnerschaft des Leistungsempfängers'}},'gross_band':{'type':'choice','instructions':'In welchem Intervall liegt der Brutto-Gesamtbetrag in Euro? Nutze das Vorzeichen des gedruckten Gesamtbetrags, nicht einzelne Positionen oder den Nettobetrag.','criteria':{'negative':'Kleiner als 0 Euro','zero_1000':'0 bis einschließlich 1.000 Euro','1000_5000':'Mehr als 1.000 bis einschließlich 5.000 Euro','5000_20000':'Mehr als 5.000 bis einschließlich 20.000 Euro','over_20000':'Mehr als 20.000 Euro'}}}
 return {'document_type':{'type':'choice','instructions':'Which document type is printed on the document?','criteria':{'rechnung':'Invoice','gutschrift':'Credit note'}},'tax_note':{'type':'choice','instructions':'Which tax notice is explicitly visible? An explicit section 19 or reverse-charge notice takes precedence over tax rates in individual line items.','criteria':{'regular':'Regular VAT with a stated tax amount; no section 19 or reverse-charge notice','small_business':'Small-business exemption notice under section 19 of the German VAT Act','reverse_charge':'Reverse charge or recipient tax liability notice'}},'gross_band':{'type':'choice','instructions':'Which interval contains the gross total in euros? Use the sign of the printed total, not individual line items or the net amount.','criteria':{'negative':'Less than 0 euros','zero_1000':'0 through 1,000 euros inclusive','1000_5000':'More than 1,000 through 5,000 euros inclusive','5000_20000':'More than 5,000 through 20,000 euros inclusive','over_20000':'More than 20,000 euros'}}}
cases=[];reqs=[];golds=[]
def add(r,kind,num):
 source_image=Path(r['image'] if kind=='chart' else r['image_absolute']);label=Path(r['labels'] if kind=='chart' else r['label_absolute']);d=json.loads(label.read_text())
 cid=f'{kind}-{num:03d}';rel=f'images/{cid}{source_image.suffix}'
 shutil.copyfile(source_image,P/rel)
 gold={'chart_type':r['type'],'legend_count':str(sum(n['class']=='legend_item' for n in d['node']))} if kind=='chart' else {'document_type':{'Rechnung':'rechnung','Gutschrift':'gutschrift'}[d['document_type']],'tax_note':{'regelbesteuert':'regular','gutschrift':'regular','kleinunternehmer':'small_business','reverse_charge':'reverse_charge'}[d['vat_scheme']],'gross_band':('negative' if d['totals']['gross']<0 else 'zero_1000' if d['totals']['gross']<=1000 else '1000_5000' if d['totals']['gross']<=5000 else '5000_20000' if d['totals']['gross']<=20000 else 'over_20000')}
 case={'case_id':cid,'kind':kind,'source_id':r['id'],'image_path':rel,'image_sha256':sha(source_image),'source_label_path':str(label.relative_to(P)),'source_label_sha256':sha(label),'source_revision':('633cf14bc4c513f6c4806e319905e573afae12f4' if kind=='chart' else 'da6044a02bd0b6c1d065b9f5615fe021272ece45'),'strata':{k:r[k] for k in (('type','difficulty') if kind=='chart' else ('variant','layout','vat_scheme','document_type'))},'gold':gold}
 if kind=='invoice':case['gross_total_source']=d['totals']['gross']
 else:case['legend_entries_source']=[n for n in d['node'] if n['class']=='legend_item']
 cases.append(case)
for i,r in enumerate(charts,1):add(r,'chart',i)
for i,r in enumerate(invoice_selected,1):add(r,'invoice',i)
# Paired subset: every chart type at medium difficulty and10 invoices selected by a deterministic VAT-stratum round robin.
pair_cases=[c for c in cases if c['kind']=='chart' and c['strata']['difficulty']=='medium']
ig=collections.defaultdict(list)
for c in cases:
 if c['kind']=='invoice':ig[c['strata']['vat_scheme']].append(c)
for cs in ig.values():cs.sort(key=lambda c:c['image_sha256'])
while len(pair_cases)<20:
 for k,cs in sorted(ig.items()):
  if cs and len(pair_cases)<20:pair_cases.append(cs.pop(0))
def request(c,lang,condition):
 if c['kind']=='chart':state='Beurteile das beigefügte Diagramm ausschließlich anhand des Bildes.' if lang=='de' else 'Judge the attached chart only from the image.'
 else:state='Lies den beigefügten Beleg ausschließlich aus dem Bild. Die Fragen betreffen sichtbare Angaben, keine rechtliche Prüfung.' if lang=='de' else 'Read the attached document only from the image. The questions concern visible information, not legal validation.'
 id=c['case_id']+'-'+lang+'-'+condition
 reqs.append({'id':id,'image_path':c['image_path'],'image_sha256':c['image_sha256'],'condition':condition,'request':{'model':'clef-flash','state':state,'questions':chart_questions(lang) if c['kind']=='chart' else invoice_questions(lang)}})
 golds.append({'id':id,'case_id':c['case_id'],'kind':c['kind'],'language':lang,'condition':condition,'expected':c['gold']})
for c in cases:request(c,'de','image')
for c in pair_cases:request(c,'en','image')
for c in pair_cases:request(c,'de','blank')
write('cases.jsonl',cases);write('requests.jsonl',reqs);write('gold.jsonl',golds)
write('pairs.jsonl',[{'case_id':c['case_id'],'de':c['case_id']+'-de-image','en':c['case_id']+'-en-image','blank':c['case_id']+'-de-blank'} for c in pair_cases])
policy={'version':'1.0','selection':'30 chart test images: smallest image SHA256 per10type×3difficulty strata.20 German invoices: all12non-regular source VAT-scheme cases plus8regular sampled round-robin over sorted(variant,layout), with per-stratum SHA256 ordering. No prediction-based changes.','chart_source_language':'English chart labels; German task questions. These are not German chart images.','invoice_source_language':'German synthetic documents, all entities fabricated per source license.','gold':'Dataset type, count of original legend_item nodes; document_type, VAT-scheme mapped to explicitly printed tax note, and source gross total mapped to fixed intervals. No model-derived labels.','gross_boundaries_eur':[0,1000,5000,20000],'primary':'Per-field exact decision accuracy and per-image all-fields accuracy, reported separately by dataset and task. Never pool synthetic chart/invoice performance into a production finance capability claim.','controls':'20paired images with English questions and same option IDs; same20 with all-white pixels at same source dimensions and German questions. No-image controls not included.','resolution':'Official processor, min65536 and max786432 pixels; no crops, rotation, OCR text, filenames, source IDs, labels or metadata passed to model.','runtime':'Original official Clef vision encoder, joint head and output embeddings BF16; language Linear layers CPU NF4 double quantization; batch1; official wrapper English.','limitations':['Small purposive stratified synthetic sample','Potential training contamination unknown','Structured choices do not measure freeform OCR, financial advice, regulatory compliance or real private document safety','Source generator inconsistencies; evaluate printed tax notices, not legal truth','Blank controls preserve dimensions and prompt priors; they are a reliance check, not a complete causal audit']}
(P/'benchmark/policies.json').write_text(json.dumps(policy,ensure_ascii=False,indent=2))
summary={'images':len(cases),'requests':len(reqs),'main_fields':sum(len(c['gold']) for c in cases),'chart_types':dict(collections.Counter(c['strata']['type'] for c in cases if c['kind']=='chart')),'invoices':{k:dict(collections.Counter(c['strata'][k] for c in cases if c['kind']=='invoice')) for k in ['vat_scheme','variant','layout']},'gold_counts':{q:dict(collections.Counter(c['gold'][q] for c in cases if q in c['gold'])) for q in ['chart_type','legend_count','document_type','tax_note','gross_band']}}
(P/'benchmark/design_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
