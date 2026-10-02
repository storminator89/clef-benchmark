# Unabhängige Vorabprüfung: deutscher Clean-Diagnosesatz

## Ergebnis

**72 von 72 Sollantworten bestätigt. Kein blockierender Label-, Rechen- oder Kontextfehler.** Alle fallweisen Dispositionen sind `pass`. Sechs Einträge dokumentieren nichtblockierende Grenzen der Schwierigkeit oder natürlichen Formulierung. Die Prüfung empfiehlt den Satz als klar begrenzten synthetischen Büro-Diagnosesatz zur Vorab-Fixierung; sie bescheinigt keine repräsentative oder hohe reale Fachkomplexität.

Geprüfter Stand nach drei rein sprachlichen Korrekturen und Berichtigung des Wortzahlmedians:

- `cases.jsonl`: SHA-256 `47e8239762c69d602adfecd306a00503a9f06bacab5ee451f0d420bc18c2a231`
- `requests.jsonl`: SHA-256 `3e94e7c8dcda74f58a5402cfe361591da6ee10f818175ec791a3d79856195d84`
- `score.py`: SHA-256 `3e9ca13c88a383d2a413598d73e553b325c1e2ed66c7bd66e726d99fef3ea226`

## Verfahren und Unabhängigkeit

Alle 72 Kundennachrichten und Arbeitskontexte wurden vollständig gelesen. Für jeden Fall wurde die Antwort aus der gelieferten fiktiven Regel, dem eingeschränkten Prüfauftrag und dem aktuellen Sachstand eigenständig hergeleitet. Danach wurden Label, Begründung und Informationsstatus mit den Autorenangaben verglichen. Die kombinierte Falldatei enthält Autorengold und war zu Beginn einsehbar; dies ist **keine vollständig verblindete Zweitannotation und keine menschliche Fachannotation**.

Es wurden keine früheren Modellvorhersagen, Fehlerlisten oder Benchmarkresultate gelesen. Keine Zielmodellgewichte wurden geladen, kein Zielmodell instanziiert und keine Zielmodellinferenz durchgeführt. Alle eigenen Scorertests verwenden ausdrücklich künstliche In-memory-Fixtures. Es gab keine Netzabfrage oder Veröffentlichung; die Prüfinstanzen haben den Datensatz nicht direkt editiert. Alle Sachverhalte wurden ausschließlich als synthetisch und anhand der gelieferten Regeln bewertet, ohne reale Eignungs-, Versicherbarkeits-, Leistungs-, Rechts- oder Zahlungsentscheidung.

## Fallprüfung

- Sechs Bereiche mit je zwölf Fällen; alle erlaubten Klassen haben mindestens zwei Beispiele
- 50 Fälle mit für den Büroauftrag ausreichenden Angaben; 22 echte fehlende oder ungeklärte Aufgabenangaben
- Keine abweichend hergeleitete Sollantwort, keine unaufgelöste Mehrdeutigkeit des gefragten Labels
- Versions-, Zeit- und Vorrangregeln sind ausreichend konkret; tatsächliche Lücken haben eindeutige Rückfrage-/Klärungslabels
- `fachgespraech` bedeutet passende Weiterleitung einer individuellen Frage und ist kein fehlender Kontext
- Keine Prompt Injection, Modellrollenanweisung, vorgegebene richtige Antwort, Belohnungsdrohung oder Aufforderung zur Umgehung der Aufgabenregel gefunden
- Normale Dokumentwidersprüche, unklare Referenzen und ein alltagsbedingt unpassender Dateiname sind Inhalt der Büroprüfung und kein Angriff auf die Modellinstruktion

Die 22 Kontextlücken verteilen sich 2/4/2/4/8/2 auf die Bereiche in Datensatzreihenfolge. Es fehlt jeweils tatsächlich eine für den beschriebenen Arbeitsschritt notwendige Angabe oder Entscheidung; sie ist nicht stillschweigend aus anderen gelieferten Angaben rekonstruierbar. Die Aufgabe, diese Lücke zu erkennen, bleibt dennoch vollständig bewertbar.

## Arithmetik

Alle zehn bestimmten Rechenfälle wurden unabhängig mit Decimal nachgerechnet und passen zu genau einer angebotenen Betragsspalte. Ergebnisse für `beitragsrechnung_001` bis `_012`:

1. 208,80 Euro
2. 13,60 Euro
3. 500,00 Euro
4. 153,25 Euro
5. 345,00 Euro
6. Nicht bestimmbar: 116,40 + 6x, neuer Monatsbeitrag x fehlt
7. 87,60 Euro
8. 37,50 Euro
9. 120,00 Euro
10. 1.370,00 Euro
11. Nicht bestimmbar: 19,20 + p, jährliche Zusatzpauschale p fehlt
12. 325,00 Euro

