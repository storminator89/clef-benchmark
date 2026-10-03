# Clef und Jev im Vergleich

Verglichen werden Cloudflare Clef Flash 9B im lokalen CPU-NF4-Profil und der gehostete Dienst `jev-1.13.0`. Beide erhalten dieselben eingefrorenen Texte, nativen Fragen und Antwortoptionen. Ein Fall ist nur vollständig richtig, wenn jedes verlangte Feld dem Goldlabel entspricht.

Der abgeschlossene Durchlauf enthält **974 einmal versuchte Anfragen**, **937 strikt gültige Antworten**, **37 technische Ausschlüsse**, **keine fehlenden Fälle** und **keine Wiederholungsanfragen**. Das ist eine Vollständigkeitsbilanz über zehn Quellsuiten, kein Gesamtscore. Die Auswertung wurde unabhängig nachgerechnet und stimmt mit den gespeicherten Scorerdateien überein.

## Getrennte Ergebnisse und Abdeckung

„Gemeinsam“ verwendet in jeder Zeile dieselben Fälle für beide Modelle: strikt gültige Jev-Antworten mit vorhandener Clef-Baseline. Die letzten beiden Spalten verwenden dagegen alle geplanten Fälle der jeweiligen Gruppe. Bei Jev zählen technische Ausschlüsse dort nicht als erfolgreich beantwortet. **Eine bedingte Genauigkeit auf gültigen Antworten und ein Ergebnis auf dem gesamten Umfang beantworten verschiedene Fragen.**

| Testgruppe | Clef gemeinsam richtig | Jev gültig richtig | Jev-Abdeckung | Technisch ausgeschlossen | Clef richtig / geplant | Jev gültig richtig / geplant |
|---|---:|---:|---:|---:|---:|---:|
| Minimalpaare, einzelne Fälle | 39/48 | 47/48 | 48/48 | 0 | 39/48 | 47/48 |
| Rückfragen | 64/72 | 71/72 | 72/72 | 0 | 64/72 | 71/72 |
| Bank-Support | 67/79 | 75/79 | 79/80 | 1 | 68/80 | 75/80 |
| Allgemeine Entscheidungen, Deutsch | 116/120 | 119/120 | 120/120 | 0 | 116/120 | 119/120 |
| Allgemeine Entscheidungen, deutscher Eingabetext / englisches Schema | 29/30 | 30/30 | 30/30 | 0 | 29/30 | 30/30 |
| Allgemeine Entscheidungen, Englischkontrolle | 29/30 | 30/30 | 30/30 | 0 | 29/30 | 30/30 |
| Finanzen, Deutsch | 75/79 | 78/79 | 79/80 | 1 | 76/80 | 78/80 |
| Finanzen, Englischkontrolle | 18/20 | 20/20 | 20/20 | 0 | 18/20 | 20/20 |
| Versicherungsdokumente | 50/60 | 56/60 | 60/60 | 0 | 50/60 | 56/60 |
| clean72 | 61/72 | 67/72 | 72/72 | 0 | 61/72 | 67/72 |
| Angriffsentfernung, mit Angriff | 4/7 | 6/7 | 7/7 | 0 | 4/7 | 6/7 |
| Angriffsentfernung, ohne Angriff | 4/6 | 6/6 | 6/7 | 1 | 5/7 | 6/7 |
| Mehrere Dokumente | 24/48 | 44/48 | 48/48 | 0 | 24/48 | 44/48 |
| MASSIVE de-DE | ausstehend | 219/266 | 266/300 | 34 | ausstehend | 219/300 |

Beispiel Bank-Support: Auf den 79 gemeinsam auswertbaren Fällen erreicht Clef 67/79 und Jev 75/79. Clefs vollständiger Lauf erreicht 68/80; Jev liefert für 79/80 Fälle eine strikt gültige Antwort. Man darf weder Clef 68/80 unmittelbar gegen Jev 75/79 stellen noch die ausgeschlossene Antwort als gültige fachliche Antwort behandeln.

