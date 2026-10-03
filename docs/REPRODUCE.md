# Ergebnisse reproduzieren

Es gibt drei getrennte Schritte: gespeicherte Ergebnisse nachrechnen, die Software prüfen und neue Modellantworten erzeugen. Die ersten beiden benötigen keine Modellgewichte und keinen API-Schlüssel. Alle Befehle laufen vom Repository-Hauptverzeichnis, sofern nicht anders angegeben.

## 1 Gespeicherte Ergebnisse nachrechnen

Python 3.12+:

```bash
python3 scripts/check_project.py
python3 scripts/check_bank_support.py
python3 scripts/check_clarification.py
python3 scripts/check_paired_reliability.py
python3 scripts/check_multidoc.py
python3 scripts/check_jev.py
```

Diese Gates prüfen die jeweils dokumentierten eingefrorenen Daten, Hashes und Auswertungen. `check_jev.py` prüft das eingefrorene Vergleichspaket und die Aktivierung; der aktuelle Ergebnisstand hat einen eigenen [Endaudit](JEV_COMPARISON.md). Ein bestandener Paketcheck allein ist keine Bestätigung neuer Modellantworten.

Einzelne historische Scores lassen sich in neue Dateien schreiben:

```bash
python3 qa/score_v1_1.py results/predictions.jsonl --out /tmp/clef-original-rescored.json
python3 finance_benchmark/score.py results/finance/predictions.jsonl --out /tmp/clef-finance-rescored.json
```

Die [Original-Reproduktion](REPRODUCIBILITY.md) und [Finanz-Reproduktion](FINANCE_REPRODUCIBILITY.md) erklären Scorerversionen, Sprachkontrollen und Ergebnisdateien. Für andere Suiten gelten deren eigene Scorer und Protokolle; keine Goldlabels oder eingefrorenen Dateien überschreiben.

## 2 Softwaretests

Die Paketabhängigkeiten sind für die JS/DOM-Tests nötig, nicht für das bloße Ansehen der Ergebnisse. Voraussetzungen: Python 3.12+ und Node.js 22+.

```bash
python3 -m unittest discover -s tests -v
npm ci
npm test
```

Mocks, synthetische Testfixtures und Browserprüfungen sind Softwaretests. Sie erzeugen keinen zusätzlichen Modellbenchmark. Für die Ergebnisansicht genügt `python3 server.py` und [localhost:8765](http://127.0.0.1:8765).

## 3 Neue lokale Clef-Inferenz

Zuerst die Zielhardware prüfen:

```bash
python3 -m runtime.setup --plan --profile cpu-nf4
```

Der [Setup-Vertrag](AGENT_SETUP.md) beschreibt die ausdrückliche Installation, Modellprüfung und den Smoke-Test. Die historischen Benchmarkbefehle sind separat dokumentiert:

```bash
bash runtime/setup_runtime.sh
runtime/venv/bin/python runtime/download_model.py
python3 scripts/verify_model_download.py
bash runtime/reproduce.sh
bash runtime/reproduce_finance.sh
```

Die beiden letzten Befehle sequenziell ausführen. Sie schreiben neue Dateien unter `runtime/reproduced_*` und ersetzen die veröffentlichten Ergebnisse nicht. Ein vollständiger Modelllauf kann auf CPU lange dauern; mehrere Modellprozesse können den Speicherbedarf überschreiten. Vorher [Hardwarebedarf](HARDWARE.md), verfügbaren Speicher und Diskbedarf prüfen. Der Download enthält ausführbaren offiziellen Modellcode, der vor der Ausführung geprüft werden sollte.

Gepinnt ist `Cloudflare/clef-flash` bei Revision `17f0b0ad64efb65d273590632833508766b2aae6`. Die historischen Läufe verwenden CPU-NF4, Double Quantization, BF16-Compute und den originalen BF16-Head, Batch 1 und sechs Torch-Threads. Goldlabels werden nicht an den Runner übergeben; Eingabekürzung wird geprüft. Ein Lauf ist erst mit vollständigen Ergebnissen und abgeschlossenen Metadaten auswertbar. Andere Hardware oder Precision sind als neue Konfiguration zu kennzeichnen; bitgleiche Modellantworten über Plattformen werden nicht zugesichert.

## Sprachvarianten nachrechnen

Der abgeschlossene 72-Fall-Lauf hat einen eigenen unabhängigen Check und Scorer. Vom Repository-Hauptverzeichnis:

```bash
python3 studies/language72/scripts/verify_public.py
python3 studies/language72/scripts/score.py \
  --data studies/language72/data \
  --predictions studies/language72/results/predictions.jsonl \
  --output /tmp/clef-language72-rescored
```

Das Ausgabeverzeichnis darf noch keine Scorerdateien enthalten. Der unabhängige Check prüft native Antworten, Metriken und öffentliche Dateihashes; die anschließende Auswertung schreibt neue Ableitungen. Details stehen in der [Sprachvarianten-Suite](../studies/language72/README.md).

## Noch offene Baselines

MASSIVE und Mehrturntests bleiben bis zu ihren abgeschlossenen Audits offen; frühere nicht verfügbare native Ergebnisse sind kein Ersatz.

## Jev nachrechnen oder neu ausführen

Der abgeschlossene 974-Fall-Lauf lässt sich ohne Netzwerk oder API-Schlüssel prüfen und auswerten:

```bash
python3 scripts/audit_jev_final_continuation.py --run studies/jev974/run
python3 experiments/jev_comparison/scripts/compare.py \
  --run studies/jev974/run \
  --output /tmp/jev974-replay
```

`/tmp/jev974-replay` darf noch nicht existieren. Der Audit prüft Vollständigkeit und den eingefrorenen Antwortvertrag; der Scorer erzeugt die getrennten Vergleichsdateien neu. Die Ergebnisse sollten den Dateien unter [studies/jev974/scoring](../studies/jev974/scoring/) entsprechen. Die vollständige Clef-MASSIVE-Baseline bleibt darin ausdrücklich nicht verfügbar; die neue Replikation wurde auf Nutzerwunsch vorzeitig beendet. Die Summenregel `abs(math.fsum(p.values()) - 1) <= 1e-5` ist eine lokale Benchmarkregel, keine bestätigte Jev-Anbietergarantie; [Details](JEV_COMPARISON.md#technische-antwortprüfung).

Neue API-Aufrufe sind ein eigener, kostenpflichtiger und datenübertragender Lauf: Modellversion, freigegebene Eingaben, Anbieterbedingungen und Budget müssen vorher feststehen. Einen API-Schlüssel niemals in Chat, Repository oder Kommandozeile ablegen. Die [eingefrorene Vorbereitung](../experiments/jev_comparison/README.md) dokumentiert den ursprünglichen Vertrag; historische Preise dort sind keine aktuelle Preiszusage.

## Datenherkunft und Lizenz

[NOTICE](../NOTICE) und [LICENSE](../LICENSE) dokumentieren die Projekt- und Modellattribution. Die synthetischen Quelldaten sind im Vergleichspaket als Apache-2.0 ausgewiesen; MASSIVE hat eine eigene CC-BY-4.0-Lizenz und [Quellenangaben](../experiments/jev_comparison/inputs/massive300/SOURCES.md). Modellgewichte sind nicht im Repository. Rohantworten, Referenzen und wissenschaftliche Hashmanifeste nicht als Nebenwirkung einer Reproduktion verändern.
