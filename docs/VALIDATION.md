# Validierung des Web-Workbenches

## Ausgeführt

- Python 3.12: 20 Server-/Validierungstests und 5 Lazy-Adapter-/Integritätstests bestanden
- Node 24.19.0: 10 UI-Logik-/Datenintegritätstests bestanden
- Python: 9 Ergebnis-Import-Gates bestanden, darunter unvollständiger Lauf, falsche Modellrevision, Hashabweichung, veränderte Labels/Scores, doppelte IDs und manipulierte Aggregatgenauigkeit
- Separater echter Live-Adapter-Smoke bestanden: neue synthetische Anfrage, Dateiverifizierung, Modellladen, Originalkopf, 203 Tokens, keine Kürzung; Nachweis in `qa/live_adapter_smoke.json`
- Allgemeiner Benchmark: 180 finale Requests, unabhängig gegengeprüft
- Separater Finanz-/Maklerbenchmark: 100 finale Requests, unabhängig gegengeprüft
- Beide UI-JSON-Dateien aus finalen, hashgeprüften Rohantworten und Scoredateien erzeugt; keine vermischten Nenner
- UI-Datenimport verlangt vollständige Metadaten, passende SHA-256-Hashes, die vollständigen eindeutigen IDs pro Suite und erfolgreiche Gegenprüfung
- Keine Modellantworten werden für UI-Zwecke simuliert

Die HTTP-Tests prüfen Startseite, Sicherheitsheader, Host-/Origin-Schutz, CORS-Ablehnung, Verzeichnisausbruch, Dateizugriffsgrenzen, Requestlimits, ungültiges JSON, deaktivierte Inferenz und Serialisierung. Der Modellstub existiert ausschließlich in den Unit-Tests. Eine zusätzliche JS-Regression sichert die Editor-Zuordnung während laufender Inferenz: Navigation zu einem anderen Fall darf den aktiven Eingabetext nicht ersetzen; alte Antwort-IDs dürfen nicht als neue Anfrage erscheinen.

## Nicht visuell verifiziert

Chromium konnte in der Erstellungssandbox seinen Prozess-Socket nicht anlegen (`Operation not permitted`), auch mit regulär angefragter Ausführung außerhalb der Befehls-Sandbox. Der bereitgestellte Cloud-Browser blockierte die Loopback-Adresse (`ERR_BLOCKED_BY_CLIENT`). Diese Grenzen wurden nicht umgangen.

Deshalb wurden die Playwright-Desktop-/Mobile-Flows und Screenshots hier **nicht erfolgreich ausgeführt**. `tests/test_browser.py` enthält reproduzierbare Checks für einen gewöhnlichen Entwicklungsrechner: vier Views, Suche, Fehler-/Sprachfilter, Replay-Grenzen nach Eingabebearbeitung, Theme-Persistenz, Back/Forward und mobile Überlaufprüfung.

Responsives CSS und semantische Bedienelemente sind implementiert, aber ersetzen keine visuelle Prüfung.

## Nachintegration der Folgetests (2. Oktober 2026)

Der modellfreie Python-Testsatz umfasst jetzt 62 bestandene Tests, Node 13. Die neue clean72-Importprüfung verweigert unvollständige Läufe, falsche Modelle, fehlende oder fremde unabhängige Gegenprüfung, veränderte Goldlabels, manipulierte Scores und fehlende Vorhersagen. Die bestehenden AMD-, Server- und Adaptertests bleiben enthalten.

`check_followups.py` prüft den unveränderten ursprünglichen 280-Request-Stand, die öffentlich dokumentierten Exporthashes, alle drei abgeschlossenen Folgetests und exakt nachgerechnete Scores. Der Bildexport bleibt byte-identisch zum separat geprüften 57-Dateien-Paket. Der clean72-Dashboarddatensatz hat einen eigenen Nenner und keine erfundenen Sprachpaare.

Der optionale Browsertest wurde um clean72, elf Fehlerfälle und das Aus-/Einblenden des Sprachvergleichs beim Suite-Wechsel ergänzt. Er wurde hier wegen der bereits dokumentierten Browserblockade **nicht ausgeführt**. Für die neuen UI-Änderungen liegt damit ebenfalls keine visuelle Desktop-/Mobile-Abnahme vor. Die HTML-/Daten-/Logik- und lokalen HTTP-Prüfungen sind gesondert testbar und kein Ersatz dafür.

