#!/usr/bin/env python3
"""Build AI-authored, fictional German clarification benchmark; no model access."""
from pathlib import Path
import json, random
from collections import Counter
R=Path(__file__).resolve().parents[1]
assert not (R/'freeze_manifest.json').exists(), 'Frozen suite may not be rebuilt'
assert not (R/'results/predictions.jsonl').exists(), 'Inference exists'
F=[]
def family(domain,key,rule,question,examples):
 assert len(examples)==6
 F.append(dict(domain=domain,family=key,rule=rule,question=question,examples=examples))
# In each family: missing fact, ambiguous target, material conflict, full yes,
# full no, sufficient despite an omission. The texts are authored, not sampled.
family('banking','giro_fee',
 'Das Monatsentgelt entfällt genau dann, wenn im betreffenden Monat mindestens 1.200 Euro als Gehalt eingegangen sind UND das elektronische Postfach aktiv war. Andere Zahlungseingänge zählen nicht als Gehalt.',
 'Entfällt das Monatsentgelt nach dieser Regel für den angefragten Monat?',[
 ('Im September kamen 1.350 Euro Gehalt an. Ob mein elektronisches Postfach im September aktiv war, steht hier nicht. Wie sieht es mit dem Entgelt für September aus?', 'Postfachstatus im September erfragen.'),
 ('Ich frage nach einem meiner beiden Monate, weiß aber noch nicht, welchem: August hatte 1.300 Euro Gehalt und ein aktives Postfach; September hatte 900 Euro Gehalt und ein aktives Postfach. Entfällt dafür das Entgelt?', 'Angefragten Monat bestimmen.'),
 ('Für September ist das Postfach als aktiv bestätigt. Zwei gleichrangige, ungeklärte Auszüge nennen zum Gehaltseingang desselben Monats 1.300 Euro beziehungsweise 900 Euro. Keiner ist als Korrektur markiert. Ist September entgeltfrei?', 'Widerspruch zum maßgeblichen Gehaltseingang klären.'),
 ('Bitte nur September bewerten: 1.200 Euro Gehalt sind eingegangen und das elektronische Postfach war aktiv.', 'Beide Bedingungen sind erfüllt, einschließlich der Grenze.'),
 ('Für September sind 1.500 Euro Gehalt bestätigt. Das elektronische Postfach war den gesamten Monat deaktiviert.', 'Die notwendige Postfachbedingung ist nicht erfüllt.'),
 ('Im September gab es definitiv keinen Gehaltseingang, nur eine private Rückzahlung über 1.500 Euro. Ob das Postfach aktiv war, habe ich nicht zur Hand.', 'Kein Gehalt: ein fehlender Postfachstatus kann das Nein nicht ändern.')])
family('banking','card_replacement',
 'Ein Ersatz wegen technischen Defekts ist genau dann kostenfrei, wenn der Defekt höchstens 24 Monate nach Ausgabe (24 Monate eingeschlossen) auftrat UND kein vorsätzlich verursachter Schaden vorliegt. Verlustfälle fallen nicht unter diese Regel.',
 'Ist der angefragte Kartenersatz nach dieser Regel kostenfrei?',[
 ('Meine einzige betroffene Karte hat einen technischen Defekt, ohne vorsätzlich verursachten Schaden. Wann sie ausgegeben wurde, kann ich den Unterlagen nicht entnehmen.', 'Alter der Karte zum Defekt erfragen.'),
 ('Zwei defekte Karten ohne vorsätzlichen Schaden liegen vor: Karte A war beim Defekt 18 Monate alt, Karte B 30 Monate. Mit „die Karte“ meinte ich eine davon, habe aber noch nicht gesagt welche.', 'Welche Karte soll bewertet werden?'),
 ('Es geht nur um Karte A. Kein vorsätzlicher Schaden, technischer Defekt. Zwei gleichrangige Einträge datieren die Ausgabe einmal 18 und einmal 30 Monate vor dem Defekt; eine Berichtigung ist nicht bekannt.', 'Widersprüchliches Ausgabedatum klären.'),
 ('Die technisch defekte Karte war beim Defekt genau 24 Monate alt. Der Schaden war nicht vorsätzlich verursacht; die Karte ist nicht verloren.', 'Beide Bedingungen einschließlich Altersgrenze erfüllt.'),
 ('Die Karte ist technisch defekt, ohne vorsätzlichen Schaden. Beim Defekt war sie seit 25 Monaten ausgegeben.', 'Altersgrenze überschritten.'),
 ('Technischer Defekt nach 12 Monaten, kein vorsätzlicher Schaden und kein Verlust. Die Kartenfarbe und die Nummer des alten Briefs kenne ich nicht.', 'Die ausgelassenen Angaben gehören nicht zur Regel.')])
