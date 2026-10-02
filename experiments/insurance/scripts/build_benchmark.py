"""Author-owned synthetic German policy excerpts; no external policy text."""
from pathlib import Path
import json,random,itertools,hashlib,collections
P=Path(__file__).resolve().parents[1]
R=random.Random(202610021)
docs=[]; cases=[]
def doc(id,title,area,clauses):
    d={'id':id,'title':title,'area':area,'synthetic':True,'clauses':[{'id':k,'text':v} for k,v in clauses]}; docs.append(d); return d
def case(d,facts,claim,label,evidence,why):
    cases.append({'document_id':d['id'],'area':d['area'],'scenario':facts,'claim':claim,'expected':{'decision':label,'evidence_clauses':evidence.split(',')},'rationale':why})
A='Deckungsumfang und Definitionen'
d=doc('paket_01','Hausrat · Versicherte Sachen und Orte',A,[
('H1','Versichert sind bewegliche Sachen, die der versicherten Person gehören und ihrem privaten Haushalt dienen. Auch beruflich genutzte Arbeitsmittel sind versichert, soweit H2 sie einschließt.'),
('H2','Für berufliche Arbeitsmittel sind ausschließlich tragbare Computer und Bildschirme eingeschlossen. Warenbestände, Bargeld und Werkzeuge sind als berufliche Sachen nicht versichert.'),
('H3','Versicherungsort ist die im Schein genannte Wohnung einschließlich eines ausschließlich dieser Wohnung zugeordneten, abschließbaren Kellerraums. Gemeinschaftliche Abstellräume gehören nicht dazu.'),
('H4','Die Außenversicherung erfasst private Haushaltsgegenstände während vorübergehender Reisen. Ein dauerhafter Umzug gilt nicht als Reise. Berufliche Arbeitsmittel sind von der Außenversicherung ausgenommen.'),
('H5','Gegenstände fremder Personen sind nicht versichert. Abweichend davon sind privat geliehene Sachen eingeschlossen, wenn sie sich am Versicherungsort befinden.'),
('H6','Für die Einordnung einer Sache zählt die tatsächliche Nutzung am Schadentag, nicht die ursprüngliche Kaufabsicht.'),
('H7','Diese Auszüge regeln nur die versicherten Sachen und Orte. Ob eine bestimmte Schadenursache versichert ist, wird damit nicht festgestellt.')])
case(d,'Ein der versicherten Person gehörender Laptop wird ausschließlich beruflich genutzt und steht in der versicherten Wohnung.','Der Laptop gehört dort zu den versicherten Sachen.','ja','H1,H2','H1 öffnet berufliche Arbeitsmittel; H2 schließt tragbare Computer ein.')
case(d,'Eigene berufliche Werkzeuge befinden sich in der versicherten Wohnung.','Die Werkzeuge gehören zu den versicherten Sachen.','nein','H2','Berufliche Werkzeuge sind ausdrücklich nicht versichert.')
case(d,'Eigene privat genutzte Koffer liegen im gemeinschaftlichen Abstellraum des Wohnhauses.','Dieser Abstellraum gehört zum Versicherungsort.','nein','H3','Gemeinschaftlicher Abstellraum ist ausdrücklich ausgeschlossen.')
case(d,'Ein privat geliehener Fotoapparat befindet sich bei einem dauerhaften Umzug bereits in der neuen, nicht im Schein genannten Wohnung.','Der Fotoapparat ist nach der Fremdsachenregel H5 an diesem Ort eingeschlossen.','nein','H5','Einschluss privat geliehener Sachen setzt den Versicherungsort voraus; laut Sachverhalt liegt dieser nicht vor.')
case(d,'Eine eigene Kamera liegt in der versicherten Wohnung. Ihre tatsächliche Nutzung am Schadentag ist nicht dokumentiert.','Die Kamera ist als privat genutzte Sache einzuordnen.','offen','H6','Die maßgebliche tatsächliche Nutzung fehlt; Eigentum und Ort belegen sie nicht.')
d=doc('paket_02','Reise · Begriffe und versicherte Ereignisse',A,[
('R1','Versicherte Reise ist ein privater Aufenthalt außerhalb des gewöhnlichen Wohnorts, der vor Reisebeginn verbindlich gebucht wurde. Reine Geschäftsreisen sind nicht versichert.'),
('R2','Reiserücktritt liegt vor, wenn die versicherte Person vor dem ersten gebuchten Beförderungs- oder Unterkunftssegment vollständig auf die Reise verzichtet. Ein bloßer Abbruch nach Reisebeginn ist kein Rücktritt.'),
('R3','Reisebeginn ist der Antritt des ersten gebuchten Segments. Die Fahrt von zu Hause zum Flughafen zählt nicht dazu, sofern sie nicht selbst ein gebuchtes Segment ist.'),
('R4','Als versichertes Rücktrittsereignis gilt eine unerwartete schwere Erkrankung der versicherten Person oder einer Risikoperson. Andere Ereignisse sind durch diesen Auszug nicht eingeschlossen.'),
('R5','Risikopersonen sind Ehepartner, eingetragene Lebenspartner und minderjährige eigene Kinder. Freunde und Arbeitskollegen sind keine Risikopersonen.'),
('R6','Die bloße Sorge vor einer Erkrankung ist keine Erkrankung im Sinne von R4. Eine bestätigte Diagnose allein belegt noch nicht, dass die Erkrankung schwer und unerwartet war.'),
('R7','Dieser Auszug enthält keine Bestimmung über Leistungen bei Reiseabbruch.')])
case(d,'Eine privat gebuchte Reise beginnt laut Buchung mit dem Flug. Auf der ungebuchten Fahrt zum Flughafen wird vollständig auf die Reise verzichtet.','Es handelt sich um einen Rücktritt vor Reisebeginn im Sinne der Bedingungen.','ja','R2,R3','Der ungebuchte Zubringer ist noch kein Reisebeginn; vollständiger Verzicht erfüllt Rücktritt.')
case(d,'Der erste gebuchte Flug wurde angetreten. Am Ziel wird die restliche Reise abgebrochen.','Der Vorgang ist ein Reiserücktritt im Sinne der Bedingungen.','nein','R2,R3','Das erste Segment wurde angetreten; danach liegt kein Rücktritt vor.')
case(d,'Ein Arbeitskollege erkrankt unerwartet schwer. Ausschließlich deshalb sagt die versicherte Person die Reise ab.','Die Erkrankung dieses Kollegen ist ein in R4 eingeschlossenes Ereignis.','nein','R4,R5','R4 erfasst nur versicherte Person oder Risikoperson, Kollegen sind keine.')
case(d,'Der Ehepartner erkrankt nachweislich unerwartet schwer. Die privat gebuchte Reise wird noch vor Beginn vollständig storniert.','Die Erkrankung des Ehepartners zählt zu den in R4 eingeschlossenen Rücktrittsereignissen.','ja','R4,R5','Ehepartner sind Risikopersonen; Erkrankungsmerkmale stehen fest.')
case(d,'Für die versicherte Person liegt eine Diagnose vor. Angaben zu Schwere und Unerwartetheit fehlen.','Ein versichertes Rücktrittsereignis nach R4 ist belegt.','offen','R4,R6','Diagnose genügt ausdrücklich nicht für die fehlenden Merkmale.')
A='Ausschlüsse und Rückausnahmen'
d=doc('paket_03','Privathaftpflicht · Geliehene Sachen',A,[
('L1','Der Grundschutz erfasst gesetzliche Haftpflicht wegen fahrlässig verursachter Sachschäden im privaten Alltag, soweit kein Ausschluss greift.'),
('L2','Schäden an gemieteten, geliehenen oder zur Verwahrung übernommenen beweglichen Sachen sind ausgeschlossen.'),
('L3','Abweichend von L2 sind Schäden an privat geliehenen Musikinstrumenten eingeschlossen. Dieser Einschluss gilt nicht für berufliche Nutzung oder für den Verlust der Sache.'),
('L4','Schäden an Kraftfahrzeugen bleiben auch dann ausgeschlossen, wenn eine andere Bestimmung geliehene Sachen einschließt.'),
('L5','Vorsätzlich herbeigeführte Schäden sind ausgeschlossen. Ein absichtliches Benutzen einer Sache ist für sich allein keine vorsätzliche Herbeiführung des Schadens.'),
('L6','Der bloße Umstand, dass ein Gegenstand einem Freund gehört, beweist keine Leihe; eine Leihe setzt die vereinbarte zeitweise Überlassung zur Nutzung voraus.'),
('L7','Die folgenden Aussagen sind ausschließlich auf die jeweilige ausdrücklich benannte Ausschlussregel zu beziehen; weitere Voraussetzungen werden hierdurch nicht ersetzt.')])
case(d,'Eine privat geliehene Geige wird bei privatem Spielen fahrlässig beschädigt; sie geht nicht verloren.','Der Ausschluss für geliehene Sachen L2 greift wegen L3 für diesen Schaden nicht.','ja','L2,L3','Die Rückausnahme erfasst privat geliehenes Musikinstrument ohne Verlust.')
case(d,'Eine privat geliehene Geige wird bei einem bezahlten beruflichen Konzert fahrlässig beschädigt.','L3 hebt den Ausschluss L2 für diesen Schaden auf.','nein','L2,L3','Die berufliche Nutzung ist von der Rückausnahme ausgenommen.')
case(d,'Ein privat geliehenes Musikinstrument wird verloren und nicht beschädigt.','Der Verlust ist durch die Rückausnahme L3 eingeschlossen.','nein','L3','L3 gilt ausdrücklich nicht für Verlust.')
case(d,'Die versicherte Person spielt absichtlich Klavier, beschädigt es dabei aber nachweislich nur fahrlässig.','Allein das absichtliche Spielen löst den Vorsatzausschluss L5 aus.','nein','L5','Absichtliches Benutzen ist nicht gleich absichtliches Schädigen.')
case(d,'Ein Freund besitzt die beschädigte Kamera. Ob sie zur Nutzung überlassen wurde, ist nicht dokumentiert.','Die Kamera ist als geliehene Sache im Sinne von L2 einzuordnen.','offen','L2,L6','Fremdes Eigentum genügt nicht; Vereinbarung über Überlassung fehlt.')
d=doc('paket_04','Gebäude · Wasser und Frost',A,[
('W1','Versichert sind Schäden durch bestimmungswidrig ausgetretenes Leitungswasser aus fest verlegten Trinkwasserleitungen oder angeschlossenen Haushaltsgeräten.'),
('W2','Niederschlagswasser und aufsteigendes Grundwasser sind vom Leitungswasserschutz ausgeschlossen, auch wenn sie durch eine beschädigte Gebäudestelle eindringen.'),
('W3','Frostbedingte Brüche an fest verlegten Trinkwasserleitungen sind eingeschlossen. Frostschäden an mobilen Gartenschläuchen sind nicht eingeschlossen.'),
('W4','Schimmel ist grundsätzlich ausgeschlossen. Abweichend davon ist er eingeschlossen, wenn er unmittelbare Folge eines nach W1 versicherten Leitungswasserschadens ist und kein anderer selbstständiger Schimmelauslöser vorliegt.'),
('W5','Bei mehreren Ursachen genügt für die Rückausnahme W4 nicht, dass Leitungswasser lediglich eine mögliche Ursache ist. Die unmittelbare Folge und das Fehlen eines anderen selbstständigen Auslösers müssen feststehen.'),
('W6','Schäden durch planmäßig zur Reinigung ausgeschüttetes Wasser gelten nicht als bestimmungswidriger Austritt aus einer Leitung oder einem Gerät.'),
('W7','Die Bezeichnung Wasserschaden in einer Meldung legt die Herkunft des Wassers nicht fest.')])
case(d,'Regen dringt durch ein vom Sturm geöffnetes Dach ein. Es tritt kein Wasser aus Leitungen oder Geräten aus.','Der Schaden fällt unter den Leitungswasserschutz W1.','nein','W1,W2','Niederschlagswasser bleibt ausgeschlossen, auch durch beschädigtes Dach.')
case(d,'Eine fest verlegte Trinkwasserleitung bricht nachweislich durch Frost.','Der Rohrbruch ist nach W3 eingeschlossen.','ja','W3','W3 erfasst gerade diesen frostbedingten Leitungsbruch.')
case(d,'Nach einem versicherten Leitungswasseraustritt entsteht unmittelbar Schimmel. Ein anderer selbstständiger Auslöser ist nachweislich nicht vorhanden.','Die Rückausnahme vom Schimmelausschluss ist erfüllt.','ja','W4','Beide ausdrücklich verlangten Voraussetzungen stehen fest.')
case(d,'Es gibt Schimmel; als Ursachen kommen ein früherer Leitungswasserschaden und bauliche Feuchte in Betracht. Die Ursache ist ungeklärt.','Die Rückausnahme W4 ist sachlich anwendbar.','offen','W4,W5','Ungeklärte Ursache lässt keine Feststellung zu; mögliches Leitungswasser allein reicht nicht.')
case(d,'In der Schadenmeldung steht nur Wasserschaden. Über Herkunft oder Austrittsort gibt es keine Angaben.','Der Schaden erfüllt die Wasseraustrittsdefinition W1.','offen','W1,W7','Der Meldungstitel belegt keine erforderliche Herkunft.')
A='Voraussetzungen und Obliegenheiten'
d=doc('paket_05','Fahrrad · Sicherungsvoraussetzungen',A,[
('F1','Ein einfacher Diebstahl des Fahrrads außerhalb der Wohnung ist genau dann eingeschlossen, wenn das Rad im Schadentatbestand nach F2 gesichert war. Einbruchdiebstahl aus der Wohnung wird hier nicht geregelt.'),
('F2','Das Fahrrad muss mit einem eigenständigen Schloss an einen ortsfesten Gegenstand angeschlossen sein. Ein reines Rahmenschloss oder ein lediglich durch das Rad geführtes loses Schloss genügt nicht.'),
('F3','Innerhalb eines abgeschlossenen, ausschließlich vom Versicherungsnehmer genutzten Fahrradkellers entfällt das Anschließen an einen ortsfesten Gegenstand. Ein eigenständiges verschlossenes Schloss am Rad bleibt erforderlich.'),
('F4','Ein gemeinschaftlicher Fahrradkeller fällt nicht unter F3, auch wenn seine Tür abgeschlossen ist.'),
('F5','Die Sicherungsregeln F2 bis F4 gelten zu jeder Tageszeit. Aus nächtlichem Abstellen allein folgt kein zusätzlicher Ausschluss.'),
('F6','Für den Einschluss nach F1 sind außer der Sicherung keine weiteren Voraussetzungen in diesem Dokument geregelt.'),
('F7','Ein Kaufbeleg weist das Eigentum nach, nicht die Sicherung am Schadenort.')])
case(d,'Ein Rad wird nachts außerhalb der Wohnung gestohlen. Es war mit einem eigenständigen Schloss an einem fest eingebauten Bügel angeschlossen.','Der einfache Diebstahl ist nach F1 eingeschlossen.','ja','F1,F2,F5','Sicherung erfüllt; Nacht ändert dies nicht.')
case(d,'Ein Rad steht in einem abgeschlossenen gemeinschaftlichen Keller. Ein eigenständiges Schloss blockiert das Rad, ist aber nirgends angeschlossen.','Die Sicherung erfüllt die Bedingungen durch die Keller-Ausnahme.','nein','F2,F3,F4','Gemeinschaftskeller ist keine Ausnahme; ortsfeste Verbindung fehlt.')
case(d,'Das Rad steht im abgeschlossenen, ausschließlich vom Versicherungsnehmer genutzten Fahrradkeller. Ein eigenständiges geschlossenes Schloss sichert das Rad ohne ortsfeste Verbindung.','Die Sicherung genügt nach den Bedingungen.','ja','F2,F3','Privatkeller-Ausnahme beseitigt Anschließpflicht, eigenes Schloss bleibt erfüllt.')
case(d,'Draußen wird ein Rad nur mit dem eingebauten Rahmenschloss verschlossen.','Die Sicherungsvoraussetzung F2 ist erfüllt.','nein','F2','Rahmenschloss allein ist ausdrücklich ungenügend.')
case(d,'Der Kaufbeleg ist vorhanden. Wo und wie das Rad beim Diebstahl gesichert war, ist unbekannt.','Die Sicherungsvoraussetzung für den Einschluss nach F1 war erfüllt.','offen','F1,F7','Kaufbeleg kann fehlende Sicherungsangaben nicht ersetzen.')
d=doc('paket_06','Schadenverfahren · Meldung und Folgen',A,[
('O1','Ein Schaden soll unverzüglich nach seiner Entdeckung gemeldet werden. Die verspätete Meldung führt nicht automatisch zum Verlust des Leistungsanspruchs.'),
('O2','Eine vollständige Leistungsablehnung wegen verspäteter Meldung ist nach diesen Bedingungen genau dann zulässig, wenn die Verspätung vorsätzlich war und die Feststellung des Versicherungsfalls tatsächlich erschwert hat.'),
('O3','Bei nur fahrlässiger Verspätung ist eine vollständige Ablehnung aus diesem Grund nicht zulässig. Eine andere Leistungsfolge wird hier nicht geregelt.'),
('O4','Notwendige Sofortmaßnahmen zur Abwendung größerer Schäden dürfen vor Rücksprache erfolgen. Ihr Umfang soll soweit möglich dokumentiert werden.'),
('O5','Nicht dringende Reparaturen dürfen erst nach Freigabe beauftragt werden. Ein Kostenvoranschlag ist noch kein Reparaturauftrag.'),
('O6','Eine Freigabe zur Besichtigung ist keine Freigabe zur Reparatur. Eine Freigabe zur Reparatur ist keine Zusage der Kostenerstattung.'),
('O7','Ob der Schaden dem Grunde nach versichert ist, wird unabhängig von den hier beschriebenen Verfahrensschritten geprüft.')])
case(d,'Ein Schaden wurde verspätet gemeldet. Weitere Angaben zu Verschulden und Folgen der Verzögerung liegen nicht vor.','Eine vollständige Ablehnung wegen der verspäteten Meldung ist nach O2 zulässig.','offen','O1,O2','Verspätung allein reicht nicht; beide Ablehnungsvoraussetzungen sind unbekannt.')
case(d,'Die Meldung war vorsätzlich verspätet. Die Feststellung des Versicherungsfalls wurde dadurch nachweislich nicht erschwert.','O2 erlaubt die vollständige Ablehnung wegen der Verspätung.','nein','O2','Kumulative Voraussetzung der tatsächlichen Erschwerung fehlt.')
case(d,'Die Verspätung war nachweislich vorsätzlich und hat die Feststellung des Versicherungsfalls tatsächlich erschwert.','O2 erlaubt eine vollständige Ablehnung wegen dieser Verspätung.','ja','O2','Beide kumulativen Bedingungen sind erfüllt.')
case(d,'Eine undichte Leitung muss sofort abgestellt werden, um weiteren Wasseraustritt zu verhindern. Die Maßnahme ist notwendig; Rücksprache ist noch nicht erfolgt.','Die notwendige Sofortmaßnahme darf bereits durchgeführt werden.','ja','O4','Notwendige Schadensabwendung ist vor Rücksprache erlaubt.')
case(d,'Der Versicherer hat schriftlich eine Besichtigung freigegeben, aber nichts zur Reparatur erklärt. Es besteht keine Dringlichkeit.','Eine nicht dringende Reparatur darf auf Grundlage dieser Freigabe beauftragt werden.','nein','O5,O6','Besichtigung ist keine erforderliche Reparaturfreigabe.')
A='Nachweise und Verfahrensstatus'
d=doc('paket_07','Hausrat · Nachweisalternativen',A,[
('N1','Für den Eigentumsnachweis genügt entweder eine auf die versicherte Person ausgestellte Rechnung oder gemeinsam ein Foto des Gegenstands und ein zugehöriger, eindeutig zuordenbarer Kontoauszug. Andere Nachweiswege sind in diesem Paket nicht vereinbart.'),
('N2','Bei Diebstahl ist zusätzlich eine polizeiliche Anzeigenbestätigung erforderlich. Sie ersetzt den Eigentumsnachweis nicht.'),
('N3','Für den Nachweis der Beschädigung genügt ein aussagekräftiges Schadenfoto oder ein Reparaturbericht, der den Gegenstand eindeutig bezeichnet. Beide Dokumente müssen nicht gleichzeitig vorliegen.'),
('N4','Bei Verlust ohne Beschädigung ist N3 nicht anzuwenden. Diebstahl und Verlust sind für die Anzeigenpflicht N2 nicht gleichgestellt.'),
('N5','Eine Zahlungsbestätigung ohne Bezeichnung oder Zuordnung des gekauften Gegenstands ist kein zugehöriger Kontoauszug im Sinne von N1.'),
('N6','Die Vollständigkeit der Unterlagen ist keine Anerkennung der Deckung oder der geforderten Schadenhöhe.'),
('N7','Eine Nachforderung muss benennen, welcher der vereinbarten Nachweise fehlt; sie darf nicht aus einer Oder-Verknüpfung eine Pflicht zu beiden Alternativen machen.')])
case(d,'Bei einem Beschädigungsschaden liegen eine Rechnung auf die versicherte Person und ein eindeutiger Reparaturbericht vor; ein Schadenfoto fehlt.','Die Nachweise für Eigentum und Beschädigung sind nach N1 und N3 vollständig.','ja','N1,N3','Rechnung erfüllt Eigentum, Reparaturbericht die alternative Beschädigungsdokumentation.')
case(d,'Nach einem Diebstahl liegen nur ein Foto des Gegenstands und eine polizeiliche Anzeigenbestätigung vor. Es gibt weder Rechnung noch zuordenbaren Kontoauszug.','Eigentumsnachweis und zusätzlicher Diebstahlnachweis sind vollständig.','nein','N1,N2','Foto allein erfüllt N1 nicht; Polizeibestätigung ersetzt es nicht.')
case(d,'Ein Foto des Gegenstands und ein eindeutig zugehöriger Kontoauszug liegen vor; eine Rechnung fehlt.','Der Eigentumsnachweis nach N1 ist vollständig.','ja','N1','Die zweite Nachweisalternative ist vollständig.')
case(d,'Die Unterlagen sind formal vollständig. Eine Prüfung der Deckung oder Schadenhöhe ist noch nicht erfolgt.','Mit der Vollständigkeit ist die Deckung anerkannt.','nein','N6','Vollständigkeit ist ausdrücklich keine Deckungsanerkennung.')
case(d,'Es liegt ein Foto und ein Kontoauszug vor. Ob der Kontoauszug dem Gegenstand eindeutig zuzuordnen ist, geht aus der Akte nicht hervor.','Der alternative Eigentumsnachweis nach N1 ist vollständig.','offen','N1,N5','Eindeutige Zuordnung ist erforderlich, aber unbekannt.')
d=doc('paket_08','Leistungsprüfung · Medizinische Bescheinigung',A,[
('M1','Für den vertraglichen Nachweis einer Reiseunfähigkeit ist eine ärztliche Bescheinigung erforderlich, die die versicherte Person, den Untersuchungszeitpunkt und eine konkrete Reiseunfähigkeit für die gebuchte Reise bestätigt.'),
('M2','Eine Arbeitsunfähigkeitsbescheinigung ohne Aussage zur konkreten Reise ersetzt den Nachweis nach M1 nicht.'),
('M3','Die Diagnose muss in dieser Bescheinigung nicht genannt werden. Das Fehlen der Diagnose ist allein kein formaler Mangel.'),
('M4','Ein Attest kann digital eingereicht werden. Ein Original auf Papier ist nur erforderlich, wenn seine Vorlage unter Angabe eines konkreten Echtheitszweifels ausdrücklich angefordert wurde.'),
('M5','Ein Eingangshinweis des Portals bestätigt nur den Empfang. Er bestätigt weder die formale Vollständigkeit noch die materielle Berechtigung des Anspruchs.'),
('M6','Eine Bescheinigung nach M1 betrifft allein den Nachweis der Reiseunfähigkeit. Ob ein versichertes Ereignis und alle übrigen Leistungsvoraussetzungen vorliegen, wird gesondert geprüft.'),
('M7','Ein Ausstellungsdatum ist kein ausdrücklich benannter Untersuchungszeitpunkt, wenn die Bescheinigung beides nicht gleichsetzt.')])
case(d,'Eine digitale ärztliche Bescheinigung nennt Person, Untersuchungszeitpunkt und konkrete Reiseunfähigkeit für die gebuchte Reise. Die Diagnose fehlt; ein Papieroriginal wurde nicht angefordert.','Das fehlende Diagnosefeld macht den Nachweis formal unzureichend.','nein','M3','Diagnose ist nicht erforderlich und fehlt nur als einzelnes betrachtetes Merkmal.')
case(d,'Eingereicht ist ausschließlich eine Arbeitsunfähigkeitsbescheinigung ohne Reisebezug.','Der Nachweis der Reiseunfähigkeit nach M1 liegt vor.','nein','M1,M2','Arbeitsunfähigkeit ohne Reisebezug ersetzt die verlangte Bescheinigung nicht.')
case(d,'Ein inhaltlich vollständiges Attest liegt digital vor. Es gab keine Anforderung eines Papieroriginals.','Für diesen Nachweis muss zusätzlich ein Papieroriginal eingereicht werden.','nein','M4','Papieroriginal nur nach qualifizierter Anforderung.')
case(d,'Das Portal bestätigt nur den Eingang der ärztlichen Bescheinigung. Sonstige Prüfergebnisse fehlen.','Die Bescheinigung ist formal vollständig.','offen','M5','Eingangsstatus lässt Vollständigkeit offen; kein positiver oder negativer Prüfbefund.')
case(d,'Eine ärztliche Bescheinigung nennt Person, ausdrücklichen Untersuchungszeitpunkt und konkrete Reiseunfähigkeit für die gebuchte Reise.','Der in M1 beschriebene Nachweis ist inhaltlich vollständig.','ja','M1','Alle drei vertraglich verlangten Angaben sind vorhanden.')
A='Nachträge und Dokumentvorrang'
d=doc('paket_09','Elektronik · Vertrag und Nachtrag',A,[
('V1','Rangfolge: Ein zum Schadentag wirksamer individueller Nachtrag geht dem Versicherungsschein und den allgemeinen Bedingungen vor. Der Schein geht den allgemeinen Bedingungen vor. Broschüren ändern den Vertrag nicht.'),
('V2','Allgemeine Bedingungen, Fassung A: Beschädigungen durch versehentliches Fallenlassen tragbarer Computer sind nicht versichert.'),
('V3','Versicherungsschein: Versicherte Geräte sind die im Verzeichnis genannten tragbaren Computer. Das Verzeichnis enthält Gerät Delta.'),
('V4','Individueller Nachtrag, gültig ab 1. Juli 2026: Für Gerät Delta sind versehentliche Sturzschäden eingeschlossen. Für andere Geräte bleibt der Ausschluss unverändert.'),
('V5','Broschüre, Ausgabe August 2026: Unser Geräteschutz begleitet alle Ihre Computer auch bei Missgeschicken.'),
('V6','Der Nachtrag wirkt nicht rückwirkend; maßgeblich ist der Schadentag, nicht der Meldetag.'),
('V7','Weitere Änderungen sind in diesem vollständigen Paket nicht enthalten.')])
case(d,'Gerät Delta wird am 10. August 2026 durch versehentliches Fallenlassen beschädigt.','Dieser Sturzschaden ist trotz V2 eingeschlossen.','ja','V1,V2,V4','Wirksamer individueller Nachtrag geht dem allgemeinen Ausschluss vor.')
case(d,'Gerät Delta fällt am 15. Juni 2026 herunter; der Schaden wird erst im August gemeldet.','Der Nachtrag V4 schließt diesen Sturzschaden ein.','nein','V4,V6','Schaden vor Geltungsbeginn; Meldetag macht Nachtrag nicht rückwirkend.')
case(d,'Ein anderes tragbares Gerät als Delta fällt am 10. August 2026 versehentlich herunter.','V4 hebt den Sturzausschluss für dieses andere Gerät auf.','nein','V4','Der Nachtrag beschränkt sich auf Delta und lässt andere Ausschlüsse unverändert.')
case(d,'Es wird nur die aktuelle Broschüre V5 als Argument für die Erweiterung des Vertrags angeführt.','Die Broschüre kann nach der vereinbarten Rangfolge den vertraglichen Ausschluss ändern.','nein','V1','Broschüren ändern den Vertrag ausdrücklich nicht.')
case(d,'Gerät Delta wurde versehentlich fallen gelassen. Der Schadentag ist nicht bekannt; die Meldung erfolgt im August 2026.','Der Schaden fällt unter den zeitlich wirksamen Einschluss V4.','offen','V4,V6','Wirksamkeit hängt vom unbekannten Schadentag ab, nicht vom Meldetag.')
d=doc('paket_10','Wohngebäude · Geltung mehrerer Nachträge',A,[
('Z1','Individuelle Nachträge gehen allgemeinen Bedingungen vor. Eine spätere Unterzeichnung verdrängt frühere Nachträge nur, wenn der spätere Text die ersetzte Regel ausdrücklich nennt. Gleiche Rangstufe ohne solche Auflösung wird nicht durch das Dateidatum entschieden.'),
('Z2','Allgemeine Bedingungen: Überschwemmungsschäden sind nicht versichert.'),
('Z3','Nachtrag Alpha, von beiden Parteien unterzeichnet und für den ganzen Prüfzeitraum wirksam: Überschwemmungsschäden am Wohngebäude sind eingeschlossen.'),
('Z4','Nachtrag Beta, ebenfalls unterzeichnet und für denselben Prüfzeitraum wirksam: Überschwemmungsschäden am Wohngebäude sind ausgeschlossen. Beta enthält keine Aufhebung von Alpha.'),
('Z5','Nachtrag Gamma, für den ganzen Prüfzeitraum wirksam: Für Schäden an der Garage ersetzt Gamma die Regel aus Beta; Überschwemmungsschäden an der Garage sind eingeschlossen. Gamma trifft keine Regel über das Wohngebäude.'),
('Z6','Der Anhang Entwurf Delta wurde von keiner Partei unterzeichnet und ist als unverbindlicher Verhandlungsvorschlag gekennzeichnet; er erweitert keinen Schutz.'),
('Z7','Wohngebäude und Garage sind in diesem Paket getrennte versicherte Objekte. Aussagen über eines gelten nicht automatisch für das andere.')])
case(d,'Eine Überschwemmung beschädigt das Wohngebäude im gemeinsamen Geltungszeitraum von Alpha und Beta.','Überschwemmungsschäden am Wohngebäude sind eingeschlossen.','konflikt','Z1,Z3,Z4','Gleichrangige wirksame Nachträge widersprechen sich ohne vertragliche Auflösung.')
case(d,'Die Garage wird durch Überschwemmung beschädigt. Gamma ist wirksam.','Überschwemmungsschäden an der Garage sind nach Gamma eingeschlossen.','ja','Z5','Gamma enthält einen ausdrücklich auf die Garage bezogenen Einschluss.')
case(d,'Beta wurde später als Alpha unterzeichnet, enthält aber keine ausdrückliche Ersetzung von Alpha.','Allein die spätere Unterzeichnung löst den Widerspruch zugunsten von Beta auf.','nein','Z1','Spätere Unterzeichnung allein genügt nach der speziellen Rangfolgeregel nicht.')
case(d,'Ein nicht unterzeichneter Entwurf Delta sieht zusätzlichen Schutz vor.','Dieser Entwurf erweitert bereits den verbindlichen Versicherungsschutz.','nein','Z6','Der Anhang ist ausdrücklich unverbindlich.')
case(d,'Gamma hat für die Garage die Regel aus Beta ersetzt. Am Wohngebäude entsteht ein Überschwemmungsschaden.','Der Widerspruch zwischen Alpha und Beta über das Wohngebäude ist durch Gamma zugunsten eines Einschlusses aufgelöst.','nein','Z5,Z7','Gamma betrifft nur die getrennte Garage und löst den Wohngebäudekonflikt nicht.')
A='Unvollständige und widersprüchliche Akten'
d=doc('paket_11','Gewerbe · Fehlende Vertragsangaben',A,[
('U1','Versichert ist nur die Betriebsstätte, deren Anschrift im verbindlichen Versicherungsschein genannt ist. Eine Angebotsanschrift beweist den vereinbarten Versicherungsort nicht.'),
('U2','Die Akte enthält ein Angebot für Standort Nord, aber keinen Versicherungsschein und keine bestätigte Annahme dieses Angebots.'),
('U3','Elektronikschutz besteht nur, wenn der Baustein im Versicherungsschein ausdrücklich als aktiv ausgewiesen ist. In dieser Akte fehlt eine solche Ausweisung ebenso wie eine verbindliche Deaktivierung.'),
('U4','Ein Beratungsvermerk empfiehlt Elektronikschutz. Eine Empfehlung aktiviert den Baustein nicht.'),
('U5','Schäden aus vorsätzlicher Herbeiführung durch den Versicherungsnehmer sind ausgeschlossen; fahrlässige Herbeiführung fällt nicht unter diesen Ausschluss.'),
('U6','Die Schadenaufnahme beschreibt das Geschehen, enthält aber keine Feststellung dazu, ob der Versicherungsnehmer vorsätzlich oder fahrlässig handelte.'),
('U7','Fehlende Dokumente dürfen nicht als Beleg für den gegenteiligen Vertragsinhalt gewertet werden. Ein Angebotsstatus ist weder Deckungszusage noch verbindliche Ablehnung.')])
case(d,'Ein Schaden tritt am Standort Nord ein. Es liegen ausschließlich die in U2 genannten Unterlagen vor.','Standort Nord ist der verbindlich vereinbarte Versicherungsort.','offen','U1,U2','Angebot ohne Schein oder Annahme belegt keine vereinbarte Adresse.')
case(d,'Zu Elektronikschutz sind nur die in U3 und U4 beschriebenen Informationen vorhanden.','Der Elektronikbaustein ist verbindlich aktiv.','offen','U3,U4','Empfehlung genügt nicht; verbindliche Ausweisung fehlt ohne Gegenbeweis.')
case(d,'Aus dem fehlenden Versicherungsschein wird geschlossen, es gebe verbindlich keinen Elektronikschutz.','Das Fehlen des Scheins beweist die verbindliche Deaktivierung des Elektronikbausteins.','nein','U3,U7','Fehlen beweist ausdrücklich keinen gegenteiligen Vertragsinhalt.')
case(d,'Die Angaben zum Verschulden entsprechen ausschließlich U6.','Der Vorsatzausschluss U5 greift.','offen','U5,U6','Der für den Ausschluss nötige Vorsatz ist weder belegt noch widerlegt.')
case(d,'Die Schadenursache wurde nun eindeutig als fahrlässiges Handeln des Versicherungsnehmers festgestellt.','Dieser Schaden fällt unter den Vorsatzausschluss U5.','nein','U5','Fahrlässigkeit ist ausdrücklich nicht vom Vorsatzausschluss erfasst.')
d=doc('paket_12','Reiseschutz · Widersprüchliche Bestätigungen',A,[
('K1','Für den Prüfzeitraum liegen zwei von beiden Parteien unterzeichnete Vertragsbestätigungen gleicher Rangstufe vor. Keine ist als Ersatz der anderen bezeichnet. Es existiert keine vereinbarte Regel, die eine davon vorzieht.'),
('K2','Bestätigung Epsilon: Der Schutz gilt weltweit einschließlich Kanada. Reine Geschäftsreisen sind eingeschlossen.'),
('K3','Bestätigung Zeta: Kanada ist vom räumlichen Geltungsbereich ausgeschlossen. Reine Geschäftsreisen sind ausgeschlossen.'),
('K4','Beide Bestätigungen stimmen darin überein, dass private Reisen nach Portugal räumlich eingeschlossen sind.'),
('K5','Die Informationskarte ist unverbindlich und nennt nur Europa. Sie hat keinen Vorrang vor einer unterzeichneten Bestätigung.'),
('K6','Die eingereichte Buchung ist eine Reise nach Kanada. Ob sie privat oder geschäftlich ist, ist in der Buchung nicht angegeben.'),
('K7','Keine Unterlage regelt, ob Wintersport als Tätigkeit eingeschlossen oder ausgeschlossen ist. Aus dem räumlichen Geltungsbereich allein lässt sich keine Tätigkeitsdeckung ableiten.')])
case(d,'Für eine Reise nach Kanada sind beide Bestätigungen wirksam und gleichrangig. Gefragt ist ausschließlich der räumliche Schutz.','Kanada liegt im vereinbarten räumlichen Geltungsbereich.','konflikt','K1,K2,K3','Epsilon schließt Kanada ein, Zeta aus; kein Vorrang.')
case(d,'Eine Reise ist nachweislich rein geschäftlich. Beide Bestätigungen sind wirksam und gleichrangig. Gefragt ist nur der Reisezweck.','Reine Geschäftsreisen sind eingeschlossen.','konflikt','K1,K2,K3','Gleichrangige Dokumente geben entgegengesetzte Zweckdeckung an.')
case(d,'Eine private Reise führt nach Portugal. Gefragt ist ausschließlich der räumliche Schutz, keine bestimmte Tätigkeit.','Portugal liegt im räumlichen Geltungsbereich.','ja','K4','Hier stimmen die beiden Bestätigungen ausdrücklich überein.')
case(d,'Eine private Reise nach Portugal enthält Wintersport. Gefragt ist ausschließlich die Deckung der Tätigkeit Wintersport.','Wintersport ist als Tätigkeit eingeschlossen.','offen','K7','Keine Tätigkeitsregel vorhanden; räumliche Deckung ersetzt sie nicht.')
case(d,'Die unterzeichneten Bestätigungen widersprechen sich für Kanada. Die unverbindliche Informationskarte nennt nur Europa.','Die Informationskarte löst den Vertragswiderspruch verbindlich zugunsten des Ausschlusses von Kanada auf.','nein','K5','Informationskarte ist unverbindlich und ohne Vorrang.')

