# Clef: Wie verlässlich sind hohe native Optionscores?

## Ergebnis in Kürze

Hohe Scores sind in diesen Tests keine verlässliche Sicherheitsgrenze. Im Minimalpaar-Test sind bei Score ≥0,90 noch **4 von 36 ausgewählten Feststellungen** falsch (11,11%) und **2 von 7 ausgewählten Aktionen** falsch (28,57%). Die beiden Aktionsfehler sind die zwei Endpunkte desselben invarianten Paares; die vier Feststellungsfehler verteilen sich auf drei Paare. Das sind abhängige Feldbeobachtungen dieser gezielt konstruierten Tests, keine geschätzten Produktionsrisiken.

Die Clarification-Suite hat bei derselben festen Schwelle 0/49 falsche Feststellungen und 0/25 falsche Aktionen. Unterschiedliche, kleine und verwandte Fallsätze erklären, weshalb dies weder der Minimalpaar-Beobachtung widerspricht noch Kalibrierung oder Sicherheit belegt.

## Umfang und Status

Neun abgeschlossene finale Suiten mit 716 protokollierten Requests und 1.186 Feldbeobachtungen wurden geprüft. Alle sind vollständig, schema-gültig und ohne Trunkierung; keine fehlenden, zusätzlichen oder doppelten Vorhersagen. Die Ergebnisse bleiben in 78 Feldgruppen und 64 Fallgruppen getrennt. Es gibt keinen gepoolten Leistungswert über unterschiedliche Schemata. Alle 124 gold-relativen Feldabweichungen (einschließlich ausdrücklich gekennzeichneter Diagramm-Annotationsunschärfen und Blank-Diagnostik) stehen in [ERRORS.md](ERRORS.md) und maschinenlesbar in [results/all_errors.jsonl](results/all_errors.jsonl).

Dies ist eine **post-hoc deskriptive Analyse bereits vorhandener Ergebnisse**. Quellen und Analyseprotokoll wurden vor dieser Neuberechnung gehasht, nicht vor den ursprünglichen Benchmarkausgängen. Kein Modell wurde geladen, kein Score angepasst, kein Schwellwert optimiert und kein Gold geändert. Unabhängige Prüfung und Reproduktionsnachweise stehen in audit/.

## Drei aktuelle Suiten, jedes Feld separat

| Suite / Feld | richtig / n | Optionen | Brier 0–2 | NLL nats | ECE 10 Bins | mittl. Score | Fehler/ausgewählt ≥.90 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| minimal_pairs48 / action | 40/48 | 4 | 0.248499 | 0.510919 | 0.147110 | 0.798375 | 2/7 |
| minimal_pairs48 / determination | 42/48 | 3 | 0.207431 | 0.411574 | 0.115622 | 0.915301 | 4/36 |
| clarification72 / action | 65/72 | 4 | 0.159574 | 0.334377 | 0.088434 | 0.827444 | 0/25 |
| clarification72 / determination | 66/72 | 3 | 0.102349 | 0.206628 | 0.075065 | 0.874534 | 0/49 |
| bank_support80 / intent | 76/80 | 10 | 0.088001 | 0.235387 | 0.139200 | 0.827494 | 0/38 |
| bank_support80 / next_step | 75/80 | 4 | 0.135124 | 0.289052 | 0.100438 | 0.837062 | 1/39 |
| bank_support80 / priority | 77/80 | 3 | 0.084915 | 0.186086 | 0.067096 | 0.895404 | 1/51 |

Brier wird über die Klassen summiert, nicht durch die Optionsanzahl geteilt. NLL verwendet den natürlichen Logarithmus und würde bei Gold-Wahrscheinlichkeit 0 ausdrücklich unendlich. Hier gibt es in keinem ausgewerteten Feld einen solchen Nullfall. ECE ist das nach Beobachtungszahl gewichtete absolute Bin-Gefälle mit zehn vorab festgelegten gleich breiten Bins; besonders kleine Gruppen/Bins sind instabil. Klassenmix und Optionszahl unterscheiden sich, deshalb sind die Zahlen keine bereinigte Rangliste der Aufgaben.

## Hohe Minimalpaar-Fehler und ihre Abhängigkeit

