# Clef Deutsch: neue alltagsnahe Maklerfälle ohne Manipulation, v1

Separater, vor der ersten Inferenz eingefrorener Diagnosesatz vom 2. Oktober 2026: **72 vollständig synthetische deutsche Fälle**, sechs Bereiche mit je zwölf Aufgaben. Dies ist ein neu verfasster Satz, keine Entfernung von Angriffssätzen aus dem früheren Benchmark, keine Übersetzung und keine Anpassung an dessen Modellfehler.

## Was hier gemessen wird

Die Fälle sind an typischen Bürofragen einer Finanzberatung oder eines Versicherungsmaklers orientiert: längere Kundenanfrage plus kurzer Akten-/Dokumentauszug, mehrere Anliegen, überholte und aktuelle Angaben, ausdrücklich begrenzte Prüfaufträge, Rechnungen mit mehreren Schritten und wirklich fehlende Angaben. Es wird jeweils **eine feste Entscheidung aus vier oder fünf Optionen** geprüft. Es geht nicht um die Qualität einer frei formulierten ausführlichen Kundenantwort.

Alle Regeln sind kurze, ausdrücklich fiktive Arbeitsanweisungen. Keine Nachricht oder Anlage enthält Prompt Injection, eine an das Modell gerichtete Fremdanweisung, einen vorgegebenen Antwortschlüssel, eine Belohnungsdrohung oder einen Versuch, die Aufgabenregel zu umgehen. Normale Kundenaufträge und fachliche Prioritäten bleiben natürlich Teil der Nachricht. Normale alltagsbedingte Dokument- und Dateinamensunklarheiten können vorkommen. Es gibt keine adversarialen Modellanweisungen und keine aus einem alten Modellfehler abgeleiteten Minimalpaare.

Die unabhängige Vorabprüfung bewertet alle 72 Sollantworten, Mehrdeutigkeit, Rechenwege, Kontextlücken, natürliche Formulierung und Manipulationsfreiheit. Sie ersetzt keine menschliche Fachannotation. Details stehen in `pre_inference_review.md` und den fallweisen Prüfeinträgen. Der Autor hat frühere Modellvorhersagen und Fehlerlisten nicht zur Gestaltung betrachtet; das existierende Dateiformat und der Offline-Metrikkern wurden zur Kompatibilität gelesen. Auch die unabhängige Prüfung nutzt keine Modellausgaben. Die Zweitprüfung hat die Antworten eigenständig aus Regeln und Texten abgeleitet, war aber nicht vollständig gegenüber dem Autorengold verblindet, weil die bereitgestellte Fall-Datei dieses enthält.

## Zusammensetzung

| Bereich | Fälle | Ausreichender Kontext | Fehlend/ungeklärt | Aufgabe |
|---|---:|---:|---:|---|
| Anliegen priorisieren | 12 | 10 | 2 | Aktuellen ersten Büroauftrag aus mehreren Wünschen und Verlauf bestimmen |
| Unterlagen abgleichen | 12 | 8 | 4 | Angeforderte Felder gegen bestätigte Referenzen prüfen, Versionskonflikte erkennen |
| Beiträge berechnen | 12 | 10 | 2 | Zeitabschnitte, Zahlungsrhythmen, Gutschriften, Prozentrechnung und Summen |
| Vorgangsstand | 12 | 8 | 4 | Vollständigkeit, Versandstand und dokumentierte Antwortfrist zusammenführen |
| Nächste Rückfrage | 12 | 4 | 8 | Wirklich fehlende Angabe auswählen; vier vollständige Kontrollfälle benötigen keine Rückfrage |
| Finanzservice routen | 12 | 10 | 2 | Dokument, neue Rechnung, festgelegte Änderung oder individuelles Fachgespräch unterscheiden |
| Gesamt | 72 | 50 | 22 | 69,4 % ausreichend, 30,6 % fehlend oder ungeklärt |

