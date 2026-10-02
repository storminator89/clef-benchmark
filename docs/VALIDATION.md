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