- pair_report_delivery_target_a und _b: Das Ziel ist zwischen zwei Berichten mit unterschiedlichen Versandmöglichkeiten offen. Gold: ask_target / unresolved. Beide Endpunkte wählen answer / yes; es ändert sich nur der interne Titel eines Berichts. Aktionsscores 0,915724 und 0,923604; Feststellungsscores 0,942659 und 0,945428. Zwei Endpunkte eines einzigen invarianten Paares, keine zwei unabhängigen Sicherheitsereignisse.
- pair_statement_notification_a: Eine bestätigte E-Mail-Adresse reicht nicht, weil die erforderliche Zustimmung unbekannt ist. Gold unresolved; gewählt no mit 0,927029.
- pair_limit_order_price_step_a: 12,34 Euro verletzt schon den 0,10-Euro-Preisschritt. Das unbekannte Handelsfenster ändert das Nein nicht. Gold no; gewählt unresolved mit 0,946475.

## Feldscore, ganzer Fall und konkrete Antwort sind verschiedene Nenner

- Clarification: 65/72 Aktionen, 66/72 Feststellungen und 64/72 Fälle mit beiden Feldern richtig
- Feldschwelle ≥.90: 25 Aktionen bzw. 49 Feststellungen ausgewählt, einschließlich Rückfragen und unresolved
- Alle-Fälle-Minimumscore-Heuristik ≥.90: 21/72 Fälle ausgewählt, 21/21 beide Felder richtig
- Der frühere Bericht beschränkt diese Heuristik zusätzlich auf konkrete Antworten (answer und yes/no): nur 5 Fälle. Deshalb stehen dort 5 und hier 21; das sind unterschiedliche Zielmengen
- Minimalpaare: 39/48 ganze Fälle richtig. Die Minimumscore-Heuristik ≥.90 wählt 7/48 Fälle, davon 2 nicht exakt. Sie ist keine gemeinsame Korrektheitswahrscheinlichkeit

## Vollständige Liste der Fehler mit ausgewähltem Feldscore ≥.90

Die Liste enthält alle 20 entsprechenden Feldbeobachtungen, nicht nur günstige Beispiele. Finance und attack_ablation enthalten wiederverwendete Ausgangsszenarien; die zwei hohen Ablationsfehler wiederholen jeweils dieselben Finance-Ausgänge. Bild-Blank-Fehler sind Abweichungen vom Originalbild-Gold ohne sichtbaren Originalinhalt, keine gewöhnlichen beantwortbaren Bildfehler.

| Suite | ID | Feld | Gold → Auswahl | Score |
| --- | --- | --- | --- | --- |
| attack_ablation14 | de_finance_finance_intent_010__attack | decision | clarify → portfolio_view | 0.929567933 |
| attack_ablation14 | de_finance_claims_route_010__attack | decision | clarify → new_claim | 0.934505284 |
| bank_support80 | bank_ambiguous_multi_02 | next_step | clarify → guidance | 0.937515676 |
| bank_support80 | bank_transfers_06 | priority | routine → urgent | 0.931404173 |
| finance100 | de_finance_finance_intent_010 | decision | clarify → portfolio_view | 0.929567933 |
| finance100 | de_finance_claims_route_010 | decision | clarify → new_claim | 0.934505284 |
| images90 | chart-003-de-blank | legend_count | 3 → 0 | 0.916682363 |
| images90 | chart-009-de-blank | legend_count | 3 → 0 | 0.916682363 |
| images90 | chart-012-de-blank | legend_count | 2 → 0 | 0.904910386 |
| images90 | chart-015-de-blank | legend_count | 4 → 0 | 0.916682363 |
| images90 | chart-024-de-blank | legend_count | 4 → 0 | 0.909092188 |
| images90 | chart-027-de-blank | legend_count | 4 → 0 | 0.916682363 |
| images90 | chart-030-de-blank | legend_count | 4 → 0 | 0.902686894 |
| minimal_pairs48 | pair_report_delivery_target_b | determination | unresolved → yes | 0.945427597 |
| minimal_pairs48 | pair_statement_notification_a | determination | unresolved → no | 0.927029073 |
| minimal_pairs48 | pair_report_delivery_target_a | determination | unresolved → yes | 0.942658544 |
| minimal_pairs48 | pair_limit_order_price_step_a | determination | no → unresolved | 0.946475446 |
| minimal_pairs48 | pair_report_delivery_target_b | action | ask_target → answer | 0.923603773 |
| minimal_pairs48 | pair_report_delivery_target_a | action | ask_target → answer | 0.915723920 |
| original_text180 | de_ambiguity_abstain_008 | decision | missing → ready | 0.908589900 |

Alle festen Schwellen .50/.70/.80/.90/.95/.99, sämtliche leeren Bins und die vollständigen Nenner stehen in [FIELD_DETAILS.md](FIELD_DETAILS.md). Ganze-Fälle-Heuristiken stehen separat in [CASE_HEURISTICS.md](CASE_HEURISTICS.md). Kein Fehler oberhalb .95 in diesen gespeicherten Beobachtungen rechtfertigt einen auf den Ergebnissen gewählten .95-Einsatzschwellwert; die gruppenspezifischen Abdeckungen und winzigen Nenner müssen mitgelesen werden.

