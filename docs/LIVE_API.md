# Lokale Live-API: mehrere Choice-Felder

Die opt-in API `POST /api/infer` verarbeitet **1 bis 8 native `choice`-Fragen gemeinsam** in einem Textrequest. Damit können beispielsweise `decision` und `evidence` getrennte Antworten und Wahrscheinlichkeiten erhalten. Eine zusätzliche Frage erzeugt keine weitere Chat-Generierung. Gespeicherte Benchmark-Ergebnisse und neue Live-Ergebnisse bleiben getrennt.

## Grenzen

| Bestandteil | Grenze |
| --- | --- |
| Gesamter HTTP-Body | 1–32.768 Bytes einschließlich JSON-Syntax und UTF-8-Kodierung |
| Top-Level-Felder | Genau `state` und `questions`; Modellkennung wird serverseitig festgelegt |
| `state` | Nicht leerer Text, höchstens 6.000 Zeichen |
| `questions` | Objekt mit 1–8 verschiedenen Frage-IDs |
| Jede Frage | Genau `type`, `instructions`, `criteria`; `type` muss `choice` sein |
| `instructions` je Frage | Nicht leerer Text, höchstens 4.000 Zeichen |
| `criteria` je Frage | Objekt mit 2–12 verschiedenen Auswahl-IDs |
| Kriterienbeschreibung | Nicht leerer Text, höchstens 300 Zeichen |
| Frage-/Auswahl-ID | ASCII-Buchstabe am Anfang, danach ASCII-Buchstaben, Ziffern, `_` oder `-`; insgesamt 1–64 Zeichen |
| Tokenbudget | Gesamter modellkodierter Request höchstens 2.048 Tokens, einschließlich Text, aller Fragen, Kriterien und Systemvorlage |
| Parallelität | Eine laufende Modellanfrage; weitere Anfragen erhalten HTTP 409 |

Die Zeichengrenzen sind keine Zusage, dass ein Request in das Tokenbudget passt. Der Adapter kodiert zunächst den vollständigen Request und lehnt überlange Eingaben vor dem Modell-Forward mit HTTP 422 ab. Danach wird die begrenzte Kodierung mit der vollständigen verglichen. **Es wird nichts still gekürzt, und kein Feld wird weggelassen.**

Doppelte JSON-Schlüssel sind auf jeder Ebene verboten. Der Server lehnt sie ab, statt eine frühere Frage, Auswahl oder Eingabe durch den letzten Wert zu ersetzen. IDs dürfen in unterschiedlichen Fragen erneut verwendet werden; innerhalb eines Objekts müssen sie eindeutig sein.

## Beispielrequest

```json
{
  "state": "Synthetischer Vertrag: Hausrat ist versichert. Fundstelle: Abschnitt 2.",
  "questions": {
    "decision": {
      "type": "choice",
      "instructions": "Welcher Schutz ist ausdrücklich genannt?",
      "criteria": {
        "hausrat": "Hausratversicherung",
        "other": "Andere Versicherung"
      }
    },
    "evidence": {
      "type": "choice",
      "instructions": "Welche Fundstelle stützt die Antwort?",
      "criteria": {
        "section_1": "Abschnitt 1",
        "section_2": "Abschnitt 2",
        "absent": "Nicht angegeben"
      }
    }
  }
}
```

Header: `Content-Type: application/json` und `X-Clef-Request: 1`. Ein mitgesendeter `Origin` muss exakt `http://` plus dem erlaubten `Host` entsprechen. Der Server akzeptiert nur `127.0.0.1:<port>` oder `localhost:<port>` als Host und bindet ausschließlich an IPv4-Loopback. Cross-Origin-Requests werden nicht freigeschaltet.

## Vollständiger Antwortvertrag

Erfolgreiche Antworten enthalten `answers` und `probabilities_unrounded` als **Objekte nach Frage-ID**. Beide enthalten jede angeforderte Frage genau einmal und in der angeforderten Feldreihenfolge. Jede native Choice-Antwort enthält `type`, `choice`, `confidence` und `probabilities`. `choice` ist eine erlaubte ID. `probabilities_unrounded` enthält für jede Frage genau deren Kriterien und die ungerundeten Wahrscheinlichkeiten.

Der originale Vendor-Encoder sortiert Choice-IDs lexikographisch, während die Reihenfolge der Fragen erhalten bleibt. Die Zuordnung erfolgt immer über IDs; Clients dürfen weder Felder noch Optionen anhand einer zufälligen Objektposition zuordnen. Die gerundete native Antwort und die ungerundeten Wahrscheinlichkeiten können unterschiedliche Optionenreihenfolgen haben.

