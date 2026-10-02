# Vollständige Fehlerliste

Die Texte unter „Referenz“ sind geprüfte Testreferenzen. Clef erzeugt keine freie Begründung; angezeigt werden ausschließlich seine nativen Auswahlfelder und Wahrscheinlichkeiten. Alle Policen und Szenarien sind synthetisch.

## fall_003 · Deckungsumfang und Definitionen

**Sachverhalt:** Ein der versicherten Person gehörender Laptop wird ausschließlich beruflich genutzt und steht in der versicherten Wohnung.

**Aussage:** Der Laptop gehört dort zu den versicherten Sachen.

**Entscheidung:** Modell `ja` (89,4 %); Referenz `ja`.

**Belegmenge:** Modell H1 (62,3 %); Referenz H2.

**Referenzerläuterung:** H1 öffnet berufliche Arbeitsmittel; H2 schließt tragbare Computer ein.

- **H1:** Versichert sind bewegliche Sachen, die der versicherten Person gehören und ihrem privaten Haushalt dienen. Auch beruflich genutzte Arbeitsmittel sind versichert, soweit H2 sie einschließt.
- **H2:** Für berufliche Arbeitsmittel sind ausschließlich tragbare Computer und Bildschirme eingeschlossen. Warenbestände, Bargeld und Werkzeuge sind als berufliche Sachen nicht versichert.

## fall_028 · Nachträge und Dokumentvorrang

**Sachverhalt:** Gerät Delta fällt am 15. Juni 2026 herunter; der Schaden wird erst im August gemeldet.

**Aussage:** Der Nachtrag V4 schließt diesen Sturzschaden ein.

**Entscheidung:** Modell `ja` (83,1 %); Referenz `nein`.

**Belegmenge:** Modell V4, V6 (86,0 %); Referenz V4, V6.

**Referenzerläuterung:** Schaden vor Geltungsbeginn; Meldetag macht Nachtrag nicht rückwirkend.

- **V4:** Individueller Nachtrag, gültig ab 1. Juli 2026: Für Gerät Delta sind versehentliche Sturzschäden eingeschlossen. Für andere Geräte bleibt der Ausschluss unverändert.
- **V6:** Der Nachtrag wirkt nicht rückwirkend; maßgeblich ist der Schadentag, nicht der Meldetag.

## fall_029 · Nachträge und Dokumentvorrang

**Sachverhalt:** Gamma hat für die Garage die Regel aus Beta ersetzt. Am Wohngebäude entsteht ein Überschwemmungsschaden.

**Aussage:** Der Widerspruch zwischen Alpha und Beta über das Wohngebäude ist durch Gamma zugunsten eines Einschlusses aufgelöst.

**Entscheidung:** Modell `konflikt` (50,7 %); Referenz `nein`.

**Belegmenge:** Modell Z1 (37,7 %); Referenz Z5.

**Referenzerläuterung:** Gamma betrifft nur die getrennte Garage und löst den Wohngebäudekonflikt nicht.

- **Z1:** Individuelle Nachträge gehen allgemeinen Bedingungen vor. Eine spätere Unterzeichnung verdrängt frühere Nachträge nur, wenn der spätere Text die ersetzte Regel ausdrücklich nennt. Gleiche Rangstufe ohne solche Auflösung wird nicht durch das Dateidatum entschieden.
- **Z5:** Nachtrag Gamma, für den ganzen Prüfzeitraum wirksam: Für Schäden an der Garage ersetzt Gamma die Regel aus Beta; Überschwemmungsschäden an der Garage sind eingeschlossen. Gamma trifft keine Regel über das Wohngebäude.

## fall_033 · Nachträge und Dokumentvorrang

**Sachverhalt:** Gerät Delta wurde versehentlich fallen gelassen. Der Schadentag ist nicht bekannt; die Meldung erfolgt im August 2026.

**Aussage:** Der Schaden fällt unter den zeitlich wirksamen Einschluss V4.

**Entscheidung:** Modell `ja` (63,9 %); Referenz `offen`.

**Belegmenge:** Modell V4, V6 (94,3 %); Referenz V4, V6.

**Referenzerläuterung:** Wirksamkeit hängt vom unbekannten Schadentag ab, nicht vom Meldetag.

- **V4:** Individueller Nachtrag, gültig ab 1. Juli 2026: Für Gerät Delta sind versehentliche Sturzschäden eingeschlossen. Für andere Geräte bleibt der Ausschluss unverändert.
- **V6:** Der Nachtrag wirkt nicht rückwirkend; maßgeblich ist der Schadentag, nicht der Meldetag.

## fall_035 · Ausschlüsse und Rückausnahmen

**Sachverhalt:** Eine privat geliehene Geige wird bei einem bezahlten beruflichen Konzert fahrlässig beschädigt.

**Aussage:** L3 hebt den Ausschluss L2 für diesen Schaden auf.

**Entscheidung:** Modell `ja` (69,0 %); Referenz `nein`.

