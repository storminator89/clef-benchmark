# Clef Lab Projektüberblick

Clef Lab untersucht strukturierte deutsche Entscheidungsaufgaben mit Cloudflare Clef Flash 9B und vergleicht sie mit Jev 1.13.0 und Wähler 4B. Testeingaben, Referenzlabels, native Antworten und Auswertung bleiben fallweise prüfbar. Eine lokale Oberfläche macht diese Ergebnisse ohne Modellinstallation zugänglich.

Der [aktuelle Vergleich](../README.md#ergebnisse-im-direkten-vergleich) zeigt Clef, Jev und Wähler auf denselben 580 deutschen Fällen in acht Gruppen. Jede Gruppe behält ihren eigenen Nenner; nur vollständig richtige Fälle zählen. Alle nativen Auswahloptionen, vollständigen numerischen Verteilungen und Referenzen sind [reproduzierbar](WAEHLER_COMPARISON.md). Die unterschiedlichen Modellgrößen, Quantisierungen und Ausführungsumgebungen erlauben keine isolierte Architektur- oder Geschwindigkeitsaussage.

Die separate Clef-Sprachvariantendiagnose erreicht 64/72 vollständige Fälle und 40/48 an beiden Endpunkten richtige invariante Paare. Alle acht Fehler betreffen Zielunklarheit; keine richtige Basis wird durch ihre Variante falsch. Abhängige Varianten und KI-verfasste Labels begrenzen die Aussagekraft.

Zum Nachlesen: [Methodik](EVALUATION_GUIDE.md), [Jev-Vergleich](JEV_COMPARISON.md), [Reproduktion](REPRODUCE.md), [Workbench](../README.md#ergebnisse-lokal-ansehen). Die genaue lokale Modellkonfiguration, Auswertungsdefinitionen und fehlende Baselines stehen jeweils neben den Ergebnissen. Menschliche Fachvalidierung, reale Kundeneignung, Sicherheit und wirtschaftlicher Nutzen wurden nicht nachgewiesen.

## English

Clef Lab evaluates structured German decision tasks with Cloudflare Clef Flash 9B and compares them with Jev 1.13.0 and Wähler 4B. Inputs, reference labels, native responses and scoring are available for case-level inspection. The local workbench displays recorded results without requiring a model installation.

The [current comparison](../README.md#ergebnisse-im-direkten-vergleich) reports exact counts for all three models on the same 580 planned cases in eight separate groups. Native answers, complete numeric score tables and an offline replay scorer are available. These are small synthetic, partly dependent tasks with different model sizes, quantization and execution environments, not a general ranking or production validation.

See the [methodology](EVALUATION_GUIDE.md), [full comparison](JEV_COMPARISON.md) and [reproduction guide](REPRODUCE.md) for validation rules, provenance and limitations. No real-world safety, customer outcome or economic benefit was measured.