Die zusätzlich veröffentlichte unabhängige Standardbibliothek-Gegenrechnung lässt sich mit `python3 qa/verify_published_followup_metrics.py clean --project-root .` und entsprechend `ablation` ausführen. Sie importiert keinen eingefrorenen Scorer. Originale Start-/Konsolenprotokolle und die erneute Prüfung der Modellgewichte sind im öffentlichen Paket nicht verfügbar; diese Grenze wird im Ergebnis explizit markiert. Die finale ursprüngliche QA bescheinigt diese Prüfungen anhand des vollständigen Ursprungspakets. `qa/verify_original_completed_results.py` erhält den ursprünglichen Prüfumfang mit expliziten Wurzelpfaden und benötigt dafür dieses vollständige ursprüngliche Capture-Layout. Quell-/Exporthashes stehen in `provenance/independent_verifier_export.json`.

## Dokument-Workbench und Mehrfeld-API (2. Oktober 2026)

Die Oberfläche wurde als dokumentzentrierter Desktop-/Mobile-Workbench neu
aufgebaut. Der Live-Vertrag unterstützt 1–8 native Choice-Fragen, ohne den
32-KiB-Body-, 6.000-Zeichen- oder 2.048-Token-Schutz aufzuheben. Fehlende Fragen,
Optionen oder Antworten werden abgewiesen; es gibt keine stillen Teilergebnisse.

Modellfreie Prüfungen des Redesigns:

- **42 JavaScript-Tests bestanden:** bisherige Daten-/Logikprüfungen plus reale
  DOM-Interaktionen mit LinkeDOM 0.18.13. Enthalten sind Fall-/Klauselnavigation,
  Entscheidung versus Evidenz, leere Filter, alle bisherigen Suite-Nenner,
  unverändertes Mehrfeld-Replay, geänderte Eingaben und Fragenreihenfolge,
  Pending-Navigation, Doppelstarts, Serverfehler, unvollständige Antworten,
  History, Theme, XSS-Textescaping, Datenadmission und Fokusziele
- **119 Python-Tests bestanden:** Server-/Adapter-/AMD-Profil-, Importer-,
  Integritäts-, Mehrfeld-HTTP- und Smoke-Schutztests. Modellstub-Ausgaben bleiben
  ausschließlich in Tests; sie sind keine Benchmarkmessungen
- Licht-/Dunkel-Kontrastwerte der informativen Texttokens wurden rechnerisch
  gegen ihre vorgesehenen Oberflächen geprüft (mindestens 4,5:1)
- Responsives CSS und DOM-Bereichszustände für Smartphoneansichten geprüft;
  keine Behauptung einer pixelbasierten oder Screenreader-Abnahme
- Unabhängige Code-/UX-Prüfung: Datenadmission, XSS, Deep-Links, Kontrast,
  Fokuswiederherstellung, schmale Toolbar und Evidenzlayout geprüft; alle dabei
  gemeldeten materiellen Codebefunde behoben und nachgeprüft
- `check_project.py` und `check_followups.py` bestanden. Originale Benchmark-
  Dateien, Rohresultate, Vendor-Code und Gerätekonfiguration bleiben geschützt.
  Die drei absichtlich weiterentwickelten API-/Testdateien haben einen engen
  Vorher-/Nachher-Hashnachweis in `provenance/workbench_evolution.json`; der alte
  Baseline-Nachweis bleibt unverändert

`npm test` benötigt nur für die DOM-Regression eine Entwicklungsabhängigkeit.
Der Workbench selbst bleibt buildfrei und ohne npm-Laufzeitabhängigkeiten.
[Bedienung, Architektur und Zustandsinvarianten](UI_WORKBENCH.md).

### Weiterhin offen: tatsächliche Browserdarstellung

Die bereits dokumentierten Sicherheitsbeschränkungen wurden nicht erneut umgangen
oder über eine andere Adresse, einen Tunnel, Sicherheitsflags oder einen anderen
Executor umgangen. Deshalb gibt es für dieses Redesign **keine erfolgreiche echte
Desktop-/Mobile-Browserabnahme und keine echten Screenshots**. LinkeDOM ist keine
CSS-Layoutengine. Tatsächliches Clipping, Umbruch, visuelle Fokusringe und die
Darstellung bei 320 bzw. 390 Pixeln bleiben ungeprüft. `tests/test_browser.py`
enthält einen aktualisierten erlaubten Regressionsablauf für eine normale lokale
Entwicklungsumgebung; er sendet keine Modellanfrage.