family('banking','transfer_recall',
 'Eine vorgemerkte Überweisung ist im Selfservice genau dann stornierbar, wenn ihr Status noch „geplant“ lautet UND der nächste Ausführungslauf noch nicht begonnen hat. Eine bereits ausgeführte Überweisung ist dort nicht stornierbar.',
 'Ist die angefragte Überweisung nach dieser Regel jetzt im Selfservice stornierbar?',[
 ('Die Überweisung an den Sportverein steht noch auf „geplant“. Ob der zugehörige Ausführungslauf inzwischen begonnen hat, ist in meiner Ansicht nicht erkennbar.', 'Status des Ausführungslaufs erfragen.'),
 ('Ich meine eine meiner beiden Überweisungen, habe sie aber noch nicht ausgewählt: A ist geplant, ihr Lauf hat nicht begonnen; B ist bereits ausgeführt. Kann ich die Überweisung stornieren?', 'Zielüberweisung bestimmen.'),
 ('Für denselben Auftrag ist der Lauf sicher noch nicht gestartet. Zwei gleichrangige Statusmeldungen stehen nebeneinander: „geplant“ und „ausgeführt“. Beide gelten als aktuell, eine Korrektur fehlt.', 'Widersprüchlichen Auftragsstatus klären.'),
 ('Der einzige angefragte Auftrag steht auf „geplant“. Der dafür zuständige Ausführungslauf hat bestätigt noch nicht begonnen.', 'Planstatus und noch nicht gestarteter Lauf liegen vor.'),
 ('Der Auftrag ist noch als „geplant“ gelistet. Der zugehörige Ausführungslauf hat aber nachweislich bereits begonnen.', 'Notwendige Laufbedingung ist verletzt.'),
 ('Die Überweisung ist bestätigt bereits ausgeführt. Wann der Ausführungslauf begonnen hatte, weiß ich nicht mehr. Mir geht es nur um die Stornierbarkeit im Selfservice.', 'Ausgeführt reicht für ein Nein; fehlende Laufzeit ist unerheblich.')])
family('banking','statement_download',
 'Ein Kontoauszug steht im Standard-Download genau dann bereit, wenn er höchstens 24 Monate alt ist UND das zugehörige Konto noch offen ist. Für geschlossene Konten ist dieser Download nicht verfügbar.',
 'Ist der angefragte Auszug nach dieser Regel im Standard-Download verfügbar?',[
 ('Das Konto ist noch offen. Für den gesuchten Auszug habe ich weder Auszugsmonat noch Alter angegeben. Ist er im Standard-Download?', 'Alter oder Monat des Auszugs erfragen.'),
 ('Konto A ist offen, sein gesuchter Auszug 8 Monate alt. Konto B ist geschlossen, sein gesuchter Auszug ebenfalls 8 Monate alt. Welchen dieser beiden Auszüge ich meine, ist noch offen.', 'Angefragten Auszug beziehungsweise das Konto bestimmen.'),
 ('Es geht um denselben 10 Monate alten Auszug. Zwei gleichrangige aktuelle Datensätze widersprechen sich beim Konto: „offen“ und „geschlossen“. Eine verbindliche Korrektur fehlt.', 'Widerspruch zum Kontostatus klären.'),
 ('Mein Konto ist weiterhin offen. Der konkret gesuchte Auszug ist genau 24 Monate alt.', 'Grenze und offener Kontostatus erfüllen die Regel.'),
 ('Das Konto ist noch offen. Der gesuchte Auszug ist 25 Monate alt.', 'Auszug liegt außerhalb der Altersgrenze.'),
 ('Der Auszug vom offenen Konto ist 4 Monate alt. Auf den Unterlagen fehlt lediglich meine interne Ablagebezeichnung, die ich selbst vergeben hatte.', 'Interne Ablagebezeichnung ist nicht erforderlich.')])
