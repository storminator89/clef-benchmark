# Clef Flash: Nachfragen statt raten

## Ergebnis dieses eingefrorenen Tests

- Beide Felder exakt: **64/72 (88.9 %)**
- Nächster Schritt: 65/72 (90.3 %)
- Ja/Nein/offen-Feststellung: 66/72 (91.7 %)
- Erforderliche Rückfragen übergangen: 4/36 (11.1 %)
- Überflüssige Rückfragen bei beantwortbaren Fällen: 2/36 (5.6 %)
- Falsche Rückfrageart: 1/36 (2.8 %)
- Riskante falsche konkrete Antworten: 4/72 (5.6 %); unter den konkreten Modellantworten 4/37 (10.8 %)
- Technisch gültige Fälle: 72/72; inkonsistente Feldkombinationen: 3

Ein riskanter Fehler bedeutet hier eine konkrete Ja/Nein-Antwort, obwohl die Information nicht entscheidbar war oder das richtige Ergebnis das Gegenteil ist. Es wurden keine echten Leistungen oder Transaktionen ausgeführt.

## Hohe Modellscores

Eine „zuversichtliche Antwort“ verlangt, dass die gewählte Antwortoption in beiden Feldern mindestens die angegebene Wahrscheinlichkeit hat. Das sind rohe marginale Softmax-Scores, keine nachgewiesene kalibrierte oder gemeinsame Wahrscheinlichkeit. Die Schwellen waren vor dem Lauf festgelegt.

- Schwelle 0.8: 0 falsche von 23 zuversichtlichen konkreten Antworten; 0/23 (0.0 %)
- Schwelle 0.9: 0 falsche von 5 zuversichtlichen konkreten Antworten; 0/5 (0.0 %)
- Schwelle 0.95: 0 falsche von 0 zuversichtlichen konkreten Antworten; 0/0 (nicht definiert)

Die 0,90-Schwelle erfasst nur 5 von 72 Testfällen (5 von 37 konkreten Modellantworten); bei 0,95 bleibt gar keine konkrete Antwort übrig. Null Fehler in so wenigen ausgewählten Fällen sind kein Zuverlässigkeits- oder Sicherheitsnachweis. Eine falsche Antwortaktion im unklaren Kontoauszug-Fall hatte bereits einen Score von 0,864; die gleichzeitig falsche Ja-Feststellung hatte 0,742. Die Zwei-Feld-Schwelle darf daher nicht als Aussage über jeden einzelnen hohen Feldscore gelesen werden.

## Beobachtetes Fehlermuster

Alle acht nicht in beiden Feldern korrekten Fälle liegen in zwei Gruppen: fünf Fälle mit unbestimmtem Zielvorgang und drei beantwortbare Fälle trotz einer Lücke. Bei vier unbestimmten Zielvorgängen wählte Clef eine Antwortaktion, obwohl zuerst geklärt werden musste, welcher Vorgang gemeint war. Bei zwei logisch bereits entschiedenen Nein-Fällen fragte es unnötig nach weiteren Angaben. Im Giro-Entgeltfall antwortete es fälschlich Ja, obwohl ausdrücklich kein Gehalt, sondern nur eine private Rückzahlung eingegangen war.

Die drei inkonsistenten Feldpaare sind zusätzlich wichtig: Eine Anfrage kann zugleich eine Rückfrageaktion und eine konkrete Feststellung erhalten oder eine Antwortaktion und „unresolved“. Strukturell gültige Einzelfelder garantieren keine gemeinsame inhaltliche Konsistenz. Der native Output wurde weder repariert noch durch nachgelagerte Regeln ersetzt.

## Teilgruppen

| Gruppe | Fälle | Beide Felder exakt |
|---|---:|---:|
| finance | 24 | 20/24 (83.3 %) |
| insurance | 24 | 22/24 (91.7 %) |
| banking | 24 | 22/24 (91.7 %) |
| ambiguous_target | 12 | 7/12 (58.3 %) |
| complete_yes | 12 | 12/12 (100.0 %) |
| conflicting_evidence | 12 | 12/12 (100.0 %) |
| missing_fact | 12 | 12/12 (100.0 %) |
| complete_no | 12 | 12/12 (100.0 %) |
| sufficient_despite_omission | 12 | 9/12 (75.0 %) |

