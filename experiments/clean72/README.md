# Alltagsnahe deutsche Bürofragen ohne Manipulation

**61 von 72 Entscheidungen richtig (84,7 %)**, alle 72 nativen Antworten schema-gültig. Ein neuer, vor Inferenz unabhängig geprüfter synthetischer Satz mit sechs Aufgabenbereichen; keine nachträglich bereinigten alten Fehlerfälle.

- Anliegen priorisieren: **10/12**
- Unterlagen abgleichen: **11/12**
- Beiträge berechnen: **6/12**
- Vorgangsstand: **11/12**
- Nächste Rückfrage: **11/12**
- Finanzservice routen: **12/12**

Die größte Schwäche sind mehrstufige Rechenaufgaben. Bei vollständigem Kontext sind 42/50 richtig, bei fehlenden oder ungeklärten Angaben 19/22. Drei notwendige Informationsanforderungen wurden verpasst. Alle elf Fehlentscheidungen stehen in [`results/decision_errors.jsonl`](results/decision_errors.jsonl), auch wenn das Feld `errors` im Scorer nur Schema- und Laufzeitfehler zählt.

[Ergebnisbericht](results/RESULTS.md) · [Unabhängige finale Gegenprüfung](results/verification.json) · [Vollständiges Testdesign](benchmark/README.md) · [Portable Provenienz](provenance/portable_export.json)

Die Website im Repository bietet diese Suite unter „Alltagsnah · ohne Manipulation“ separat an. 72 lange, ordentlich strukturierte synthetische Nachrichten sind keine repräsentative Feldstudie und keine frei formulierte Beratung. Es gibt keine englischen Kontrollfälle. Andere Aufgaben und Schwierigkeiten als in den früheren Suiten: die Differenz der Quoten ist kein kausaler Manipulationseffekt.

## Ohne Modell prüfen

Vom Repository-Hauptverzeichnis:

```bash
python3 experiments/clean72/benchmark/validate.py
python3 experiments/clean72/benchmark/independent_scorer_tests.py
python3 scripts/build_clean_web_data.py
python3 scripts/check_followups.py
```

## Neue Inferenz reproduzieren

Zuerst die dokumentierte CPU-Umgebung und gepinnten Modellgewichte aus der Haupt-README einrichten. Nur einen Modellprozess gleichzeitig ausführen. Dann vom Repository-Hauptverzeichnis:

```bash
mkdir -p experiments/clean72/reproduced
runtime/venv/bin/python runtime/guard_run.py runtime/venv/bin/python runtime/run_clef.py \
  --requests experiments/clean72/benchmark/requests.jsonl \
  --output experiments/clean72/reproduced/predictions.jsonl
python3 experiments/clean72/benchmark/score.py \
  experiments/clean72/reproduced/predictions.jsonl \
  --out experiments/clean72/reproduced/scores.json
```

Die gespeicherten Ergebnisse bleiben unverändert. Ein erneuter Lauf ist separat zu prüfen und zu kennzeichnen. Der veröffentlichte Stand verwendet CPU NF4 mit originalem BF16-Kopf; kein AMD-Lauf. Das öffentliche Freeze-Manifest unterscheidet seine portablen Script-/Metadatenkopien ausdrücklich vom ursprünglichen Vorab-Freeze. Fälle, Requests, Gold und Rohvorhersagen sind byte-identisch zu den Messinputs/-outputs.
