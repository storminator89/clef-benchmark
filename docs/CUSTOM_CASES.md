# Eigene Texttests: private UI und Agenten-CLI

Eigene Testfälle können **JSON, JSONL oder CSV** sein. Die Oberfläche „Eigene Tests“ hat eine eigene Vorschau, Fallliste, Text-/Schemaeditor, echte sequentielle Auswertung, Fortschritt, Stop und explizite Exporte. Die veröffentlichten Suiten und ihre unabhängig geprüften Scores bleiben separat.

**Nur Text, 1–8 native Choice-Fragen pro Fall.** Das ist kein PDF-/OCR-/Bildimport. Dateien, Links und URLs innerhalb eines Textes werden nicht geöffnet. Es gibt keinen ZIP-Import, URL-Proxy, externen Modellanbieter oder automatischen Upload deiner Dateien.

## Schnell in der UI

1. `python server.py` starten und `http://127.0.0.1:8765/#custom` öffnen
2. Eigene Datei wählen oder das synthetische Beispiel ansehen. „Datei prüfen“ validiert **alle** Fälle, ohne eine Modellanfrage auszulösen
3. Vorschau prüfen und „Private Suite übernehmen“ wählen. Die Übernahme ersetzt eine bisherige private Suite; bei Bedarf vorher exportieren
4. Einzelne Fälle ansehen, optional Text, Fragen und eigene Goldlabels bearbeiten. Eine Bearbeitung entfernt sofort alle bisherigen Ergebnisse der Suite. Ungültige Bearbeitungen können nicht ausgeführt werden
5. Für echte Antworten den lokalen Server ausdrücklich mit Inferenz aktivieren. „Suite lokal auswerten“ schickt eine Anfrage nach der anderen, jeweils **nur `state` und `questions`**, niemals `gold`
6. Testfälle, den vollständigen JSON-Laufbericht oder flache CSV-Ergebnisse ausdrücklich herunterladen

Importierte Daten bleiben im Arbeitsspeicher dieses Tabs. Kein `localStorage`, keine Datenbank und kein automatisches Speichern. Neuladen/Schließen entfernt sie. Der Server verarbeitet einzelne angeforderte Texte im RAM und schreibt sie nicht als Kundendateien. Zum Aufbewahren muss der Nutzer exportieren. Auf geteilten Rechnern können heruntergeladene Dateien für andere zugänglich sein; sensible echte Kundendaten sind für diese Demo nicht empfohlen.

Das Servermodell ist fest gewählt. Die UI behauptet keinen Modellwechsel durch einen Dropdown. Standard ist **Clef Flash 9B mit CPU-NF4**; Clef 27B ist eine getrennte, explizit konfigurierte Option mit deutlich höheren Anforderungen. Modell, feste Revision, Profil, tatsächliches Gerät, Präzision und Laufzeiten stehen im Bericht. Ein Lauf darf nach einem Modell-/Revisions-/Profilwechsel nicht fortgesetzt werden.

## Kanonisches JSON

[Schema v1](../schemas/custom-suite-v1.schema.json) · [vollständiges synthetisches Beispiel](../examples/custom_cases/support.json)

```json
{
  "schema_version": 1,
  "name": "Meine synthetischen Fälle",
  "cases": [
    {
      "id": "fall_001",
      "state": "Ich habe mein Passwort vergessen.",
      "questions": {
        "intent": {
          "type": "choice",
          "instructions": "Welches Anliegen wird ausdrücklich beschrieben?",
          "criteria": {
            "zugang": "Anmeldung oder Passwort",
            "anderes": "Ein anderes Anliegen"
          }
        }
      },
      "gold": { "intent": "zugang" }
    }
  ]
}
```

- `id` ist eine **selbst vergebene, stabile, eindeutige** ASCII-ID mit 1–64 Zeichen: erstes Zeichen Buchstabe/Ziffer, danach zusätzlich `_` oder `-`. Keine Pfade, Dateinamen oder automatisch geratenen IDs
- `state` bleibt byteinhaltlich als Unicode-Text erhalten, einschließlich Leerzeichen und Zeilenumbrüchen. Es wird nicht getrimmt, umgeschrieben oder still gekürzt
- `questions` ist das native Choice-Schema. Die Reihenfolge der Fragen bleibt erhalten, weil der Modellencoder sie verwendet. Auswahl-IDs ordnet der Vendor-Encoder selbst
- `gold` ist optional. Fehlende Fragen bleiben unbeschriftet; `{}` ist zulässig. Vorhandene Werte müssen exakt eine erlaubte Options-ID der betreffenden Frage sein. `null`, leere oder unbekannte Labels sind keine Sollantwort
- Andere Root-/Fallfelder, gespeicherte Vorhersagen, Prüfsiegel und Vertrauensmarkierungen werden beim Testfallimport abgewiesen. Der Import stellt niemals eine unabhängige Prüfung dar