family('insurance','bicycle_theft',
 'Nach dem fiktiven Tarif wird ein Fahrraddiebstahl genau dann erstattet, wenn das Fahrrad beim Diebstahl angeschlossen war UND die Meldung spätestens 7 Kalendertage nach dem Diebstahl einging. Die Frist beginnt am Folgetag; hier ist die Anzahl vergangener Tage schon angegeben.',
 'Sind die genannten Erstattungsbedingungen für den angefragten Diebstahl erfüllt?',[
 ('Die Diebstahlmeldung ging 3 Tage nach dem Ereignis ein. Ob das Fahrrad damals angeschlossen war, ist weder bestätigt noch verneint.', 'Ob das Fahrrad angeschlossen war, erfragen.'),
 ('Zwei gemeldete Diebstähle stehen zur Auswahl: A betraf ein angeschlossenes Rad und wurde nach 3 Tagen gemeldet; B betraf ein nicht angeschlossenes Rad und wurde nach 3 Tagen gemeldet. Welchen Fall ich meine, habe ich noch nicht ausgewählt.', 'Den gemeinten Diebstahlsfall bestimmen.'),
 ('Die Meldung zu einem einzigen Diebstahl kam nach 3 Tagen. Zwei gleichrangige Aussagen zum selben Ereignis lauten „angeschlossen“ und „nicht angeschlossen“, ohne geklärte Rangfolge.', 'Widerspruch zum Anschließen klären.'),
 ('Das Fahrrad war angeschlossen. Die Meldung ging genau 7 Kalendertage nach dem Diebstahl ein.', 'Beide Bedingungen einschließlich Fristgrenze sind erfüllt.'),
 ('Das Fahrrad war angeschlossen. Die Meldung ging erst 8 Kalendertage nach dem Diebstahl ein.', 'Meldefrist überschritten.'),
 ('Das Fahrrad war ausdrücklich nicht angeschlossen. Die Zahl der Tage bis zur Meldung fehlt noch. Kann die Bedingungskombination trotzdem erfüllt sein?', 'Nicht angeschlossen schließt Erfüllung unabhängig von der Meldezeit aus.')])
family('insurance','travel_delay',
 'Die fiktive Verspätungspauschale wird genau dann gewährt, wenn die Ankunft mindestens 6 Stunden verspätet war UND eine schriftliche Bestätigung des Beförderers vorliegt. Der Preis der Reise ist dafür ohne Bedeutung.',
 'Sind die Voraussetzungen für die Pauschale im angefragten Vorgang erfüllt?',[
 ('Die schriftliche Bestätigung des Beförderers liegt vor. Wie lange die Ankunft tatsächlich verspätet war, ist in dieser Anfrage noch nicht angegeben.', 'Dauer der Ankunftsverspätung erfragen.'),
 ('Ich beziehe mich unbestimmt auf eine meiner Reisen: Reise A kam 7 Stunden später an und hat eine schriftliche Bestätigung; Reise B kam 2 Stunden später an und hat dieselbe Art Bestätigung. Welche Reise gemeint ist, steht noch nicht fest.', 'Gemeinte Reise bestimmen.'),
 ('Die schriftliche Bestätigung liegt vor. Zwei gleichrangige Datensätze nennen für dieselbe Ankunft einmal 7 und einmal 2 Stunden Verspätung. Keine Angabe wurde als korrigiert bestätigt.', 'Widersprüchliche Verspätungsdauer klären.'),
 ('Für die einzelne betroffene Reise sind genau 6 Stunden Ankunftsverspätung sowie die schriftliche Bestätigung des Beförderers dokumentiert.', 'Beide Voraussetzungen einschließlich Grenze liegen vor.'),
 ('Die Ankunft war 8 Stunden verspätet. Eine schriftliche Bestätigung des Beförderers liegt ausdrücklich nicht vor.', 'Schriftliche Bestätigung fehlt nachweislich.'),
 ('Die Ankunft war 9 Stunden verspätet, die schriftliche Bestätigung liegt vor. Den damaligen Reisepreis kann ich nicht nennen.', 'Der unbekannte Reisepreis ist ausdrücklich irrelevant.')])