**Belegmenge:** Modell L3 (90,0 %); Referenz L3.

**Referenzerläuterung:** Die berufliche Nutzung ist von der Rückausnahme ausgenommen.

- **L3:** Abweichend von L2 sind Schäden an privat geliehenen Musikinstrumenten eingeschlossen. Dieser Einschluss gilt nicht für berufliche Nutzung oder für den Verlust der Sache.

## fall_036 · Voraussetzungen und Obliegenheiten

**Sachverhalt:** Die Meldung war vorsätzlich verspätet. Die Feststellung des Versicherungsfalls wurde dadurch nachweislich nicht erschwert.

**Aussage:** O2 erlaubt die vollständige Ablehnung wegen der Verspätung.

**Entscheidung:** Modell `ja` (71,8 %); Referenz `nein`.

**Belegmenge:** Modell O2 (92,8 %); Referenz O2.

**Referenzerläuterung:** Kumulative Voraussetzung der tatsächlichen Erschwerung fehlt.

- **O2:** Eine vollständige Leistungsablehnung wegen verspäteter Meldung ist nach diesen Bedingungen genau dann zulässig, wenn die Verspätung vorsätzlich war und die Feststellung des Versicherungsfalls tatsächlich erschwert hat.

## fall_047 · Unvollständige und widersprüchliche Akten

**Sachverhalt:** Zu Elektronikschutz sind nur die in U3 und U4 beschriebenen Informationen vorhanden.

**Aussage:** Der Elektronikbaustein ist verbindlich aktiv.

**Entscheidung:** Modell `nein` (62,1 %); Referenz `offen`.

**Belegmenge:** Modell U3 (95,0 %); Referenz U3.

**Referenzerläuterung:** Empfehlung genügt nicht; verbindliche Ausweisung fehlt ohne Gegenbeweis.

- **U3:** Elektronikschutz besteht nur, wenn der Baustein im Versicherungsschein ausdrücklich als aktiv ausgewiesen ist. In dieser Akte fehlt eine solche Ausweisung ebenso wie eine verbindliche Deaktivierung.

## fall_050 · Deckungsumfang und Definitionen

**Sachverhalt:** Eigene berufliche Werkzeuge befinden sich in der versicherten Wohnung.

**Aussage:** Die Werkzeuge gehören zu den versicherten Sachen.

**Entscheidung:** Modell `konflikt` (46,4 %); Referenz `nein`.

**Belegmenge:** Modell H2 (82,8 %); Referenz H2.

**Referenzerläuterung:** Berufliche Werkzeuge sind ausdrücklich nicht versichert.

- **H2:** Für berufliche Arbeitsmittel sind ausschließlich tragbare Computer und Bildschirme eingeschlossen. Warenbestände, Bargeld und Werkzeuge sind als berufliche Sachen nicht versichert.

## fall_055 · Unvollständige und widersprüchliche Akten

**Sachverhalt:** Ein Schaden tritt am Standort Nord ein. Es liegen ausschließlich die in U2 genannten Unterlagen vor.

**Aussage:** Standort Nord ist der verbindlich vereinbarte Versicherungsort.

**Entscheidung:** Modell `nein` (51,1 %); Referenz `offen`.

**Belegmenge:** Modell U1, U2 (96,0 %); Referenz U1, U2.

**Referenzerläuterung:** Angebot ohne Schein oder Annahme belegt keine vereinbarte Adresse.

- **U1:** Versichert ist nur die Betriebsstätte, deren Anschrift im verbindlichen Versicherungsschein genannt ist. Eine Angebotsanschrift beweist den vereinbarten Versicherungsort nicht.
- **U2:** Die Akte enthält ein Angebot für Standort Nord, aber keinen Versicherungsschein und keine bestätigte Annahme dieses Angebots.

## fall_056 · Deckungsumfang und Definitionen

**Sachverhalt:** Ein privat geliehener Fotoapparat befindet sich bei einem dauerhaften Umzug bereits in der neuen, nicht im Schein genannten Wohnung.

**Aussage:** Der Fotoapparat ist nach der Fremdsachenregel H5 an diesem Ort eingeschlossen.

**Entscheidung:** Modell `ja` (75,9 %); Referenz `nein`.

**Belegmenge:** Modell H3, H5 (88,3 %); Referenz H3, H5.

**Referenzerläuterung:** Einschluss privat geliehener Sachen setzt den Versicherungsort voraus; laut Sachverhalt liegt dieser nicht vor.

- **H3:** Versicherungsort ist die im Schein genannte Wohnung einschließlich eines ausschließlich dieser Wohnung zugeordneten, abschließbaren Kellerraums. Gemeinschaftliche Abstellräume gehören nicht dazu.
- **H5:** Gegenstände fremder Personen sind nicht versichert. Abweichend davon sind privat geliehene Sachen eingeschlossen, wenn sie sich am Versicherungsort befinden.

