# Clef: Pilot für deutschen Bankkundenservice

**Alle drei Felder richtig: 68/80 (85.00 %).**

- Anliegen/Route: 76/80 (95.00 %)
- Priorität: 77/80 (96.25 %)
- Nächster Supportschritt: 75/80 (93.75 %)
- Insgesamt richtige Teilentscheidungen: 228/240 (95.00 %)

## Einordnung

Als einfacher Häufigkeitsmaßstab erreicht die konstante Vorhersage routine beim Prioritätsfeld 64/80 (80 %). Deshalb sind kritische/dringende Fehlzuordnungen und die gemeinsame Drei-Feld-Genauigkeit wichtiger als eine isolierte hohe Prioritätsquote.

80 neu geschriebene synthetische Nachrichten für den Privatkundenservice einer fiktiven Bank. Drei native Choice-Felder pro Fall, ein eingefrorener Hauptlauf. Eigener deutscher Support-Pilot; kein BANKING77, keine repräsentative Stichprobe des Bankverkehrs und kein numerischer Vergleich mit Hersteller- oder Jev-Ergebnissen. Andere Testsuiten werden nicht eingerechnet.

Geprüft werden begrenzte Entscheidungen über Route, Dringlichkeit und die Art des nächsten Schritts. Das Modell formuliert keine freie Antwort. Die in den Daten gespeicherten konkreten Rückfragen stammen von den Testautoren, nicht von Clef. Es wird weder Geld bewegt noch eine Karte gesperrt oder ein Rechts-/Erstattungs-/Kreditanspruch entschieden.

## Sicherheitsrelevante Fehler

Vollständig richtige kritische Fälle: 8/10 (80.00 %). Zwei kritische Nachrichten wurden zur falschen Intent-Route eingeordnet (unerwartete TAN-Anforderung und unautorisierte Lastschrift), obwohl das Modell jeweils critical und security_handoff richtig wählte. Null verfehlte Sicherheitsweiterleitungen bedeutet deshalb nicht, dass alle kritischen Fälle vollständig richtig waren.

- Kritische Priorität verfehlt: 0/10
- Erforderlichen sofortigen Sicherheitsweg verfehlt: 0/10
- Kritische Fälle mit mindestens einem dieser beiden Fehler: 0/10
- Dringende Fälle fälschlich als routine eingestuft: 0/6
- Unnötige critical-Einstufungen: 0/70 nicht-kritische Referenzfälle
- Unnötige Sicherheitsweiterleitungen: 1/70
- Unnötige Eskalationen statt Information/Rückfrage: 3/45

„Unnötige Eskalation“ ist hier eng definiert: Referenz guidance oder clarify, Modell specialist_review oder security_handoff. Normale fachliche Prüfaufträge zählen nicht als unnötige Eskalation. Sicherheitskennzahlen sind keine umfassende Messung von Sicherheit; zehn kritische Fälle reichen nicht zum Nachweis seltener Fehlerraten.

## Routing-bereite Fälle und notwendige Rückfragen

route_ready bedeutet: Der nächste Supportweg ist aus der Nachricht bestimmbar. Es bedeutet nicht, dass alle Angaben zur späteren Bearbeitung vorliegen; ein Sicherheitsweg kann trotz unklarer Einzelheiten sofort nötig sein. clarification_needed bezeichnet Fälle, in denen zuerst eine konkrete nicht-geheime Sachfrage oder die Reihenfolge geklärt werden muss.

- route_ready: alle drei Felder 58/66 (87.88 %); nächster Schritt 64/66 (96.97 %)
- clarification_needed: alle drei Felder 10/14 (71.43 %); nächster Schritt 11/14 (78.57 %)

Verfehlte notwendige Rückfragen: 3/14.

## Themen und Sprachformen

| Themenstratum | Fälle | Alle drei Felder richtig |
|---|---:|---:|
| access_tan | 8 | 7/8 (87.50 %) |
| account_documents | 8 | 8/8 (100.00 %) |
| ambiguous_multi | 8 | 6/8 (75.00 %) |
| cards | 8 | 7/8 (87.50 %) |
| cash | 8 | 8/8 (100.00 %) |
| direct_debits | 8 | 6/8 (75.00 %) |
| fees | 8 | 7/8 (87.50 %) |
| security | 8 | 7/8 (87.50 %) |
| standing_orders | 8 | 8/8 (100.00 %) |
| transfers | 8 | 4/8 (50.00 %) |

| Primärer Sprachform-Tag | Fälle | Alle drei Felder richtig |
|---|---:|---:|
| colloquial_typo | 8 | 6/8 (75.00 %) |
| multi_intent | 5 | 3/5 (60.00 %) |
| negation_context | 15 | 14/15 (93.33 %) |
| plain | 40 | 34/40 (85.00 %) |
| uncertain | 12 | 11/12 (91.67 %) |

Die zehn Themenstrata sind absichtlich gleich groß; die Goldlabels sind es nicht. Sprachform-Tags benennen den primären Schwerpunkt, nicht das Fehlen anderer Merkmale. Kategorienhäufigkeiten sind keine Schätzung realer Bankanfragen.

