#!/usr/bin/env python3
"""AI-authored minimal-span pairs. No model calls. Existing policy schema reused."""
from pathlib import Path
import json,hashlib,random
from collections import Counter
R=Path(__file__).resolve().parents[1]
assert not (R/'freeze_manifest.json').exists()
P=[]
def add(domain,key,kind,subtype,rule,question,prefix,a,b,suffix,ga,gb,ra,rb,fact):
 def gold(g):return dict(action=g[0],determination=g[1])
 P.append(dict(id='pair_'+key,domain=domain,family=key,kind=kind,subtype=subtype,rule=rule,question=question,unchanged_prefix=prefix,span_a=a,span_b=b,unchanged_suffix=suffix,gold_a=gold(ga),gold_b=gold(gb),rationale_a=ra,rationale_b=rb,changed_fact=fact))
Y=('answer','yes');N=('answer','no');F=('ask_fact','unresolved');T=('ask_target','unresolved');C=('resolve_conflict','unresolved')
add('banking','paper_transfer_quota','flip','yes_to_no',
 'Im fiktiven Tarif ist eine beleghafte Überweisung genau dann im Monatskontingent kostenfrei, wenn ihre laufende Nummer im Monat höchstens 3 beträgt UND der Tarif „Basis Plus“ aktiv ist.',
 'Ist diese Überweisung nach der Regel im Monatskontingent kostenfrei?',
 'Basis Plus ist aktiv. Diese Überweisung ist im betreffenden Monat Nummer ','3','4','.',Y,N,'Nummer 3 liegt noch im Kontingent.','Nummer 4 liegt außerhalb des Kontingents.','Laufende Überweisungsnummer 3 → 4')
add('banking','savings_stamp','flip','no_to_yes',
 'Eine fiktive Sparmarke wird genau dann vergeben, wenn im Monat mindestens 75 Euro auf den Sparplan eingezahlt wurden UND der Sparplan aktiv ist.',
 'Wird nach dieser Regel eine Sparmarke vergeben?',
 'Der Sparplan ist aktiv. Im betreffenden Monat wurden insgesamt ','74','75',' Euro eingezahlt.',N,Y,'74 Euro unterschreiten die Mindestzahlung.','75 Euro erreichen die Mindestzahlung.','Monatliche Einzahlung 74 → 75 Euro')
add('banking','statement_notification','flip','clarify_to_answer',
 'Die fiktive Auszugsbenachrichtigung ist genau dann einschaltbar, wenn eine bestätigte E-Mail-Adresse hinterlegt ist UND die Zustimmung zu dieser Benachrichtigung vorliegt.',
 'Ist die Benachrichtigung nach dieser Regel einschaltbar?',
 'Eine bestätigte E-Mail-Adresse ist hinterlegt. Der Zustimmungsstatus lautet: ','nicht angegeben','Zustimmung liegt vor','.',F,Y,'Die notwendige Zustimmung ist unbekannt.','Adresse und Zustimmung sind bestätigt.','Zustimmung unbekannt → bestätigt')
add('banking','envelope_pickup','flip','answer_to_clarify',
 'Ein fiktiver Unterlagenumschlag darf genau dann abgeholt werden, wenn er in der Filiale bereitliegt UND der Abholschein vorliegt.',
 'Darf der angefragte Umschlag nach dieser Regel abgeholt werden?',
 'Umschlag A liegt bereit, aber sein Abholschein liegt nicht vor. Umschlag B liegt bereit und sein Abholschein liegt vor. Angefragt ist ','Umschlag A','noch keiner der beiden Umschläge eindeutig','.',N,T,'Für A fehlt der Abholschein nachweislich.','A ergibt Nein, B Ja; der Zielumschlag muss geklärt werden.','Ziel A → unbestimmtes Ziel unter A/B')
add('banking','standing_order_express','invariant','irrelevant_text',
 'Eine fiktive Expressänderung am Dauerauftrag ist genau dann verfügbar, wenn der Auftrag aktiv ist UND der Änderungswunsch vor 12 Uhr eingeht. Der selbst vergebene Auftragsname spielt keine Rolle.',
 'Ist die Expressänderung nach dieser Regel verfügbar?',
 'Der Dauerauftrag ist aktiv; der Änderungswunsch geht um 11 Uhr ein. Mein eigener Auftragsname lautet „','Vereinsbeitrag','Monatsbeitrag','“.',Y,Y,'Aktiver Auftrag und Eingang vor 12 Uhr.','Aktiver Auftrag und Eingang vor 12 Uhr; nur der irrelevante Name ändert sich.','Privater Auftragsname verändert')