„Fehlend/ungeklärt“ bedeutet eine echte Lücke für den begrenzten Arbeitsschritt: fehlende Referenzseite, Betrag, Zeitraum, Priorität, Zuordnung, notwendiger Beleg oder unaufgelöster Versionskonflikt. Diese Fälle haben eine eindeutige Sollantwort zum Nachfragen/Zurückstellen. Sie sind keine unbewertbaren Testfälle. Die fachliche Gesprächsroute ist dagegen eine eindeutige Dienstleistungszuordnung und zählt nicht automatisch als Informationsabstention.

Die Klassen sind bewusst **nicht künstlich exakt gleichverteilt**; alle kommen vor. Exakte Zahlen stehen in `design_summary.json`. Gleichverteiltes Zufallsraten ergäbe im Erwartungswert 20,83 % (zwölf Aufgaben mit vier, sechzig mit fünf Optionen); dies ist kein ausgeführtes Modellresultat. Der Satz enthält keine englischen Kontrollen, keine Bilder und keine Angriffs-/Kontrollpaare. Sein Ergebnis darf nicht mit den früheren Sätzen zu einer gemeinsamen Quote vermischt werden.

## Komplexität und Realitätsgrenzen

Die beabsichtigten Komplexitätsachsen sind:

1. Mehrfachanliegen und Priorität: erledigte, aktuelle und später gewünschte Arbeit unterscheiden
2. Mehrere Quellen und Bezug: Nachricht, Dokumentfeld, Vertrag und Bearbeitungseintrag zusammenführen
3. Zeit und Version: bestätigte Korrektur, verschiedene Monatsabschnitte sowie konkret dokumentierte Antwortfristen berücksichtigen
4. Zahlen und Prüfumfang: mehrere Rechenschritte mit ausschließlich gelieferten Annahmen; individuelle Vertragswerte statt nur Gesamtsumme
5. Fehlende Information: gezielte Rückfrage statt erfundener Ergänzung; bei mehreren Lücken die mitgelieferte Arbeitsabhängigkeit beachten
6. Aufgabengrenzen: reine Dokumentenarbeit und Berechnung von persönlicher Fachentscheidung unterscheiden, ohne diese Entscheidung zu treffen

Die Texte haben 122–141 durch Leerraum getrennte Wörter (Median 130,5), insgesamt 9.400 Wörter in Nachricht plus Aktenauszug. Der lokale native Encoder benötigt einschließlich Regel und Optionen 601–710 Token (Median 647,5); alle 72 bleiben ohne Trunkierung unter dem gepinnten 2.048-Token-Limit.

**Alltagsnah formuliert ist nicht gleich repräsentativ für den Alltag.** Es sind KI-verfasste, bewusst ausgewählte Szenarien, keine tatsächlichen Kundenkontakte und keine zufällige Stichprobe. Die Nachrichten sind sprachlich ordentlich; der Aktenauszug ist kompakt und normalisiert. Entscheidende Unterschiede werden oft ausdrücklich genannt und teils in Nachricht und Akte wiederholt. Das erleichtert die Zuordnung gegenüber ungeordneten realen E-Mails. Die Texte sind länger als die früheren kurzen Klassifikationsfälle, aber keine Langakten. Wiederkehrende Formulierungs- und Aufgabenmuster, nur zwölf Fälle pro Bereich sowie mindestens zwei Beispiele je Klasse begrenzen die Aussagekraft.

Nicht enthalten sind OCR, Screenshots, Tabellenextraktion aus Dateien, echte Anhänge, fragmentierte E-Mail-Ketten, frei zu recherchierende Gesetze, offene Produktberatung, echte Werkzeugaktionen oder eine Beratungskonversation. Eine hohe Quote wäre ein Befund für genau diese klar begrenzten synthetischen Entscheidungen. Sie wäre kein Nachweis, dass das Modell komplexe Maklerarbeit oder ausführliche Beratung zuverlässig übernimmt. Die neuen Aufgaben sind nicht mit den früheren Testfällen schwierigkeitsgleich kalibriert; eine Differenz der Gesamtquoten ist kein kausaler Manipulationseffekt.

