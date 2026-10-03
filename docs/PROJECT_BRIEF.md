# Clef Lab Projektüberblick

Clef Lab untersucht strukturierte deutsche Entscheidungsaufgaben mit Cloudflare Clef Flash 9B und vergleicht sie mit Jev 1.13.0. Testeingaben, Referenzlabels, native Antworten und Auswertung bleiben fallweise prüfbar. Eine lokale Oberfläche macht diese Ergebnisse ohne Modellinstallation zugänglich.

Der [aktuelle Vergleich](../README.md#ergebnisse-im-direkten-vergleich) zeigt die genauen Zähler und gleichen Nenner je Suite. Auf den dort ausgewiesenen Testgruppen erzielt Jev mehr vollständig richtige Antworten. Beispielsweise sind es bei mehreren Dokumenten 44/48 gegenüber Clef 24/48, bei notwendigen Rückfragen 71/72 gegenüber 64/72. Das sind Ergebnisse kleiner synthetischer Aufgaben, kein allgemeines Modellranking.

Die separate Clef-Sprachvariantendiagnose erreicht 64/72 vollständige Fälle und 40/48 an beiden Endpunkten richtige invariante Paare. Alle acht Fehler betreffen Zielunklarheit; keine richtige Basis wird durch ihre Variante falsch. Abhängige Varianten und KI-verfasste Labels begrenzen die Aussagekraft.

Zum Nachlesen: [Methodik](EVALUATION_GUIDE.md), [Jev-Vergleich](JEV_COMPARISON.md), [Reproduktion](REPRODUCE.md), [Workbench](../README.md#ergebnisse-lokal-ansehen). Die genaue lokale Modellkonfiguration, Auswertungsdefinitionen und fehlende Baselines stehen jeweils neben den Ergebnissen. Menschliche Fachvalidierung, reale Kundeneignung, Sicherheit und wirtschaftlicher Nutzen wurden nicht nachgewiesen.

## English

Clef Lab evaluates structured German decision tasks with Cloudflare Clef Flash 9B and compares them with Jev 1.13.0. Inputs, reference labels, native responses and scoring are available for case-level inspection. The local workbench displays recorded results without requiring a model installation.

The [current comparison](../README.md#ergebnisse-im-direkten-vergleich) reports exact counts and technical coverage by suite. Jev has more fully correct cases on those matched valid subsets, including 44/48 versus 24/48 for multiple documents and 71/72 versus 64/72 for clarification. These are observations on the tested synthetic tasks and configurations, with dependent examples and AI-authored labels. They do not establish a general ranking or production suitability.

See the [methodology](EVALUATION_GUIDE.md), [full comparison](JEV_COMPARISON.md) and [reproduction guide](REPRODUCE.md) for validation rules, provenance and limitations. No real-world safety, customer outcome or economic benefit was measured.