Goldlabels kommen ausschließlich vom Nutzer. Clef erzeugt keine Goldlabels, und eine Modellantwort wird nie nachträglich als Sollantwort eingesetzt.

## JSONL

[JSONL-Beispiel](../examples/custom_cases/support.jsonl)

Jede Zeile ist ein vollständiges Fallobjekt mit `id`, `state`, `questions`, optional `gold`. Kein Suite-Wrapper. Der Dateiname ohne Endung wird der Suitename. Zeilenumbrüche **im JSON-String** müssen als `\n` escaped sein. Ein abschließender Dateizeilenumbruch ist erlaubt; leere Zwischenzeilen sind Fehler. Doppelte IDs werden über die gesamte Datei geprüft.

## Einfaches CSV ohne JSON pro Zeile

[CSV-Beispiel](../examples/custom_cases/support.csv) · [zugehörige Fragenspezifikation](../examples/custom_cases/support-spec.json) · [Spezifikationsschema](../schemas/custom-csv-spec-v1.schema.json)

```csv
id,state,gold.intent,gold.priority
fall_001,"Passwort vergessen",zugang,normal
fall_002,"Meine Karte wurde gestohlen, bitte sperren",karte,
fall_003,"Wann ist die nächste Sprechstunde?",,
```

Pflichtspalten sind `id` und `state`. Optionale Spalten heißen `gold.FRAGE`, zum Beispiel `gold.intent`. Ein leeres Goldfeld bedeutet **unbeschriftet**, nicht falsch und nicht „unbekannt“ als Modellklasse. Unbekannte oder doppelte Spalten werden abgewiesen; es wird nichts ignoriert.

Alle CSV-Zeilen verwenden ein gemeinsames Fragenschema:

- UI-Preset **Support**: `intent` mit `zugang/karte/sonstiges`; `priority` mit `normal/dringend`
- UI-Preset **Aussage**: `decision` mit `ja/nein/offen`; Eingabetext muss Dokument und zu prüfende Aussage enthalten
- Eigene Spezifikationsdatei: genau `{"schema_version":1,"questions":{...}}`. In der UI „Eigene Spezifikationsdatei“ wählen; CLI `--spec DATEI` verwenden

UTF-8 mit/ohne BOM, Kommas, CRLF/LF/CR, korrekt gequotete Kommas, `""` für ein Anführungszeichen und mehrzeilige gequotete Zellen werden unterstützt. Semikolon-Dateien müssen als Komma-CSV exportiert werden. Werte werden nicht still getrimmt. Fehler nennen Fall/Zeile oder CSV-Datensatznummer. Der Import bleibt atomar: entweder sämtliche Fälle sind gültig, oder keine neue Suite wird übernommen.

## Agenten und Batch-Auswertung

Die CLI verwendet nur die Python-Standardbibliothek. Sie startet **kein** Modell, installiert nichts und lädt keine Gewichte herunter. Sie nutzt einen bereits ausdrücklich aktivierten lokalen Server. Betriebssystem-Python genügt für Import, Validierung und HTTP; das Server-Python muss zur eingerichteten Modellumgebung gehören.

Private Dateien gehören nach `user_cases/`, Resultate nach `user_runs/`. Beide Verzeichnisse sind gitignored. Nie tatsächliche Nutzer-/Kundenfälle, Exporte oder Zugangsdaten in Git, Dokumentation, Issues oder öffentliche Benchmark-Ordner übernehmen. Die versionierten Beispiele sind ausschließlich synthetisch.

```bash
mkdir -p user_cases user_runs
cp examples/custom_cases/support.json user_cases/meine-tests.json

# Alle Eingaben prüfen; keine Modell- oder Netzwerkanfrage.
python scripts/evaluate_custom.py \
  --input user_cases/meine-tests.json --validate-only \
  --output user_runs/validierung.json

# Bereits eingerichteten lokalen Server in einem anderen Terminal starten.
# Standard bleibt Flash 9B / CPU-NF4. Den tatsächlichen Setup-Python verwenden.
runtime/venv/bin/python server.py --enable-inference --model-dir runtime/model

# Echte sequentielle Inferenz; Gold wird NICHT übertragen.
python scripts/evaluate_custom.py \
  --input user_cases/meine-tests.json \
  --output user_runs/lauf-001.json \
  --csv-output user_runs/lauf-001.csv

# CSV mit gemeinsamer Fragenspezifikation.
python scripts/evaluate_custom.py \
  --input examples/custom_cases/support.csv \
  --spec examples/custom_cases/support-spec.json \
  --validate-only --output user_runs/csv-validierung.json
```

