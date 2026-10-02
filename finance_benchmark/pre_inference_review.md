# Unabhängige Vorabprüfung: Finanz-/Makler-Erweiterung

Prüfung abgeschlossen am 2. Oktober 2026, 05:17 UTC. **Ergebnis: Freigabe zum Freeze und zur ersten Inferenz dieser Erweiterung.**

Die Prüfung erfolgte durch einen getrennten KI-Prüfer, nicht durch ein menschliches Fachannotationsteam. Der Prüfer kannte die bereits abgeschlossenen Ergebnisse des allgemeinen Benchmarks. Diese Prüfung ist daher vorab gegenüber den neuen Finanzresultaten, nicht blind gegenüber sämtlichen früheren Experimenten. Es wurden keine Modellausgaben dieser Erweiterung eingesehen. Die nachstehenden Korrekturen betreffen semantische Eindeutigkeit und Auswertungsrichtigkeit; Fälle und Labels wurden nicht anhand früherer Modellfehler optimiert.

## Inhalt und Übersetzung

Alle 80 deutschen Fälle wurden gegen die jeweils vollständige TEST-Richtlinie einschließlich Klassenbeschreibung geprüft. Alle 20 englischen Übersetzungen und alle acht zweisprachigen Richtlinien wurden auf Bedeutung, Negation, Geltungsbereich, Korrekturen und Vorrangregeln verglichen. Nach der unten dokumentierten Klarstellung sind die Sollklassen durch die ausdrücklich mitgelieferten Regeln eindeutig begründet. Kein Goldlabel wurde geändert.

Die Vertragsbeendigungsfälle unterscheiden die beschriebene Absicht, nicht tatsächliche Rechtswirksamkeit. Die Maklercheckliste behandelt Vollmacht, spezifische Empfänger-/Paket-Einwilligung und Unterlagen getrennt und legt die Reihenfolge fehlender oder widersprüchlicher Angaben ausdrücklich fest. `ready` bezeichnet nur den fiktiven Checklistenstatus. Empfehlungs-, Leistungs- und Täuschungswünsche werden ausschließlich klassifiziert; kein Label ist eine fachliche Entscheidung oder Ausführungserlaubnis.

Die arithmetischen und kalendarischen Sollwerte wurden unabhängig überprüft: 19,50 + 5,25 = 24,75; die korrigierte Gesamtsumme 51 stimmt nicht mit 40 + 12 überein. Vom 28. Februar 2026 bis 7. März 2026 liegen sieben Tage, vom 1. bis 9. Oktober acht Tage. Die erste Frist ist gemäß erfundener Regel eingeschlossen, die zweite nicht. Fehlende Werte und gleichzeitige unaufgelöste Widersprüche sind ausdrücklich gesonderte Klassen.

## Vor dem Freeze korrigiert

1. Bei `de_finance_advice_escalation_007` wurde der neutrale zusammenzufassende Text ausdrücklich als „fiktiven Maklervermerk“ bezeichnet. Dadurch ist sein Domänenbezug eindeutig und `routine` konkurriert nicht mit `out_of_scope`. Das Label blieb unverändert.
2. Die englischen Kontrollen decken nur zwei oder drei der fünf Klassen pro Kategorie ab. Der Scorer benennt deshalb das F1-Mittel über alle Policy-Klassen ausdrücklich, ergänzt ein Mittel über Klassen mit positiver Goldunterstützung und warnt vor einem Vergleich dieser EN-Werte mit dem vollständigen deutschen Satz. Ein perfektes englisches Ergebnis erreicht beim Alle-Klassen-Mittel insgesamt nur 0,5; synthetische Tests bestätigen dies. Sprachvergleiche verwenden die Korrektheit derselben 20 Paare.
3. Der Scorer behandelt fehlerhafte Antwortobjekte als ungültige Ausgaben statt mit einem Parserfehler abzubrechen. Er weist neben beidseitig gültigen Paaren auch sämtliche 20 geplanten Paare aus, wobei fehlende oder ungültige Hälften als falsch zählen. Die zugrunde liegenden Accuracy-, F1-, Kalibrierungs- und Konfidenzformeln bleiben unverändert. Diese Anpassungen wurden vor der ersten Finanz-Inferenz getestet und werden mit eingefroren.

## Technische Prüfungen

- Genau 100 eindeutige IDs: 80 deutsche Hauptfälle, 20 englische Kontrollen, keine gemischtsprachigen Diagnosen
- Acht Kategorien mit je zehn deutschen Fällen und genau zwei Beispielen pro fünf Klassen
- Gold, Fälle und Requests stimmen in IDs, Labels und Zuordnung überein; alle 20 DE/EN-Paare haben dieselbe Sollklasse
- Sämtliche Frageschemas entsprechen exakt ihrer Kategorie und Sprache in `policies.json`
- Die Modellnutzlast enthält nur `model`, `state` und `questions`; Goldlabels, Begründungen, Tags und Paar-Metadaten bleiben getrennt. Sieben absichtlich falsche eingebettete Antwortanweisungen sind deklarierter Angriffsinhalt, kein Goldhinweis
- Deterministischer Neuaufbau reproduziert die sieben generierten Datenartefakte bytegenau; der Validator besteht einschließlich synthetischer Scorer-, Parser-, ID- und fehlender-Paarhälften-Tests
- Der vorliegende reine Encoder-Vorabtest passt zum aktuellen Request-Hash und weist für alle 100 Inputs keine Kürzung aus: 391 bis 569 Tokens. Dabei wurde laut Protokoll kein Modell instanziiert; dies ist kein Inferenzergebnis

Geprüfter `requests.jsonl`-SHA-256: `543b90344f7c67e6b94d35bca548d4c0235d2879daee9ff46205f585fe45fedb`.

## Grenzen

Dies sind synthetische, teils ausdrücklich formulierte Routing-/Checklistenaufgaben unter erfundenen Regeln. Sie prüfen weder reales deutsches Recht noch regulatorische Konformität, Versicherbarkeit, Leistungsansprüche, Anlageeignung, umfassende Täuschungserkennung oder Produktionssicherheit. Nur zwei Beispiele je Klasse und bewusst gewählte Übersetzungen erlauben keine belastbaren allgemeinen Qualitäts- oder Kalibrierungsversprechen. Der Satz enthält 80 unabhängige Ausgangsszenarien und 20 korrelierte Übersetzungen, nicht 100 unabhängige Szenarien. Ergebnisse sind separat vom ursprünglichen Benchmark und mit genauer Modell-/Laufkonfiguration zu berichten.