## Exakte Goldverteilungen

- intent: access_tan=9, account_documents=9, cards=9, cash=8, direct_debits=7, fees=8, security=10, standing_orders=8, transfers=8, unclear=4
- next_step: clarify=14, guidance=31, security_handoff=10, specialist_review=25
- priority: critical=10, routine=64, urgent=6

## Methode, Freeze und Prüfung

- Alle 80 Nachrichten und alle 240 Goldlabels vor dem Modelllauf separat geprüft
- Separater KI-Prüfer mit sichtbaren Goldlabels; keine verblindete menschliche oder bankfachliche Validierung
- Der erste Audit fand zwei nicht eindeutig spezifizierte Intents; die Nachrichten/Regeln wurden vor Freeze präzisiert. Goldlabels blieben unverändert
- Abschließender Audit: 80/80 Fälle und 240/240 Labels konsistent; genaue Prüfprotokolle im audit-Verzeichnis
- Ein Validatorfehler bei der Reihenfolge von JSON-Schlüsseln wurde vor jeder Inferenz korrigiert; der frühere Freeze und die Begründung sind archiviert. Modellinputs und Gold wurden dadurch nicht verändert
- Label-freie Requests getrennt von Gold und Metadaten; der Runner kodiert nur das innere request-Objekt, nicht die themenhaltigen IDs
- Kein Tuning an den Ergebnissen, keine ausgeschlossenen Fehler, keine gekürzten Eingaben
- Ein bewusst konstruierter Randfall (bank_ambiguous_multi_07) kombiniert globale Dringlichkeit mit zwei gleichrangigen Routen; seine Antwort folgt nur der ausdrücklich fiktiven Regel

## Laufzeit und technische Grenzen

- Modell: Cloudflare/clef-flash, Revision 17f0b0ad64efb65d273590632833508766b2aae6
- Experimentelle CPU-NF4-Quantisierung des Backbones, originale BF16-Kopf- und Output-Embedding-Gewichte; kein Ersatzmodell
- 6 CPU-Threads, Batch 1, 2048-Token-Grenze
- Gemessene Eingabelängen: 1549–1595 Tokens; 0 gekürzte Eingaben
- Schema-valide Fälle: 80/80
- Modell-Forward-Latenz: Median 40.877 s, p95 45.108 s
- Modellladen: 56.598 s, nicht in den Falllatenzen
- Maximaler Prozess-RSS laut Runner: 6.403 GiB
- Repeatability-Probe (erster Fall, außerhalb der Scores): maximale absolute Wahrscheinlichkeitsabweichung 0.0
- Der ursprüngliche offizielle Wrapper bleibt Englisch; Kundennachrichten und Anweisungen sind Deutsch
- Technischer Warmup und erste-Fall-Wiederholung sind aus Genauigkeit und Latenzaggregaten ausgeschlossen
- Modellrevision, unveränderter Runner, native Anfragen und Paketversionen sind für den wissenschaftlichen Lauf dokumentiert; private Wiederherstellungs- und Hostdiagnostik ist im öffentlichen Paket nicht enthalten
- CPU-Zeiten gelten ausschließlich für diesen dokumentierten Lauf; keine Hardware- oder Produktionslatenzvergleiche ableiten

## Beobachtete Fehlermuster

- Drei erforderliche Rückfragen wurden übersprungen: zweimal zugunsten einer Fachprüfung, einmal zugunsten allgemeiner Information
- Drei routine-Fälle wurden als urgent eingestuft: ausstehender Empfängereingang, doppelte bekannte Lastschrift und noch unbestätigte Doppelüberweisung
- Eine selbst verursachte technische Login-Sperre führte zu einem unnötigen Sicherheitsweg
- Zusätzlich gab es falsche Routen für eine Mietüberweisung und eine Kontaktlos-Einstellung sowie eine Fachprüfung statt allgemeiner Anleitung zur Empfängerprüfung
- Diese Beobachtungen beschreiben Fehler in diesem Satz, nicht deren interne Ursache oder ihre Häufigkeit in echten Tickets

## Nachvollziehbarkeit

- Jede Fehlentscheidung: [ERRORS.md](ERRORS.md)
- Rohwerte, alle Optionen und Messdaten: results/predictions.jsonl
- Konfusionsmatrizen, Strata und Definitionen: results/summary.json
- Quellen und genaue Grenzen: [SOURCES.md](SOURCES.md)
- Reproduktion und Dateistruktur: [README.md](README.md)
- Endgültige unabhängige Scorer-Prüfung: audit/independent_score_check.json

Der Test liefert keine Aussage über reale Kundenzufriedenheit, juristische Korrektheit, Rechtssicherheit, Betrugsdetektionsleistung im Livebetrieb, demografische Fairness oder Produktionsfreigabe. Wahrscheinlichkeiten sind keine kalibrierten Sicherheitsgarantien.