`--format auto|json|jsonl|csv` kann die Erkennung über die Dateiendung überschreiben. Der Standardendpunkt ist `http://127.0.0.1:8765`; `--endpoint` akzeptiert ausschließlich HTTP-Loopback (`127.0.0.1`, `localhost`, `[::1]`). Der derzeitige Server bindet IPv4-Loopback. Keine Redirects, Proxy-Umgebungsvariablen, entfernten Hosts, Zugangsdaten oder frei eingebbaren API-Pfade.

Exitcodes: `0` = validiert oder ohne Laufzeitfehler beendet, `1` = blockiert oder mindestens ein Fallfehler, `2` = ungültige Eingaben/Ausgabekonfiguration, `130` = unterbrochen. Ein fachlich falsches, aber gültiges Modelllabel ist kein Prozessfehler; dafür den Score prüfen.

Die CLI schreibt vor dem ersten Request und nach jedem abgeschlossenen Versuch einen atomar ersetzten Bericht. Unter POSIX werden Dateien mit Modus `0600`, das neue Zielverzeichnis mit `0700` angelegt; bestehende Verzeichnisberechtigungen und das Windows-ACL-Modell ändern sich nicht. Existierende neue Ausgabedateien werden ohne explizites Resume nicht überschrieben. Standardausgabe: `user_runs/<Dateiname>.report.json`; explizite Pfade müssen ebenfalls privat gewählt werden.

### Stop und sichere Fortsetzung

In der UI hält „Nach diesem Fall stoppen“ die nächste Anfrage an. Der aktuelle Request darf fertig werden. Kein falsches „abgebrochen“: Browser schließen beendet die serverseitige Modellberechnung nicht. Im selben unveränderten Tab lassen sich die verbleibenden Fälle fortsetzen. JSON-Teilexport ist während des Laufs möglich und ist sichtbar als Teillauf gekennzeichnet. Ein gerade laufender Request wird im exportierten Snapshot als `error` mit `kind: in_flight` und ungewissem Ausgang markiert; so kann ein späteres CLI-Resume ihn nicht unbemerkt erneut senden. Im weiterlaufenden Browser darf die echte Antwort regulär ankommen.

CLI `Ctrl-C`/SIGTERM setzt ebenfalls einen Stop-Wunsch; eine laufende Anfrage darf enden. Der Bericht enthält bisherige Antworten, Fehler und offene Fälle. Nur offene Fälle werden fortgesetzt:

```bash
python scripts/evaluate_custom.py \
  --input user_cases/meine-tests.json \
  --resume user_runs/lauf-001.json \
  --output user_runs/lauf-001.json
```

Resume validiert das vollständige eingebettete Suite-Schema, eindeutige IDs, native Antworten und die Zuordnung jedes Ergebnisses. Gespeicherte Summen werden neu berechnet. Erfolg oder Fehler werden nicht automatisch wiederholt; ein neuer vollständiger Lauf braucht einen neuen Outputpfad. Vor jedem CLI-POST wird ebenfalls ein `in_flight`-Checkpoint geschrieben; auch nach einem abrupten Prozessende gilt dieser Fall als unsicherer Versuch statt als ungesendeter Fall. Eine bereits fehlgeschlagene Anfrage kann serverseitig noch laufen, wenn die Verbindung verloren ging: vor einem Neustart Backendzustand prüfen.

Der Suite-SHA-256 entsteht aus kanonischem UTF-8-JSON (rekursiv sortierte Objektkeys, kompakt, Unicode unverändert) des Objekts `{"suite":SUITE,"question_order":[[FRAGE_IDS_PRO_FALL],...]}`. Dadurch wird auch eine native Frage-Umordnung erkannt. `model_identity_sha256` bindet zusätzlich `suite_sha256` und die Modellidentität `model_key/model_id/model/revision/requested_profile`. Ein anderer Text, Goldwert, Fallauftrag, Modell, Pin oder Profil ist kein gültiges Resume. Die tatsächlichen Geräte-/Präzisionsmetadaten und Timings bleiben je Antwort erhalten.

**Ein Fingerprint ist keine Signatur.** Ein geladener Resume-Bericht ist vom Nutzer bereitgestellt, nicht unabhängig überprüft. Es gibt keinen Vertrauensbadge und keine Übernahme in veröffentlichte Scores. Die UI importiert nur Testfall-Dateien; für einen auf Platte gespeicherten Teillauf dient die CLI.

## Was wird bewertet?