Vor dem Modell-Forward prüft der Adapter die vollständige und die begrenzte Kodierung auf exakte Frage-IDs, Frageanzahl und Choice-IDs. Nach dem Forward müssen Batchanzahl, Frageanzahl und jede Optionsanzahl exakt stimmen. Fehlende, zusätzliche, doppelte oder falsch zugeordnete Felder sowie ungültige Wahrscheinlichkeiten werden abgewiesen. Der Server prüft zusätzlich, dass das Runtime-Ergebnis alle angeforderten Antworten und Optionen enthält. Ein Fehler liefert **keinen Teilerfolg und keine Teilantworten**.

Zusätzlich bleiben unter anderem `source: "live_local_inference"`, `benchmark_result: false`, `truncated: false`, Tokenanzahl, Modellrevision, Laufzeit und Geräte-/Präzisionsmetadaten erhalten. Das sind Angaben eines neuen lokalen Laufs; sie ändern keine archivierten Scores.

## Strukturierte Dokumentdaten als Text

`state` bleibt auf der Live-HTTP-Schnittstelle ein String. Ein strukturierter Benchmark-Originalrequest wird unverändert archiviert. Für einen neuen Text-Livelauf kann dessen `state` separat in exakt die Textdarstellung des gepinnten Vendor-Renderers überführt werden:

```python
text_state = json.dumps(original_state, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
```

Bereits vorhandene Strings bleiben unverändert. Bei dieser kanonischen Projektion eines JSON-Objekts entsteht derselbe modellseitige Text wie beim ursprünglichen strukturierten `state`. Eine anders formatierte oder bearbeitete Projektion ist eine geänderte Eingabe. Der Client muss die Projektion und etwaige Bearbeitung sichtbar machen; die ursprüngliche strukturierte Quelle bleibt für Reproduktion und Replay erhalten. Diese Regel erlaubt keinen Medienzugriff. Der getrennte [private Testfallimport](CUSTOM_CASES.md) liest JSON/JSONL/CSV im Browser und sendet ausschließlich einzelne validierte Textrequests an diese API. Es gibt keinen serverseitigen Dateiupload.

## Sicherheit, Fehler und Hardwarestatus

- Nur Text; keine Top-Level-Medienfelder, vom Server geöffneten lokalen Dateien, serverseitigen Uploads, Remote-URLs zum Laden oder automatische Downloads. URLs innerhalb eines normalen Eingabetexts werden nicht abgerufen
- Host-/Origin-Prüfung, Pflichtheader, Content-Security-Policy, `nosniff` und `no-store` bleiben unverändert; keine CORS-Freigabe
- HTTP 400: ungültiges JSON, doppelte Schlüssel, unzulässiges Schema oder Zeichengrenzen; 413: leerer/zu großer Body; 415: falscher Content-Type oder fehlender Pflichtheader
- HTTP 403: fremder Host/Origin; 409: Modell bereits beschäftigt; 422: Tokenbudget überschritten oder sonstiger Adapter-Validierungsfehler
- HTTP 503: Inferenz deaktiviert oder gewünschtes Backend nicht verfügbar; 500: unvollständige/ungültige Modellantwort oder interner Fehler. Stacktraces erscheinen ausschließlich im Serverterminal
- `requested_profile` bestätigt nur die angeforderte Konfiguration. Eine nicht geladene Runtime meldet kein verifiziertes Gerät. Es gibt keinen stillen CPU-Fallback
- Standard bleibt CPU-NF4; `rocm-bf16` und `rocm-fp16` sind explizite experimentelle AMD-Profile. Modellfreie Tests bestätigen Kontrollfluss und Vertragsprüfungen, **keine erfolgreiche Ausführung auf AMD-Hardware**. Voraussetzungen: [AMD-Dokumentation](AMD_GPU.md)

## Modellfreie Prüfung

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_multifield_live.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_server.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_adapter.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_device_profiles.py' -v
```

Die Multi-Feld-Tests führen den echten Adapter- und HTTP-Code mit Testdoubles für Encoder und Modell aus. Sie prüfen unter anderem 1/2/8 Felder, fehlende und zusätzliche Antworten, Optionszuordnung, doppelte JSON-Schlüssel, Tokenlimit, fehlende Kürzung, Mediensperre und Sicherheit der HTTP-Schnittstelle. Es werden keine Modellgewichte, ML-Pakete oder Treiber geladen, heruntergeladen oder installiert; die Stub-Ausgaben sind keine Benchmark-Ergebnisse.

## Separater echter HTTP-Smoke

`scripts/smoke_multifield_http.py` kann genau **einen neuen realen CPU-NF4-Lauf über die lokale HTTP-Schnittstelle** ausführen. Der feste neue synthetische Fall betrifft eine fiktive Materialausgabe mit zwei Klauseln; er gehört zu keiner Versicherungssuite. Die Felder `decision` und `evidence` werden gemeinsam bewertet. Die vorher festgelegten Erwartungen (`nein`, `b1`) stehen ausschließlich außerhalb des Modellrequests.

Ohne `--run` validiert und zeigt das Skript nur den Request; es lädt kein Modell:

```bash
python3 scripts/smoke_multifield_http.py
```

Ein echter Lauf darf erst starten, wenn frühere Modellprozesse beendet sind und ausreichend RAM freigegeben ist. Die vorhandene gepinnte CPU-Umgebung und die bereits beschafften Gewichte werden verwendet. Es werden keine Dateien heruntergeladen und keine Pakete oder Treiber installiert. Die folgende Bestätigung ist nur nach tatsächlicher Prüfung zu setzen:

```bash
runtime/venv/bin/python scripts/smoke_multifield_http.py \
  --run --confirm-exclusive-runtime \
  --model-dir runtime/model \
  --output qa/live_multifield_smoke-new.json