# Opaque IDs, seeded option ordering and seeded request order; no labels in inference records.
criteria={
'ja':'Die Aussage ist durch die maßgeblichen Unterlagen und den Sachverhalt gestützt.',
'nein':'Die Aussage wird durch die maßgeblichen Unterlagen und den Sachverhalt widerlegt.',
'offen':'Weder Aussage noch Gegenteil sind entscheidbar: notwendige Information fehlt; kein unaufgelöster maßgeblicher Regelwiderspruch.',
'konflikt':'Die für diese Aussage maßgeblichen Unterlagen widersprechen sich ausdrücklich und der Widerspruch ist durch keinen vereinbarten Vorrang auflösbar.'}
R.shuffle(cases)
for i,c in enumerate(cases,1):
 c['id']=f'fall_{i:03d}'
 # Pre-inference corrections from independent full-case audit. No model has seen cases.
 minimal={2:'F3',3:'H2',5:'U7',6:'V1,V4',8:'L6',10:'F4',11:'N1',18:'W1',19:'R4',29:'Z5',30:'N1',31:'F2',35:'L3',37:'W2',38:'W4',47:'U3',48:'F1,F2',52:'R2',53:'L3',54:'O2',56:'H3,H5',58:'M2',59:'R2'}
 if i in minimal:c['expected']['evidence_clauses']=minimal[i].split(',')
 if i==19:
  c['claim']='Die Erkrankung erfüllt die in R4 geforderten Ereignismerkmale.'
  c['rationale']='Ob die diagnostizierte Erkrankung schwer und unerwartet ist, bleibt unbekannt; R4 verlangt beides.'
 if i==31:
  c['scenario']='Ein Fahrrad wurde außerhalb der Wohnung gestohlen. Ein Kaufbeleg ist vorhanden; wie es am Schadenort gesichert war, ist unbekannt.'
  c['claim']='Die Sicherungsvoraussetzung F2 war am Schadenort erfüllt.'
  c['rationale']='F2 verlangt eine bestimmte Sicherung; die tatsächliche Sicherung ist unbekannt.'
 if i==38:
  c['claim']='Der Schimmel ist unmittelbare Folge eines nach W1 versicherten Leitungswasserschadens und hat keinen anderen selbstständigen Auslöser.'
  c['rationale']='Die tatsächlichen Ursachen sind ungeklärt; weder beide Voraussetzungen aus W4 noch ihr Gegenteil sind feststellbar.'
 c['tags']=['date_version_application'] if i in (6,28,33) else []
 d=next(x for x in docs if x['id']==c['document_id'])
 ids=[x['id'] for x in d['clauses']]; g=tuple(sorted(c['expected']['evidence_clauses']))
 # Do not offer another sufficient proof under a different option ID.
 # These alternative minimal proofs were identified independently before inference.
 alternative={5:[['U3']],10:[['F2'],['F3']],18:[['W7']],19:[['R6']],24:[['M1']],28:[['V4']],30:[['N5']],31:[['F7']],33:[['V4']],37:[['W1']],38:[['W5']],46:[['K2']],51:[['O5']],54:[['O1']],55:[['U2']],58:[['M1']]}
 sufficient=[set(g)]+[set(x) for x in alternative.get(i,[])]
 combos=[tuple(x) for x in itertools.combinations(ids,len(g)) if not any(proof.issubset(set(x)) for proof in sufficient)]
 assert len(combos)>=4, (i,g,combos)
 R.shuffle(combos);sets=[g]+combos[:4];R.shuffle(sets)
 c['evidence_options']={f'b{j+1}':list(s) for j,s in enumerate(sets)}
 c['expected']['evidence']=next(k for k,v in c['evidence_options'].items() if tuple(sorted(v))==g)
 keys=list(criteria);R.shuffle(keys)
 c['decision_options']={k:criteria[k] for k in keys}
 c['request']={'model':'clef-flash','state':{
  'hinweis':'SYNTHETISCHE Versicherungsunterlagen und fiktiver Fall. Keine reale Police. Beurteile nur den gegebenen Text; ergänze kein externes Recht und keine üblichen Bedingungen. Alle Sachverhaltsangaben gelten als wahr. Fehlende Informationen sind nicht automatisch falsch.',
  'unterlagen':[{'klausel':x['id'],'text':x['text']} for x in d['clauses']],
  'sachverhalt':c['scenario'],'zu_pruefende_aussage':c['claim']},
 'questions':{
  'decision':{'type':'choice','instructions':'Wie ist ausschließlich die zu prüfende Aussage nach Unterlagen und Sachverhalt einzuordnen? Beachte einen dokumentierten Vorrang, bevor du einen Konflikt annimmst. Ein Konflikt an anderer Stelle macht diese Aussage nicht widersprüchlich.','criteria':c['decision_options']},
  'evidence':{'type':'choice','instructions':'Welche der folgenden Klauselmengen trägt die Entscheidung vollständig und unmittelbar? Wähle die vollständige Belegmenge, auch wenn die Entscheidung offen oder konflikt lautet. Beziehe den Sachverhalt ein; keine externen Annahmen.','criteria':{k:', '.join(v) for k,v in c['evidence_options'].items()}}}}
