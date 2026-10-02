# Clef Deutsch: separate Finanz-/Makler-Erweiterung v1

Erstellt am 2. Oktober 2026. Dieser eigenständige Diagnosesatz ergänzt den allgemeinen deutschen Entscheidungsbenchmark: **80 vollständig synthetische deutsche Fälle und 20 englische Kontrollübersetzungen, insgesamt 100 native Entscheidungsanfragen**. Der ursprüngliche Benchmark bleibt unverändert. Beide Sätze sind getrennt auszuwerten; ein gemeinsamer Gesamtwert ist nicht vorab definiert.

## Aussagebereich und Sicherheit

Der Satz prüft, ob ein Modell deutschsprachige Anliegen aus einem Finanzberatungs-/Versicherungsmaklerumfeld anhand **explizit erfundener TEST-Richtlinien** klassifizieren kann. Die Szenarien orientieren sich sprachlich an typischen Vorgängen einer Finanzberatung oder eines Maklerbüros. Sie behaupten weder tatsächliche Arbeitsabläufe eines bestimmten Unternehmens noch eine Kooperation, Freigabe oder Konformität mit dessen Vorgaben.

- Keine echten Personen, Kundenakten, Gesundheits-, Vermögens-, Konto- oder Vertragsdaten
- Keine Bewertung von Kreditwürdigkeit, Versicherbarkeit, Leistungsberechtigung oder Produkteignung
- Keine individualisierte Finanz-/Rechtsberatung, keine Transaktionen, keine Weitergabe von Dokumenten, keine echten Vertragsaktionen
- Vollmacht, Einwilligung und Dokumentenvollständigkeit werden ausschließlich gegen die mitgelieferte fiktive Checkliste geprüft; diese ist **keine vollständige oder behauptete gesetzliche Compliance-Regel**
- Kündigung und Widerruf werden nur nach der im Test definierten Absicht unterschieden. Ein Label sagt nichts über Existenz, Voraussetzungen, Wirksamkeit oder Frist eines tatsächlichen Rechts aus
- Die siebentägige Dokumentenfrist in Test B ist frei erfunden, keine gesetzliche Frist. Kalenderarithmetik bleibt reine Rechenprüfung
- Riskante oder täuschende Wünsche werden ausschließlich als Weiterleitungs-/Prüfkategorie erkannt. Ein Label wie `ready`, `routine`, `savings_change` oder `recommendation` erlaubt keine Handlung und enthält keine Empfehlung

**Diagnostischer synthetischer Test, keine Produktions-, Rechts-, Regulierungs- oder Sicherheitsvalidierung.** Für einen echten Einsatz wären separat konzipierte, fachlich und datenschutzgerecht geprüfte Fälle, reale Prozessvorgaben und qualifizierte menschliche Kontrolle erforderlich. Die Domänennähe der Formulierungen ist kein Nachweis fachlicher Vollständigkeit.

## Kategorien

Jede Kategorie enthält zehn deutsche Fälle, jeweils zwei pro Klasse:

| Kategorie | Inhalt | Klassen | EN-Paare |
|---|---|---|---:|
| `insurance_intent` | Versicherungsanliegen | quote, coverage_info, contribution, termination, clarify | 3 |
| `claims_route` | Schaden-/Leistungsanliegen routen | new_claim, claim_status, evidence, benefit_question, clarify | 3 |
| `contract_service` | Bestandsservice und Beendigungsabsicht | copy, data_change, cancellation, withdrawal, clarify | 3 |
| `broker_workflow` | Erfundene Vollmacht-/Einwilligungs-/Unterlagencheckliste | ready, missing_authority, missing_consent, missing_documents, conflict | 3 |
| `broker_document` | Funktion synthetischer Maklerdokumente | application, policy, advisory_record, authority, other | 2 |
| `finance_intent` | Finanz-/Depot-/Sparplanabsichten | general_info, portfolio_view, savings_change, recommendation, clarify | 2 |
| `synthetic_rule_check` | Summenabgleich und erfundene administrative Datumsregel | passes, fails, missing, conflict, out_of_scope | 2 |
| `advice_escalation` | Routine, Rückfrage oder fachliche Prüfung erkennen | prohibited_request, qualified_review, clarify, routine, out_of_scope | 2 |