family('insurance','device_damage',
 'Die fiktive Geräteversicherung ersetzt einen Bruchschaden genau dann, wenn das Schadendatum innerhalb der Vertragslaufzeit liegt UND der Schaden versehentlich entstand. Vorsätzlich verursachte Schäden sind ausgeschlossen.',
 'Erfüllt der angefragte Schaden die beiden genannten Deckungsbedingungen?',[
 ('Der Bildschirm zerbrach versehentlich. Den Zeitpunkt des Schadens im Verhältnis zur Vertragslaufzeit haben wir noch nicht festgestellt.', 'Ob der Schaden innerhalb der Vertragslaufzeit eintrat, klären.'),
 ('Ich habe zwei Schadenfälle und meine noch keinen bestimmten: A war ein versehentlicher Bruch innerhalb der Laufzeit; B ein versehentlicher Bruch nach Ende der Laufzeit.', 'Den gemeinten Schadenfall auswählen lassen.'),
 ('Versehen ist bestätigt. Zum selben Bruchdatum widersprechen sich zwei gleichrangige aktuelle Unterlagen: eine ordnet es innerhalb, die andere außerhalb der Vertragslaufzeit ein. Es gibt keine Korrektur.', 'Widerspruch zur zeitlichen Deckung klären.'),
 ('Der versehentliche Bruch geschah nachweislich innerhalb der Vertragslaufzeit. Es geht nur um diesen einen Schaden.', 'Zeitliche Deckung und Versehen sind bestätigt.'),
 ('Der Bruch lag innerhalb der Vertragslaufzeit, wurde aber ausdrücklich vorsätzlich verursacht.', 'Vorsatz ist ein Ausschluss.'),
 ('Der Bruch ist nachweislich erst nach dem Ende der Vertragslaufzeit passiert. Ob er versehentlich geschah, ist noch offen.', 'Außerhalb der Laufzeit genügt für Nein; Versehen ändert das nicht.')])
family('insurance','luggage_delay',
 'Der fiktive Tarif erstattet notwendige Ersatzkäufe bei verspätetem Gepäck genau dann, wenn die Gepäckverspätung mindestens 24 Stunden betrug UND Kaufbelege vorliegen. Die Farbe des Koffers spielt keine Rolle.',
 'Sind die genannten Erstattungsbedingungen im angefragten Gepäckfall erfüllt?',[
 ('Das Gepäck war 30 Stunden verspätet. Ob Belege für die notwendigen Ersatzkäufe vorliegen, wurde noch nicht mitgeteilt.', 'Belegstatus erfragen.'),
 ('Zwei Gepäckfälle liegen vor: Fall A dauerte 30 Stunden, Belege liegen vor; Fall B dauerte 10 Stunden, Belege liegen vor. Meine Frage legt nicht fest, welchen der beiden Fälle ich meine.', 'Gemeinten Gepäckfall bestimmen.'),
 ('Belege für notwendige Ersatzkäufe liegen vor. Zur Dauer desselben Gepäckfalls liegen zwei gleichrangige aktuelle Angaben vor: 30 Stunden und 10 Stunden. Welche zutrifft, ist ungeklärt.', 'Widerspruch zur Gepäckverspätung klären.'),
 ('Die Verspätung des einen betroffenen Gepäckstücks betrug genau 24 Stunden. Belege für die notwendigen Ersatzkäufe liegen vor.', 'Grenze und Belegbedingung sind erfüllt.'),
 ('Das Gepäck war 40 Stunden verspätet. Es liegen ausdrücklich keine Kaufbelege für die notwendigen Ersatzkäufe vor.', 'Belegbedingung ist nicht erfüllt.'),
 ('Die Gepäckverspätung betrug 27 Stunden und die Belege der notwendigen Ersatzkäufe liegen vor. An die Farbe des Koffers erinnere ich mich nicht.', 'Kofferfarbe ist kein Kriterium.')])