### Tatsächlich ausgeführter neuer Mehrfeld-HTTP-Lauf

Nach dem vollständigen Ende des Versicherungsbenchmarks und Freigabe des RAM wurde
genau eine neue, vorab festgelegte synthetische Materialausgabe-Anfrage über
`POST /api/infer` ausgeführt. Ergebnis: `decision=nein` und `evidence=b1`, beide
vorab festgelegten Erwartungen getroffen. Alle 21 Vertrags-/Integritätsprüfungen
bestanden: 442 Tokens, keine Kürzung, beide nativen Felder und alle ungerundeten
Wahrscheinlichkeiten vorhanden, HTTP 200, echte CPU-NF4-Runtime bestätigt.

Forward: 19,33 s; kalter HTTP-Aufruf: 94,93 s einschließlich 14,26 s Dateiüberprüfung
und 57,58 s Modellladen. Der Prozess endete mit Exitcode 0 und gab seinen RAM frei.
Der Lauf ist **kein Bestandteil irgendeines Benchmarks** und keine Aussage über
allgemeine Qualität oder AMD-Hardware. Öffentlicher Nachweis:
[`qa/live_multifield_smoke.json`](../qa/live_multifield_smoke.json). Dieser
HTTP-Nachweis ersetzt weiterhin keine Browserdarstellungsprüfung.

### Endintegration des Versicherungsdatensatzes

Das separat freigegebene Paket mit 45 Dateien liegt byte-identisch unter
`experiments/insurance`. Alle 60 Requestzustände stimmen mit dem Vendor-Renderer
überein; 120 Felder mit 540 ungerundeten Wahrscheinlichkeiten stimmen exakt mit
den Rohoutputs überein. Der Standardimport rekonstruiert `web/data/insurance.json`
byte-identisch. Die drei früheren UI-Datensätze sind unverändert.

Ein zusätzlicher DOM-Test prüft die tatsächlich eingebundenen Überschriftenwerte
51/60 Entscheidung, 58/60 Evidenz und 50/60 vollständig richtig sowie die acht
Fälle mit richtiger Evidenz und falscher Entscheidung. Die Belegquote wird nicht
als Gesamtverständnisquote bezeichnet.

## Bank-Support-Endintegration

Die zusätzliche Suite ist vollständig freigegeben: 80 synthetische Fälle,
240 native Auswahlfelder, keine Kürzung. Alle eingefrorenen Eingaben/Quellen und bewerteten Ergebnisse unter
`experiments/bank-support` sind unverändert übernommen; nicht eingefrorene private
Wiederherstellungs-/Hostdiagnostik und redundante Betriebsprotokolle sind
ausdrücklich ausgelassen und im Exportmanifest dokumentiert; alle 34 eingefrorenen
Quellhashes, das vollständige Exportmanifest und die finalen unabhängigen
QA-Bindungen sind geprüft. Die UI bewahrt sämtliche Nachrichten, Feldregeln,
240 Vorhersagen und ungerundeten Wahrscheinlichkeitsvektoren exakt.

- 134 Python-Tests bestanden, darunter 15 Bank-Importer-Tests
- 53 JavaScript-/DOM-Tests bestanden
- Original-, Follow-up- und Bank-Integritätsgates bestanden
- Alle fünf UI-Datensätze byte-identisch rekonstruierbar
- Beide Bank-Scorer unabhängig erneut in temporären Kopien ausgeführt
- Alle 80 tatsächlichen Bank-Requests passen unverändert in bestehende UI-/API-Grenzen
- 212 vorbestehende Daten-/Laufzeitdateien unverändert

Die Ergebnisdarstellung unterscheidet 76/80 Anliegen, 77/80 Prioritäten,
75/80 nächste Schritte und 68/80 vollständig richtige Fälle. Insbesondere sind
8/10 vollständig richtige kritische Fälle von 0/10 kritischen Prioritäts- und
Handoff-Fehlern getrennt; die 80-%-Routine-Baseline wird ausdrücklich gezeigt.

Die Browser-Darstellungsgrenze bleibt bestehen. Für diese UI-Integration wurde
keine zusätzliche Modellinferenz gestartet und keine visuelle Abnahme behauptet.
Die eigentlichen 80 Bank-Messungen und ihre Laufprovenienz stehen im separaten
[Bankbericht](../experiments/bank-support/REPORT.md).

## Agenten-Setup und private Eigentests (2. Oktober 2026)

