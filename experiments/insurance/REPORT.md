# Clef: Verständnis synthetischer Versicherungsunterlagen

- Entscheidung richtig: **51/60 (85,0 %)**
- Belegmenge richtig: **58/60 (96,7 %)**
- Vollständig richtiger Fall: **50/60 (83,3 %)**

60 deutschsprachige Fälle, sechs Bereiche und zwölf synthetische Dokumentpakete. Je fünf Fälle teilen dieselben Klauseln. Das ist ein kleiner kontrollierter Funktionstest, kein unabhängiger oder repräsentativer Produktionstest. Alle Bedingungen und Fälle sind erfunden; keine reale Produkt- oder Rechtsberatung.

## Nach Verständnisbereich

| Bereich | Entscheidung | Belegmenge | Vollständiger Fall |
|---|---:|---:|---:|
| Deckungsumfang und Definitionen | 8/10 (80,0 %) | 9/10 (90,0 %) | 7/10 (70,0 %) |
| Ausschlüsse und Rückausnahmen | 9/10 (90,0 %) | 10/10 (100,0 %) | 9/10 (90,0 %) |
| Voraussetzungen und Obliegenheiten | 9/10 (90,0 %) | 10/10 (100,0 %) | 9/10 (90,0 %) |
| Nachweise und Verfahrensstatus | 10/10 (100,0 %) | 10/10 (100,0 %) | 10/10 (100,0 %) |
| Nachträge und Dokumentvorrang | 7/10 (70,0 %) | 9/10 (90,0 %) | 7/10 (70,0 %) |
| Unvollständige und widersprüchliche Akten | 8/10 (80,0 %) | 10/10 (100,0 %) | 8/10 (80,0 %) |

## Fehlerbild

Nur die Entscheidung richtig, Belegmenge falsch: 1 Fälle. Nur die Belegmenge richtig, Entscheidung falsch: 8 Fälle.

| Referenzentscheidung | Richtige Entscheidung | Vollständiger Fall |
|---|---:|---:|
| nein | 21/27 (77,8 %) | 21/27 (77,8 %) |
| ja | 16/16 (100,0 %) | 15/16 (93,8 %) |
| offen | 11/14 (78,6 %) | 11/14 (78,6 %) |
| konflikt | 3/3 (100,0 %) | 3/3 (100,0 %) |

Entscheidung: 0 falsche Auswahlen mit mindestens 90 % maximalem Softmax-Wert.

Belegmenge: 0 falsche Auswahlen mit mindestens 90 % maximalem Softmax-Wert.

In acht der neun Fälle mit falscher Entscheidung wählt Clef dennoch die richtige angebotene Belegmenge. Die beobachtete Schwäche liegt hier daher häufiger in der Anwendung einer gefundenen Regel als in der Auswahl ihrer Textstelle; aus der Auswahl folgt allerdings kein Nachweis des internen Denkwegs.

- Vier ausdrücklich zu verneinende Aussagen werden bejaht: fehlende Rückwirkung des Nachtrags, berufliche Nutzung trotz Rückausnahme, eine nicht erfüllte UND-Voraussetzung sowie falscher Versicherungsort
- Ein fehlender Schadentag führt zusätzlich zu einem unbelegten `ja`; zwei andere unvollständige Akten werden als `nein` statt `offen` eingestuft
- Zweimal wird ein `konflikt` gewählt, obwohl die genau gestellte Aussage klar zu verneinen ist. Alle drei tatsächlichen Konfliktfälle werden erkannt; drei Fälle erlauben keine allgemeine Robustheitsaussage

Die vollständige Fehlerliste enthält jeden abweichenden Fall samt exaktem Modelloutput, Referenz und Klauseltext in [ERRORS.md](ERRORS.md). Eine passende Belegmenge allein beweist nicht, dass Clef sie kausal für die Entscheidung verwendet hat. Hohe Softmax-Werte sind keine validierte Zuverlässigkeitsgarantie.

## Kontrolle der Rechenabgrenzung

Keine Summen, Betragsklassen, Selbstbeteiligungen oder Fristberechnungen. Die drei explizit markierten Fälle zur Anwendung eines Nachtragsdatums erreichen 1/3 (33,3 %) vollständig richtige Fälle. Ohne diese drei Fälle: 50/57 (87,7 %) Entscheidungen, 55/57 (96,5 %) Belegmengen und 49/57 (86,0 %) vollständige Fälle.

## Vergleichsmaßstab und Lauf

Die häufigste Referenzentscheidung ist `nein`; ständiges Wählen der häufigsten Klasse erzielt 45,0 %. Klassen-Balanced-Accuracy des Modells: 89,1 %. Eine gleichverteilte zufällige Belegauswahl erzielt im Erwartungswert 20 %. Ständiges Wählen der häufigsten Belegoption b1 erreicht hier bereits 20/60 (33,3 %); diese stärkere Positionsbaseline wird ebenfalls ausgewiesen. Das häufigste feste Paar aus Entscheidungs- und Belegoption erreicht 11/60 (18,3 %) vollständig richtige Fälle. Diese Baselines ersetzen keine größere externe Validierung.

Ein primärer Lauf mit 60 Fällen und 120 nativen Choice-Feldern. Alle 60 vollständigen Inputs passten ungekürzt in den unveränderten 2.048-Token-Deckel: 835–917 Tokens, Median 864.5. Median der reinen Inferenzzeit 20.61 s/Fall, P95 (Nearest Rank) 24.66 s. Laden und separates Warm-up sind nicht darin enthalten.

Modell: `Cloudflare/clef-flash`, Revision `17f0b0ad64efb65d273590632833508766b2aae6`. CPU NF4, BF16-Rechnung und originaler BF16-Joint-Head sowie Ausgabe-Embeddings, Batch 1, sechs Threads. Dieselbe Laufzeit und derselbe unveränderte Runner wie im vorausgehenden Textpilot. Kein paralleler Modellprozess und kein Upgrade. Diese Konfiguration ist keine Hersteller-GPU- oder ROCm-Leistungsmessung.

## Nachvollziehbarkeit

Alle Labels und Belegoptionen wurden vor Inferenz durch einen separaten KI-Reviewer überprüft und korrigiert, dann per SHA-256 eingefroren. Keine externe menschliche Fachprüfung. Der Inferenzprozess las nur die label-freien Requests. Die Referenzbegründungen stammen aus dem Testdatensatz, nicht aus Clef. Primärer Lauf ohne Nachoptimierung von Labels oder Prompts anhand der Ergebnisse.

Vollständige Methodik: [METHODOLOGY.md](METHODOLOGY.md). Daten: `benchmark/`; tatsächliche Modelloutputs und ungerundete Wahrscheinlichkeiten: `results/`; Vorab-Freeze, Audit und nachträgliche unabhängige Score-QA: `qa/`. Reproduktion: `scripts/reproduce.sh`. Eine vollständige Neuinstallation wurde für diese Veröffentlichung nicht zusätzlich ausgeführt; der dokumentierte Lauf nutzt die bereits gepinnte Umgebung.
