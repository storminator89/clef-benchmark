# Reproduktion des Bildtests

Immer eine separate Arbeitskopie verwenden. Die ursprünglichen Ergebnisse und das Freeze-Manifest werden nicht überschrieben. Rohbilder sind absichtlich nicht im Ergebnis-Paket enthalten.

## Voraussetzungen

- Python 3.12; Paketversionen in `provenance/runtime_requirements.txt`
- Zusätzlich `pyarrow==25.0.1` und Pillow für die Datenextraktion
- Der unveränderte offizielle Clef-Release `Cloudflare/clef-flash` in Revision `17f0b0ad64efb65d273590632833508766b2aae6`, mit allen vier Backbone-Safetensors, `joint_head.safetensors`, offiziellem Python-Loader, Processor und Tokenizer
- CPU-RAM mit ausreichend Reserve. Originalcomputer: 9,7 GiB, kein Swap; sechs Threads. Der RAM-Wächter beendet den Lauf bei mehr als 8,3 GiB Prozess-RSS oder weniger als 0,4 GiB freiem verfügbarem RAM

Der Unterordner `runtime/` enthält kopierte, unveränderte Setup- und Modelldownload-Skripte des zuvor geprüften Clef-Textprojekts. In einer frischen Arbeitskopie lassen sich `bash runtime/setup_runtime.sh`, `runtime/venv/bin/python runtime/download_model.py` und `runtime/venv/bin/python runtime/verify_files.py` ausführen. Dafür werden etwa 19 GB Modelldaten plus Arbeitsreserve heruntergeladen. Die zusätzlichen Datenpakete lassen sich mit `runtime/venv/bin/python -m pip install -r provenance/data_requirements.txt` installieren. `--runtime` bezeichnet dessen Runtime-Verzeichnis mit Unterordner `model`, nicht nur einen Modellnamen. Alternativ den offiziellen Release über `huggingface_hub.snapshot_download` mit der genannten Revision in `<runtime>/model` laden. Keine fremden Checkpoints oder umgebauten GGUF-Sprachmodelle verwenden.

## Daten erneut beschaffen und identisch aufbauen

In der frischen Paket-Arbeitskopie:

```bash
python scripts/acquire_sources.py
python scripts/materialize_pilot.py
python scripts/build_benchmark.py
python scripts/verify_freeze.py
```

`acquire_sources.py` lädt nur den gepinnten Diagramm-Test-Parquet und die freie 40-Belege-Vorschau, keine kostenpflichtigen Daten. Originalbildbytes bleiben unverändert. Der unabhängige Extraktionscheck bestätigte für 200 Bild-/Labeldateien identische Bytes. Manifest-Pfade sind maschinenabhängig; alle benchmarkrelevanten Fälle und Dateiprüfwerte sind relativ und reproduzierbar.

Das ursprüngliche `source/provenance.json`, die Vorab-Audits, `qa/encoding_preflight.json` und das originale Testprotokoll bleiben als Nachweise im Paket. Neue Preflight-/Testprotokolle in separate Dateien oder eine weitere Arbeitskopie schreiben; ihre Zeitangaben können abweichen. Das Freeze-Manifest bestätigt exakt die ursprünglichen Messinputs.

## Inferenz

Mit der gepinnten Runtime-Python-Umgebung:

```bash
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6
<runtime>/venv/bin/python scripts/guard_run.py \
  <runtime>/venv/bin/python scripts/run_images.py \
  --runtime <runtime> \
  --requests benchmark/requests.jsonl \
  --output results/reproduced_predictions.jsonl \
  --max-pixels 786432 \
  --visual-warmup benchmark/pilot_requests.jsonl
```

Der Runner verweigert bestehende Ausgabedateien. Er verlangt Original-BF16-Ausgabeembedding, BF16-Joint-Head und komplett BF16-Vision-Encoder. Der Sprachkern ist NF4; die offizielle Encoder-/Collate-/Forward-/Answer-Kette bleibt erhalten. Batch 1, maximal 4.096 Tokens; jeder Request wird zusätzlich ungekürzt kodiert und auf Gleichheit geprüft. Keine Auflösung oder Fragen nach Betrachtung der Testergebnisse ändern.

## Auswerten

```bash
python scripts/score_images.py \
  --predictions results/reproduced_predictions.jsonl \
  --output results/reproduced_scores.json
```

Der Scorer überprüft zunächst das Freeze-Manifest und verlangt exakt alle 90 eindeutigen Vorhersagen. Unvollständige Läufe werden nicht als Resultat ausgegeben. Gold wird ausschließlich hier gelesen. Ein einzelner Erstfall wird am Laufende erneut gerechnet; dies ist nur ein enger Wiederholbarkeitscheck, kein Nachweis plattformübergreifender Deterministik.

## Datenlizenz und Weitergabe

Diagramme: Publisher-Deklaration CC-BY-4.0, Attribution YuukiAsuna / Synthetic Chart Dataset. Belege: „Belege (Immineal, 2026)“, freie Vorschau eines kostenpflichtigen Datensatzes; lokale kommerzielle und nichtkommerzielle Evaluierung erlaubt. Ein öffentlich weiterverteilbarer unveränderter Vorschau-Spiegel hat besondere Bedingungen. Das Ergebnis-Paket enthält daher keine Originalbilddateien oder vollständigen ursprünglichen Rechnungslabels. Zwei im Bericht eingebettete dokumentarische Gesamtsummen-Ausschnitte sind nach der ausdrücklichen Abbildungsfreigabe mit Belege-Attribution zulässig. Siehe `NOTICE` und `licenses/BELEGE-LICENCE.txt`.

## Portable Veröffentlichung

Die gemessenen Rohvorhersagen, Konfigurationen, Aufgaben, Goldlabels und das Original-Freeze-Manifest bleiben byteidentisch. Für die Veröffentlichung wurden ausschließlich zwei lokale Runtime-Defaults auf das Paketverzeichnis umgestellt und zugehörige Prüfungen um ein transparentes Original-zu-Export-Hashmapping erweitert. `provenance/portable_export.json` nennt für jede betroffene Datei beide Hashes und die Änderung. Die Auswertungsfunktion sowie die Inferenzlogik bleiben unverändert. Historische Hashes werden nicht nachträglich umgeschrieben. `scripts/provenance_checks.py` akzeptiert genau diese dokumentierte Portierung. Originalbilder fehlen absichtlich; die vollständige Freeze-Prüfung ist erst nach dem gepinnten Download und Aufbau möglich. Der Paketinhalt selbst kann vorab anhand `package_manifest.json` geprüft werden.