add('banking','coin_bag_limit','invariant','within_region_fact',
 'Ein fiktiver Münzbeutel wird am Automaten genau dann angenommen, wenn er höchstens 50 Münzen enthält UND die Beutelkennung lesbar ist.',
 'Wird der Beutel nach dieser Regel am Automaten angenommen?',
 'Die Beutelkennung ist lesbar. Der Beutel enthält ','51','52',' Münzen.',N,N,'51 Münzen überschreiten die Obergrenze.','52 Münzen überschreiten dieselbe Obergrenze.','Münzzahl 51 → 52, beide oberhalb der Grenze')
add('banking','fx_pickup_stock','invariant','irrelevant_text',
 'Eine fiktive Bargeldabholung ist genau dann zusagbar, wenn die angefragte Währung in der Filiale vorrätig ist UND ein Abholtermin bestätigt ist. Die gewünschte Papierhülle ist ohne Bedeutung.',
 'Ist diese Abholung nach der Regel zusagbar?',
 'Der Abholtermin ist bestätigt. Ob die Währung vorrätig ist, ist nicht angegeben. Die gewünschte Papierhülle ist ','weiß','braun','.',F,F,'Der entscheidende Währungsbestand fehlt.','Der Währungsbestand bleibt unbekannt; die Hüllenfarbe hilft nicht.','Irrelevante Hüllenfarbe weiß → braun')
add('banking','locker_waitlist','invariant','short_circuit_control',
 'Ein fiktiver Schließfachplatz wird genau dann fest reserviert, wenn die Kaution vollständig bezahlt ist UND ein passendes Fach frei ist.',
 'Ist eine feste Reservierung nach der Regel möglich?',
 'Die Kaution ist ausdrücklich nicht bezahlt. Zum freien Fach lautet die Angabe: ','unbekannt','ein passendes Fach ist frei','.',N,N,'Fehlende Kaution schließt die Reservierung trotz unbekannter Verfügbarkeit aus.','Fehlende Kaution schließt sie auch bei bestätigter Verfügbarkeit aus.','Verfügbarkeit unbekannt → bestätigt, Kaution bleibt nicht bezahlt')
add('insurance','gadget_theft_notice','flip','yes_to_no',
 'Ein fiktiver Diebstahlbaustein leistet genau dann, wenn ein Kaufbeleg vorliegt UND die Meldung spätestens 48 Stunden nach dem Diebstahl eingeht. Die verstrichene Stundenzahl ist bereits vollständig berechnet.',
 'Sind die Bedingungen dieses Diebstahlbausteins erfüllt?',
 'Der Kaufbeleg liegt vor. Die Meldung ging nach genau ','48','49',' Stunden ein.',Y,N,'Die eingeschlossene 48-Stunden-Grenze wird eingehalten.','49 Stunden überschreiten die Meldefrist.','Meldeabstand 48 → 49 Stunden')
add('insurance','glass_cost_limit','flip','no_to_yes',
 'Eine fiktive Glaspauschale ist genau dann vorgesehen, wenn es sich um einen versehentlichen Bruch handelt UND der Rechnungsbetrag höchstens 500 Euro beträgt.',
 'Ist die Glaspauschale nach der Regel vorgesehen?',
 'Es war ein versehentlicher Bruch. Der Rechnungsbetrag beträgt ','501','500',' Euro.',N,Y,'501 Euro liegen über der Grenze.','500 Euro sind von der Grenze eingeschlossen.','Rechnungsbetrag 501 → 500 Euro')
add('insurance','tow_distance_records','flip','clarify_to_answer',
 'Die fiktive Abschlepppauschale gilt genau dann, wenn die Panne gedeckt ist UND die Abschleppstrecke höchstens 20 Kilometer beträgt. Gleichrangige ungeklärte Streckenangaben haben keinen Vorrang.',
 'Gilt die Abschlepppauschale nach dieser Regel?',
 'Die Panne ist gedeckt. Zwei gleichrangige aktuelle Belege nennen für dieselbe Abschleppstrecke 25 Kilometer und ','12','25',' Kilometer. Keiner ist als Korrektur markiert.',C,N,'12 und 25 Kilometer ergeben unterschiedliche Ergebnisse; Konflikt klären.','Beide Belege nennen 25 Kilometer; die 20-Kilometer-Grenze ist überschritten.','Zweite Streckenangabe 12 → 25 Kilometer; erste bleibt 25')