Auf den acht deutschen Haupt- und Minimalpaargruppen im [README](../README.md#ergebnisse-im-direkten-vergleich) hat Jev jeweils mehr vollständig richtige Fälle. Das gilt für diese Aufgaben und die dokumentierten Konfigurationen. Die kleine synthetische Auswahl, abhängige Fälle und unterschiedliche Ausführung erlauben kein allgemeines Überlegenheits- oder Produktionsversprechen.

## Technische Antwortprüfung

Die eingefrorene lokale Summenregel lautet `abs(math.fsum(p.values()) - 1) <= 1e-5`. Jede Optionswahrscheinlichkeit muss außerdem endlich und zwischen 0 und 1 liegen; Optionsmenge und Felder müssen exakt passen, die gewählte Option ein natives Maximum sein. Der [Validator](../experiments/jev_comparison/scripts/jev_runner.py#L62-L82) prüft zusätzlich Modellkennung, Konfidenzbereich und Nutzungsangaben. **Die Toleranz 1e-5 ist eine Regel dieses Benchmarks, keine bestätigte Jev-Anbietergarantie.** Die Anbieterbeschreibung einer nur ungefähren Summe von 1 belegt diese konkrete Toleranz nicht. Ein daran scheiternder Vektor ist daher nicht automatisch eine falsche fachliche Auswahl oder ein nachgewiesener Verstoß gegen den Anbietervertrag.

Die Ausschlüsse bestehen aus zwei bereits dokumentierten technischen Fehlern sowie 35 weiteren Antworten, deren native Wahrscheinlichkeitsvektoren die festgelegte Summenprüfung verfehlen: 34 MASSIVE-Fälle und ein Angriffsentfernungsfall ohne Angriff. Diese 35 wurden unverändert separat aufbewahrt und nicht durch Normalisierung oder Reparatur in gültige Ergebnisse umgewandelt. Alle übrigen vorgegebenen Prüfungen bleiben bestehen.

Bank und deutscher Finanztest haben je einen technischen Ausschluss, Angriffsentfernung ohne Angriff einen und MASSIVE 34. Die übrigen Gruppen haben vollständige technische Abdeckung. Ein HTTP-Erfolg allein genügt nicht als gültiges Benchmarkresultat. Die ausgeschlossenen Antworten bleiben in der Vollständigkeitsbilanz sichtbar; valid-only Werte beschreiben eine ausgewählte Teilmenge.

## MASSIVE und weitere Tests

Jev hat 219 richtige unter 266 strikt gültigen MASSIVE-Antworten, also 219/266 bedingte Genauigkeit bei 266/300 Abdeckung. 219/300 beschreibt gültig und richtig beantwortete Fälle bezogen auf den gesamten geplanten Umfang. Beide Größen gehören nebeneinander.

Eine auditierte Clef-Baseline für genau diese 300 Fälle steht noch aus. Frühere historische native Outputs sind nicht verfügbar; die neue exakte 300-Fall-Replikation wird erst nach ihrem abgeschlossenen Audit aufgenommen. Bis dahin gibt es weder einen gepaarten MASSIVE-Score noch einen nachgewiesenen Clef-Jev-Vorsprung auf dieser Suite.

Die separate [deutsche Sprachvariantenstudie](../studies/language72/REPORT_DE.md) enthält Clef-Ergebnisse. Zusätzliche Jev-Sprachvarianten- und Mehrturntests sind noch nicht ausgeführt. Die 90 Bildrequests des ursprünglichen Projekts sind vollständig außerhalb dieses Vergleichs, weil Jev keinen nativen Bildeingang hat; ein OCR-Ersatz wurde nicht eingesetzt.

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
- [Alle Ergebnisgruppen](../studies/jev974/scoring/comparison_summary.json) und [fallweiser Vergleich](../studies/jev974/scoring/case_comparison.jsonl)
- [Feldmetriken](../studies/jev974/scoring/field_metrics.json), [Paardiagnosen](../studies/jev974/scoring/special_diagnostics.json) und [getrennte Zeitmessungen](../studies/jev974/scoring/latency.json)

Die exakten modellfreien Audit- und Scorerbefehle stehen unter [Jev nachrechnen](REPRODUCE.md#jev-nachrechnen-oder-neu-ausführen).

[Methodik](EVALUATION_GUIDE.md) · [Reproduktion](REPRODUCE.md)