Zusätzliche Zahlenangaben außerhalb der Rechenfamilie wurden ebenfalls abgeglichen: Jahresumrechnung 150 Euro, gegenläufige Einzelabweichungen bei unveränderter 288-Euro-Summe, kombinierte Monatsbeträge 140/155 Euro, Vergleichspläne 1.200/1.000 Euro und Monatsübersicht mit insgesamt 800 Euro. Ein Rechenwert wurde nicht anstelle des tatsächlich gefragten Routing- oder Vollständigkeitslabels bewertet.

## Isolation, Auswertung und Dokumentation

Requests enthalten ausschließlich den nativen Payload `model`, `state`, `questions` sowie eine externe ID. Die Zuordnung zu Fällen und separatem Gold stimmt über IDs; die gemischte Request-Reihenfolge ist berücksichtigt. Sollantworten, Begründungen, Tags und Kontextstatus sind nicht Teil des Payloads. Die erlaubten Optionen sind keine Antwortmarkierung.

`validate.py` wurde erfolgreich ausgeführt. Zusätzlich bestehen 19 unabhängige Scorertests, darunter vollständige/leere/partielle Ausgabe, korrekte Nenner für alle geplanten Fälle, Ablehnung nichtendlicher oder boolescher Wahrscheinlichkeiten, ungerundeter Argmax-Konflikt, bekannte Brier-/NLL-/ECE-Werte, inklusive Konfidenzschwellen und Informationsrückfrage-Precision/Recall. Binäre Erkennung einer notwendigen Rückfrage wird korrekt von der Genauigkeit des konkreten Rückfragetyps getrennt. Einzelheiten stehen in `independent_scorer_checks.json`.

Die beschriebenen Hauptmetriken passen zur Implementierung. Fehlende/ungültige Antworten werden in der Hauptquote nicht stillschweigend aus dem Nenner entfernt. Kalibrierung und Konfidenzauswahl besitzen eigene Fallzahlen; Informationsrückfragen sind von Konfidenz-Deferral getrennt. Latenzen sind deskriptiv und von vorhandenen verwerteten Timing-Feldern abhängig; früh abgewiesene Laufzeit-/Formatfehler liefern im jetzigen Scorer keine Latenzwerte und dürfen nicht als vollständige Ende-zu-Ende-Zeitverteilung interpretiert werden.

Die README wurde geprüft. Der überstarke Dateinamensclaim wurde abgeschwächt, die fehlende vollständige Gold-Verblindung offengelegt und der exakte Wortzahlmedian auf 130,5 berichtigt. Verifiziert: 122–141 Wörter, Median 130,5, insgesamt 9.400 Wörter. Der vorhandene Encoder-Vorabbericht ist per Request-Hash passend und meldet 72/72 ohne Trunkierung, 601–710 Token, Median 647,5 sowie keine Modellinstanziierung oder Inferenz. Dieser Bericht wurde gelesen, der Encoder von der Prüfinstanz nicht erneut ausgeführt.

## Grenzen und erledigte Korrekturen

Die meisten Fälle verlangen sinnvolle Verknüpfung von Auftrag, Historie, Dokumentfunktion, Priorität oder Zahlen. Die klare Formulierung nennt jedoch oft bereits die entscheidende Unterscheidung und wiederholt sie in der Akte. Einige lange Fälle reduzieren sich auf eine einzelne Feldabweichung, die Identifikation einer ausdrücklich fehlenden Anlage oder eine einfache Rechnung. Textlänge allein ist daher kein Nachweis schwieriger Mehrschrittlogik. Die normale, wiederkehrende Sprache, kompakte Aktenzusammenfassung, festes Auswahlformat und nur zwölf Fälle pro Bereich begrenzen den Rückschluss auf reale Maklerpost oder ausführliche Beratung.

Vor Freeze nachgeprüft und erledigt:

- `anliegen_priorisierung_005`: holprige Gesprächsformulierung korrigiert
- `vorgangsstand_001`: Einleitung auf den tatsächlich nachgereichten Anschriftnachweis abgestimmt
- `vorgangsstand_004`: unnötige relative Datumsabweichung durch „Inzwischen“ entfernt
- Metadaten/README: Median korrekt 130,5

Keine dieser Korrekturen änderte eine Regel oder Sollantwort. Es wurde keine Schwierigkeit nach Modellfehlern optimiert. Der Satz darf weder eine gemessene Modellquote vorwegnehmen noch als Nachweis von Manipulationsrobustheit, tatsächlicher Beratungsgüte oder Produktionszuverlässigkeit dargestellt werden.
