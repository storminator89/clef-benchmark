# Clef Lab · Deutscher Entscheidungsbenchmark

Ein nachvollziehbarer Test von **Cloudflare/Clef Flash** mit einer deutschsprachigen, lokal laufenden Website: Ergebnisse erkunden, Fehler analysieren und eigene Texte mit einem nativen Entscheidungsschema ausprobieren.

**Repository:** [storminator89/clef-benchmark](https://github.com/storminator89/clef-benchmark)

## Schnellstart: Website ohne Modell

Voraussetzung: **Python 3.12+**. Keine Python-Pakete, kein npm, keine GPU und keine Internetverbindung erforderlich.

```bash
git clone https://github.com/storminator89/clef-benchmark.git
cd clef-benchmark
python3 server.py
```

Dann **http://127.0.0.1:8765** öffnen. Unter Windows heißt der Befehl gegebenenfalls `python server.py`.

- **Drei getrennte Texttests:** allgemeine Entscheidungen, Finanzen/Versicherungsmakler und 72 alltagsnahe Fälle ohne Manipulation, mit eigenständigen Ergebnissen
- **Übersicht:** echte, abgeschlossene und unabhängig nachgerechnete Ergebnisse
- **Fälle entdecken:** Filter nach Sprache, Kategorie, Herausforderung und Fehlern; Input, Sollantwort, Richtlinie und Wahrscheinlichkeiten
- **Playground:** Eingabetext und natives `choice`-Schema bearbeiten; unveränderte gespeicherte Antworten ansehen
- **Methodik:** Grenzen, Konfiguration und Primärquellen
- Dunkles/helles Design, mobile Layouts, Tastaturbedienung, JSON-Export

Die Website funktioniert offline über den lokalen Server. Direktes Öffnen von `web/index.html` als `file://` wird wegen Modul-/Dateizugriffsbeschränkungen nicht unterstützt. Die statischen Dateien unter `web/` funktionieren auch auf einem gewöhnlichen Static-File-Server; echte Inferenz benötigt dagegen `server.py`.

**Gespeicherte Antwort ≠ neue Inferenz:** Replay zeigt ausschließlich die unveränderte Antwort eines tatsächlichen Benchmark-Laufs. Sobald Text oder Schema verändert werden, wird Replay deaktiviert. Ohne aktives lokales Modell werden keine Antworten simuliert.

## Echte lokale Inferenz aktivieren

Experimentell getestet auf **Linux x86-64, Python 3.12, CPU**. Andere Betriebssysteme oder GPUs sind hier nicht validiert.

**AMD-GPU optional vorbereitet:** Der Live-Server kann ausdrücklich `--inference-profile rocm-bf16` oder `rocm-fp16` verwenden. Standard bleibt `cpu-nf4`. Die neuen GPU-Pfade sind modellfrei getestet, aber **nicht auf AMD-Hardware ausgeführt**. Sie brauchen eine separate ROCm-PyTorch-Umgebung und deutlich mehr GPU-Speicher; die CPU-Installation unten reicht dafür nicht. Voraussetzungen, Linux-Mint-/Windows-Grenzen und Startbefehle: [`docs/AMD_GPU.md`](docs/AMD_GPU.md). Das betrifft die Radeon-GPU, nicht die Ryzen-AI-NPU.

Der gepinnte Download umfasst ungefähr **19 GB Modellgewichte**; zusätzliche Umgebung, Cache und temporäre Dateien brauchen weiteren Speicher. Im CPU-NF4-Profil verlangt der Adapter vor dem Laden **mindestens 7,5 GiB freien RAM**; mindestens 8 GiB verfügbarer RAM werden empfohlen. Das Modell belegt in dieser CPU-NF4-Konfiguration ungefähr 6–7,5 GB RAM. Die erste Anfrage prüft Datei-Hashes und lädt das Modell, was je nach Rechner mehrere Minuten dauern kann. Es erfolgt kein automatischer Download.

```bash
bash runtime/setup_runtime.sh
runtime/venv/bin/python runtime/download_model.py
python3 scripts/verify_model_download.py
runtime/venv/bin/python server.py --enable-inference --model-dir runtime/model
```

Im Playground wird „Echte Inferenz starten“ erst aktiv, wenn der lokale Server explizit mit diesem Flag gestartet wurde. Neue Anfragen bleiben getrennt von den eingefrorenen Testdaten und verändern keine Scores. Nur eine Modellanfrage wird gleichzeitig ausgeführt; parallele Anfragen erhalten HTTP 409. Der Server lädt das Modell erst bei der ersten Anfrage. Das Schließen der Browserseite bricht eine bereits laufende Modellberechnung nicht ab.

### Modell und Konfiguration

- Offizielles Modell: [`Cloudflare/clef-flash`](https://huggingface.co/Cloudflare/clef-flash)
- Revision: `17f0b0ad64efb65d273590632833508766b2aae6`
- Originaler Joint-Schema-Head, **keine Chat-Generierung als Ersatz**
- CPU-NF4-Backbone mit Double Quantization; Head und Output-Embeddings BF16
- Torch 2.11.0+cpu, Torchvision 0.26.0+cpu, Transformers 5.10.2, bitsandbytes 0.50.2
- Vollständige Pins in [`runtime/requirements_frozen.txt`](runtime/requirements_frozen.txt)
- 6 CPU-Threads, Batchgröße 1, maximal 2.048 Tokens, keine stille Kürzung

Diese experimentelle CPU-Quantisierung ist nicht die BF16-/GPU-Herstellerkonfiguration. Qualität und Laufzeiten gelten ausschließlich für die dokumentierte lokale Konfiguration.

### Sicherheit und Grenzen des Playgrounds

- Bindet ausschließlich an `127.0.0.1`; keine öffentliche Modell-API
- Validiert Host und Origin; kein CORS, kein URL-Proxy, kein Datei-Upload, keine API-Keys
- Keine externen Skripte, Fonts, Analytics oder CDN-Abhängigkeiten
- Maximal 32 KiB Request, 6.000 Eingabezeichen, eine `choice`-Frage, 2–12 Klassen
- Richtlinie maximal 4.000 Zeichen; Klassenbeschreibung maximal 300 Zeichen
- Klassennamen: Buchstabe am Anfang, danach Buchstaben/Ziffern/`_`/`-`, maximal 64 Zeichen
- Nur Text ist hier getestet und freigeschaltet; keine Bildinferenz
- Eingaben werden vom Server nicht in Dateien oder Zugriffslogs geschrieben; sie werden für die Berechnung im RAM verarbeitet
- Nicht als Mehrbenutzer- oder Produktionsdienst betreiben. Kein Reverse-Proxy oder Port-Forwarding ohne eigene Authentifizierung und Sicherheitsprüfung
- Keine echten Gesundheits-, Finanz- oder Kundendaten für diese Demo verwenden

## Ergebnisse des allgemeinen Benchmarks

**120 deutsche Hauptfälle**, dazu 30 englische Kontrollen und 30 Deutsch/Englisch-Schema-Diagnosen: **180 Requests aus 120 eigenständigen Szenarien**.

| Teilmenge | Korrekt | Genauigkeit |
|---|---:|---:|
| Deutsch / Deutsch, Haupttest | 116 / 120 | 96,7 % |
| Englisch / Englisch, ausgewählte Kontrollen | 29 / 30 | 96,7 % |
| Deutsch / Englisch, separate Diagnose | 29 / 30 | 96,7 % |

Alle 180 nativen Ausgaben sind schema-gültig. Ein Sprachvergleich muss die **gleichen 30 gepaarten Fälle** vergleichen, nicht den gesamten deutschen Hauptsatz mit der ausgewählten Kontrollgruppe. Die gepaarten deutschen Fälle sind 30/30 korrekt, die englischen 29/30. Das ist eine kleine explorative Stichprobe, kein Beweis einer allgemeinen Sprachüberlegenheit.

Die Fälle sind vollständig synthetisch, KI-verfasst, balanciert und vor der Inferenz fixiert. Sie sind kein repräsentativer Produktionsdatensatz. Keine allgemeine Sprachkompetenz, Beratungseignung oder Sicherheit wird daraus abgeleitet.

Vollständige Methodik: [`benchmark/README.md`](benchmark/README.md). Nachweis und Provenienz: [`provenance/`](provenance/). Reproduktion: [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Separate Erweiterung: Finanzen & Versicherungsmakler

**80 deutsche Fälle in acht Kategorien**, ergänzt um **20 ausgewählte englische Kontrollen**: 100 Requests aus 80 eigenständigen Szenarien. Die Erweiterung wurde nach dem allgemeinen Test separat beauftragt und vor ihrer eigenen Inferenz unabhängig geprüft und eingefroren. Es werden keine Scores beider Suiten zusammengerechnet.

Die Aufgaben betreffen Versicherungsanliegen, Schadenrouting, Vertragsservice, Makler-Workflows, Dokumentklassen, Finanzanliegen, ausdrücklich fiktive Regelprüfungen und Eskalation zur qualifizierten Prüfung. Alle Beispiele und Personen sind synthetisch. Es werden keine Verträge abgeschlossen, Produkte empfohlen, Transaktionen ausgeführt oder reale Entscheidungen über Menschen getroffen. Ein korrektes Routinglabel bestätigt weder eine Vollmacht noch rechtliche Zulässigkeit, Deckung, Beratungsqualität oder Produktionstauglichkeit.

Der abgeschlossene Finanz-/Maklertest erreicht **76/80 (95,0 %) deutsche** und **18/20 (90,0 %) englische** Entscheidungen. Alle 100 Antworten sind schema-gültig. Auf den gleichen 20 Paaren sind die deutschen Varianten 20/20 korrekt und die englischen 18/20; daraus folgt kein belastbares allgemeines Sprachranking.

Unter den vier deutschen Fehlern sind drei verpasste Rückfragen und eine Fristberechnung über einen Monatswechsel. Zwei falsche Entscheidungen entsprechen dem eingeschleusten Antwortziel mit mehr als 92 % Modellkonfidenz. Das unterstreicht die Grenze hoher Konfidenz und verbietet eine pauschale Sicherheits- oder Produktionstauglichkeitsaussage.

Die Website hat einen Suite-Umschalter; beide abgeschlossenen Suiten sind unabhängig geprüft und verfügbar. Dateien: [`finance_benchmark/`](finance_benchmark/) und [`results/finance/`](results/finance/). Reproduktion und Grenzen: [`docs/FINANCE_REPRODUCIBILITY.md`](docs/FINANCE_REPRODUCIBILITY.md).

Wichtig für Sprachvergleiche: Die 20 englischen Kontrollen decken nur zwei bis drei der fünf Klassen je Kategorie ab. Der Macro-F1 über alle fünf Richtlinienklassen kann dadurch selbst bei perfekten englischen Vorhersagen höchstens 0,5 erreichen. Die Website vergleicht deshalb die Genauigkeit auf den gleichen 20 Paaren; sie verwendet keinen solchen F1-Unterschied als Sprachlücke.

## Neue Folgetests: ohne Manipulation, Bilder und Angriffsentfernung

- **72 neue alltagsnahe deutsche Bürofragen ohne Manipulation:** **61/72 (84,7 %)** richtig, alle Antworten schema-gültig. Mehrstufige Beitragsrechnungen liegen bei **6/12**; die übrigen Bereiche bei 10–12/12. In der Website als eigene Suite verfügbar. [Ergebnisse und Reproduktion](experiments/clean72/README.md)
- **Separater Bildtest mit HuggingFace-Daten:** 30 synthetische Diagramme und 20 deutsche synthetische Belege, dazu gepaarte Englisch- und Weißbildkontrollen, insgesamt **90 echte Vision-Läufe**. Diagrammart 27/30, Legendenanzahl 30/30, Belegart 20/20, Steuerhinweis 19/20, Bruttosummen-Intervall 18/20. Die drei Diagrammart-Abweichungen haben überlappende Antwortbeschreibungen und sind keine drei eindeutig belegten Erkennungsfehler. [Ergebnisbericht und Grenzen](experiments/images/README.md) · [PDF](experiments/images/report/Clef_Bildbenchmark_2026-10-02.pdf)
- **Sieben Angriff-/Entfernungs-Paare:** mit Angriff **4/7**, nach Entfernung **5/7** richtig; zwei Entscheidungen ändern sich, nur ein Fehler wird behoben. Separate nachträgliche Diagnose der ursprünglichen Finance-Fälle. Nur der angehängte Angriffstext wurde entfernt; Sachverhalt, Regeln und Gold bleiben gleich. [Alle Paare und Resultate](experiments/attack_ablation14/RESULTS.md)

Diese Suiten werden weder miteinander noch mit den ursprünglichen 280 Textrequests gepoolt. Der neue saubere Satz hat andere Aufgaben und Schwierigkeiten, daher belegt ein Quotenunterschied keinen kausalen Manipulationseffekt. Die Bildresultate bleiben ein eigener Bericht; der lokale Playground unterstützt weiterhin ausschließlich Text. Das Paket enthält keine Rohbilder oder vollständigen ursprünglichen Rechnungslabels; Quellen, Lizenzen und reproduzierbare Beschaffung stehen im Bildpaket. Die zwei gekennzeichneten Berichtsausschnitte sind mit Attribution enthalten.

## Dateien

```text
web/                 Dependency-freie Website mit geprüften Ergebnisdaten
server.py            Loopback-Server, Requestvalidierung und opt-in Live-API
benchmark/           Eingefrorene allgemeine Fälle, Requests, Goldlabels und Scorer
runtime/             Gepinnter Download, Original-Head, Runner und Lazy-Live-Adapter
finance_benchmark/   Separat eingefrorene Finanz-/Makler-Erweiterung
results/             Abgeschlossene Originalresultate; Finance unter results/finance/
experiments/         Getrennte clean72-, Bild- und Sieben-Paar-Folgetests
qa/                  Unabhängige Daten-/Scorerprüfungen
scripts/             Prüfungen, UI-Datenimport und Public-Release-Audit
tests/               Server-, UI-Logik- und optionale Browsertests
docs/                Reproduktion und Validierungsdokumentation
licenses/            Upstream-Lizenz
```

Modelle, virtuelle Umgebungen, Caches, Schlüssel und private Pfade gehören nicht ins Repository.

## Prüfen und reproduzieren

Die folgenden Befehle laden kein Modell und führen keine Inferenz aus:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/test_web.mjs
python3 scripts/check_project.py
python3 scripts/check_followups.py
python3 scripts/build_web_data.py --suite general
python3 scripts/build_web_data.py --suite finance
python3 scripts/build_clean_web_data.py
python3 scripts/audit_public.py
```

Die gleichen modellfreien Prüfungen laufen in GitHub Actions; Details und gepinnte Action-Revisionen in [`docs/CI.md`](docs/CI.md). Eine lokale Prüfung ersetzt keinen Nachweis des späteren CI-Laufs.

Node **22+** ist nur für die JavaScript-Tests erforderlich; getestet mit Node 24.19.0. Es gibt keine npm-Abhängigkeiten. `scripts/build_web_data.py` verweigert unvollständige Läufe, fehlende IDs, geänderte Freeze-Dateien oder eine unpassende unabhängige Gegenprüfung. `--cases-only` erzeugt ausdrücklich als ergebnisfrei markierte Testdaten für Entwicklung, niemals partielle Scores.

Die Unit-Test-Discovery importiert das optionale Browserskript ohne Browserstart; der Start erfolgt nur beim direkten Aufruf.

Optionale echte Browserregression: `tests/test_browser.py` verwendet **Playwright 1.62.0** und ein lokal verfügbares Chromium (`CHROMIUM_PATH` setzt den Pfad). Die optionale Abhängigkeit steht in `tests/requirements-browser.txt`. Server vorher starten; dann `python3 tests/test_browser.py` ausführen. Browserlaunch und visuelle QA waren in der Erstellungssandbox blockiert; diese Prüfung ist **nicht als bestanden** ausgewiesen. Details in [`docs/VALIDATION.md`](docs/VALIDATION.md).

Für eine neue vollständige Modellreproduktion nach Einrichtung: `bash runtime/reproduce.sh`. Eigene Läufe in neue Dateien schreiben, niemals die archivierten Originalresultate überschreiben.

## Lizenz & Attribution

Eigener Code und synthetische Daten: **Apache-2.0**, siehe [LICENSE](LICENSE). Unveränderter Cloudflare-Code und Modell: eigene Upstream-Attribution in [NOTICE](NOTICE) und [licenses/](licenses/). Modellgewichte werden nicht mitgeliefert. Unabhängiges Projekt ohne Zugehörigkeit zu oder Bestätigung durch Cloudflare.
