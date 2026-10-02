# Clef · Versicherungsverständnis

60 deutsche synthetische Dokumentfälle, 12 Dokumentpakete, sechs Verständnisbereiche. Ein vorab unabhängig KI-geprüfter und eingefrorener Lauf mit dem gepinnten Clef-flash9B.

- Entscheidungen: 51/60 (85,0 %)
- Belegauswahl: 58/60 (96,7 %)
- Entscheidung und Beleg zusammen: 50/60 (83,3 %)

Die fünf Fälle je Dokument sind korreliert. Kurze konstruierte Auszüge sind keine Produktionsvalidierung oder Rechtsberatung. Kein Rechnen, keine realen Policen, keine externe menschliche Fachprüfung.

[Ergebnisbericht](REPORT.md) · [Vollständige Fehlerliste](ERRORS.md) · [Methodik](METHODOLOGY.md)

Die portable UI liest ausschließlich das nach unabhängiger Score-QA freigegebene `public/`-Paket. Alle nativen Modelloutputs und Rohwahrscheinlichkeiten liegen zusätzlich unter `results/`; die Inferenzrequests und Referenzen unter `benchmark/`. `qa/freeze_manifest.json` fixiert die Inputs vor dem einzigen primären Modelllauf. `qa/post_inference_audit.json` dokumentiert die separate Neuberechnung.

Reproduktion: `bash scripts/reproduce.sh`. Das lädt das offizielle Modell separat in eine neue Python-Umgebung; Modellgewichte und Laufzeit sind nicht Teil dieses Exports. Die vollständige Neuinstallation wurde nicht zusätzlich getestet; die tatsächliche Ausführung erfolgte in der unverändert gepinnten Umgebung des vorausgehenden Textpilots.