## Sicherheit und Fiktion

- Keine echten Personen, Kundenakten, Kontodaten, Gesundheits- oder Vermögensdaten
- Keine Entscheidung über Produkteignung, Kreditwürdigkeit, Versicherbarkeit, Deckung, Leistungsansprüche oder tatsächliche Zahlungen
- Individuelle Finanzfragen werden nur zum Fachgespräch geroutet; ihre Voraussetzungen werden nicht bewertet
- Fiktive Checklisten sind nur für den ausdrücklich begrenzten internen Büroschritt vollständig; sie bilden kein reales Gesetz oder vollständiges Compliance-Verfahren ab
- Antwortfristen sind im jeweiligen Aktenauszug dokumentierte Bürotermine, keine erfundenen gesetzlichen Fristen
- Rechenfälle nutzen nur vorgegebene Beträge und explizite Rechenregeln, keine Anlageerträge, Steuern oder Versicherungsleistungen aus externem Wissen
- Kein Versand, keine Vertragsänderung, keine Transaktion, keine Veröffentlichung

## Native Schnittstelle, Isolation und Reihenfolge

Verwendet wird derselbe native Clef-Vertrag wie im ursprünglichen Test:

```json
{"id":"Fallkennung","request":{"model":"clef-flash","state":"Kundennachricht und Aktenauszug","questions":{"decision":{"type":"choice","instructions":"Deutsche fiktive Arbeitsregel","criteria":{"deutsches_label":"Deutsche Beschreibung"}}}}}
```

Nur `request` geht an den Encoder bzw. die Inferenz. Die lokale ID wird nicht in den Modellinput geschrieben. In `requests.jsonl` befinden sich weder Sollantwort, Begründung, Fallkategorie, Komplexitäts-Tags noch Kennzeichnung der Kontextvollständigkeit. Optionen enthalten selbstverständlich die erlaubten Antworten, aber keine Markierung der richtigen Option. Im Rechenbereich sind es vier Beträge plus `daten_fehlen`; die Reihenfolge ist pro Fall vorab festgelegt. Andere Kategorien verwenden dieselbe Kriterienreihenfolge für ihre zwölf Fälle. Reihenfolgeeffekte werden nicht separat getestet.

Die 72 Requests sind mit `random.Random(2026100204).shuffle` einmal deterministisch gemischt; Gold und Requests haben dieselbe feste ID-Reihenfolge. Keine nachträgliche Fallauswahl anhand von Ergebnissen. Vor der ersten Inferenz werden Regeln, Daten, Scorer, Validator, Dokumentation und Auditdateien mit SHA-256 gesperrt. Der Freeze ist eine Integritätssperre, keine Zugriffskontrolle.

## Dateien und Wiederholung

- `build_benchmark.py`: selbstständige deterministische Assemblierung aller handverfassten synthetischen Fälle; verweigert Überschreiben eines eingefrorenen Zielordners
- `cases.jsonl`: 72 Fälle mit Fragen, Sollantworten, Begründungen und Metadaten für Prüfung/Auswertung
- `requests.jsonl`: ausschließlich native label-freie Requests mit externer ID
- `gold.jsonl`: gesonderte Sollantworten und Metadaten in Request-Reihenfolge
- `policies.json`: gemeinsame deutsche Arbeitsregeln; Betragsoptionen sind fallbezogen in den Requests
- `design_summary.json`: Verteilung, Längen, Tags, Taxonomie und vorab festgelegte Hauptmetrik
- `score.py`: selbstständiger Offline-Scorer, nativer Inspektions-/Metrikkern aus dem bestehenden Satz übernommen; Aggregation für diesen Satz gesondert
- `validate.py`: Mengen-, Schema-, Isolations-, Arithmetik-, Rebuild-, Audit-, Hash- und Scorertests ohne Modellzugriff
- `check_encoding.py`, `encoding_preflight.json`: lokaler nativer Tokenizer-/Encoder-Test ohne Gewichte, Modellinstanziierung oder Inferenz
- `pre_inference_review.jsonl`, `pre_inference_review.md`: unabhängige Einzelprüfung und Einschränkungen
- `independent_scorer_tests.py`, `independent_scorer_checks.json`: 19 zusätzliche unabhängig erstellte Offline-Scorertests und deren Ergebnis; keine Modellvorhersagen
- `freeze.py`: einmaliges Einfrieren nach bestandener Prüfung, ohne Modellzugriff
- `freeze_manifest.json`: endgültige Hashes und Vorab-Freeze-Zeitpunkt