```

Das Skript prüft freien RAM, startet den unveränderten Loopback-Server mit explizit aktivierter Inferenz und neuer Lazy-Runtime, ruft vor und nach genau einem `POST /api/infer` die Health-API ab und fährt den Server herunter. Erfolgsnachweise enthalten vollständigen Request und Modellantwort, jede Feld-/Optionsprüfung, Tokenanzahl, fehlende Kürzung, Hashes der beteiligten Quellen und Modellmanifest, Paketversionen, tatsächliches Gerät/Präzision sowie getrennte Prüf-, Lade-, Forward- und HTTP-Zeiten. Bestehende Nachweise werden nicht überschrieben. Modellpfad, Interpreterpfad, Hostname und private Rohlogs sind nicht Teil der öffentlichen Nachweisdatei.

Ein einzelner Smoke prüft Integration und diesen festen Fall; er belegt keine allgemeine Qualität, keinen Durchsatz und keine AMD-Ausführung. Sein Ergebnis wird niemals zu Benchmarkscores addiert. Das aufrufende Verfahren muss zusätzlich das tatsächliche Prozessende und die anschließende RAM-Freigabe prüfen.

### Verifizierter Lauf vom 2. Oktober 2026

Der separate neue HTTP-Smoke wurde nach dem Ende der Versicherungsinferenz von **09:48:46 bis 09:50:21 UTC** tatsächlich ausgeführt. Beide Felder entsprachen den vorher festgelegten Erwartungen: `decision = nein`, `evidence = b1`. Alle **21 Prüfungen** bestanden, einschließlich aller Optionen, vollständiger Antworten, HTTP-Sicherheitsheader und unveränderter Quelldateien.

- **442 Tokens**, keine Kürzung; genau eine erfolgreiche Inferenz
- Tatsächliches Gerät **CPU**, NF4-Backbone mit Double Quantization, BF16-Head und BF16-Output-Embeddings; 6 Threads, Batchgröße 1
- Modell-Forward **19,33 s**; kalter HTTP-Request **94,93 s** einschließlich **14,26 s** Dateiverifikation und **57,58 s** Modellladen
- Prozessende mit Exitcode **0** zusätzlich geprüft; anschließend kein Smoke-Prozess mehr aktiv und rund **7,9 GiB RAM** verfügbar
- Optionale optimierte CPU-/Fast-Path-Kernel waren nicht installiert; der bereits vorhandene Torch-Pfad führte den Lauf erfolgreich aus. Es wurde nichts nachinstalliert

[Sanitisierter vollständiger Laufnachweis](../qa/live_multifield_smoke.json) · [Separater Prozessende-/RAM-Nachweis](../qa/live_multifield_smoke_completion.json)

Dieser einzelne neue Fall ist ausdrücklich kein Versicherungsscore und keine allgemeine Qualitätsbewertung. Die experimentellen AMD-Profile wurden dabei nicht ausgeführt.

## Eigene Suiten und feste Modellidentität

Die [private Suite-Auswertung](CUSTOM_CASES.md) und `scripts/evaluate_custom.py` verwenden dieselbe API, strikt eine Anfrage nach der anderen. Erwartete Labels werden nie übertragen. Nur der Serverstart wählt das Modell (`--model flash-9b` als Standard, `--model clef-27b` ausdrücklich opt-in); ein Request kann es nicht umschalten.

Health und neue Antworten nennen `model_key`, `model_id`/`model` (offizielles Repository), die gepinnte `revision` und `requested_profile`. Vor dem Laden sind tatsächliches Gerät und Präzision weiterhin unbekannt. Erfolgreiche Antworten enthalten `runtime.profile`, tatsächliche `runtime.device` und `runtime.precision` sowie die unveränderten Timings. Batch-Berichte binden Suite und Modellidentität per Fingerprint und verweigern ein Resume mit anderem Modell, Pin oder Profil. Das ist Zuordnungsintegrität, keine unabhängige Zertifizierung eines Nutzerberichts.