add('insurance','equipment_inspection','flip','answer_to_clarify',
 'Ein fiktiver Sportgerätebaustein zahlt genau dann, wenn der Schaden versehentlich entstand UND eine gültige Prüfbescheinigung vorliegt.',
 'Sind die Leistungsbedingungen dieses Bausteins erfüllt?',
 'Der Schaden entstand versehentlich. Zur gültigen Prüfbescheinigung steht hier: ','liegt vor','Vorliegen ist unbekannt','.',Y,F,'Versehentlicher Schaden und gültige Bescheinigung erfüllen die Regel.','Ob die entscheidende Bescheinigung vorliegt, muss erfragt werden.','Bescheinigung bestätigt vorhanden → unbekannt')
add('insurance','camera_rental_cover','invariant','irrelevant_text',
 'Ein fiktiver Leihkamerabaustein greift genau dann, wenn die Leihdauer höchstens 14 Tage beträgt UND ein unterschriebener Leihbeleg vorliegt. Die Kamerafarbe ist unerheblich.',
 'Greift der Baustein nach der Regel?',
 'Die Leihdauer beträgt 10 Tage; der Leihbeleg ist unterschrieben. Die Kamera ist ','schwarz','silberfarben','.',Y,Y,'10 Tage und unterschriebener Leihbeleg erfüllen die Regel.','Die unveränderten Voraussetzungen erfüllen die Regel.','Irrelevante Kamerafarbe geändert')
add('insurance','baggage_weight_cap','invariant','within_region_fact',
 'Die fiktive Gepäckpauschale gilt genau dann, wenn das Gepäckstück höchstens 20 Kilogramm wiegt UND sein Verlust bestätigt ist.',
 'Gilt die Gepäckpauschale nach dieser Regel?',
 'Der Verlust ist bestätigt. Das Gepäckstück wog ','19','20',' Kilogramm.',Y,Y,'19 Kilogramm liegen innerhalb der Gewichtsgrenze.','20 Kilogramm sind von der Grenze eingeschlossen.','Gewicht 19 → 20 Kilogramm, beide innerhalb der Grenze')
add('insurance','rental_days_conflict','invariant','irrelevant_text',
 'Ein fiktiver Mietersatzbaustein gilt genau dann, wenn die Mietdauer höchstens 5 Tage beträgt UND eine Rechnung vorliegt. Gleichrangige ungeklärte Angaben zur Dauer haben keinen Vorrang; die Lackfarbe ist irrelevant.',
 'Gilt der Mietersatzbaustein nach dieser Regel?',
 'Die Rechnung liegt vor. Zwei gleichrangige ungeklärte Belege nennen für denselben Mietvorgang 3 beziehungsweise 8 Tage. Das Mietfahrzeug ist ','blau','grün',' lackiert.',C,C,'3 versus 8 Tage ändern die Entscheidung; den Konflikt klären.','Der materielle Dauerkonflikt bleibt trotz geänderter Lackfarbe bestehen.','Irrelevante Lackfarbe blau → grün')
add('insurance','festival_cancellation','invariant','short_circuit_control',
 'Ein fiktiver Festivalausfallbaustein gilt genau dann, wenn das Festival vollständig abgesagt wurde UND der Eintritt nicht anderweitig erstattet wurde.',
 'Gilt der Ausfallbaustein nach der Regel?',
 'Das Festival fand vollständig statt und wurde nicht abgesagt. Zur anderweitigen Erstattung ist angegeben: ','unbekannt','keine Erstattung erfolgt','.',N,N,'Ohne Absage scheitert die Regel unabhängig von der Erstattung.','Ohne Absage scheitert sie auch ohne Erstattung.','Erstattung unbekannt → nicht erfolgt, Absage bleibt verneint')
add('finance','rebalance_interval','flip','yes_to_no',
 'Eine fiktive Portfolio-Neugewichtung ist im Basistarif genau dann kostenfrei, wenn seit der letzten Neugewichtung mindestens 30 Tage vergangen sind UND keine Sonderausführung verlangt wird.',
 'Ist diese Neugewichtung nach der Regel kostenfrei?',
 'Es gilt der Basistarif. Es wird keine Sonderausführung verlangt. Seit der letzten Neugewichtung sind genau ','30','29',' Tage vergangen.',Y,N,'30 Tage erreichen die Mindestwartezeit.','29 Tage unterschreiten die Mindestwartezeit.','Wartezeit 30 → 29 Tage')