family('finance','savings_fee',
 'Die Ausführungsgebühr des fiktiven Sparplans entfällt genau dann, wenn die einzelne Sparrate mindestens 50 Euro beträgt UND der gewählte Fonds auf der Aktionsliste steht. Für diesen Test stehen nur die Fonds Mohn und Linde auf dieser Liste.',
 'Entfällt die Ausführungsgebühr für die angefragte Sparrate?',[
 ('Meine Sparrate beträgt 70 Euro. Welcher Fonds im betroffenen Plan gewählt wurde, geht aus meiner Anfrage noch nicht hervor.', 'Gewählten Fonds erfragen.'),
 ('Ich habe zwei Pläne und meine noch keinen bestimmten: Plan A spart 70 Euro in Mohn, Plan B 70 Euro in Kiesel. Gilt die Gebührenbefreiung für meinen Plan?', 'Gemeinten Sparplan bestimmen.'),
 ('Die Rate des einzigen betroffenen Plans beträgt 70 Euro. Zwei gleichrangige aktuelle Ansichten nennen für denselben Plan einmal Mohn und einmal Kiesel; keine gilt als Korrektur.', 'Widersprüchliche Fondsauswahl klären.'),
 ('Der einzige angefragte Sparplan führt genau 50 Euro in den Fonds Linde aus.', 'Grenze und Aktionsfondsbedingung erfüllt.'),
 ('Ich frage nach einer Rate in Höhe von genau 49 Euro in den Fonds Mohn.', 'Die Rate unterschreitet die Mindesthöhe.'),
 ('Der Fonds ist bestätigt Kiesel. Die genaue Rate habe ich gerade nicht zur Hand. Kann sie nach dieser Regel gebührenfrei ausgeführt werden?', 'Kiesel ist nicht auf der Liste; die unbekannte Rate kann das nicht ändern.')])
family('finance','welcome_bonus',
 'Der fiktive Depot-Willkommensbonus gilt genau dann, wenn das Depot neu eröffnet wurde UND innerhalb des Aktionszeitraums mindestens 1.000 Euro eingezahlt wurden. Einzahlungen außerhalb des Zeitraums zählen nicht.',
 'Sind die Voraussetzungen für den Willkommensbonus beim angefragten Depot erfüllt?',[
 ('Das Depot wurde neu eröffnet. Die Höhe der Einzahlungen innerhalb des Aktionszeitraums wurde noch nicht angegeben.', 'Einzahlungsbetrag im Aktionszeitraum erfragen.'),
 ('Ich spreche von einem meiner Depots, ohne es festzulegen: A wurde neu eröffnet und erhielt im Zeitraum 1.100 Euro; B besteht seit Jahren und erhielt im Zeitraum 1.100 Euro.', 'Gemeintes Depot bestimmen.'),
 ('Das Depot ist neu. Für die Einzahlungen desselben Aktionszeitraums nennen zwei gleichrangige ungeklärte Buchungsübersichten 1.100 Euro und 900 Euro. Keine ist als Korrektur ausgewiesen.', 'Widerspruch zum relevanten Einzahlungsbetrag klären.'),
 ('Das betroffene Depot wurde neu eröffnet. Im Aktionszeitraum wurden genau 1.000 Euro eingezahlt.', 'Neueröffnung und Mindestbetrag erfüllt.'),
 ('Das Depot ist neu. Insgesamt kamen 1.200 Euro an, davon 800 Euro im Aktionszeitraum und 400 Euro erst danach.', 'Nur 800 Euro zählen; Mindestbetrag nicht erreicht.'),
 ('Das Depot wurde neu eröffnet und erhielt innerhalb des Aktionszeitraums 1.500 Euro. Die persönlich gewählte Depotbezeichnung fehlt in meiner Nachricht.', 'Persönliche Depotbezeichnung ist kein Kriterium; Ziel ist eindeutig.')])