Der abschließende integrierte Stand besteht die **244 Python-Tests** und
**87 JavaScript-/DOM-Tests**, die Original-/Follow-up-/Bank-Integritätsgates und
die byte-identische Rekonstruktion aller fünf UI-Datensätze. Die bisherigen
Bank-Felder, Zulassungsprüfungen und Ergebnisnenner bleiben erhalten.

Die ursprüngliche `bank_support_baseline.json` ist unverändert. Von ihren
212 geschützten Dateien sind 209 weiterhin byte-identisch; ausschließlich
`runtime/check_backend.py`, `runtime/device_profiles.py` und
`runtime/live_adapter.py` haben eng begrenzte Vorher-/Nachher-Hashbindungen in
`provenance/bank_feature_evolution.json`. Keine historischen Eingaben,
Vorhersagen, Scorer, Modellmanifeste, Vendor-Implementierungen oder ursprünglichen
Runner werden ausgenommen. Die neun zum alten HTTP-Smoke gehörenden Quelldateien
sind separat archiviert; alte Smoke-Nachweise wurden nicht auf neue Quellen
umgeschrieben.

Private Dateien werden im Browser eingelesen; nur `state` und `questions` gehen
bei ausdrücklich gestarteter Inferenz an den lokalen Server. Goldlabels bleiben
außerhalb der Modellanfrage. Neue Regressionen prüfen unter anderem das Entfernen
privater Editor-/Vorschau-/Ergebnisinhalte auch aus dem ausgeblendeten DOM beim
Leeren und Verwerfen einer Vorschau. Der Public-Audit weist `user_cases/`,
`user_runs/`, `.clef/` und zusätzliche Umgebungs-/Modellverzeichnisse zurück.

### Ein echter aktueller HTTP-/Eigentest-Smoke

Mit vorhandenen, erneut hashgeprüften Flash-9B-Gewichten wurde genau eine neue,
kurze synthetische Drei-Feld-Anfrage durch den echten Custom-Evaluator und
`POST /api/infer` geschickt. HTTP 200, `state=ready`, Modellschlüssel `flash-9b`,
Modell `Cloudflare/clef-flash`, Revision
`17f0b0ad64efb65d273590632833508766b2aae6`, Profil `cpu-nf4`.
Alle erwarteten Feld-/Options-IDs und endlichen normalisierten Wahrscheinlichkeiten
sind vorhanden; 335 Tokens, keine Kürzung. Der Forward dauerte 20,23 Sekunden.
Der Prozess endete mit Exitcode 0 und die RAM-Freigabe wurde anschließend geprüft.

[Separater echter Nachweis](../qa/setup_custom_smoke.json) ·
[Prozessabschluss](../qa/setup_custom_smoke_completion.json) ·
[Integrationsübersicht](../qa/setup_custom_integration.json).
Dieser Lauf ist ausdrücklich **kein Benchmark-Ergebnis**, wird nirgends in
Benchmarkstatistiken aufgenommen und beweist keine allgemeine Qualität oder
Geschwindigkeit. Er nutzt denselben `ClefRuntime.infer`-Pfad wie `smoke_ready`,
ohne dafür ein zweites Modell zu laden.

Keine frische Installation und kein Download wurden durchgeführt. Der neue
Installer-Lebenszyklus bleibt mockgetestet; CPU-BF16, ROCm und 27B bleiben ohne
Hardwarevalidierung. Browserdarstellung, Desktop-/Mobile-Screenshots und
Screenreader-Abnahme wurden weiterhin nicht ausgeführt.


## Additional UI polish and genuine screenshot contract

The guided evaluation update keeps every frozen dataset, probability vector and
benchmark score unchanged. Model-free DOM regressions additionally cover the
five-suite catalogue, exact readiness stages, fail-closed malformed health,
newest-refresh-wins behavior, no premature private accuracy display, cancellable
replace/remove confirmation, dirty editor feedback, private search/status reset
and complete private DOM clearing. These tests do not render CSS.

The opt-in [browser gallery workflow](BROWSER_GALLERY.md) runs the actual app with
sandboxed Playwright Chromium on an already permitted host. It forbids all model
inference and off-origin requests, checks served source hashes, and generates
screenshots plus a README fragment only after every browser check passes. The
creation environment's earlier Chromium/loopback denial is respected. No real
browser pass or screenshot is claimed by this source-only update; a later capture
must carry its own commit/source hashes, browser diagnostics and visual review.
