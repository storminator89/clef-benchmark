#!/usr/bin/env python3
"""Independent model-free review of authored visible states. Does not load a model or score model outputs."""
import collections,datetime,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; OUT=ROOT/'audit'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def records(name): return [json.loads(l) for l in (DATA/name).read_text().splitlines() if l.strip()]
def date(s): return datetime.datetime.strptime(s,'%d.%m.%Y').date()
cases=records('cases.jsonl'); gold=records('gold.jsonl'); requests=records('requests.jsonl'); meta=records('metadata.jsonl')
policy=json.loads((DATA/'policy.json').read_text()); design=json.loads((DATA/'design_summary.json').read_text())
inputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(DATA.iterdir()) if p.is_file()}
inputs['scripts/build_dataset.py']=sha(ROOT/'scripts/build_dataset.py')
G={x['id']:x for x in gold}; Q={x['id']:x for x in requests}; M={x['id']:x for x in meta}
assert len(cases)==len(gold)==len(requests)==len(meta)==48
assert all(len(set(x['id'] for x in rows))==48 for rows in [cases,gold,requests,meta])
assert {c['id'] for c in cases}==set(G)==set(Q)==set(M)
assert list(Q)==[c['id'] for c in cases]==list(G)==list(M)==design['case_order']
assert list(policy)==['source','determination']
assert set(policy['source']['criteria'])=={'D1','D2','D3','not_unique'}
assert set(policy['determination']['criteria'])=={'yes','no','unresolved'}
reviews=[]; all_doc_reviews=[]
for c in sorted(cases,key=lambda x:x['id']):
 s=c['state']; p=s.split('Vorrang und Geltung: ',1)[1].split('\n\n',1)[0]
 facts=s.split('Bekannte Fakten: ',1)[1].split('\nKundenfrage:',1)[0]
 amount=int(re.search(r'(?:Überweisungsbetrag|Schadenbetrag|Änderungsbetrag): (\d+) EUR',facts)[1])
 docpat=r'Dokument (D[123]) — ([^\n]+)\nVeröffentlicht: (.+?)\. Gültig ab: (.+?)\. Geltungsbereich: (.+?)\.\nVollständige Regel: (.+?)(?=\n\n|$)'
 docs=[]
 for pos,m in enumerate(re.finditer(docpat,s),1):
  did,title,pub,eff,scope,rule=m.groups()
  threshold=int(re.search(r'bis einschließlich (\d+) EUR',rule)[1])
  assert '(Ja). Höhere Beträge: nicht ' in rule and rule.endswith('(Nein).')
  docs.append(dict(id=did,title=title,publication=pub,effective=eff,scope=scope,threshold=threshold,position=pos,outcome='yes' if amount<=threshold else 'no',visible_complete_rule=rule))
 assert len(docs)==len(c['documents']) and len({d['id'] for d in docs})==len(docs)
 for d,stored in zip(docs,c['documents']):
  assert all(d[k]==stored[k] for k in ['id','title','publication','effective','scope','threshold','outcome'])
 assert p==c['precedence'] and facts==c['facts']
 assert s.endswith('Kundenfrage: '+c['question'])
 reason=''; possible=[]
 if p.startswith('Für den Zielvorgang gelten alle aufgeführten Dokumente.'):
  if 'Servicehinweis hat in diesem Fall ausdrücklich Vorrang vor Vertragsanlage.' in p: winner='Servicehinweis'
  elif 'Unterschriebener Nachtrag hat Vorrang vor Grundtarif; Grundtarif vor FAQ.' in p: winner='Unterschriebener Nachtrag'
  elif 'Fachfreigabe hat Vorrang vor Preisblatt; Preisblatt vor Übersicht.' in p: winner='Fachfreigabe'
  elif 'Vertragsanlage hat Vorrang vor Servicehinweis.' in p: winner='Vertragsanlage'
  else: raise AssertionError(c['id'])
  possible=[d for d in docs if d['title']==winner]
  reason=f'Visible exclusive authority ordering selects {winner}; all listed documents are expressly applicable and dates/order cannot break or reverse this ordering.'
 elif p.startswith('Die Dokumente sind Versionen derselben vollständigen Regel.'):
  event=facts.split('Ereignistag: ',1)[1]
  eventdates=re.findall(r'\d{2}\.\d{2}\.\d{4}',event)
  winners=[]
  for e in eventdates:
   eligible=[d for d in docs if date(d['effective'])<=date(e)]
   assert eligible
   last=max(date(d['effective']) for d in eligible)
   winners.extend(d['id'] for d in eligible if date(d['effective'])==last)
  possible=[d for d in docs if d['id'] in winners]
  reason='For each explicitly allowed event date, select the latest already-effective complete version; publication is not a tie-break. Allowed event dates: '+', '.join(eventdates)+'.'
 elif p.startswith('Für alle Vorgänge gilt die Basisregel.'):
  tariff=re.search(r'Tarif: ([^.]+)',facts)[1]
  target=re.search(r'Zielvorgang: ([^.]+)',facts)[1]
  specials=[d for d in docs if d['title']!='Basisregel' and d['scope'] in [target,'Tarif '+tariff]]
  possible=specials or [d for d in docs if d['title']=='Basisregel']
  reason=f'The visible special-rule replacement applies only within its stated scope. Target={target}, tariff={tariff}; incompatible scopes are excluded before selection.'
 elif p.startswith('Für Tarif Basis gilt allein die Basisregel, für Tarif Plus allein die Plusregel.'):
  assert 'Tarif: Basis oder Plus; die Auswahl ist unbekannt.' in facts
  possible=[d for d in docs if d['scope'] in ['Tarif Basis','Tarif Plus']]
  reason='The two and only two tariffs remain possible. Each tariff selects exactly its own full document; source remains not_unique regardless of whether their resulting answers coincide.'
 elif p.startswith('Für den Zielvorgang sind Regelblatt Rot und Regelblatt Blau gleichzeitig anwendbar und gleichrangig.'):
  possible=[d for d in docs if d['title'] in ['Regelblatt Rot','Regelblatt Blau']]
  reason='Rot and Blau are explicitly tied applicable alternatives; Grün is explicitly excluded for this target. There is no tie-break or clause combination.'
 elif p.startswith('Beide Dokumente sind gleichzeitig anwendbar und gleichrangig.') or p.startswith('Alle drei Dokumente sind gleichzeitig anwendbar und gleichrangig.'):
  possible=docs
  reason='Every listed complete document is explicitly an applicable tied alternative, with no tie-break or correction.'
 elif p.startswith('Nur eine der beiden Versionen ist für diesen Vorgang aktiv.'):
  possible=docs
  reason='Exactly one version is active, but the two-way choice is unknown and no further selection rule exists; both remain possible.'
 else: raise AssertionError('Unreviewed precedence '+c['id'])
 assert possible
 ps=[d['id'] for d in possible]; answers={d['outcome'] for d in possible}
 independent={'source':ps[0] if len(ps)==1 else 'not_unique','determination':next(iter(answers)) if len(answers)==1 else 'unresolved'}
 assert independent==c['expected']==G[c['id']]['expected'],c['id']
 assert ps==c['plausible_source_ids']==G[c['id']]['plausible_source_ids'],c['id']
 assert G[c['id']]['rationale']==c['rationale']
 assert c['source_position']==(next(d['position'] for d in possible) if len(ps)==1 else None)
 assert c['material_clarification']==(independent['determination']=='unresolved')
 assert c['source_uncertain_answer_definite']==(independent['source']=='not_unique' and independent['determination']!='unresolved')
 assert M[c['id']]=={k:c[k] for k in M[c['id']]}
 request=Q[c['id']]
 assert set(request)=={'id','request'} and set(request['request'])=={'model','state','questions'}
 assert request['request']['model']=='clef-flash' and request['request']['state']==s and request['request']['questions']==policy
 for d in docs:
  d['case_id']=c['id']; d['plausible_governing_source']=d['id'] in ps
  d['threshold_evaluation']=f'{amount} '+('≤' if d['outcome']=='yes' else '>')+f' {d["threshold"]} ⇒ {d["outcome"]}'
  d['source_sha256']=hashlib.sha256((s.split('Dokument '+d['id']+' — ',1)[1].split('\n\n',1)[0]).encode()).hexdigest()
  all_doc_reviews.append(d)
 reviews.append({'id':c['id'],'domain':c['domain'],'family':c['family'],'stratum':c['stratum'],'subtype':c['subtype'],'state_sha256':hashlib.sha256(s.encode()).hexdigest(),'case_json_canonical_sha256':hashlib.sha256(json.dumps(c,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),'visible_precedence':p,'visible_facts':facts,'visible_question':c['question'],'document_count':len(docs),'reviewed_documents':docs,'independently_derived_possible_sources':ps,'independently_derived_expected':independent,'reason':reason+' Complete-rule amount comparisons: '+'; '.join(d['id']+': '+d['threshold_evaluation'] for d in possible)+'.','gold_match':True,'plausible_source_match':True,'all_governing_rules_visible':True,'no_clause_composition':True,'source_uncertainty_does_not_imply_unresolved':True,'case_gold_request_metadata_consistent':True,'semantic_status':'pass','semantic_blockers':[]})
# 16 semantic archetypes are exactly repeated over three domains after normalizing their domain vocabulary, ID and presentation order.
sigs=collections.defaultdict(list)
for c in cases:
 dnorm=[]
 for d in c['documents']:
  scope=d['scope']
  if scope in ['Bargeldabhebung','Glasschaden','Depotübertrag']:scope='OTHER_TARGET'
  dnorm.append((d['title'],d['publication'],d['effective'],scope,d['threshold']))
 sig=(c['precedence'],tuple(sorted(dnorm)),c['facts'].split('400 EUR.',1)[1])
 sigs[repr(sig)].append(c['id'])
assert len(sigs)==16 and set(map(len,sigs.values()))=={3}
count=lambda field:dict(collections.Counter(c[field] for c in cases))
scount=dict(collections.Counter(c['expected']['source'] for c in cases)); dcount=dict(collections.Counter(c['expected']['determination'] for c in cases))
summary={'review_type':'independent AI review; exhaustive visible-state semantic audit; no human-expert validation','model_free':True,'model_loaded':False,'inference_performed':False,'previous_benchmark_predictions_read':False,'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':inputs,'case_count':len(cases),'document_count':len(all_doc_reviews),'semantic_pass_count':len(reviews),'semantic_blockers':[],'case_gold_request_metadata_consistency':'pass, 48/48','request_label_leakage':'No expected/rationale/document outcome/metadata keys enter request payload; row id is outside the payload. Visible Ja/Nein rule language is task evidence, not gold leakage. Static runner inspection confirms outer ids are not encoded.','source_label_counts':scount,'determination_counts':dcount,'joint_label_counts':{s+'|'+d:n for (s,d),n in collections.Counter((c['expected']['source'],c['expected']['determination']) for c in cases).items()},'unique_source_count':27,'nonunique_source_count':21,'material_clarification_denominator':12,'definite_answer_denominator':36,'source_uncertain_definite_denominator':9,'domains':count('domain'),'strata':count('stratum'),'families':count('family'),'source_position_counts_unique_only':dict(collections.Counter(c['source_position'] for c in cases if c['source_position'])),'unique_source_position_by_document_count':{str(n):dict(collections.Counter(c['source_position'] for c in cases if c['source_position'] and len(c['documents'])==n)) for n in [2,3]},'semantic_archetype_count':16,'semantic_archetype_groups':[sorted(v) for v in sigs.values()],'paired_order_intervention':False,'iid_claim_supported':False,'all_27_unique_source_labels_are_subtype_fixed_across_domains':True,'D3_unique_source_is_always_no':True,'pre_freeze_reporting_corrections':[{'id':'R1','priority':'required','finding':'48 independently written cases is inaccurate: source code applies one list of 16 templates to three domain vocabularies. These are 48 template-generated instances in 12 descriptive domain×stratum families, with stronger cross-domain archetype dependence.','recommendation':'Use 48 AI-authored template-generated instances from 16 archetypes; do not call the rows independent observations or claim domain transfer from these lexical variants.'},{'id':'R2','priority':'required','finding':'Comments claiming exact balance/counterbalance of winner positions are false. Two-document unique cases: position 1=9, 2=6. Three-document unique cases: 1=2, 2=5, 3=5. Overall 1=11, 2=11, 3=5. No explicit position-counterbalance logic follows the random shuffle.','recommendation':'Replace claims with deterministic shuffled document order and report exact position counts. Never claim order robustness without a paired order intervention.'},{'id':'R3','priority':'design_limitation_or_pre_run_change','finding':'Unique source ID repeats by subtype in each domain. D3 is the correct source in nine cases, all no; D1 and D2 are each yes six/no three. Titles, thresholds and answers are also repeated across archetypes.','recommendation':'Either pre-run correct the source-ID schedule to break this avoidable association and re-review/refreeze, or retain the dataset with explicit shortcut/confounding caveats. No model-dependent adjustment is permitted.'},{'id':'R4','priority':'reporting','finding':'This corpus has 16 shared semantic archetypes, and the 12 domain×stratum families are not independent clusters because archetypes cross domains.','recommendation':'Report exact descriptive counts and family slices only; no IID confidence interval, statistical significance, robustness, or broad domain generalization claim.'}], 'minor_notes':['The design_summary key unique_source_labels includes not_unique and should be renamed source_label_counts for clarity.','Absent D labels remain schema-valid choices in two-document cases and must count as wrong source choices, not malformed outputs.','Nonapplicable banking/finance distractors retain target-amount terminology under a different scope. They are clearly excluded, so this is artificiality rather than a gold ambiguity.','The stratum named unresolved contains six definite-answer controls; compute clarification metrics from gold determination, never from stratum names.']}
for key,actual in [('cases',len(cases)),('domains',summary['domains']),('strata',summary['strata']),('determinations',dcount),('source_uncertain_answer_definite',9),('unique_source_labels',scount)]:assert design[key]==actual
OUT.mkdir(exist_ok=True)
(OUT/'independent_semantic_case_reviews.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in reviews))
(OUT/'independent_semantic_document_reviews.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in all_doc_reviews))
(OUT/'independent_semantic_review_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(OUT/'independent_semantic_reviewed_sha256.json').write_text(json.dumps(inputs,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['case_count','document_count','semantic_pass_count','semantic_blockers','source_label_counts','determination_counts','semantic_archetype_count','source_position_counts_unique_only']},indent=2))