family('finance','depot_statement_fee',
 'Die fiktive Gebühr für den Jahres-Depotbericht entfällt genau dann, wenn das Depot am Berichtstag mindestens 12 Monate bestand UND digitale Zustellung gewählt war. Papierzustellung ist in diesem Tarif nicht gebührenfrei.',
 'Entfällt die Gebühr für den angefragten Jahres-Depotbericht?',[
 ('Am Berichtstag war digitale Zustellung gewählt. Seit wann das Depot damals bestand, wurde nicht angegeben.', 'Depotdauer am Berichtstag erfragen.'),
 ('Ich meine einen von zwei Berichten, ohne ihn auszuwählen: Bericht A gehört zu einem 18 Monate alten Depot mit digitaler Zustellung; Bericht B zu einem 8 Monate alten Depot mit digitaler Zustellung.', 'Gemeinten Jahresbericht bestimmen.'),
 ('Das Depot bestand am Berichtstag 18 Monate. Zwei gleichrangige aktuelle Einträge zur gewählten Zustellung desselben Berichts lauten digital und Papier. Eine maßgebliche Korrektur ist nicht bekannt.', 'Widerspruch zur gewählten Zustellung klären.'),
 ('Das Depot bestand am Berichtstag genau 12 Monate. Digitale Zustellung war gewählt.', 'Beide Voraussetzungen einschließlich Grenze erfüllt.'),
 ('Das Depot bestand am Berichtstag 18 Monate, gewählt war Papierzustellung.', 'Papierzustellung erfüllt die Zustellbedingung nicht.'),
 ('Für den Bericht war definitiv Papierzustellung gewählt. Wie lange das Depot am Berichtstag schon bestand, ist unbekannt.', 'Papierzustellung reicht für Nein unabhängig vom Depotalter.')])
family('finance','order_cancellation',
 'Ein fiktiver Wertpapierauftrag ist über die Storno-Funktion genau dann stornierbar, wenn er noch den Status „offen“ hat UND noch keine Ausführung bestätigt wurde. Eine bestätigte Teilausführung zählt bereits als Ausführung.',
 'Ist der angefragte Auftrag nach dieser Regel über die Storno-Funktion stornierbar?',[
 ('Der Auftrag steht noch auf „offen“. Ob inzwischen eine Ausführung oder Teilausführung bestätigt wurde, lässt sich meiner Nachricht nicht entnehmen.', 'Ob eine Ausführung bestätigt wurde, erfragen.'),
 ('Ich habe noch keinen der beiden Aufträge ausgewählt: A ist offen und ohne bestätigte Ausführung; B ist offen, aber mit bestätigter Teilausführung. Kann ich den Auftrag stornieren?', 'Gemeinten Wertpapierauftrag bestimmen.'),
 ('Der eine betroffene Auftrag ist offen. Zwei gleichrangige aktuelle Meldungen widersprechen sich: keine Ausführung bestätigt beziehungsweise Teilausführung bestätigt. Eine Korrektur fehlt.', 'Widerspruch zum Ausführungsstatus klären.'),
 ('Der einzige betroffene Auftrag ist offen. Es ist ausdrücklich weder eine Voll- noch eine Teilausführung bestätigt.', 'Offen und keine bestätigte Ausführung erfüllen die Regel.'),
 ('Der Auftrag steht auf offen, eine Teilausführung wurde jedoch bereits bestätigt.', 'Bestätigte Teilausführung verletzt die notwendige Bedingung.'),
 ('Der offene Auftrag hat ausdrücklich keine bestätigte Voll- oder Teilausführung. Die Farbe des Symbols in meiner Anzeige kann ich nicht nennen.', 'Symbolfarbe ist für beide Bedingungen unerheblich.')])