Enthalten sind Negationen, Selbstkorrekturen, falsche Überschriften, historische oder bloß zitierte Aussagen, fehlende Unterlagen, Geltungsbereich von Einwilligungen, bewusst widersprüchliche Angaben, Dezimalkomma, Monatsgrenzen und sieben deutsche Prompt-Injection-Fälle. Tags beschreiben beabsichtigte Herausforderungen im deutschen Original; Übersetzungen müssen nicht dieselben orthografischen Merkmale haben. Die Fälle sind KI-verfasst und anspruchsorientiert ausgewählt, keine repräsentative Stichprobe produktiver Anfragen.

Bei fünf gleichverteilten Klassen je Kategorie wäre gleichverteiltes Raten im Erwartungswert 20 Prozent korrekt. Das ist ein theoretischer Referenzwert, keine ausgeführte Modellbaseline.

## Native Schnittstelle und Datenisolation

Verwendet wird die native `choice`-Frage `decision`, entsprechend dem ursprünglichen Benchmarkvertrag und der [offiziellen Clef-Schnittstellenbeschreibung](https://developers.cloudflare.com/workers-ai/models/clef/) beziehungsweise der [Clef-Flash-Modellkarte](https://huggingface.co/Cloudflare/clef-flash).

```json
{"id":"Fallkennung","request":{"model":"clef-flash","state":"synthetischer Eingabetext","questions":{"decision":{"type":"choice","instructions":"vollständige erfundene Testregel","criteria":{"label":"Beschreibung"}}}}}
```

Nur `request` wird dem Inferenzdienst übergeben; lokale native Encoder verwenden `state` und `questions`. Die ID dient nur der Zuordnung im Runner. Goldlabel, Begründung, Kategorie, Tags, Split und Paarzuordnung gelangen nicht in den Modellinput. Absichtlich falsche Antwortanweisungen in Angriffsfällen sind Teil der unzuverlässigen Eingabe, kein versteckter Goldhinweis. Die übergeordnete Aufgabenanweisung grenzt diese explizit ab.

Die Fragen testen feste Entscheidungen, keine freie Textgenerierung. Ein Runner muss den nativen Entscheidungskopf nutzen und darf eine generische Textgenerierung nicht als gleichwertigen Ersatz ausgeben. Identische Klassen-ID-Reihenfolge wird zwischen den Sprachen beibehalten; Optionsreihenfolge wird nicht variiert und mögliche Reihenfolgeeffekte werden hier nicht isoliert.

## Dateien und Wiederholung

- `cases.jsonl`: 80 deutsche Hauptfälle und 20 englische Kontrollen mit Goldlabel und fester Begründung
- `requests.jsonl`: 100 label-freie native Requests in deterministisch gemischter Reihenfolge; Seed 2026100202
- `gold.jsonl`: separate Sollantworten und Metadaten
- `pairs.jsonl`: exakte Zuordnung der 20 DE/EN-Paare
- `diagnostic_cases.jsonl`: absichtlich leer zur Dateivertragskompatibilität; keine gemischtsprachigen Zusatzanfragen
- `policies.json`: alle acht vollständigen Regeln und Klassenbeschreibungen in beiden Sprachen
- `design_summary.json`: Mengen, Labels und Herausforderungen
- `build_benchmark.py`: deterministische Assemblierung der handverfassten synthetischen Fälle; verweigert Neuaufbau am eingefrorenen Ort
- `score.py`: eigenständiger Offline-Scorer; Metrikkern vom Original wiederverwendet, Auswahl der Kategorien/Splits/Paare separat angepasst
- `validate.py`: Schema-, Isolations-, Mengen-, Paar-, deterministische Rebuild- und Scorerprüfungen einschließlich fehlender Paarhälften und fehlerhafter Antwortobjekte ohne Modellzugriff
- `pre_inference_review.md`: unabhängige Vorabprüfung und dokumentierte Korrektur
- `encoding_preflight.json`: nativer Tokenizer-/Encoder-Vorabtest ohne Modellinferenz
- `freeze_manifest.json`: SHA-256-Sperrmarke nach abgeschlossener Vorabprüfung und vor Inferenz

Aus dem Verzeichnis ausführen:

```bash
python validate.py
python score.py /pfad/zu/finance_predictions.jsonl --out /pfad/zu/finance_scores.json
```

Alle Datenpfade werden relativ zur jeweiligen Skriptdatei aufgelöst. Keine Konten, API-Schlüssel oder Netzverbindung sind für die Datei-/Scorerprüfungen erforderlich. Ein Neuaufbau zur Vergleichsprüfung erfolgt in einem temporären Verzeichnis und überschreibt keine eingefrorenen Dateien.

Der Scorer akzeptiert native Antworten mit `id` und `response.answers.decision` oder unmittelbar `answers.decision`. Er erhält den bisherigen Vertrag für `choice`, `type`, `confidence`, `probabilities`, optional `probabilities_unrounded.decision`, `latency_ms` und `error`. Doppelte oder unbekannte IDs werden abgelehnt. Seine Unit-Tests erzeugen künstliche Antwortobjekte ausschließlich zur Programmprüfung; deren perfekte Werte sind keine Modellresultate.

## Vorab festgelegte Auswertung

**Primär ist die Auswahlgenauigkeit auf allen 80 geplanten deutschen Fällen.** Fehlende Ausgaben, Laufzeitfehler und unbekannte Labels zählen dabei als falsch. Gültige Auswahlgenauigkeit und strengere Genauigkeit mit vollständiger nativer Schemagültigkeit werden ergänzend angegeben. Unvollständige Runs sind vorläufige Untergrenzen, keine abgeschlossenen Modellbewertungen.

Weitere Kennzahlen:

1. Pro Kategorie Accuracy, Precision/Recall/F1 je Klasse und Macro-F1. Deutsches Gesamt-Macro-F1 ist das ungewichtete Mittel der acht Kategorie-Macro-F1-Werte, keine gemeinsame F1 über inkompatible Labelräume
2. Native Schema-Gültigkeit: Typ, erlaubtes Label, endlicher vollständiger Wahrscheinlichkeitsvektor in [0,1], Summe innerhalb 0,001 von 1 sowie Konsistenz von Auswahl, Argmax und Confidence. Die bestehenden Rundungstoleranzen bleiben unverändert
3. Kalibrierung, sofern verfügbar: mehrklassiger Brier-Score als Summe über Klassen, NLL mit Clip 1e-12 und ECE mit fünf gleich breiten Bins. Vollpräzise Wahrscheinlichkeiten werden bevorzugt. ECE verwendet schema-gültige Fälle; Wahrscheinlichkeitsscores und ihre Fallzahlen werden separat ausgewiesen
4. Coverage und Accuracy bei festen Konfidenzschwellen 0,60 / 0,80 / 0,90 / 0,95; keine nachträgliche Optimierung dieser Schwellen
5. Kategoriebezogene Zurückstellungsdiagnose: `clarify` in Anliegen-/Servicekategorien; fehlende Punkte und `conflict` in der Maklercheckliste; `missing/conflict/out_of_scope` bei Rechentests; alle Klassen außer `routine` bei Eskalationsrouting. `missed_deferral_rate` bedeutet einen Klassifikationsfehler relativ zu dieser Testmenge, keine gemessene echte Gefährdung. `other`, `fails` und die reine Intentklasse `recommendation` werden nicht pauschal als Abstention behandelt
6. DE/EN-Paare: beide richtig, beide falsch, nur DE richtig, nur EN richtig und gepaarte Accuracy-Differenz; exakter zweiseitiger McNemar-Test nur explorativ. `paired_all_planned` wertet alle 20 geplanten Paare aus, fehlende/fehlerhafte/ungültige Hälften als falsch. `paired` ist ergänzend auf beidseitig gültige Auswahlen begrenzt; ausgeschlossene Hälften werden ausdrücklich gezählt. Unterschiede im ersten Wert können auch Ausgabereliabilität statt Sprache widerspiegeln
7. Latenz: Median und p95, wenn gemessen. Modellladen, Warm-up, Tokenisierung und Inferenz getrennt dokumentieren. CPU-/Quantisierungsergebnisse sind kein Vergleich mit beworbenen GPU-/API-Latenzen

### Besonderheit der englischen Kontrollen

Die 20 Paare wurden bewusst nach Herausforderungen ausgewählt, nicht zufällig; je Kategorie sind nur zwei oder drei der fünf Goldklassen vertreten. `macro_f1` / `macro_f1_all_policy_labels` und das aggregierte `category_macro_f1` berücksichtigen trotzdem sämtliche fünf Klassen, fehlende Goldklassen mit F1=0. Bei perfekter EN-Vorhersage beträgt der Wert daher je Kategorie 0,4 oder 0,6 und insgesamt 0,5. Ergänzend gibt es `macro_f1_observed_support` / `category_macro_f1_observed_support`, die nur Goldklassen mit positiver Unterstützung berücksichtigen. Keine der beiden EN-F1-Varianten darf als unmittelbare Sprachlücke zum vollen deutschen Hauptsatz gelesen werden.

**Sprachvergleiche erfolgen ausschließlich anhand der gepaarten Korrektheit derselben 20 Vorgänge.** Deutsch/Deutsch gegenüber Englisch/Englisch ändert sowohl Eingabesprache als auch Regel- und Beschreibungssprache. Es ist keine isolierte Messung der deutschen Sprachfähigkeit. Anders als der allgemeine Benchmark enthält diese Erweiterung keine Deutsch/Englisch-Schemadiagnose. Übersetzungen erhalten die Bedeutung, nicht Wortfolge, Länge oder eine nachweislich identische Schwierigkeit.

## Vorabprüfung, Freeze und Grenzen

Die Daten werden vor der ersten Inferenz dieser Erweiterung mit festen Begründungen erstellt, unabhängig geprüft und gehasht. Der Autor dieser Erweiterung hat keine Originalbenchmark-Modellausgaben zur Gestaltung oder Optimierung dieser Fälle herangezogen. Der unabhängige Prüfer kannte Ergebnisse des vorherigen allgemeinen Experiments; die Prüfung ist deshalb **vorab und blind gegenüber den neuen Finanz-Ergebnissen**, nicht gegenüber sämtlichen früheren Experimenten. Korrekturen sind auf semantische Eindeutigkeit, Übersetzung, Isolation und Auswertungsrichtigkeit beschränkt. Die separate Prüfung ersetzt keine menschliche Fachannotation.

Nach Ansicht der Finanzresultate dürfen Fälle, Goldlabels, Regeln, Kontrollauswahl, Schwellen und Scoring nicht stillschweigend für bessere Resultate verändert werden. Notwendige Fehlerkorrekturen verlangen eine neue dokumentierte Version und erneute Auswertung. Der Freeze deckt Daten, Regeln, Aufbau, Scorer, Validator und Dokumentation ab; Laufresultate werden separat abgelegt.

Zusätzliche Grenzen: nur zwei Beispiele je Klasse; kein repräsentativer Produktionsmix; teilweise explizite, dadurch vereinfachende Intentformulierungen; kleines Angriffs- und Rechenrepertoire; keine Prüfung langer Akten, OCR, Mehrfragen-Abhängigkeiten, realer Werkzeugausführung oder komplexer Beratung; keine belastbare allgemeine Kalibrierungs-, Robustheits- oder Sicherheitsgarantie. Neu formulierte Fälle können allgemeinen Trainingsmustern ähneln; nach Veröffentlichung kann der Satz selbst kontaminiert werden. Jedes Ergebnis muss Modell-ID/Revision, nativen Entscheidungskopf, Quantisierung, Software, Hardware, Kontext-/Trunkierungsgrenzen und Fehlerquoten nennen und gilt nur für die konkret gemessene Konfiguration.