add('finance','savings_plan_components','flip','no_to_yes',
 'Ein fiktiver Sammelsparplan kann genau dann im Standardpaket angelegt werden, wenn er höchstens 10 Positionen enthält UND alle Positionen sparplanfähig sind.',
 'Kann dieser Sammelsparplan im Standardpaket angelegt werden?',
 'Alle vorgesehenen Positionen sind sparplanfähig. Ihre Anzahl beträgt ','11','10','.',N,Y,'11 Positionen überschreiten die Paketgrenze.','10 Positionen liegen noch im Standardpaket.','Positionszahl 11 → 10')
add('finance','fund_switch_target','flip','clarify_to_answer',
 'Ein fiktiver Fondswechsel ist genau dann im internen Standardweg möglich, wenn Ausgangs- und Zielfonds im selben Depot liegen UND beide zum Standarduniversum gehören.',
 'Ist der angefragte Wechsel nach der Regel im Standardweg möglich?',
 'Bei Wechsel A liegen beide Fonds im selben Depot und gehören zum Standarduniversum. Bei Wechsel B liegen sie in verschiedenen Depots, gehören aber beide zum Standarduniversum. Angefragt ist ','noch keiner der beiden Wechsel eindeutig','Wechsel A','.',T,Y,'A ist möglich, B nicht; das Ziel muss geklärt werden.','A erfüllt beide Bedingungen eindeutig.','Unbestimmtes Ziel → Wechsel A')
add('finance','redemption_window_conflict','flip','answer_to_clarify',
 'Eine fiktive Anteilrückgabe ist genau dann im aktuellen Fenster möglich, wenn das Rückgabefenster offen ist UND die Mindesthaltezeit erfüllt ist. Gleichrangige ungeklärte Fensterangaben haben keinen Vorrang.',
 'Ist die Anteilrückgabe nach dieser Regel im aktuellen Fenster möglich?',
 'Die Mindesthaltezeit ist erfüllt. Zwei gleichrangige aktuelle Meldungen für dasselbe Fenster lauten „geschlossen“ und „','geschlossen','offen','“. Keine ist als Korrektur markiert.',N,C,'Beide Quellen bestätigen geschlossen; daher Nein.','Offen und geschlossen ergeben einen materiellen Konflikt.','Zweite Fensterangabe geschlossen → offen')
add('finance','fractional_sale_batch','invariant','irrelevant_text',
 'Ein fiktiver Bruchstückverkauf ist genau dann im Sammellauf möglich, wenn der Bestand kleiner als ein ganzer Anteil ist UND der Sammellauf noch offen ist. Der eigene Ablagename spielt keine Rolle.',
 'Ist dieser Bruchstückverkauf im Sammellauf möglich?',
 'Der Bestand beträgt 0,4 Anteile; der Sammellauf ist offen. Mein Ablagename lautet „','Restbestand','Kleinbestand','“.',Y,Y,'0,4 Anteile und offener Sammellauf erfüllen die Regel.','Nur der irrelevante Ablagename ändert sich.','Irrelevanter Ablagename geändert')
add('finance','research_credit_age','invariant','within_region_fact',
 'Ein fiktiver Analyse-Gutschein ist genau dann einlösbar, wenn er höchstens 90 Tage alt ist UND noch nicht verwendet wurde.',
 'Ist dieser Gutschein nach der Regel einlösbar?',
 'Der Gutschein wurde noch nicht verwendet. Sein Alter beträgt ','89','90',' Tage.',Y,Y,'89 Tage liegen innerhalb der Altersgrenze.','90 Tage sind von der Altersgrenze eingeschlossen.','Gutscheinalter 89 → 90 Tage, beide innerhalb der Grenze')