```bash
python validate.py
python score.py /pfad/zu/clean_predictions.jsonl --out /pfad/zu/clean_scores.json
```

Zum deterministischen Nachbau ein separates Verzeichnis übergeben: `python build_benchmark.py /tmp/clean-rebuild`. Ergebnisse nicht im eingefrorenen Benchmarkordner speichern.

## Vorab festgelegte Auswertung

Primär: Auswahlgenauigkeit auf **allen 72 geplanten deutschen Fällen**. Fehlende Antworten, Laufzeitfehler und unbekannte Labels zählen falsch. Bei noch laufendem Run ist dies nur eine vorläufige Untergrenze. Zusätzlich: Genauigkeit auf gültigen Auswahlen und strengere Genauigkeit mit vollständigem nativem Antwortschema.

Weitere Kennzahlen:

- Je Bereich Accuracy, Confusion Matrix, Klassen-Precision/Recall/F1 und Macro-F1; das Gesamt-Macro-F1 ist der ungewichtete Mittelwert der sechs Bereichs-Macro-F1-Werte
- Getrennte Ergebnisse für 50 ausreichende und 22 fehlende/ungeklärte Kontexte; überlappende Komplexitäts-Tags nur deskriptiv, nicht als unabhängige Stichproben
- Informationsrückfragen: Recall/Precision, unnötige Rückfrage bei vollständigem Kontext und verpasste Rückfrage bei gültiger Auswahl; ungültige/fehlende Antworten separat
- Native Schemagültigkeit: erlaubtes Label, Typ `choice`, vollständiger endlicher Wahrscheinlichkeitsvektor in [0,1], Summe mit Toleranz 0,001 und konsistente Auswahl/Confidence; Rundungstoleranzen des bestehenden Metrikkerns bleiben erhalten
- Kalibrierung je Bereich, sofern vorhanden: mehrklassiger Brier-Score als Summe, NLL mit Clip 1e-12, ECE mit fünf gleichen Bins; vollständige Wahrscheinlichkeiten werden für Kalibrierung bevorzugt, Fallzahlen separat angegeben
- Coverage und Accuracy bei unveränderten Konfidenzgrenzen 0,60 / 0,80 / 0,90 / 0,95; keine nachträgliche Optimierung
- Latenz je Bereich als Median und p95, sofern übergeben; Modellladen, Tokenisierung und Inferenzzeit getrennt dokumentieren

Der Scorer lehnt doppelte IDs, unbekannte IDs und nicht zuordenbare Ausgabezeilen ab. Seine Tests erzeugen ausdrücklich künstliche perfekte/falsche Antworten nur zum Testen der Software. Diese sind keine Modellinferenz und kein Benchmarkresultat.

Der spätere Run soll die bereits gepinnte CPU-Textkonfiguration wiederverwenden und erst nach dem Bildtest sowie ausdrücklicher Freigabe beginnen. Der aktuelle Ordner enthält **keine Modellausgaben und keine gemessene Modellquote**. Modellrevision, nativer Entscheidungskopf, Quantisierung, Software, Hardware und Fehlerquote sind im späteren Lauf getrennt nachzuweisen. Ein AMD-Lauf oder eine andere Ausführungsvariante wäre gesondert zu kennzeichnen.

Nach Sichtung der neuen Outputs dürfen Fälle, Gold, Regeln und Bewertung nicht stillschweigend geändert werden. Falls sich ein echter Annotierungsfehler zeigt, ist eine neue dokumentierte Version mit gesonderter Auswertung nötig.
