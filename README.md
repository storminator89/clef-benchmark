<div align="center">

# Clef Lab

### Entscheidungen nachvollziehen. Fehler verstehen. Eigene Fälle prüfen.

Eine lokale Workbench für **Cloudflare Clef**: deutsche Benchmarks, transparente Fehleranalyse und private Texttests mit dem **nativen Decision Head**.

**Flash 9B als Standard · Fünf getrennte Textsuiten · Buildfreie Oberfläche · Apache-2.0**

[Geprüfte CI](https://github.com/storminator89/clef-benchmark/actions/runs/37017832006) · [Echter CPU-Smoke](qa/setup_custom_smoke.json) · [Lizenz](LICENSE)

[Schnellstart](#schnellstart) · [Ergebnisse](#ergebnisse) · [Eigene Tests](#eigene-tests) · [Modell & Hardware](#modell-und-hardware) · [Agenten-Setup](AGENTS.md)

</div>

---

Clef Lab macht aus Modellantworten prüfbare Ergebnisse: Originaltext, Aufgabenregeln, Referenzlabels, Entscheidung und sämtliche Modellwahrscheinlichkeiten bleiben sichtbar. Du kannst abgeschlossene Läufe ohne Modell erkunden oder ausdrücklich aktivierte, lokale Inferenz für eigene Fälle verwenden.

**Der Fokus liegt auf nachvollziehbarer Evaluation.** Das Projekt ist ein unabhängiger, experimenteller Test von Cloudflare Clef. Die kleinen synthetischen Suiten belegen weder State-of-the-Art-Leistung noch Produktionsreife oder Sicherheit bei echten Kundenanfragen.

<!-- CLEF_GALLERY_START -->
<!-- Only insert actual inspected PNGs, their verified manifest and the passing-run
     README-GALLERY.txt here. No placeholder image links or browser-pass claim. -->
<!-- CLEF_GALLERY_END -->

## Schnellstart

### Ergebnisse ansehen: nur Python

Voraussetzung: **Python 3.12+** und eine Kopie dieses Repositories. Nach dem Klonen funktioniert die Ergebnisansicht offline: **keine ML-Pakete, kein npm, kein Modell, keine GPU**.

```bash
git clone https://github.com/storminator89/clef-benchmark.git
cd clef-benchmark
python3 server.py
```

**[http://127.0.0.1:8765](http://127.0.0.1:8765)** öffnen. Unter Windows heißt der Befehl gegebenenfalls `python server.py`.

| Du möchtest … | Einstieg |
|---|---|
| Verstehen, was getestet wurde | Suite-Katalog und Übersicht öffnen |
| Eine Entscheidung überprüfen | Fall wählen, Regeln lesen, Gold und Modell vergleichen |
| Versicherungsbelege prüfen | Dokument-Workbench mit Klauseln und Evidenzmengen öffnen |
| Eigene Texte auswerten | „Eigene Tests“ öffnen und zuerst die Datei prüfen |
| Das lokale Modell einrichten | Mit dem [Setup-Plan](#lokale-inferenz-einrichten) beginnen |

`web/index.html` bitte nicht direkt per `file://` öffnen: Browser begrenzen dort Modul- und Dateizugriffe. Die Dateien unter `web/` funktionieren auch auf einem gewöhnlichen Static-File-Server; echte Inferenz benötigt `server.py`.

### Ein Repository-Link für deinen Agenten

Gib deinem Agenten [dieses Repository](https://github.com/storminator89/clef-benchmark) und bitte ihn, `AGENTS.md` zu folgen. Der Einstieg ist vollständig im Projekt dokumentiert: Hardware prüfen, Profil ausdrücklich wählen, isolierte Umgebung vorbereiten, gepinnte Modellbytes verifizieren und einen echten synthetischen Smoke ausführen.

```bash
# Nur prüfen: keine Installation, kein Download, kein Modellladen
python3 -m runtime.setup --plan --profile cpu-nf4

# Erst nach Freigabe und erfolgreicher Prüfung: Setup + Verifikation + Smoke
python3 -m runtime.setup --profile cpu-nf4 --execute --smoke
```

Ein Agent benötigt Zugriff auf den gewünschten Rechner und deine Freigabe für Installation, Download und Modelllauf. Unbekanntes Betriebssystem, fehlende Rechte oder Treiber sind mögliche Blocker. Der Setup-Plan liefert sie als JSON; er verspricht keine universell unbeaufsichtigte Installation.

[Agentenanweisungen](AGENTS.md) · [Vollständiger Setup-Vertrag](docs/AGENT_SETUP.md) · [RAM, VRAM und Festplatte](docs/HARDWARE.md)

## Die Workbench

| Bereich | Was du bekommst |
|---|---|
| **Ergebnisse erkunden** | Fünf getrennte Textsuiten, eigene Nenner, Suche, Fehlerfilter, Fall-Deep-Links und passende Sprachkontrollen |
| **Dokumente verstehen** | Fallbibliothek, Klauselleser und Antwortprüfung auf dem Desktop; getrennte Bereiche auf schmalen Displays |
| **Entscheidungen prüfen** | Gold-/Modellvergleich pro Feld, vollständige angebotene Belegmengen und alle ungerundeten Modellwahrscheinlichkeiten |
| **Playground nutzen** | 1–8 native `choice`-Fragen pro Anfrage; gespeichertes Replay und neue lokale Inferenz klar getrennt |
| **Eigene Tests ausführen** | JSON-/JSONL-/CSV-Vorschau, privater Editor, sequentieller Lauf, Fortschritt, Stop und ausdrücklicher Export |
| **Zustand erkennen** | Server erreichbar, Inferenz freigegeben und Modell geladen sind drei getrennte Stufen |

Helles/dunkles Design, Tastaturbedienung, sichtbare Editoränderungen und mobile Bereichsumschaltung sind implementiert. Den tatsächlichen Browser-Prüfstand findest du unter [Prüfung und Reproduktion](#prüfung-und-reproduktion).

**Gespeicherte Antwort ≠ neue Inferenz:** Replay zeigt ausschließlich die unveränderte Antwort eines tatsächlichen Benchmark-Laufs. Eine Änderung an Text oder Schema deaktiviert Replay. Ohne aktives lokales Modell werden keine Antworten simuliert. „Status aktualisieren“ prüft nur das Backend und startet weder Download noch Inferenz.

[Architektur und Bedienung](docs/UI_WORKBENCH.md) · [Live-API](docs/LIVE_API.md) · [Versicherungsdaten in der UI](docs/INSURANCE_UI_DATA.md) · [Bankdaten in der UI](docs/BANK_SUPPORT_UI_DATA.md)

## Ergebnisse

Alle folgenden Werte stammen aus abgeschlossenen **Flash-9B-/CPU-NF4-Läufen**. Jede Suite hat ihre eigenen Aufgaben, Referenzen und Nenner. **Es gibt keinen gepoolten Gesamtscore und kein Modellranking.** Schema-Gültigkeit, Fachgenauigkeit und Sicherheit sind unterschiedliche Größen.

| Textsuite | Eigenständige Szenarien | Hauptmaß | Wichtigste Einordnung |
|---|---:|---:|---|
| **Bank-Kundensupport** | 80 | **68/80 · 85,0 %** alle drei Felder richtig | Anliegen, Priorität und nächster Schritt; nur 8/10 kritische Fälle vollständig richtig |
| **Versicherungsdokumente** | 60 | **50/60 · 83,3 %** beide Felder richtig | Entscheidung und Evidenz; fünf korrelierte Fälle je Dokument |
| **Allgemeine Entscheidungen** | 120 | **116/120 · 96,7 %** deutscher Haupttest | Weitere 60 Sprachkontroll-/Diagnose-Requests aus vorhandenen Szenarien |
| **Finanzen & Makler** | 80 | **76/80 · 95,0 %** deutscher Haupttest | Weitere 20 ausgewählte englische Kontrollen; eigene Suite |
| **clean72** | 72 | **61/72 · 84,7 %** deutsche Entscheidungen | Neue Bürofragen ohne Manipulation; andere Aufgaben und Schwierigkeit |

Der Bildtest und die Angriffsentfernungs-Diagnose bleiben **separate Berichte**, keine weiteren Textsuiten im Dashboard. Die folgenden Details gehören zur Interpretation der Zahlen.

### Bank-Kundensupport

**80 synthetische deutsche Anfragen**, zehn gestaltete Themenbereiche, keine Manipulationsanweisungen. Grundlage ist eine ausdrücklich **fiktive Servicerichtlinie**. Dies ist ein eigener Pilot, kein BANKING77 und keine repräsentative Stichprobe realer Bank-Tickets.

| Feld | Korrekt | Anteil |
|---|---:|---:|
| Anliegen (`intent`) | 76 / 80 | 95,0 % |
| Priorität (`priority`) | 77 / 80 | 96,3 % |
| Nächster Schritt (`next_step`) | 75 / 80 | 93,8 % |
| **Alle drei Felder** | **68 / 80** | **85,0 %** |

**Die Prioritätsbaseline ist bereits 80 %:** Immer `routine` zu wählen ergibt 64/80. Kritische Fehler und vollständige Fälle müssen deshalb separat betrachtet werden:

- **0/10** verfehlte kritische Prioritäten und **0/10** fehlende kritische Security-Handoffs
- Trotzdem nur **8/10 kritische Fälle vollständig richtig**: Zwei erhielten das falsche Anliegen
- **0/6** dringende Fälle als Routine eingeordnet; ein unnötiger Security-Handoff unter 70 nicht-kritischen Fällen
- **3/45** unnötige Eskalationen bei Referenzfällen ohne Eskalationsbedarf
- Bei notwendiger Rückfrage: **11/14** nächste Schritte, aber nur **10/14** vollständige Fälle richtig

Null beobachtete kritische Prioritätsfehler bei zehn Beispielen sind **kein Sicherheitsnachweis**. Alle 80 Requests beziehungsweise 240 Felder sind schema-gültig und ungekürzt. Der reine CPU-NF4-Forward dauerte im Median **40,88 s**; Laden und Warm-up sind ausgeschlossen. Daraus folgt keine GPU- oder Produktionslatenz.

[Ergebnisbericht](experiments/bank-support/REPORT.md) · [Alle zwölf Fehlerfälle](experiments/bank-support/ERRORS.md) · [Quellen und Reproduktion](experiments/bank-support/README.md)

### Versicherungsdokumente

**60 synthetische deutsche Fälle zu zwölf fiktiven Dokumenten** in sechs Bereichen. Je fünf Fälle teilen ein Dokument und sind daher korreliert. Pro Fall gibt es zwei native Fragen: Ist die Aussage gestützt, widerlegt, offen oder widersprüchlich? Welche **angebotene Klauselmenge** trägt die Entscheidung?

| Prüfkriterium | Korrekt | Anteil |
|---|---:|---:|
| Entscheidung | 51 / 60 | 85,0 % |
| Evidenzauswahl | 58 / 60 | 96,7 % |
| **Beide Felder** | **50 / 60** | **83,3 %** |

**Acht der neun falschen Entscheidungen wählen trotzdem die richtige Evidenz.** Die Belegquote ist keine Gesamtgenauigkeit für Dokumentverständnis. Alle 120 Felder in 60 Requests sind schema-gültig; die unabhängige Nachprüfung umfasst 1.811 erfolgreiche Prüfungen.

Referenzbegründungen wurden von einer KI verfasst und vor der Inferenz durch eine zweite KI geprüft. Sie sind keine externen menschlichen Fachgutachten und keine von Clef erzeugten Erklärungen. Kurze konstruierte Klauseln und angebotene Belegmengen prüfen weder vollständige reale Policen, OCR, freie Zitatgenerierung noch Rechtsberatung oder Produktionsreife. Diese Suite enthält keine arithmetischen Aufgaben.

[Ergebnisbericht](experiments/insurance/REPORT.md) · [Alle Fehlerfälle](experiments/insurance/ERRORS.md) · [Methodik](experiments/insurance/METHODOLOGY.md) · [Quellen und Reproduktion](experiments/insurance/README.md)

<details>
<summary><strong>Allgemeine Entscheidungen: Haupttest und Sprachkontrollen</strong></summary>

**120 deutsche Hauptfälle**, 30 englische Kontrollen und 30 Deutsch/Englisch-Schema-Diagnosen: **180 Requests aus 120 eigenständigen Szenarien**.

| Teilmenge | Korrekt | Genauigkeit |
|---|---:|---:|
| Deutsch / Deutsch, Haupttest | 116 / 120 | 96,7 % |
| Englisch / Englisch, ausgewählte Kontrollen | 29 / 30 | 96,7 % |
| Deutsch / Englisch, separate Diagnose | 29 / 30 | 96,7 % |

Alle 180 Ausgaben sind schema-gültig. Der Sprachvergleich verwendet die **gleichen 30 gepaarten Fälle**: Deutsch 30/30, Englisch 29/30. Der gesamte deutsche Hauptsatz darf nicht mit der ausgewählten englischen Kontrollgruppe verglichen werden. Diese kleine explorative Stichprobe belegt keine allgemeine Sprachüberlegenheit.

Die Fälle sind vollständig synthetisch, KI-verfasst, balanciert und vor der Inferenz fixiert. Sie erlauben keine Aussage über repräsentative Produktionsdaten, allgemeine Sprachkompetenz, Beratungseignung oder Sicherheit.

[Methodik und Daten](benchmark/README.md) · [Provenienz](provenance/) · [Reproduktion](docs/REPRODUCIBILITY.md)

</details>

<details>
<summary><strong>Finanzen & Makler: eigener Test, eigene Fehleranalyse</strong></summary>

**80 deutsche Fälle in acht Kategorien**, ergänzt um **20 ausgewählte englische Kontrollen**: 100 Requests aus 80 eigenständigen Szenarien. Die Erweiterung wurde separat beauftragt und vor ihrer eigenen Inferenz unabhängig geprüft und eingefroren.

- Deutscher Haupttest: **76/80 · 95,0 %**
- Englische Kontrollen: **18/20 · 90,0 %**
- Auf denselben 20 Paaren: Deutsch **20/20**, Englisch **18/20**
- Alle **100 Antworten schema-gültig**

Die vier deutschen Fehler: drei verpasste Rückfragen und eine Fristberechnung über einen Monatswechsel. Zwei falsche Entscheidungen entsprechen dem eingeschleusten Antwortziel mit **mehr als 92 % Modellkonfidenz**. Hohe Konfidenz begründet keine pauschale Sicherheits- oder Produktionstauglichkeit.

Die Aufgaben betreffen Versicherungsanliegen, Schadenrouting, Vertragsservice, Makler-Workflows, Dokumentklassen, Finanzanliegen, fiktive Regelprüfungen und Weiterleitung zur qualifizierten Prüfung. Alle Personen und Beispiele sind synthetisch. Es werden keine Verträge abgeschlossen, Produkte empfohlen, Transaktionen ausgeführt oder reale Entscheidungen über Menschen getroffen. Ein korrektes Routinglabel bestätigt weder Vollmacht, rechtliche Zulässigkeit, Deckung noch Beratungsqualität.

Die 20 englischen Kontrollen decken nur zwei bis drei der fünf Klassen je Kategorie ab. Ein Macro-F1 über alle fünf Klassen kann deshalb selbst bei perfekten englischen Vorhersagen höchstens 0,5 erreichen. Die Website vergleicht die Genauigkeit auf denselben Paaren und deutet einen solchen F1-Unterschied nicht als Sprachlücke. Auch der gepaarte Test liefert kein belastbares allgemeines Sprachranking.

[Daten](finance_benchmark/) · [Originalresultate](results/finance/) · [Reproduktion und Grenzen](docs/FINANCE_REPRODUCIBILITY.md)

</details>

<details>
<summary><strong>clean72, Bilder und Angriffsentfernung: getrennte Folgetests</strong></summary>

**clean72:** 72 neue alltagsnahe deutsche Bürofragen ohne Manipulation. **61/72 · 84,7 %** richtig, alle Antworten schema-gültig. Mehrstufige Beitragsrechnungen erreichen **6/12**, die übrigen Bereiche 10–12/12. Andere Aufgaben und Schwierigkeiten bedeuten: Der Quotenunterschied zu früheren Tests belegt keinen kausalen Manipulationseffekt. [Ergebnisse und Reproduktion](experiments/clean72/README.md)

**Bildtest:** 30 synthetische Diagramme und 20 deutsche synthetische Belege aus HuggingFace-Daten, ergänzt um gepaarte Englisch- und Weißbildkontrollen. Insgesamt **90 echte Vision-Läufe**:

| Aufgabe | Korrekte Quellenlabels |
|---|---:|
| Diagrammart | 27 / 30 |
| Legendenanzahl | 30 / 30 |
| Belegart | 20 / 20 |
| Ausdrücklicher Steuerhinweis | 19 / 20 |
| Bruttosummen-Intervall | 18 / 20 |

Die drei Diagrammart-Abweichungen haben überlappende Antwortbeschreibungen. Sie sind **keine drei eindeutig belegten Erkennungsfehler**; Gold und Resultate bleiben unverändert. Die Bildresultate sind ein eigener Bericht. Der Live-Playground bleibt textbasiert. Das Paket enthält keine Rohbilder oder vollständigen ursprünglichen Rechnungslabels; Beschaffung, Quellen und Lizenzen sind dokumentiert. Zwei gekennzeichnete Berichtsausschnitte sind mit Attribution enthalten. [Bericht und Grenzen](experiments/images/README.md) · [PDF](experiments/images/report/Clef_Bildbenchmark_2026-10-02.pdf)

**Angriffsentfernung:** Sieben nachträglich untersuchte Angriff-/Entfernungs-Paare aus den ursprünglichen Finance-Fällen. Mit Angriff **4/7**, nach Entfernung **5/7** richtig; zwei Entscheidungen ändern sich, nur ein Fehler wird behoben. Nur der angehängte Angriffstext wurde entfernt, Sachverhalt, Regeln und Gold bleiben gleich. [Alle Paare und Resultate](experiments/attack_ablation14/RESULTS.md)

Diese Folgetests werden weder miteinander noch mit den ursprünglichen 280 Textrequests gepoolt.

</details>

## Eigene Tests

Importiere **JSON, JSONL oder CSV**, prüfe die Vorschau und übernimm die Fälle ausdrücklich in „Eigene Tests“. Dort lassen sich Texte, Choice-Schemas und eigene Referenzlabels bearbeiten. Die Auswertung läuft sequentiell; „Nach diesem Fall stoppen“ lässt den aktuellen Request fertig werden. JSON und CSV werden nur auf ausdrücklichen Wunsch exportiert.

**Privat und getrennt:** Die UI liest importierte Dateien im Browser. Private Fälle bleiben im Speicher des Tabs und werden nicht automatisch veröffentlicht oder dauerhaft gespeichert. Erst eine ausdrücklich gestartete lokale Auswertung sendet `state` und `questions` an den Loopback-Server, **niemals `gold`**. Neuladen oder Schließen entfernt die nicht exportierten Tab-Daten; es beendet keine bereits laufende Modellberechnung.

Für Agenten und reproduzierbare eigene Läufe:

```bash
mkdir -p user_cases user_runs
cp examples/custom_cases/support.json user_cases/suite.json

# Eingaben validieren, ohne Netzwerk- oder Modellanfrage
python3 scripts/evaluate_custom.py --input user_cases/suite.json \
  --validate-only --output user_runs/validation.json

# Erst mit ausdrücklich aktiviertem, bereits laufendem lokalen Server
python3 scripts/evaluate_custom.py --input user_cases/suite.json \
  --output user_runs/evaluation.json
```

Die CLI startet oder lädt kein Modell. `user_cases/`, `user_runs/`, `.clef/` und `.venvs/` sind gitignored; das ist Schutz vor versehentlichem Commit, **keine Verschlüsselung**. Private Inputs, Vorhersagen und Berichte gehören nicht in öffentliche Benchmarks, Issues oder Commits.

Ohne unabhängige Referenzlabels gibt es Vorhersagen, aber **keine Genauigkeit**. Goldabdeckung, Antwortabdeckung, Feldgenauigkeit und vollständig richtige Fälle werden getrennt ausgewiesen. Offene oder fehlgeschlagene beschriftete Fälle bleiben im Nenner. Ein privater Lauf verändert keine veröffentlichten Scores.

[Import, Stop, Resume und Export](docs/CUSTOM_CASES.md) · [JSON-Schema](schemas/custom-suite-v1.schema.json) · [Synthetische Beispiele](examples/custom_cases/)

## Modell und Hardware

### Größe und Präzision getrennt wählen

| Modellwahl | Rolle | Gepinnter Download | Nachweis hier |
|---|---|---:|---|
| **`flash-9b`** | **Standard**, Cloudflare/Clef-Flash 9B | **19,08 GB** | Echte Linux-CPU-NF4-Läufe und aktueller HTTP-Smoke |
| `clef-27b` | Nur ausdrücklich mit `--model clef-27b` | **54,99 GB** | Vorbereitet; nicht heruntergeladen, geladen oder hardwarevalidiert |

Der Download ist pro Modell bei NF4 und nativer Präzision **gleich groß**. Die 4-Bit-Quantisierung entsteht erst beim Laden. „Voll/nativ“ bedeutet hier unquantisierte **16-Bit-Gewichte**, nicht FP32; ein anderes Präzisionsprofil macht aus 9B kein 27B-Modell.

| Profil | Verarbeitung | Status |
|---|---|---|
| **`cpu-nf4`** | 4-Bit-NF4-Backbone mit Double Quantization; originaler Head und Output-Embeddings BF16 | **Flash 9B auf Linux x86-64 / Python 3.12 tatsächlich ausgeführt** |
| `cpu-bf16` | Unquantisierte BF16-Gewichte auf CPU | Vorbereitet, kein vollständiger Hardwarelauf |
| `rocm-bf16` | Unquantisierte BF16-Gewichte auf AMD Radeon GPU | Vorbereitet, kein AMD-Hardwarelauf |
| `rocm-fp16` | Explizite FP16-Konvertierung auf AMD Radeon GPU | Vorbereitet, numerisch und auf Hardware unvalidiert |

**Alle 27B-Kombinationen sind unvalidiert.** Die AMD-Profile benötigen eine separate passende ROCm-PyTorch-Umgebung; die CPU-Installation genügt nicht. Sie verwenden die Radeon-GPU, nicht die Ryzen-AI-NPU. Andere Betriebssysteme und GPUs sind hier nicht validiert.

Beim gemessenen 9B-CPU-NF4-Pfad verlangt der Adapter mindestens **7,5 GiB aktuell verfügbaren RAM**; mindestens 8 GiB verfügbarer RAM werden empfohlen. Beobachteter Modell-/Prozessbedarf lag je nach dokumentiertem Lauf ungefähr bei **6–7,5 GB**, ohne daraus ein universelles Maximum abzuleiten. Zu den Gewichten kommen Umgebung, Cache und temporäre Dateien; eine frische CPU-9B-Installation benötigt laut Setup-Reserve ungefähr **29 GiB freien Plattenplatz**. Höhere Kapazitätsempfehlungen und 27B-Schätzungen stehen im Hardwareleitfaden. Ein bestandener Ressourcencheck garantiert keinen erfolgreichen Modelllauf.

[Hardware-, RAM-/VRAM- und Festplattenleitfaden](docs/HARDWARE.md) · [AMD, Linux Mint und Windows](docs/AMD_GPU.md) · [27B-Manifest und Herkunft](runtime/models/clef-27b/README.md)

### Lokale Inferenz einrichten

Für den gepinnten ML-Installer **Python 3.12** verwenden; der reine Ergebnisviewer unterstützt Python 3.12+. Plane zuerst, prüfe die Blocker und erlaube Installation, Download und Ausführung ausdrücklich:

```bash
python3 -m runtime.setup --plan --profile cpu-nf4
python3 -m runtime.setup --profile cpu-nf4 --execute --smoke
# Danach den ausgegebenen start_server_argv-Befehl unverändert ausführen
```

Ein reiner Plan installiert nichts. Der Server lädt nichts automatisch herunter und lädt das vorhandene Modell erst bei der ersten Live-Anfrage. Diese kann wegen SHA-256-Prüfung und Laden mehrere Minuten dauern. Echte Inferenz muss mit `--enable-inference` ausdrücklich freigegeben sein. Nur eine Modellanfrage läuft gleichzeitig; parallele Anfragen erhalten HTTP 409.

Für andere bewusste Entscheidungen zunächst nur planen:

```bash
# Dasselbe Flash-9B-Modell, unquantisiert; noch nicht hardwarevalidiert
python3 -m runtime.setup --plan --profile cpu-bf16

# Größeres 27B-Modell ausdrücklich wählen; alle 27B-Pfade unvalidiert
python3 -m runtime.setup --plan --model clef-27b --profile cpu-nf4
```

**Nachweisgrenze:** Der neue Installer-Lebenszyklus ist mit simulierten Schritten getestet; eine frische Installation wurde hier nicht ausgeführt. Der [aktuelle HTTP-/Eigentest-Smoke](qa/setup_custom_smoke.json) lief dagegen wirklich mit der vorhandenen, hashgeprüften Flash-9B-/CPU-NF4-Umgebung: **ein Request, drei Felder, 335 Tokens, 20,23 s reiner Forward, keine Kürzung**. Das ist ein Integrationsnachweis, kein Benchmark und keine allgemeine Latenzzusage. Laden, Verifikation und gesamter HTTP-Aufruf werden im Nachweis separat ausgewiesen. [Prozessabschluss](qa/setup_custom_smoke_completion.json)

Historische Skripte wie `runtime/setup_runtime.sh` bleiben zur Reproduktion alter Läufe erhalten. Neue Installationen folgen dem [aktuellen Setup-Vertrag](docs/AGENT_SETUP.md).

<details>
<summary><strong>Exakte Konfiguration der dokumentierten Flash-9B-Läufe</strong></summary>

- Offizielles Modell: [`Cloudflare/clef-flash`](https://huggingface.co/Cloudflare/clef-flash)
- Revision: `17f0b0ad64efb65d273590632833508766b2aae6`
- **Originaler Joint-Schema-Head**, keine Chat-Generierung als Ersatz
- CPU-NF4-Backbone mit Double Quantization; Head und Output-Embeddings BF16
- Torch 2.11.0+cpu, Torchvision 0.26.0+cpu, Transformers 5.10.2, bitsandbytes 0.50.2
- [Vollständige Paketpins](runtime/requirements_frozen.txt) und [Modell-SHA-256-Manifest](runtime/model_file_manifest.json)
- 6 CPU-Threads, Batchgröße 1, maximal 2.048 Tokens, keine stille Kürzung

Diese experimentelle CPU-Quantisierung ist nicht die BF16-/GPU-Herstellerkonfiguration. Die Qualität und Zeiten gelten für die jeweilige dokumentierte Konfiguration. Hier wird keine eigene GPU-Leistung oder 27B-Genauigkeit behauptet.

</details>

## Architektur

Zwei bewusst getrennte Wege führen in dieselbe Oberfläche:

```text
Eingefrorene Suiten + Originalantworten
           │
           └── Hash-/Score-Gates → web/data/ → Ergebnis-Workbench

Eigene Texte + Choice-Schema
           │
           └── explizite lokale Auswertung → server.py → nativer Clef-Head
                                                        │
                                                        └── Auswahl + Wahrscheinlichkeiten
```

Goldlabels dienen der Auswertung und gehen **nicht** in den Modellrequest. Es gibt keine generative Chat-Schicht, die Entscheidungen oder Erklärungen ersetzt. Für Versicherungsfälle entspricht die deterministische Textdarstellung exakt dem gepinnten Modell-Renderer.

| Pfad | Aufgabe |
|---|---|
| `web/` | Buildfreie Oberfläche ohne npm-Laufzeitabhängigkeiten |
| `server.py` | Loopback-Server, Requestvalidierung und Opt-in-Live-API |
| `runtime/` | Gepinnte Modellassets, Original-Head, Profile, Setup und Lazy-Live-Adapter |
| `benchmark/`, `finance_benchmark/` | Getrennte eingefrorene Original-Textsuiten |
| `results/` | Archivierte Originalresultate; Finance unter `results/finance/` |
| `experiments/` | Separate Bank-, Versicherungs-, clean72-, Bild- und Ablationstests |
| `qa/`, `provenance/` | Unabhängige Gegenprüfungen und Herkunftsnachweise |
| `scripts/`, `tests/` | Import-Gates, Integritätsprüfungen und Regressionstests |
| `docs/`, `licenses/` | Einrichtung, Methodik, Validierung und Upstream-Lizenz |

Modelle, virtuelle Umgebungen, Caches, Schlüssel und private Pfade gehören nicht ins Repository.

## Prüfung und Reproduktion

Der dokumentierte lokale Integrationsstand umfasst **254 bestandene Python-Tests**, **99 bestandene JavaScript-/DOM-Tests** und **drei bestandene Integritätsgates**. Alle fünf UI-Datensätze wurden byte-identisch rekonstruiert. Diese modellfreien Prüfungen sind von echter Inferenz und visueller Browserprüfung getrennt. [Aktueller UI-Prüfnachweis](qa/ui_polish_review.json) · [Validierungsverlauf](docs/VALIDATION.md)

Die folgenden Befehle laden kein Modell und führen keine Inferenz aus:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/test_web.mjs

# Vollständige UI-DOM-Regressionen, ohne Browser oder Modell
npm ci --ignore-scripts --no-audit --no-fund
npm test

# Drei getrennte Integritätsgates
python3 scripts/check_project.py
python3 scripts/check_followups.py
python3 scripts/check_bank_support.py

# Alle fünf Ergebnisdatensätze rekonstruieren
python3 scripts/build_web_data.py --suite general
python3 scripts/build_web_data.py --suite finance
python3 scripts/build_clean_web_data.py
python3 scripts/build_insurance_web_data.py
python3 scripts/build_bank_web_data.py

# Nur im sauberen Export ohne node_modules/ oder lokale Caches
python3 scripts/audit_public.py
```

**Node 22+** wird nur für JavaScript-Tests benötigt; getestet wurde mit Node 24.19.0. Die DOM-Tests verwenden LinkeDOM 0.18.13 aus der Lockdatei. `node --test tests/test_web.mjs` bleibt ohne npm-Installation ausführbar.

Die gleichen modellfreien Checks laufen in [GitHub Actions](https://github.com/storminator89/clef-benchmark/actions/workflows/check.yml). [CI-Umfang und Action-Pins](docs/CI.md). Ein lokaler Testpass ersetzt keinen bestandenen CI-Lauf für einen später veröffentlichten Commit.

Die Importe verweigern unvollständige Läufe, fehlende IDs, geänderte Freeze-Dateien und unpassende unabhängige Gegenprüfungen. `scripts/build_web_data.py --cases-only` erzeugt ausdrücklich ergebnisfreie Entwicklungsdaten, niemals partielle Scores. Eigene Reproduktionen gehören in **neue Dateien**, niemals über archivierte Originalresultate. Nach erfolgreicher Modelleinrichtung: `bash runtime/reproduce.sh`.

### Browserprüfung und echte Screenshots

Der vorbereitete [Browser-Gallery-Workflow](.github/workflows/browser-gallery.yml) verwendet **Playwright 1.62.0** und den normal installierten stabilen Google-Chrome-Kanal mit aktiviertem Chromium-Sandboxing auf einem gewöhnlichen `ubuntu-24.04`-Runner. Er prüft Desktop, Hell/Dunkel sowie 320-/390-Pixel-Ansichten mit öffentlichen synthetischen Fällen. Der Lauf verbietet Modellinferenz, nutzt keine Secrets und begrenzt das Artefakt auf **10 MiB mit einem Tag Aufbewahrung**, ohne Trace oder Video.

**Browserstatus: noch kein erfolgreicher Capture nachgewiesen.** Der erste CI-Versuch mit dem heruntergeladenen Chromium-Headless-Shell stoppte vor dem ersten Bild an `No usable sandbox`. Der vorhandene normale Chrome-Kanal startete mit bestehendem AppArmor-Profil und aktivierter Sandbox erfolgreich. Die echte Prüfung fand anschließend einen 320-Pixel-Überlauf am privaten Dateiformat-Select; die Korrektur wird erneut geprüft. Es gab keine Sicherheitsänderung oder Sandbox-Abschaltung. Auch in der Erstellungssandbox war der Browserstart blockiert. Unit-/DOM-Tests sind kein Ersatz für CSS-Layout, tatsächliches Clipping oder sichtbare Fokuszustände. Erst ein vollständig bestandener Lauf mit überprüften Quell-/Bildhashes und anschließend geöffneten, visuell geprüften PNGs darf als Galerie ergänzt werden. Smartphone-Viewports ersetzen keinen Test auf physischen Geräten oder ein Screenreader-Audit.

[Ausführen, prüfen und veröffentlichen](docs/BROWSER_GALLERY.md) · [Prüfgrenzen](docs/VALIDATION.md)

## Datenschutz und Grenzen

### Lokale Verarbeitung

- Server ausschließlich an **`127.0.0.1`**, Host-/Origin-Prüfung, kein CORS und keine öffentliche Modell-API
- Kein URL-Proxy, kein serverseitiger Datei-Upload, keine API-Keys; JSON-/JSONL-/CSV-Dateien werden im Browser gelesen
- Keine externen Skripte, Fonts, Analytics oder CDN-Abhängigkeiten in der Workbench
- Neue Eingaben werden für die angeforderte Berechnung im RAM verarbeitet und vom Server weder in Dateien noch in Zugriffslogs geschrieben
- Import und Export sind ausdrücklich; eigene Fälle und Läufe werden niemals automatisch veröffentlicht

### Bewusst begrenzter Umfang

- **Nur Text im Live-Playground:** kein PDF-/OCR-/Bildimport, keine Live-Bildinferenz
- Maximal **32 KiB Request**, **6.000 Eingabezeichen**, **2.048 Tokens**, **1–8 `choice`-Fragen** mit jeweils **2–12 Klassen**; keine stille Kürzung
- Richtlinie maximal 4.000 Zeichen, Klassenbeschreibung maximal 300 Zeichen; Klassennamen beginnen mit einem Buchstaben, danach Buchstaben/Ziffern/`_`/`-`, maximal 64 Zeichen
- Modellwahrscheinlichkeiten sind keine kalibrierten Zuverlässigkeits- oder Sicherheitsgarantien
- Synthetische, teils korrelierte und KI-geprüfte Fälle ersetzen keine unabhängige menschliche Fachprüfung oder repräsentative Evaluation
- Keine Gesundheits-, Finanz-, Rechts- oder Kundenentscheidungen aus diesen Demos ableiten; **keine echten Gesundheits-, Finanz- oder Kundendaten für diese Demo verwenden**
- Kein Mehrbenutzer- oder Produktionsdienst; kein Reverse-Proxy oder Port-Forwarding ohne eigene Authentifizierung und Sicherheitsprüfung

[Exakter Live-API-Vertrag](docs/LIVE_API.md) · [Private Tests und Datenhaltung](docs/CUSTOM_CASES.md)

## Roadmap: die nächsten Nachweise

Die sinnvolle Richtung ist mehr belastbare Evidenz. Diese Punkte sind **offene Validierungsziele, keine zugesagten Features oder Termine**:

- [ ] Echte Desktop-/Mobile-Browserprüfung und eine ausschließlich daraus erzeugte, visuell geprüfte Galerie
- [ ] Frische Installation mit dem neuen Setup auf einem dokumentierten Zielrechner vollständig ausführen
- [ ] CPU-BF16, AMD-ROCm und 27B jeweils gesondert auf Hardware validieren; Qualität, Speicherbedarf und Zeiten getrennt messen
- [ ] Größere, repräsentativere und menschlich fachgeprüfte Tests für die jeweilige Anwendung schaffen
- [ ] Modellvergleiche nur mit identischen Aufgaben, Schemas, Nennern und offengelegten Laufbedingungen ausweisen

## Lizenz und Attribution

Eigener Code und synthetische Daten: **Apache-2.0**, siehe [LICENSE](LICENSE). Unveränderter Cloudflare-Code und Modell haben eigene Upstream-Attribution in [NOTICE](NOTICE) und [licenses/](licenses/). Modellgewichte werden nicht mitgeliefert.

**Unabhängiges Projekt, ohne Zugehörigkeit zu oder Bestätigung durch Cloudflare.**
