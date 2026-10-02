# Versicherungsdokumente: UI-Datenimport

Der Versicherungsdatensatz bleibt ein eigenständiger Test: 60 Fälle, 12 synthetische
Dokumentpakete, sechs Bereiche, zwei native Choice-Felder je Fall. Die Ergebnisse
werden nicht mit den vorherigen allgemeinen, Finanz- oder clean72-Tests vermischt.

## Aufrufen

Nur Fälle ansehen, ohne Modellresultate:

```sh
python3 scripts/build_insurance_web_data.py \
  --source /path/to/insurance/benchmark --cases-only
```

Vollständig unabhängig geprüfte Resultate übernehmen:

```sh
python3 scripts/build_insurance_web_data.py \
  --source /path/to/insurance/public
```

`--source` akzeptiert das Verzeichnis mit den öffentlichen Dateien oder dessen
Projektwurzel. Ohne Angabe wird `experiments/insurance` verwendet. Standardausgabe:
`web/data/insurance.json`; `--out` überschreibt diesen Zielpfad. Das Ziel wird erst
nach vollständiger Prüfung atomar ersetzt. Quellartefakte bleiben unverändert.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tests -p test_insurance_importer.py -v
```

Die Tests verwenden ausschließlich temporäre synthetische Modelloutputs. Diese
sind keine Benchmarkresultate und gelangen nicht in die ausgelieferte JSON-Datei.
Es werden weder ein Modell geladen noch Tokenisierung oder Inferenz gestartet.

## Datenvertrag, Schema 2

- `status`: `test_data_only` oder `completed`
- `suite.id`: `insurance`; `primary_split`: `german_insurance_primary`
- `metadata`, `documents`: unveränderte Originalinhalte, einschließlich stabiler
  Dokument- und Klausel-IDs
- `cases`: Originalfälle mit `category = area`, `title = claim`,
  `gold_rationale = rationale`, `split`, `input` und `questions`
- `input`: vollständiges `request.state` als UTF-8-JSON mit sortierten Schlüsseln
  und kompakten Trennzeichen, ohne Umschreibung oder Ergänzung
- `questions`: unveränderte native `request.questions` mit `decision` und `evidence`
- `result.fields.decision` und `result.fields.evidence`: `prediction`, `correct`,
  `probabilities`, `schema_valid`
- `result.correct`: beide Felder korrekt; `result.actual_evidence_clauses`:
  Klauselmenge der tatsächlich gewählten Belegoption
- `latency_ms`, `input_tokens`: Originalwerte des jeweiligen Modelloutputs
- `summary`, `by_area`, `by_document`, `by_decision_label`, `date_version_subset`
  und `without_date_version_subset`: exakt gegen Rohoutputs nachgerechnete
  Auswertungen des unabhängigen Versicherungsberichts
- `run_metadata`, `verification`: originale Laufmetadaten und Freigabe
- `source_artifacts`: SHA-256-Werte zur Identifikation der importierten Dateien

Alle Vektoren in `result.fields.*.probabilities` stammen aus
`probabilities_unrounded`. Sie werden weder gerundet noch neu normiert. Die auf vier
Stellen gerundeten nativen API-Antworten werden auf Konsistenz geprüft, aber nicht
als Quelle für diese Vektoren verwendet.

Die getrennte Speicherung von Originalzustand als String ändert den Encodertext
nicht: Die Vendor-Funktion `render` serialisiert Objekte genau in diesem Format
und gibt Strings unverändert zurück. Ein modellfreier Test extrahiert nur diese
reine Vendor-Funktion per AST und prüft die Gleichheit für alle 60 Requests.

`test_data_only` enthält keine `summary`, Gruppenresultate, `result`, `latency_ms`
oder `input_tokens`. `verification.status` ist ausdrücklich `pending`, die
Laufmetadaten sind leer. Diese Darstellung behauptet keine durchgeführte Inferenz.

## Harte Freigabeschranke

Ein abgeschlossener Import erfordert folgende fünf Dateien sowie die Freigabe:

- `benchmark.json`
- `requests.jsonl`
- `predictions.jsonl`
- `predictions.metadata.json`
- `results.json`
- `verification.json`

Die Freigabe muss `status: verified`, einen Prüfzeitpunkt, 60 Fälle und 120 Felder,
bestandene Vor- und Nachinferenzprüfungen sowie `no_truncation: true` und
`single_primary_run: true` ausweisen. Ihre `input_hashes` müssen die SHA-256-Werte
aller fünf Inhaltsdateien exakt benennen. Die Metadaten müssen einen abgeschlossenen
Lauf der festgelegten Clef-Version mit unverändertem nativen Modellcode, denselben
Requests und derselben Reihenfolge belegen. Eingebettete und separat veröffentlichte
Laufmetadaten müssen übereinstimmen.

Zusätzlich prüft der Importer unter anderem:

- vollständige, eindeutige Fall-, Dokument-, Request- und Resultatmengen
- exakt zwei Felder und alle vier Entscheidungs- bzw. fünf Belegoptionen
- Übereinstimmung von Request, Dokumentklauseln, Szenario und Aussage
- gültige Referenz- und gewählte Klauselmengen
- vollständige native Antwortstruktur samt Vendor-Rundung und Optionswahl
- endliche Vektoren, erlaubte Optionen, gültige Wahrscheinlichkeiten und Summe
- keine Kürzung, plausible Tokenzahlen und konsistente Inferenzlatenz
- sämtliche Einzelresultate, Gesamtwerte und Teilgruppen gegen eigene Nachrechnung
- fehlende, beschädigte oder noch ausstehende Freigaben; doppelte JSON-Schlüssel
- unveränderte Bytes der drei bereits vorhandenen Benchmark-JSON-Dateien

Der Importer ersetzt keine unabhängige fachliche Prüfung: Er übernimmt nur deren
inhaltlich und per Hash gebundene Freigabe und ergänzt deterministische
Struktur-/Konsistenzprüfungen. Ein bestehendes Ziel bleibt bei einem Fehler erhalten.

## Ausgelieferter, unabhängig geprüfter Stand

`experiments/insurance/` ist der unveränderte, ausdrücklich zur Veröffentlichung
freigegebene Export: 45 Dateien und 1.594.749 Bytes. `EXPORT_MANIFEST.json` benennt
44 Inhaltsdateien samt Größe und SHA-256; die 45. Datei ist dieses Manifest selbst.
Die bewusst ausgewählten Lauf- und Ressourcenprotokolle dokumentieren ausschließlich
diesen synthetischen Versuch. Modellgewichte, virtuelle Umgebungen, Caches,
Zugangsdaten und vorherige Kandidaten gehören nicht zum Paket.

- Exportmanifest: `64c66048012c8bb67197cf5e6c1fdf48a9eb5b9308a6a14801ac4be62373a851`
- Freigabe: `c1cf1174ec84b7689a6a255279f2b42c3e7f7b92fc99d5138ac3a2fb3ad9340d`
- Unabhängige Nachprüfung: 1.811 Prüfungen, keine Blocker
- Entscheidung: 51/60; Belegauswahl: 58/60; beide Felder: 50/60

Der modellfreie Regressionstest kontrolliert alle Exportbytes gegen das Manifest,
alle 60 Zustände gegen den ursprünglichen Request und den reinen Vendor-Renderer,
alle 120 Feldvektoren gegen die tatsächlichen ungerundeten Rohoutputs sowie die
Byteidentität der erneut erzeugten UI-Datei. Der Standardaufruf benötigt keine
externen Workspace-Dateien, kein Netzwerk und kein Modell.

Der freigegebene Export normalisiert ausschließlich das Ausgabeziel im
Abschlussereignis des öffentlichen Laufprotokolls zu `results/predictions.jsonl`.
Das Manifest dokumentiert die ursprüngliche und veröffentlichte Protokoll-Prüfsumme;
der ursprüngliche private Laufmitschnitt bleibt unverändert erhalten. Fachliche
Inputs, Rohvorhersagen, Scores und unabhängige Freigabe wurden nicht verändert.
Ein zusätzlicher Test prüft sämtliche Exportdateien gegen die privaten Pfad- und
Credential-Muster des regulären Veröffentlichungsaudits.