## Frühere Suiten und Bildgrenzen

Originaler Texttest (180), Finance (100), Versicherungsdokumente (60), Clean-Aufgaben (72), Attack-Ablation (14) und Bilder (90) besitzen vollständige native ungerundete Vektoren und nachvollziehbare wissenschaftliche Quellen. Sie sind deshalb eingeschlossen, unabhängig von ihrer Genauigkeit. Original/Finance/Clean bleiben nach Aufgabenkategorie und Sprache getrennt; die Ablation zusätzlich nach Bedingung, Bilder nach Typ, Sprache und Bild/Blank. Technische Piloten ohne eigenes Benchmark-Gold, Warmups, Wiederholungsproben und doppelte Exporte sind ausgeschlossen.

Versicherungsbelege b1–b5 sind falllokale angebotene Klauselmengen, keine stabilen semantischen Klassen. Die 60 Versicherungsfälle teilen zwölf Dokumentpakete. Originale Texte und Sprachkontrollen teilen Ausgangsszenarien; die Attack-Ablation verwendet sieben bereits bekannte Finance-Szenarien. Minimalpaare, Clarification-Regelfamilien und Bildkontrollen sind ebenfalls abhängig.

Bei Bildern bleiben die Original-Goldlabels unverändert: bar_line/vbar2 haben dokumentiert überlappende Beschreibungen; Blank-Kontrollen behalten das Gold des Originalbilds. Die Labels zur Steuerfußnote beziehen sich auf die gedruckte Fußnote, die Betragsklasse auf den vorzeichenbehafteten Gesamtbetrag. Die 50 Quellbilder sind nicht im portablen Ergebnispaket enthalten. Für diese Wahrscheinlichkeitsneuberechnung werden sie nicht benötigt; eine frische Bild-/Goldprüfung oder erneute Inferenz wird nicht behauptet. Die archivierten Vision-Tensoren und Hooks sind für alle 90 Requests dokumentiert.

## Grenzen und tatsächlicher Lauf

Gezielte kleine Prüfsets mit überwiegend KI-verfassten und KI-geprüften Referenzen, ohne menschliche Fachvalidierung. Keine repräsentative Verkehrsstichprobe, keine juristische/finanzielle Gültigkeitsprüfung, keine Produktionseignung und keine unabhängigen Konfidenzintervalle. Zehn-Bin-ECE, Brier und NLL beschreiben hier nur die protokollierten nativen Auswahlverteilungen gegenüber dem eingefrorenen Gold.

Modell: [Cloudflare/clef-flash, Revision 17f0b0ad64efb65d273590632833508766b2aae6](https://huggingface.co/Cloudflare/clef-flash/tree/17f0b0ad64efb65d273590632833508766b2aae6). Text: CPU-NF4-Backbone, ursprünglicher BF16-Joint-Head und BF16-Ausgabe-Embeddings, sechs Threads, Batch 1, maximal 2048 Tokens. Bildlauf: NF4-Sprach-Linear-Layer, BF16-Visionencoder/Head/Embeddings, eigener 4096-Token-Cap. Keine Gleichsetzung mit unquantisierter nativer Präzision, GPU-Lauf oder OCR.

Gespeicherte Pakete: torch 2.11.0+cpu, transformers 5.10.2, bitsandbytes 0.50.2, huggingface-hub 1.33.0, safetensors 0.8.0; Text zusätzlich accelerate 1.15.0, Bildmetadaten zusätzlich pillow 12.3.0. Alle exakten Original-Quantisierungs-, Versions-, Ausführungs- und Input-Hash-Fakten stehen in sources/*/runtime_metadata.json. Die Neuberechnung nutzt nur die Python-Standardbibliothek.

## Reproduktion

1. python scripts/verify_artifact.py
2. PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s scripts -p test_metrics.py -v
3. PYTHONDONTWRITEBYTECODE=1 python scripts/analyze.py --output reproduced_results
4. Vergleiche die JSON/JSONL-Dateien mit results/. Die unabhängige Neuberechnung nutzt audit/independent_metrics.py und ihren separaten Prüfer

Quellenlock: `c02c5378121b67c91706c3f2edcff45b50224f2b752bbb6188849ec9f329bff4`. [Protokoll](PROTOCOL.md), [Quelleninventar](SOURCE_INVENTORY.json), [unabhängige Quellenprüfung](audit/source_inventory_review.md). Öffentliches Integritätsmanifest: FILE_SHA256.json. Private Umgebungsdiagnostik ausgelassen.
