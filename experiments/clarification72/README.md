# Clef Flash: Nachfragen statt raten

72 neu KI-verfasste deutsche Fälle aus Banking, Versicherung und Finanzen. Der Test prüft anhand ausdrücklich fiktiver Regeln, wann Clef eine konkrete Ja/Nein-Antwort wählen kann und wann es eine fehlende Angabe, den gemeinten Vorgang oder einen Widerspruch klären sollte. 36 Fälle benötigen eine Rückfrage; 36 sind beantwortbar, darunter bewusst Fälle mit irrelevanten Lücken. Zwei native Choice-Felder pro Fall, keine generierten Antworten.

Ergebnisse stehen in [REPORT.md](REPORT.md), sämtliche Feldfehler in [ERRORS.md](ERRORS.md). [PROTOCOL.md](PROTOCOL.md) wurde vor der Modellinferenz eingefroren. Synthetisch, absichtlich geschichtet, verwandte Szenariofamilien, unabhängig KI-geprüft und **nicht menschlich-fachlich validiert**. Keine realen Kundendaten, echte Tarifbedingungen, Rechtsberatung oder Produktivreifeaussage.

## Reproduzieren

1. Python 3.12 und ausreichend CPU-RAM/Speicher bereitstellen
2. In reference_runtime/ ausführen: bash setup_runtime.sh
3. venv/bin/python download_model.py und venv/bin/python verify_files.py ausführen
4. Vom Suite-Verzeichnis: python scripts/validate.py
5. scripts/reproduce.sh /absoluter/pfad/zur/reference_runtime /absoluter/pfad/zu/neuen-ergebnissen
6. Optional den öffentlichen Export prüfen: python scripts/verify_export.py

Der neue Ergebnisordner darf keine predictions.jsonl enthalten. Das unveränderte aufgezeichnete Ergebnis wird nicht überschrieben. Jeder Fall wird vollständig gegen das 2048-Token-Limit geprüft. Ein fachfremder Warmup und ein Wiederholungscheck des ersten Falls bleiben außerhalb der Qualitäts- und Forward-Laufzeitmetriken. Für neue Messungen die ursprünglichen Berichte nicht überschreiben; die JSON-Zusammenfassung wird im gewählten neuen Ergebnisordner geschrieben.

## Laufzeit

[Cloudflare/clef-flash, offizielle Revision 17f0b0ad64efb65d273590632833508766b2aae6](https://huggingface.co/Cloudflare/clef-flash/tree/17f0b0ad64efb65d273590632833508766b2aae6), experimentelles CPU NF4 mit Double Quantization, ursprünglicher BF16-Joint-Head und BF16-Ausgabe-Embeddings. Sechs Threads, Batch 1, 2048-Token-Cap, Torch 2.11.0+cpu / Transformers 5.10.2 / bitsandbytes 0.50.2. Kein Austausch des nativen Schema-Heads durch generierte JSON-Texte. Modellgewichte werden nicht verteilt.

Die englische offizielle Wrapper-Vorlage bleibt unverändert. Regeln, Szenarien und Schema-Anweisungen sind Deutsch, die Optionskennungen Englisch. Wahrscheinlichkeiten sind rohe marginale Modellscores; daraus folgt keine kalibrierte Gewissheit.
