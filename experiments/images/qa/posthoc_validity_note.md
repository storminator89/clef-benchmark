# Nachträglicher Hinweis zur Testgültigkeit

Dieser Hinweis wurde erst nach Abschluss der eingefrorenen Inferenz ergänzt. Er ändert keine Auswahl, Frage, Goldantwort oder Kennzahl.

Alle drei strikten Diagrammtyp-Abweichungen betreffen die Quellklasse `bar_line` und die vorhergesagte Option `vbar2`. Der Source-Datensatz unterscheidet diese Klassen als eigene Generatortypen. Die deutschsprachigen Optionsbeschreibungen im Test sind dagegen nicht vollständig disjunkt: „Kombination aus Säulen und Linie“ gegenüber „Senkrechte Säulen mit zwei y-Achsen“. Auch die englische zweite Beschreibung schließt Linien nicht ausdrücklich aus.

Alle drei Bilder enthalten sichtbar Säulen, eine Linie und zwei y-Achsen. Eine Wahl der zweiten Option kann daher durch die Formulierung gerechtfertigt sein, obwohl sie dem eingefrorenen Quellenlabel widerspricht. Das Resultat bleibt strikt 27/30, darf aber nicht als drei nachgewiesene visuelle Erkennungsfehler interpretiert werden. Es gibt keine rückwirkend korrigierte Genauigkeit oder nachträgliche Aussonderung.

Quellentaxonomie und Lizenz: https://huggingface.co/datasets/YuukiAsuna/synthetic_chart/blob/633cf14bc4c513f6c4806e319905e573afae12f4/README.md

Gepinnte Bild-/Labelquelle: https://huggingface.co/datasets/YuukiAsuna/synthetic_chart/blob/633cf14bc4c513f6c4806e319905e573afae12f4/data/test-00000-of-00001.parquet

| Testfall | Quellzeile | SHA256 Originalbild | Gold | Vorhersage |
| --- | ---: | --- | --- | --- |
| chart-001 | 270 (test-270) | 1158446f9f4068753dd2be4163bc94d62dabbd7e67e87157bfe2d28404a7afc7 | bar_line | vbar2 |
| chart-002 | 293 (test-293) | 00fbd70006924eb1d1f660b564eccbf00e6850c4ab36370e3bb1d6389589a263 | bar_line | vbar2 |
| chart-003 | 286 (test-286) | 007ccd50efe6ba6d6ac60740d037fe886916d02e0cf1c0735e97b5cff832d157 | bar_line | vbar2 |

Die drei Beispiele sind nach dem gepinnten Download unverändert über `benchmark/cases.jsonl` identifizierbar. Eine belastbare Folgeprüfung müsste disjunkte Beschreibungen vor einer neuen Inferenz festlegen, etwa bei `vbar2` explizit ohne überlagerte Linie. Das wurde im vorliegenden Lauf nicht nachträglich getan.

## Belegbeträge

Die zwei falschen Bruttosummen-Intervalle betreffen sichtbar negative Beträge: invoice-009 / beleg-000038: -29.838,18 EUR; invoice-016 / beleg-000028: -16.897,33 EUR. Die vorhergesagten Intervalle waren positiv. Das ist ein echter Vorzeichenfehler in dieser begrenzten Klassifikationsaufgabe. Ob Auflösungsreduktion, visuelle Verarbeitung oder die gemeinsame Entscheidungsschicht ursächlich war, wurde nicht isoliert geprüft.

Dokumentarische Ausschnitte sind im Bericht mit Quellen-Attribution enthalten. Originaldateien und vollständige Rechnungslabels werden nicht im öffentlichen Paket weitergegeben.
