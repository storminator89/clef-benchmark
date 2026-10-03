# Reproduzierbare Auswertungsgrafiken

Die beiden statischen SVG-Grafiken werden mit Python-Standardbibliothek erzeugt:

```bash
python3 scripts/generate_evaluation_charts.py
python3 scripts/generate_evaluation_charts.py --check
python3 -m unittest discover -s tests -p 'test_evaluation_charts.py' -v
```

`--check` schreibt nichts und scheitert bei fehlenden oder veralteten SVG-/Daten-Dateien. `data.json` enthält die nachgerechneten Zähler und SHA-256-Hashes aller vier Eingabedateien. Keine Auswertung startet Inferenz oder ruft einen Dienst auf.

## Daten und Nenner

- `matched_accuracy.svg`: acht Gruppen in der Reihenfolge der README-Tabelle. Beide Modelle haben je Gruppe denselben vollständigen geplanten Fallumfang. Der Dateiname bleibt zur Linkkompatibilität bestehen; die Grafik zeigt jetzt den direkten Vergleich über alle geplanten Fälle. Der Generator prüft die nativen Auswahlwerte gegen die Goldlabels und zählt [case_comparison.jsonl](../../studies/jev974-answer-correctness-v1/case_comparison.jsonl) gegen [comparison_summary.json](../../studies/jev974-answer-correctness-v1/comparison_summary.json) nach. Zwei nicht auswertbare Jev-Antworten zählen nicht als richtig. Die unveränderten ursprünglichen Daten bleiben erhalten; die neue [Antwortauswertung](../../studies/jev974-answer-correctness-v1/README.md) erklärt die Metrik.
- `language_diagnostic.svg`: Fallzeilen aus [case_scores.jsonl](../../studies/language72/scored/case_scores.jsonl), geprüft gegen [summary.json](../../studies/language72/scored/summary.json). Goldaktion `ask_target` trennt die Zielunklarheitsgruppe von sämtlichen übrigen Fällen. Das ist eine post-hoc Fehlerdiagnose auf einzelnen Fällen, kein Paar- oder Kausaleffekt. Die 13 Fälle sind nicht die 12 Fälle der separat definierten Ambiguitätsänderungsgruppe.

## Darstellung und Grenzen

Alle Prozentachsen reichen von 0 bis 100. Ganze Brüche sind exakt; Prozentwerte werden nur zur Anzeige auf eine Dezimalstelle gerundet. Die Reihenfolge bleibt fachlich vorgegeben, nicht nach Leistung sortiert. Es gibt keine gepoolte Genauigkeit, erfundenen Konfidenzintervalle, Signifikanzbehauptungen oder Latenzfaktoren. Fehlende Baselines erscheinen nicht als Nullgenauigkeit.

SVGs haben einen festen weißen Hintergrund mit dunklem Text, damit sie auf hellen und dunklen Repository-Seiten lesbar bleiben. Titel, Beschreibungen, Legenden und direkte Zahlen unterstützen die Interpretation ohne alleinige Abhängigkeit von Farben; die Tabellen bleiben die Textalternative. Keine Schriftdateien, JavaScript-Dateien oder externen Chart-Dienste werden geladen.

PNG-Dateien sind visuell geprüfte Fallbacks. Ihre Erzeugung ist optional und benötigt Inkscape; der Python-Generator bleibt abhängigkeitsfrei. Nach SVG-Änderungen die PNGs mit der lokal installierten Inkscape-Version neu rendern und prüfen:

```bash
for chart in matched_accuracy language_diagnostic; do
  inkscape "docs/charts/$chart.svg" --export-filename="docs/charts/$chart.png"
done
```

Die SVG-/JSON-Ausgaben sind byte-deterministisch. PNG-Metadaten oder Rendering können zwischen Inkscape-Versionen abweichen und gehören nicht zum deterministischen `--check`.