## Lauf und Reproduzierbarkeit

Cloudflare/clef-flash, offizielle Revision `17f0b0ad64efb65d273590632833508766b2aae6`. Experimenteller CPU-NF4-Backbone mit ursprünglichem BF16-Joint-Head und BF16-Ausgabe-Embeddings, sechs Threads, Batch 1, unverändertes offizielles Encoding. Kein GPU- oder BF16-Vergleich.

- 689–757 Eingabetokens je Fall; kein Abschneiden
- Forward-Laufzeit Median 20.77 s; p95 25.30 s
- Summe der 72 bewerteten Forward-Läufe 1511.02 s
- Modellladezeit 59.79 s; separat vom Forward-Timing
- Höchster beobachteter Fall-RSS 5.73 GiB
- Start 2026-10-02T14:00:14.893486+00:00; Ende 2026-10-02T14:27:04.672883+00:00

Ein fachfremder technischer Warmup und eine Wiederholung des ersten Falls sind aus Qualitäts- und Laufzeitaggregaten ausgeschlossen. Alle 72 Ausgaben einschließlich aller Optionen und ungerundeten Scores bleiben erhalten. Ein einzelner Wiederholungsfall beweist keine allgemeine Reproduzierbarkeit. Die Hardwaremessung ist nicht auf andere CPUs, GPU-Betrieb oder Produktivlast übertragbar.

## Was der Test aussagt und was offen bleibt

72 neu KI-verfasste deutsche Fälle: je 24 aus Banking, Versicherung und Finanzen, organisiert in zwölf verwandten Regelfamilien. Je zwölf Fälle prüfen eine fehlende entscheidende Angabe, einen unklaren Zielvorgang, widersprüchliche Angaben, ein vollständiges Ja, ein vollständiges Nein und ausreichende Informationen trotz einer Lücke. 36 Fälle brauchen eine Rückfrage, 36 sind beantwortbar. Damit wird pauschales Nachfragen bestraft.

Alle Regeln und Zahlen sind ausdrücklich fiktiv. Die Goldantworten wurden vor dem Lauf von einer anderen KI geprüft; zwei Formulierungsprobleme in den Eingaben wurden korrigiert, die Labels blieben unverändert. Kein menschlicher Fachexperte hat sie validiert. Die Rohversionen und Änderungen sind im Audit erhalten.

Die Szenarien sind bewusst klar annotierbar: einfache UND-Regeln, teilweise ausdrücklich benannte Lücken und gleichrangige Konflikte. Das erleichtert die Aufgabe und begrenzt die Nähe zu echten, undeutlichen Kundengesprächen. Eine Antwortoption wählen ist nicht dasselbe wie eine passende deutsche Rückfrage formulieren.

Die verwandten Fälle sind keine unabhängigen Stichproben; Teilgruppen enthalten nur zwölf oder 24 Fälle. Alle Prozentsätze beschreiben genau dieses festgelegte Set. Es gibt keinen Anspruch auf Bevölkerungsgenauigkeit, seltene Schadenssicherheit, Produktivreife, echte Finanzberatung oder statistische Überlegenheit gegenüber anderen Benchmarks. Keine naiven Signifikanztests und kein Zusammenwerfen verschiedener Suiten.

## Dateien

- PROTOCOL.md: vorab festgelegte Definitionen und Grenzen
- data/requests.jsonl: die einzigen Modellinputs; Gold separat
- freeze_manifest.json: Hash-Freeze vor Inferenz
- audit/pre_inference_review.md: unabhängige KI-Prüfung und Änderungen
- results/predictions.jsonl: vollständige Ausgaben und Rohscores
- results/case_scores.jsonl: strikt ID-bezogene Bewertung
- ERRORS.md: sämtliche nicht vollständig richtigen Fälle
- reference_runtime/: genaue Laufzeitquellen, Pakete und Modellhashes