add('finance','report_delivery_target','invariant','irrelevant_text',
 'Ein fiktiver Depotbericht ist genau dann elektronisch zustellbar, wenn er fertiggestellt ist UND für sein Depot der elektronische Versand aktiviert ist. Der interne Berichtstitel ist irrelevant.',
 'Ist der angefragte Bericht nach der Regel elektronisch zustellbar?',
 'Bericht A ist fertiggestellt und sein Depot hat elektronischen Versand aktiviert. Bericht B ist fertiggestellt, aber der elektronische Versand seines Depots ist deaktiviert. Welchen der beiden Berichte ich meine, ist nicht festgelegt. Der interne Titel von A lautet „','Übersicht','Bestandsübersicht','“.',T,T,'A ergibt Ja, B Nein; das Ziel fehlt.','Die Titeländerung legt das Ziel nicht fest; weiter erfragen.','Irrelevanter Titel von A verändert, Ziel bleibt offen')
add('finance','limit_order_price_step','invariant','short_circuit_control',
 'Ein fiktiver Limitauftrag wird genau dann in das Standardbuch aufgenommen, wenn sein Limit ein Vielfaches von 0,10 Euro ist UND das Handelsfenster offen ist.',
 'Wird der Auftrag nach dieser Regel ins Standardbuch aufgenommen?',
 'Das Limit beträgt 12,34 Euro. Zum Handelsfenster ist angegeben: ','Status unbekannt','Fenster ist offen','.',N,N,'12,34 ist kein Vielfaches von 0,10; das unbekannte Fenster ist unerheblich.','Die ungültige Preisstufe bleibt trotz offenem Fenster ausschlaggebend.','Fenster unbekannt → offen, ungültige Preisstufe unverändert')
policy=json.loads((R/'data/policy.json').read_text())
cases=[];pairs=[]
for p in P:
 ids=[]
 for side in ['a','b']:
  id=p['id']+'_'+side;ids.append(id);msg=p['unchanged_prefix']+p['span_'+side]+p['unchanged_suffix']
  c={k:p[k] for k in ['domain','family','kind','subtype','rule','question']};c.update(id=id,pair_id=p['id'],side=side,message=msg,expected=p['gold_'+side],rationale=p['rationale_'+side],authorship='AI-authored; separately AI-reviewed before inference; not human-expert validated');cases.append(c)
 q={k:v for k,v in p.items() if k not in ['gold_a','gold_b','rationale_a','rationale_b']};q.update(case_ids=ids,expected_a=p['gold_a'],expected_b=p['gold_b'],changed_character_offsets_a=[len(p['unchanged_prefix']),len(p['unchanged_prefix'])+len(p['span_a'])],changed_character_offsets_b=[len(p['unchanged_prefix']),len(p['unchanged_prefix'])+len(p['span_b'])],unchanged_components=['rule','question','schema_and_option_order','message_prefix','message_suffix'],unchanged_prefix_sha256=hashlib.sha256(p['unchanged_prefix'].encode()).hexdigest(),unchanged_suffix_sha256=hashlib.sha256(p['unchanged_suffix'].encode()).hexdigest());pairs.append(q)
random.Random(2026100248).shuffle(cases)
requests=[];gold=[];metadata=[]
for c in cases:
 requests.append({'id':c['id'],'request':{'model':'clef-flash','state':f"Fiktive Testregel:\n{c['rule']}\n\nSynthetische Anfrage und Unterlagen:\n{c['message']}\n\nZu beurteilende Eigenschaft:\n{c['question']}",'questions':policy}})
 gold.append({'id':c['id'],'expected':c['expected']})
 metadata.append({k:c[k] for k in ['id','pair_id','side','domain','family','kind','subtype','rationale','authorship']})
for name,rows in [('cases',cases),('pairs',pairs),('requests',requests),('gold',gold),('metadata',metadata)]:
 (R/f'data/{name}.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in rows))
summary={'suite_id':'minimal_pairs','case_count':48,'pair_count':24,'pair_domain_counts':dict(Counter(p['domain'] for p in pairs)),'pair_kind_counts':dict(Counter(p['kind'] for p in pairs)),'pair_subtype_counts':dict(Counter(p['subtype'] for p in pairs)),'gold_action_counts':dict(Counter(c['expected']['action'] for c in cases)),'gold_determination_counts':dict(Counter(c['expected']['determination'] for c in cases)),'request_order_seed':2026100248,'reused_templates':['Exact two-field action/determination schema and English option IDs from clarification72','Generic closed-rule conjunctions, threshold boundaries, absent-versus-unknown distinction, ambiguous-target and equal-source conflict templates','Original pinned native runtime and tokenizer/freeze/guard workflow'],'new_content':'24 newly authored scenario situations and rule texts; no source scenario copied','not_a_holdout':True}
(R/'data/design_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,indent=2))
