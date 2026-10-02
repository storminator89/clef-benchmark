# Eigener deutscher Clef-Entscheidungsbenchmark v1

Erstellt am 2. Oktober 2026. 120 vollständig synthetische deutsche Fälle, 30 englische Kontrollübersetzungen und 30 getrennte Diagnosevarianten. Keine echten Nutzerdaten, Kontoinhalte oder bestehenden Kundentickets. Der Benchmark prüft abgegrenzte Klassifikationsentscheidungen anhand ausdrücklich mitgelieferter Regeln. Er ist kein allgemeiner Sprach-, Wissens- oder Textgenerierungstest.

## Was geprüft wird

| Kategorie | Deutsche Fälle | Klassen und Verteilung |
|---|---:|---|
| IT-/M365-Supportrouting | 20 | identity, messaging, collaboration, endpoint, clarify: je 4 |
| Priorität inklusive Verneinung | 20 | critical, high, normal, none: je 5 |
| Werkzeugauswahl | 20 | calculator, calendar_lookup, mail_search, web_search, no_tool: je 4 |
| Dokumentfunktion | 20 | invoice, reminder, credit_note, offer, other: je 4 |
| Verwaltungs-/Zahlungs-Supportabsicht | 20 | copy, correction, refund, deadline, other: je 4 |
| Mehrdeutigkeit und Zurückhaltung | 20 | ready, missing, conflict, unsupported: je 5 |

Die Fälle enthalten unter anderem Umlaute, deutsche Komposita, Umgangssprache, Redewendungen, Rechtschreibfehler, Negation, Selbstkorrektur, irreführende Betreffzeilen, historische Zitate und sechs synthetische Prompt-Injection-Versuche. Tags kennzeichnen beabsichtigte Herausforderungen im deutschen Ausgangsfall, nicht eine exhaustive Zeichenanalyse und nicht dieselben sprachlichen Merkmale in jeder Übersetzung.

Die Regeln definieren bewusst kleine betriebliche Taxonomien. Sie sind weder universelle IT-Standards noch echte Eskalationsrichtlinien oder Rechts-/Finanzberatung. Aufgaben zur Werkzeugauswahl prüfen nur die Auswahl, nicht Ausführung, Berechtigungen oder erfolgreiche Recherche. Die Fähigkeiten in der Mehrdeutigkeits-Kategorie sind absichtlich enger als in der Werkzeug-Kategorie; diese Kontexte dürfen nicht vermischt werden.

## Native Clef-Schnittstelle

