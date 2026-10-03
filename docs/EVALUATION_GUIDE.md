# Methodik und Evidenz

Clef Lab prüft strukturierte Entscheidungen gegen vorab festgelegte Referenzlabels. Entscheidend sind die tatsächlich vorgelegte Aufgabe, die unveränderte native Antwort und der passende Nenner. [Ergebnisse](../README.md#ergebnisse-im-direkten-vergleich) · [Jev-Vergleich](JEV_COMPARISON.md) · [Reproduzieren](REPRODUCE.md)

## Was das Modell erhält

Jeder Request enthält den Falltext, die jeweils geltende fiktive Regel, native Fragen und die angebotenen Antwortoptionen. Goldlabels und Begründungen bleiben außerhalb der Inferenz. Mehrere Fragen eines Falls gehören zum selben Request; verschiedene Fälle werden nicht zusammengepackt. Die Clef-Läufe verwenden den nativen Decision Head, keine ersatzweise generierte Chatantwort.

Für Jev bleiben Zustand, Texte, Fragen, Feld- und Optionsreihenfolge sowie Aufgabenstruktur identisch. Nur die Modellkennung ändert sich. Die internen Tokenizer und die Verarbeitung der Anbieter können verschieden sein. Die vollständigen festgelegten Bedingungen stehen im [Vergleichsprotokoll](../experiments/jev_comparison/README.md).

## Wie Ergebnisse gezählt werden

- **Feldgenauigkeit:** richtige Auswahl eines einzelnen verlangten Felds.
- **Fallgenauigkeit:** sämtliche verlangten Felder eines Falls richtig. Ein gutes Quellenfeld gleicht eine falsche Entscheidung nicht aus.
- **Paargenauigkeit:** beide vollständigen Endpunkte richtig. Ein beliebiger Ausgabewechsel ist kein korrekter Übergang; unveränderte Ausgaben können stabil falsch sein.
- **Technische Gültigkeit:** Antwort erfüllt den festgelegten Vertrag für Felder, Optionen, vollständige Wahrscheinlichkeiten, Modellidentität und Nutzungsangaben. Das ist von fachlicher Richtigkeit getrennt.
- **Gesamter geplanter Umfang:** richtige gültige Fälle geteilt durch alle geplanten Fälle. Fehlende oder technisch ausgeschlossene Antworten erhöhen den Zähler nicht.
- **Gemeinsame gültige Auswahl:** beide Modelle werden auf denselben Fällen mit gültiger Jev-Antwort und verfügbarer Clef-Baseline verglichen. Diese bedingte Genauigkeit muss zusammen mit der Abdeckung erscheinen.

Suiten und Kontrollgruppen haben eigene Nenner. Es gibt keinen gepoolten Gesamtscore. Die 974 Jev-Requests und 1.362 nativen Fragen beschreiben den Ausführungsumfang, keine unabhängige Stichprobe. Für MASSIVE fehlt aktuell die auditierte Clef-Baseline; eine Null im technischen Baseline-Inventar bedeutet dort kein Modellresultat.

## Testdaten und Aussagegrenzen

Die meisten Fälle und Regeln sind KI-verfasst und synthetisch. Separate KI-Prüfungen vor dem jeweiligen Lauf helfen, fehlerhafte Labels zu finden, ersetzen aber keine menschliche Fachvalidierung. Später entwickelte Suiten können von früheren Ergebnissen beeinflusst sein; sie sind kein übergreifend verblindeter Holdout.

Versicherung nutzt fünf Fälle je Dokument. Rückfragen und Multidokumente teilen Regel- beziehungsweise Vorlagenfamilien. Minimalpaare, Sprachkontrollen und Sprachvarianten teilen Situationen; Angriffsentfernung verwendet sieben bereits getestete Finanzfälle erneut. Solche Beobachtungen dürfen nicht als unabhängige Stichproben zusammengezählt werden. Keine naive gepoolte Signifikanz- oder Produktionsrisikoschätzung folgt daraus.

MASSIVE verwendet einen eingefrorenen Ausschnitt des öffentlichen de-DE-Tests: 300 Fälle, 60 angebotene Intents und 59 im Gold vertretene Labels. Quellen und CC-BY-4.0-Attribution stehen in [SOURCES.md](../experiments/jev_comparison/inputs/massive300/SOURCES.md). Veröffentlichung und unbekannte Trainingsüberschneidungen begrenzen Aussagen zur Generalisierung.

## Scores und Laufzeit

Die nativen Verteilungen werden nicht normalisiert oder nachträglich repariert. Jevs eigenes Konfidenzmaß und Clefs historischer gerundeter Auswahlscore haben unterschiedliche Definitionen. Gemeinsame Schwellenanalysen verwenden deshalb die native Wahrscheinlichkeit der gewählten Option, nicht zwei gleich benannte Konfidenzwerte.

Die separate [Wahrscheinlichkeitsanalyse](../experiments/probability_reliability/REPORT_DE.md) ist post-hoc und deskriptiv: feste Schwellen, keine neue Inferenz, keine angepasste Kalibrierung. Feldselektion und die Auswahl ganzer Fälle nach dem kleinsten Feldscore bleiben getrennt. Ein Minimum marginaler Scores ist keine gemeinsame Richtigkeitswahrscheinlichkeit; eine leere Auswahl hat keine definierte Fehlerrate. Unterschiedliche historische Scorer haben ausdrücklich versionierte Metrikkonventionen.

Clefs `latency_ms` misst den lokalen CPU-Forward ohne Modellladen und separat erfasste Kodierung. Jevs HTTP-Zeit enthält Transport, Warteschlange und Anbieterberechnung. Diese Zahlen beschreiben verschiedene Messgrenzen und erlauben weder Geschwindigkeitsfaktor noch Kosten-Leistungs-Ranking.

## Evidenz nachschlagen

| Bereich | Eingaben und Referenzen | Native Ergebnisse und Auswertung |
|---|---|---|
| Allgemeine Entscheidungen | [benchmark](../benchmark/) | [results](../results/) |
| Finanzen und Makler | [finance_benchmark](../finance_benchmark/) | [results/finance](../results/finance/) |
| Büroentscheidungen ohne Manipulation | [clean72](../experiments/clean72/) | [Suite und Auswertung](../experiments/clean72/) |
| Angriffsentfernung | [Diagnose](../experiments/attack_ablation14/) | [Diagnose und Auswertung](../experiments/attack_ablation14/) |
| Bank-Support | [Suite](../experiments/bank-support/) | [Bericht](../experiments/bank-support/REPORT.md) |
| Versicherung | [Suite](../experiments/insurance/) | [Bericht](../experiments/insurance/REPORT.md) |
| Rückfragen | [Suite](../experiments/clarification72/) | [Bericht](../experiments/clarification72/REPORT.md) |
| Minimalpaare | [Protokoll](../experiments/minimal_pairs/PROTOCOL.md) | [Bericht](../experiments/minimal_pairs/REPORT.md) |
| Multidokumente | [Suite](../experiments/multidoc48/) | [Bericht](../experiments/multidoc48/REPORT.md) |
| Deutsche Sprachvarianten | [Suite](../studies/language72/) | [Bericht](../studies/language72/REPORT_DE.md) |
| Jev und gemeinsame Baselines | [Eingaben](../experiments/jev_comparison/inputs/) | [Vergleich und Endaudit](JEV_COMPARISON.md) |

Die zugehörigen Hashmanifeste, Rohantworten und protokollspezifischen Grenzen sind maßgeblich. Deterministisches Nachrechnen prüft die Auswertung, nicht unabhängig die fachliche Wahrheit der Labels. Software- und Browserchecks belegen ihren jeweiligen technischen Prüfbereich, keine Modellgenauigkeit. Historische Ausführungs- und UI-Nachweise bleiben für gezielte Nachprüfung erhalten.

## Übertragbarkeit

Die Ergebnisse gelten für die dokumentierten Aufgaben und Konfigurationen. Es fehlen repräsentative Kundendaten, unabhängige menschliche Annotation, ein unangetasteter anwendungsspezifischer Holdout und Nachweise für reale Sicherheit, Wirtschaftlichkeit oder Compliance. Für eine praktische Evaluation müssen Fehlerkosten, menschliche Entscheidungsverantwortung, Datenfreigabe und Akzeptanzkriterien separat festgelegt und geprüft werden.
