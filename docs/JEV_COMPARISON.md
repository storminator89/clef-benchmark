# Clef und Jev im Vergleich

Verglichen werden Cloudflare Clef Flash 9B im lokalen CPU-NF4-Profil und der gehostete Dienst `jev-1.13.0`. Beide erhalten dieselben eingefrorenen Texte, nativen Fragen und Antwortoptionen. Ein Fall ist nur vollständig richtig, wenn jedes verlangte Feld dem Goldlabel entspricht.

## Ergebnisse auf denselben Fällen

Beide Modelle werden je Zeile auf demselben geplanten Umfang bewertet. Gezählt werden die unveränderten nativen Antwortoptionen: Nur wenn alle Felder dem Gold entsprechen, ist der Fall richtig. Die Teilgruppen bleiben getrennt.

| Testgruppe | Clef richtig | Jev richtig |
|---|---:|---:|
| Minimalpaare, einzelne Fälle | 39/48 | 47/48 |
| Rückfragen | 64/72 | 71/72 |
| Bank-Support | 68/80 | 75/80 |
| Allgemeine Entscheidungen, Deutsch | 116/120 | 119/120 |
| Allgemeine Entscheidungen, deutscher Eingabetext / englisches Schema | 29/30 | 30/30 |
| Allgemeine Entscheidungen, Englischkontrolle | 29/30 | 30/30 |
| Finanzen, Deutsch | 76/80 | 78/80 |
| Finanzen, Englischkontrolle | 18/20 | 20/20 |
| Versicherungsdokumente | 50/60 | 56/60 |
| clean72 | 61/72 | 67/72 |
| Angriffsentfernung, mit Angriff | 4/7 | 6/7 |
| Angriffsentfernung, ohne Angriff | 5/7 | 7/7 |
| Mehrere Dokumente | 24/48 | 44/48 |
| MASSIVE de-DE | nicht verfügbar | 233/300 |

Bei Jev fehlt im Bank- und deutschen Finanztest jeweils eine auswertbare Antwort. Beide Fälle bleiben im Nenner und zählen nicht als richtig; sie belegen keine fachliche Fehlentscheidung.

Die acht Hauptgruppen zeigen jeweils mehr richtige Jev-Antworten. Die kleine synthetische Auswahl, abhängige Fälle und unterschiedliche Ausführung erlauben kein allgemeines Überlegenheits- oder Produktionsversprechen.

## MASSIVE und weitere Tests

Jev beantwortet 233/300 MASSIVE-Fälle richtig. Für Clef liegt keine vollständige auditierte Baseline auf denselben 300 Fällen vor; ein direkter Vergleich ist daher nicht verfügbar.

Die separate [deutsche Sprachvariantenstudie](../studies/language72/REPORT_DE.md) enthält Clef-Ergebnisse. Die 90 Bildrequests sind außerhalb des Jev-Vergleichs, weil der Dienst keinen nativen Bildeingang hat; ein OCR-Ersatz wurde nicht eingesetzt.

<details>
<summary>Auswertungsdefinition und ursprünglicher Antwortvertrag</summary>

Die Antwort-Richtigkeitsanalyse bewertet alle rekonstruierbaren nativen Entscheidungen gegen dieselben Goldlabels. Sie umfasst auch 35 vollständig erhaltene Antworten, deren Wahrscheinlichkeiten die ursprüngliche lokale Summenprüfung `abs(math.fsum(p.values()) - 1) <= 1e-5` verfehlen. Eine Summenabweichung ist kein fachlicher Auswahlfehler. Die Vektoren werden weder normalisiert noch verändert; alle übrigen Prüfungen der Antwortfelder und Auswahloptionen bleiben bestehen.

Das ist eine separat versionierte Auswertung mit einer anderen Einschlussregel als der ursprüngliche strikte Scorer. Die frühere Auswertung und ihre 937 strikt gültigen Antworten bleiben unverändert nachvollziehbar. Die Summenschwelle ist eine lokale Benchmarkregel, keine bestätigte Anbietergarantie. Zwei ältere Antworten sind nicht vollständig erhalten und werden nicht nachträglich rekonstruiert.

[Antwort-Richtigkeitsanalyse](../studies/jev974-answer-correctness-v1/README.md) · [Ursprüngliche strikte Auswertung](../studies/jev974/scoring/comparison_summary.json)

</details>

## Vergleichsbedingungen

- Die Aufgabeninhalte, Feldnamen, Optionen und Reihenfolge bleiben unverändert; nur die Modellkennung im Request ändert sich. Goldlabels gelangen nicht an den Dienst.
- Clef ist durch die Modellrevision `17f0b0ad64efb65d273590632833508766b2aae6` und das CPU-NF4/BF16-Profil beschrieben. Jev liefert die Version `jev-1.13.0`; Gewichtshash und Serving-Hardware sind nicht offengelegt.
- Native Wahrscheinlichkeiten bleiben vollständig und unnormalisiert. Jevs eigenes Konfidenzmaß ist nicht dieselbe Größe wie Clefs historischer gerundeter Auswahlscore. Gemeinsame Schwellenanalysen verwenden die native Auswahlwahrscheinlichkeit.
- CPU-Forward und gehostete HTTP-Antwortzeit haben verschiedene Messgrenzen. Daraus wird kein Geschwindigkeitsfaktor berechnet.
- Sprachkontrollen, Minimalpaare und Angriffsentfernung sind abhängige Diagnosen. Die Angriffsfälle wiederholen sieben frühere Finanzfälle. Die Tabelle darf nicht zu einer gemeinsamen Genauigkeit aufsummiert werden.
- Die Labels sind überwiegend KI-verfasst und separat KI-geprüft. Repräsentative reale Anfragen, unabhängige menschliche Fachannotation und ein neuer geschützter Holdout fehlen.

## Evidenz und Nachrechnen

Die vollständigen eingefrorenen [Requests, Labels und verfügbaren Clef-Baselines](../experiments/jev_comparison/inputs/) und das [ursprüngliche Protokoll](../experiments/jev_comparison/README.md) bleiben unverändert. Das Protokoll dokumentiert den Vorbereitungsstand; sein damaliger Ausführungsstatus wird nicht rückwirkend überschrieben.

- [Abschließender Audit](../studies/jev974/audit.json) und [Verifikation](../studies/jev974/verification.json)
- [Native Antworten und technische Ergebniszeilen](../studies/jev974/run/predictions.jsonl)
- [Unveränderte, separat markierte native Antworten](../studies/jev974/run/flagged_native.jsonl)
- [Alle Ergebnisgruppen](../studies/jev974-answer-correctness-v1/comparison_summary.json) und [fallweiser Vergleich](../studies/jev974-answer-correctness-v1/case_comparison.jsonl)
- [Feldmetriken](../studies/jev974/scoring/field_metrics.json), [Paardiagnosen](../studies/jev974/scoring/special_diagnostics.json) und [getrennte Zeitmessungen](../studies/jev974/scoring/latency.json)

Die exakten modellfreien Audit- und Scorerbefehle stehen unter [Jev nachrechnen](REPRODUCE.md#jev-nachrechnen-oder-neu-ausführen).

[Methodik](EVALUATION_GUIDE.md) · [Reproduktion](REPRODUCE.md)