- **Goldabdeckung:** beschriftete Felder / alle angefragten Felder
- **Feldgenauigkeit:** richtige beschriftete Felder / alle beschrifteten Felder. Fehlgeschlagene oder noch offene beschriftete Felder bleiben im Nenner und sind nicht richtig
- **Feld-Antwortabdeckung:** gültig beantwortete beschriftete Felder / alle beschrifteten Felder
- **Vollständige Fallgenauigkeit:** in sämtlichen Feldern richtige Fälle / alle vollständig beschrifteten Fälle. Teilbeschriftete Fälle gehören nicht in diesen Nenner
- **Fall-Antwortabdeckung:** gültig beantwortete vollständig beschriftete Fälle / alle vollständig beschrifteten Fälle
- **Ausführungsabschluss:** (Erfolge + Fehler) / geplante Fälle; **Antwortabdeckung:** Erfolge / geplante Fälle
- Ohne Gold gibt es Modellantworten und Laufmetadaten, aber keine Genauigkeit (`null` im JSON). Teilstände heißen ausdrücklich vorläufig. Eine beendete Suite mit Fehlern bleibt eine Suite mit Fehlern

Frage-IDs gruppieren die Feldstatistik. Verwende dieselbe ID nicht für semantisch unterschiedliche Aufgaben, wenn du diesen aggregierten Wert interpretierst. Modellwahrscheinlichkeiten sind keine kalibrierte Garantie.

## Bericht, CSV und Grenzen

JSON enthält vollständige unveränderte Eingaben, vom Nutzer gesetztes Gold, originale Modellantworten, Fehler und alle Metadaten. Die Ergebnisse stehen pro Fall auf `pending`, `success` oder `error`. Laufstatus: `validated`, `running`, `completed`, `interrupted` oder `blocked`. `benchmark_result` bleibt `false`. `result_provenance` ist bei einem neuen Lauf `local_execution`; ein von Platte fortgesetzter Lauf wird ausdrücklich als `user_supplied_resume_plus_local_execution` markiert. Kein Wert bedeutet unabhängige Verifizierung.

CSV liefert eine Zeile je Fall/Frage: `id,field,status,gold,prediction,correct,forward_ms,elapsed_seconds,device,precision,model,revision,requested_profile,error`. Formeln aus untrusted Text (`=`, `+`, `-`, `@`, führende Tab-/Zeilenumbrüche, auch nach Leerzeichen) werden mit einem führenden Apostroph entschärft. **JSON ist der verlustlose Export**; CSV ist eine tabellenfreundliche Ansicht und kann diese Schutzzeichen enthalten.

HTTP 400/413/422 sind transparente fallbezogene Fehler. 409, 5xx, Verbindungsfehler, ungültige oder unvollständige Antworten stoppen weitere Requests; der Bericht bleibt blockiert statt Fantasieantworten zu zeigen. Inferenz ist strikt sequentiell. Ein CPU-Lauf kann lange dauern; die erste Anfrage verifiziert und lädt das Modell.

Importgrenzen: 5 MiB UTF-8, 500 Fälle, 12 Verschachtelungsebenen. Frage-/Optionsgrenzen, 32 KiB HTTP-Request, 6.000 Textzeichen und 2.048 vollständige Modell-Tokens entsprechen der [Live-API](LIVE_API.md). Doppelte JSON-Schlüssel, reservierte Prototype-Schlüssel, falsche Goldwerte, nicht-endliche Zahlen und kaputtes Unicode werden abgewiesen. Kein `eval`, Pfadzugriff aus IDs, Prototype-Merging, HTML-Ausführung oder Abruf von importierten URLs.

## Modellfreie Tests und Nachweisgrenze

```bash
npm ci
npm test
python -m unittest discover -s tests -p 'test_custom_evaluator.py' -v
```

Unit-/DOM- und lokale HTTP-Vertragstests verwenden ausdrücklich synthetische Testdoubles; sie sind **keine Modellinferenz**. Zusätzlich wurde ein separat dokumentierter echter HTTP-Smoke mit einer synthetischen Drei-Feld-Anfrage ausgeführt: Flash9B/cpu-nf4, HTTP200, 335 Tokens ohne Kürzung, vollständige Wahrscheinlichkeiten und `benchmark_result=false`. [Nachweis](../qa/setup_custom_smoke.json) und [Prozessabschluss](../qa/setup_custom_smoke_completion.json) bleiben von allen Benchmarkstatistiken und früheren Modellnachweisen getrennt. Browser-Rendering/Screenshot-QA ist bis zum erfolgreichen CI-Capture und der Bildprüfung weiterhin offen. Die neue Installationsautomatik ist modellfrei getestet; volle Präzision, ROCm und 27B sind nicht hardwarevalidiert.