assert len(cases)==60 and len(docs)==12
assert collections.Counter(c['area'] for c in cases)=={a:10 for a in set(c['area'] for c in cases)}
meta={'name':'Clef Versicherungsverständnis 60','version':'1.0.0','language':'de','synthetic':True,'source':'Newly authored synthetic German insurance excerpts and fictitious scenarios; no real insurer policy reproduced.','areas':list(dict.fromkeys(d['area'] for d in docs)),'case_count':60,'document_count':12,'cases_per_document':5,'fields':['decision','evidence'],'seed':202610021,'limitations':['Purposive synthetic challenge set, not a random production sample.','Five cases share each document; cases and decisions are correlated.','No real legal interpretation, full policy PDFs, OCR, retrieval, arithmetic, generation, robustness or calibration test.','Evidence selection tests offered clause sets, not free-form citation generation.','Three conflict cases; small per-class samples.']}
bench={'metadata':meta,'documents':docs,'cases':[{k:v for k,v in c.items() if k!='request'} for c in cases]}
(P/'benchmark/benchmark.json').write_text(json.dumps(bench,ensure_ascii=False,indent=2)+'\n')
(P/'benchmark/requests.jsonl').write_text(''.join(json.dumps({'id':c['id'],'request':c['request']},ensure_ascii=False)+'\n' for c in cases))
print(json.dumps({'documents':len(docs),'cases':len(cases),'labels':dict(collections.Counter(c['expected']['decision'] for c in cases))},ensure_ascii=False))
