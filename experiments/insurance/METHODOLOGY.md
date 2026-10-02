# Versicherungsunterlagen: kontrollierter deutscher Verständnistest

## Gegenstand

60 neu verfasste fiktive Szenarien mit 12 vollständig synthetischen deutschen Dokumentpaketen, fünf Fälle je Paket. Keine echten Versicherungspolicen, Kundendaten, Produktzusagen oder Rechtsberatung. Sechs gezielt besetzte Bereiche à zehn Fälle: Deckungsumfang/Definitionen, Ausschlüsse/Rückausnahmen, Voraussetzungen/Obliegenheiten, Nachweise/Verfahrensstatus, Nachträge/Vorrang sowie unvollständige/widersprüchliche Akten.

Diese Auswahl ist ein kleiner, bewusst konstruierter Funktionstest. Sie ist weder eine Zufallsstichprobe aus echten Schadenfällen noch ein repräsentativer Produktionstest. Fünf Fälle teilen jeweils dieselben Klauseln; auch Dokumente verwenden verwandte Aufgabenmuster. Die 60 Fälle und 120 Feldentscheidungen sind deshalb **keine unabhängigen Beobachtungen**. Keine nominellen Konfidenzintervalle unter einer fälschlichen Unabhängigkeitsannahme. Die Dokumentauszüge sind kurz und explizit; lange Vollpolicen, OCR, Retrieval, Tabellen und freies juristisches Argumentieren werden nicht geprüft.

## Aufgaben

Pro Fall zwei native Clef-Choice-Felder in demselben Forward-Pass:

1. `decision`: Ist die genau angegebene Aussage durch Text und Sachverhalt gestützt (`ja`), widerlegt (`nein`), wegen fehlender Information offen (`offen`) oder durch maßgebliche gleichrangige Dokumente unauflösbar widersprüchlich (`konflikt`)? Ein Konflikt zu einem anderen Thema ist kein Konflikt der gefragten Aussage. Geregelter Dokumentvorrang wird zuerst angewendet.
2. `evidence`: Auswahl einer hinreichenden angebotenen Klauselmenge. Klauseln sind mit stabilen IDs bezeichnet. Dies misst Auswahl unter fünf vorgegebenen Belegmengen, **keine freie Belegsuche oder generierte Begründung**. Die im Datensatz gespeicherte Begründung ist eine unabhängig geprüfte Referenzerläuterung, kein Modellausgabefeld.

Entscheidung, Belegauswahl und vollständig richtiger Fall werden getrennt gezählt. Ein vollständig richtiger Fall erfordert beide richtigen Felder. Ergebnisse nach Bereich, Dokument und Entscheidungslabel sowie Fehler mit Softmax-Wert ≥90 % werden gesondert ausgewiesen. Softmax ist keine validierte Fehlerwahrscheinlichkeit oder Zuverlässigkeitsgarantie.

Keine Rechenaufgaben, Selbstbeteiligungen, Summen oder Betragsklassen. Drei Fälle wenden ein ausdrücklich genanntes Nachtrags-Gültigkeitsdatum auf einen bekannten oder unbekannten Schadentag an; sie werden als `date_version_application` separat ausgewiesen. Es gibt keine Datumsdifferenzen oder Fristberechnungen.

## Vor der Inferenz

Ein separater KI-Reviewer kontrolliert alle 60 Labels, angebotenen Belegmengen, Widerspruchsauflösung und Aufgabenformulierungen, ohne Vorhersagen zu sehen. Problemfälle werden vor dem Lauf korrigiert; der finale Audit muss bestehen. Danach werden Fälle, Referenzen, Modellrequests, Auswertungscode und Audit per SHA-256 eingefroren. Referenzlabels, Dateinamen, Dokumentpaket-IDs, Bereichstags und Referenzbegründungen werden **nicht** in den Modellzustand gegeben. Klauselkennungen und -texte sind Teil der ausdrücklich gegebenen Dokumente.

Der offizielle Encoder wird vorab für jeden vollständigen Request gegen ein sehr hohes Tokenlimit verglichen. Modelllauf und Vorprüfung verwerfen Kürzung statt sie still zuzulassen. Der Originalkontextdeckel bleibt bei 2.048 Tokens. Inferenz liest nur die label-freie JSONL; Auswertung läuft danach getrennt. Ein Warm-up und die vom Originalrunner verwendete einmalige Wiederholbarkeitsprobe werden nicht zusätzlich als Benchmarkfälle gezählt. Es gibt genau einen primären Lauf, keine Promptauswahl anhand seiner Resultate.

## Modellkonfiguration

`Cloudflare/clef-flash`, Revision `17f0b0ad64efb65d273590632833508766b2aae6`, offizieller unveränderter Modell-/Encoder-Code und unveränderter eigener Inferenzrunner aus dem Textpilot. CPU-only, Batch 1, sechs Threads, NF4-Backbone mit Double Quantization und BF16-Berechnung. Originaler Joint-Head und Ausgabe-Embeddings bleiben BF16. Genau dieselbe bereits installierte Umgebung wie im vorausgehenden Textpilot; kein Upgrade und kein paralleler Modellprozess. Dies ist keine Hersteller-BF16-GPU-Messung und keine Aussage über ROCm, Radeon, H200 oder Produktionslatenzen.

Für jedes Feld bleiben vollständige ungerundete Optionswahrscheinlichkeiten erhalten. Pro Fall werden Tokenanzahl, Kürzungsflag, Encoding- und Inferenzzeit sowie RAM gespeichert. Lade- und Aufwärmzeit zählen nicht zur Falllatenz. P95 verwendet die Nearest-Rank-Methode.

## Reproduktion und Rechte

Die Dokumente und fiktiven Sachverhalte wurden für diesen Test neu geschrieben; keine fremden Vertragsbedingungen wurden kopiert. Code und synthetische Daten werden im Rahmen der Apache-2.0-Projektlizenz veröffentlicht. Das Modell wird separat vom offiziellen, revisionsgebundenen Hugging-Face-Repository geladen; Gewichte und Python-Umgebung sind nicht Teil des GitHub-Exports.

`benchmark/benchmark.json` enthält lesbare Dokumente, Fälle und Referenzen. `benchmark/requests.jsonl` ist der exakte Inferenzinput. `results/predictions.jsonl` enthält tatsächliche Modelloutputs. `results/results.json` ist die deterministische Auswertung. `qa/freeze_manifest.json` belegt die vorab fixierten Dateien; `qa/pre_inference_audit.json` und der finale Scoring-Audit dokumentieren unabhängige Prüfungen. `scripts/reproduce.sh` baut eine separate Umgebung, prüft Encoding und startet den Lauf. Ergebnisse werden nicht überschrieben.