POLICY='''Beurteile ausschließlich die angefragte Ja/Nein-Eigenschaft nach der mitgelieferten fiktiven Regel. Keine echte Beratung oder Handlung. Erfinde keine fehlenden Fakten. Antworte, wenn die vorhandenen Angaben das Ergebnis bereits eindeutig festlegen; eine irrelevante Lücke oder eine bereits sicher verletzte notwendige Bedingung rechtfertigt keine Rückfrage. Rückfrage nur, wenn die Unklarheit das Ergebnis ändern kann: fehlende wesentliche Sachangabe, unbestimmter Zielvorgang mit unterschiedlichen Ergebnissen oder ungeklärte widersprüchliche Angaben zum selben Ziel. Gleichrangige widersprüchliche Quellen ohne ausdrückliche Korrektur haben keinen Vorrang nach Reihenfolge. Bei materieller Unklarheit ist die Feststellung unresolved. Eine als nicht vorhanden bestätigte Voraussetzung ist kein unbekannter Fakt. Frage keine Zugangsdaten, PIN, TAN oder vollständigen Konto-/Kartennummern ab.'''
Q={
'action':{'type':'choice','instructions':POLICY+' Welcher nächste Schritt ist angemessen?', 'criteria':{
'answer':'Die angefragte Eigenschaft ist eindeutig entscheidbar; Ja oder Nein angeben.',
'ask_fact':'Eine entscheidungswesentliche Sachangabe fehlt; gezielt danach fragen.',
'ask_target':'Mehrere mögliche Zielvorgänge haben unterschiedliche Ergebnisse; den gemeinten Zielvorgang erfragen.',
'resolve_conflict':'Widersprüchliche gleichrangige Angaben zum selben Ziel ändern das Ergebnis; Widerspruch klären.'}},
'determination':{'type':'choice','instructions':'Welche Feststellung ist nach derselben Regel und diesen Angaben möglich? Nur die angefragte Eigenschaft beurteilen, keine Leistung ausführen. Bei entscheidungswesentlicher fehlender Angabe, unklarem Ziel oder ungelöstem Widerspruch unresolved; sonst yes oder no.', 'criteria':{
'yes':'Die angefragte Eigenschaft ist sicher erfüllt.',
'no':'Die angefragte Eigenschaft ist sicher nicht erfüllt.',
'unresolved':'Die angefragte Eigenschaft ist mit den vorliegenden Angaben nicht eindeutig bestimmbar.'}}
}
strata=['missing_fact','ambiguous_target','conflicting_evidence','complete_yes','complete_no','sufficient_despite_omission']
cases=[]
for f in F:
 for i,(msg,why) in enumerate(f['examples']):
  action=['ask_fact','ask_target','resolve_conflict','answer','answer','answer'][i]
  determination='unresolved' if i<3 else ('yes' if i==3 else 'no' if i==4 else ('no' if len(cases)//6%2==0 else 'yes'))
  c={'id':f"clarify_{f['family']}_{i+1:02}",'domain':f['domain'],'family':f['family'],'stratum':strata[i], 'rule':f['rule'],'question':f['question'],'message':msg,'expected':{'action':action,'determination':determination},'rationale':why,'clarification_target':why if i<3 else None,'authorship':'AI-authored, independently AI-reviewed before inference; not human-expert validated'}
  cases.append(c)
random.Random(202610021).shuffle(cases)
def write(name,rows):
 (R/'data'/name).write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in rows))
write('cases.jsonl',cases)
write('gold.jsonl',[{'id':c['id'],'expected':c['expected']} for c in cases])
write('metadata.jsonl',[{k:v for k,v in c.items() if k not in ['rule','question','message','expected']} for c in cases])
write('requests.jsonl',[{'id':c['id'],'request':{'model':'clef-flash','state':f"Fiktive Testregel:\n{c['rule']}\n\nSynthetische Anfrage und Unterlagen:\n{c['message']}\n\nZu beurteilende Eigenschaft:\n{c['question']}",'questions':Q}} for c in cases])
(R/'data/policy.json').write_text(json.dumps({'scope':'Synthetic closed-rule determination and clarification; no legal/financial advice','general_rule':POLICY,'questions':Q},ensure_ascii=False,indent=2)+'\n')
summary={'suite_id':'clarification','case_count':len(cases),'field_count':2,'family_count':len(F),'order_seed':202610021,'domain_counts':dict(Counter(c['domain'] for c in cases)),'stratum_counts':dict(Counter(c['stratum'] for c in cases)),'label_counts':{k:dict(Counter(c['expected'][k] for c in cases)) for k in Q},'purposeful_not_population_sample':True,'related_cases_share_rule_families':True,'not_expert_validated':True}
(R/'data/design_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,indent=2))