Nach den offiziellen [Cloudflare-Modellunterlagen](https://developers.cloudflare.com/workers-ai/models/clef/) nimmt Clef einen Zustand und typisierte Fragen entgegen. Verwendet wird pro Fall genau eine native `choice`-Frage namens `decision`. Die [offizielle Clef-Flash-Modellkarte](https://huggingface.co/Cloudflare/clef-flash) beschreibt die lokale Entscheidungsinferenz über `joint_schema_model`, inklusive Auswahlwahrscheinlichkeiten. Der [Ankündigungsbeitrag](https://blog.cloudflare.com/clef-decision-models/) liefert den Produktkontext. Diese Dateien testen keine freie Textausgabe und benutzen keine generische `generate`-Abfrage als Ersatz für den Entscheidungskopf.

Jede Zeile in `requests.jsonl` hat diese Struktur:

```json
{"id":"Fallkennung","request":{"model":"clef-flash","state":"Zu klassifizierender Text","questions":{"decision":{"type":"choice","instructions":"Explizite Richtlinie","criteria":{"klasse_a":"Definition A","klasse_b":"Definition B"}}}}}
```

Die Fallkennung bleibt im Runner und wird nicht in den Modellzustand geschrieben. Nur `request` wird an die native Schnittstelle übergeben; bei direkter Kodierung genügen `state` und `questions`. Keine Goldlabels, Begründungen, Kategorien, Tags oder Paarinformationen werden mitgeschickt. Absichtlich eingefügte falsche Antwortanweisungen in sechs Angriffsfällen sind Teil der zu klassifizierenden Nutzlast, keine Metadaten-Lecks. Die Modellanweisungen grenzen diese Nutzlast ausdrücklich als nicht vertrauenswürdig ab.

## Dateien

- `cases.jsonl`: 120 deutsche Hauptfälle plus 30 englische Kontrollen, jeweils mit Input, vollständigen Fragen, Sollantwort, Tags, Begründung und Paar-ID
- `diagnostic_cases.jsonl`: 30 Fälle mit deutschem Input und englischer Richtlinie/Klassenbeschreibung
- `requests.jsonl`: 180 label-freie Requests in vorab festgelegter, deterministisch gemischter Reihenfolge; Seed 20261002
- `gold.jsonl`: gesonderte Sollantworten und Auswertungsmetadaten
- `pairs.jsonl`: exakte Zuordnung der 30 Dreiergruppen
- `policies.json`: die sechs Richtlinien in beiden Sprachen
- `design_summary.json`: Mengen, Klassenverteilung und Tags
- `build_benchmark.py`: deterministischer Aufbau der handverfassten synthetischen Daten
- `validate.py`: Daten-, Isolations-, Paar- und Scorerprüfungen; führt kein Modell aus
- `score.py`: lokale Auswertung gespeicherter Modellantworten; ruft keinen Inferenzdienst auf
- `freeze_manifest.json`: nach abgeschlossener Vorabprüfung erzeugte SHA-256-Sperrmarke für die Testversion

## Paardesign und Bedeutung einer Sprachlücke

Pro Kategorie wurden bewusst fünf Kontrollen gewählt; jede Klasse ist vertreten. Die beiden Kategorien mit vier Klassen enthalten zusätzlich einen zweiten `none`- beziehungsweise `unsupported`-Fall. Die Auswahl enthält auch Tippfehler, Redewendungen, vier Angriffe, Ablenkungen und eine Selbstkorrektur. Sie ist keine Zufallsstichprobe.

Für jede der 30 Gruppen existieren:

1. Deutsch/Deutsch: deutscher Zustand und deutsche Fragen/Klassenbeschreibungen
2. Englisch/Englisch: sinngleiche englische Übersetzung des Zustands, der Fragen und Beschreibungen
3. Deutsch/Englisch: unveränderter deutscher Zustand mit genau der englischen Frage aus Variante 2

Alle drei verwenden dieselben Antwort-IDs und Goldlabels. Die dritte Variante ist eine Diagnose und wird nicht in den deutschen 120-Fälle-Hauptwert hineingerechnet. Deutsch/Deutsch minus Englisch/Englisch misst Unterschiede des gesamten sprachlichen Pakets; Deutsch/Deutsch minus Deutsch/Englisch hilft, Einflüsse der Richtliniensprache zu erkennen. Die Vergleiche sind keine perfekte kausale Zerlegung: Tokenisierung, Formulierung, Kontextlänge und Wechselwirkungen ändern sich ebenfalls.

Idiomatische Übersetzungen erhalten die Bedeutung, nicht die Wortfolge. Englische Tippfehler sind sinngemäß vergleichbare Störungen, keine nachgewiesen gleich schwierigen Fehler. Wo ein Auftrag ausdrücklich einen deutschen Satz ins Englische übersetzen soll, bleibt dieser zitierte Operand auch in der englischen Kontrollanweisung deutsch. Das erhält denselben Auftrag und ist eine dokumentierte Ausnahme von vollständig englischem Zustand. Die Sprachlücke wird nur auf den 30 gepaarten Fällen verglichen, nicht zwischen allen 120 deutschen und den ausgewählten 30 englischen Fällen.

## Vorab festgelegte Auswertung

Primär: Auswahlgenauigkeit auf allen 120 geplanten deutschen Fällen. Fehlende Antworten, Laufzeitfehler und unbekannte Labels zählen dabei als nicht korrekt. Zusätzlich wird die Genauigkeit unter ausschließlich gültigen Auswahlen angegeben; sie darf fehlende Fälle nicht verdecken. Eine strengere Genauigkeit verlangt außerdem vollständige native Schema-Gültigkeit. Solange nicht alle Fälle vorliegen, sind Werte ausdrücklich vorläufige Untergrenzen und keine abgeschlossene Modellbewertung.

- Pro Kategorie: Genauigkeit, Klassen-Precision/Recall/F1 und Macro-F1; Gesamt-Macro-F1 ist das ungewichtete Mittel der sechs Kategorie-Macro-F1-Werte. Keine irreführende gemeinsame F1 über inkompatible Labelräume
- Schema: Antworttyp, erlaubtes Label, vollständiger endlicher Wahrscheinlichkeitsvektor in [0,1], Summe innerhalb 0,001 von 1, Konsistenz von Auswahl/Argmax und Confidence. Leichte Rundungstoleranz berücksichtigt die native Ausgabe
- Kalibrierung, wenn verfügbar: mehrklassiger Brier-Score als Summe über Klassen, NLL mit vorab festgelegtem Clip 1e-12 und ECE mit fünf gleich breiten Bins. Vollpräzise `probabilities_unrounded` werden bevorzugt, sonst native gerundete Werte. Kleine Stichproben erlauben keine belastbaren Kalibrierungsversprechen
- Konfidenzdiagnose: Coverage und Genauigkeit für festgelegte Schwellwerte 0,60 / 0,80 / 0,90 / 0,95. Keine nachträgliche Schwellenoptimierung auf diesem Test
- Abstention: `clarify` beim Routing sowie `missing/conflict/unsupported` bei Mehrdeutigkeit sind echte Sollklassen. Abstention-Precision/-Recall, unnötige Zurückhaltung und unzulässige Festlegung werden gesondert ausgewiesen. `no_tool` und `other` sind nicht pauschal Abstentionsklassen. Eine Parserpanne ist keine richtige Zurückhaltung
- Paare: beide richtig, beide falsch, nur links richtig, nur rechts richtig; gepaarte Genauigkeitsdifferenz. Exakter zweiseitiger McNemar-Test ist rein explorativ bei 30 bewusst gewählten Paaren. Ungültige/fehlende Paarhälften werden ausdrücklich gezählt und nicht als Sprachnachteil ausgelegt
- Latenz: Median/p95, sofern je Fall gemessen. Ladezeit, Warm-up, Tokenisierung und eigentliche Inferenz getrennt berichten; lokale CPU-/Quantisierungsmessungen sind kein Vergleich mit beworbenen GPU-/API-Latenzen

Gleichverteiltes Raten über die jeweils erlaubten Klassen hätte auf dem balancierten deutschen Hauptsatz im Erwartungswert 21,7 Prozent Genauigkeit. Das ist ein Rechenreferenzwert, kein ausgeführter Modellbaseline-Test.

### Ausführen der Dateiprüfung und Auswertung

```bash
python validate.py
python score.py /pfad/zu/predictions.jsonl --out /pfad/zu/scores.json
```

Der Scorer akzeptiert Zeilen mit `id` sowie `response.answers.decision` oder unmittelbar `answers.decision`. Die native Antwort enthält `type`, `choice`, `confidence`, `probabilities`. Optional werden `probabilities_unrounded.decision`, `latency_ms` und `error` ausgewertet. Doppelte oder unbekannte IDs werden abgelehnt. Scorer-Unit-Tests verwenden ausschließlich künstliche Antwortobjekte zur Programmprüfung; sie sind keine Modellresultate.

## Freeze und Grenzen

Daten, Übersetzungen, Regeln und Scoring werden vor der ersten Benchmark-Inferenz geprüft und mit SHA-256 fixiert. Eine zweite, getrennte KI-Prüfung kontrolliert Labelplausibilität, Übersetzungen und Metadatenisolation. Das ersetzt kein unabhängiges menschliches Annotationsteam. Der Ersteller sieht vor dem Freeze keine Clef-Ausgaben dieser Fälle. Nach Ergebnisansicht werden keine Testfälle, Labels, Prompts, Schwellen oder Messregeln zur Verbesserung von Scores angepasst. Fehlerkorrekturen würden eine gesonderte, offen dokumentierte Version und Neubewertung verlangen.

Wesentliche Grenzen:

- Klein, synthetisch, KI-verfasst, bewusst balanciert und herausforderungsorientiert; keine repräsentative Stichprobe deutscher Produktionsanfragen
- Einzelne klare Fälle und explizite Regeln können Ergebnisse vereinfachen; künstliche Sprachfehler und Angriffe können Ergebnisse auch erschweren
- Die 30 Übersetzungen reichen nicht für belastbare Aussagen über allgemeine Mehrsprachigkeit; Übersetzungsartefakte und semantische Restunterschiede bleiben möglich
- Kein sicherer Nachweis von Trainingsdatenfreiheit: Fälle wurden neu formuliert, aber allgemeine Ticketmuster können Trainingsdaten ähneln; nach Veröffentlichung kann dieser Satz selbst kontaminiert werden
- Keine Prüfung von `noul`, `score`, Mehrfragen-Abhängigkeiten, Bild-/Videoeingaben, langen Kontexten, echter Toolausführung, produktiver Sicherheit oder Finetuning
- Sechs Prompt-Injection-Fälle sind eine kleine Robustheitsprobe, keine Sicherheitszertifizierung
- Resultate müssen Modell-ID, Revision, Decision-Head, Quantisierung, Softwareversionen, Hardware, Trunkierung und Fehlerraten nennen. Ein NF4-CPU-Lauf gilt nur für genau diese Konfiguration
- Keine Einsatzfreigabe für automatische Finanz-, Sicherheits-, Personal- oder sonstige folgenreiche Entscheidungen; passende echte, datenschutzgerecht erhobene Testfälle und menschliche Prüfung bleiben erforderlich
