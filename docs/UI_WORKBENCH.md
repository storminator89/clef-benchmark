# Dokument-Workbench

Die Oberfläche ist ein neuer dokumentzentrierter Arbeitsplatz. Sie benötigt nur
den lokalen Python-Server; weder ein Build-Schritt noch npm ist zum Starten nötig.
Es gibt keine externen Fonts, Skripte, Bilder, Trackingdienste oder Cloud-API.

## Ansichten

- **Workbench:** Fallbibliothek, Originaldokument und Antwortprüfung nebeneinander.
  Gold- und Modell-Evidenz sind getrennt markiert; alle Markierungen beziehen sich
  auf vollständige, tatsächlich angebotene Klauseln. Die Gold-Referenzbegründung
  ist eine Annotation, keine generierte Modellbegründung.
- **Bank-Kundensupport:** eigene Suite mit Kundennachricht und fiktiver
  Servicerichtlinie; Anliegen, Priorität und nächster Schritt als drei getrennte
  Antwortfelder. [Datengrenzen und Bedienung](BANK_SUPPORT_UI_DATA.md).
- **Ergebnisse:** Entscheidungen, Evidenzauswahl und vollständig richtige Fälle
  mit eigenen Nennern. Frühere Suiten behalten ihre Sprachkontrollen und Ergebnisse.
- **Live testen:** eigenständiger Text-/Schemaeditor, 1–8 native Choice-Felder und
  ausdrückliches lokales Backend-Opt-in. Jedes Feld wird vollständig angezeigt.
- **Eigene Tests:** eigener privater Import-/Editorbereich, ohne Vermischung mit
  veröffentlichten Studien. [Schema und CLI](CUSTOM_CASES.md).
- **Methodik:** Datengrundlage, Modellkonfiguration, Referenzannotation und Grenzen.

Ab 1081 Pixeln bleibt die Desktopansicht dreigeteilt. Zwischen 761 und 1080 Pixeln
steht die Prüfung unter dem Dokument; die Fallliste bleibt daneben. Bis 760 Pixel
wird bewusst zwischen **Fälle**, **Dokument** und **Prüfung** umgeschaltet. Die
Hauptnavigation liegt auf dem Smartphone unten. Die lokale Browserprüfung für
320 und 390 Pixel ist vorbereitet, aber hier nicht ausgeführt.

## Bedienung

- **Alle Tests entdecken** öffnet einen kompakten Katalog. Jede Karte zeigt die
  deutschen Hauptfälle und ob aufgezeichnete Ergebnisse vorliegen; Quoten werden
  nicht zu einem gemeinsamen Gesamtscore zusammengerechnet.

- Eine Fallkarte öffnet das zugehörige Dokument; auf dem Smartphone wechselt die
  Ansicht zum Dokument. Die Pfeile im Dokumentkopf öffnen den vorherigen/nächsten
  Fall innerhalb der aktuellen Filter.
- Die Prüffelder richten sich nach der Suite. **Entscheidung** und **Evidenz**
  gehören zur Versicherungsprüfung; Bank-Kundensupport verwendet **Anliegen**,
  **Priorität** und **Nächster Schritt**. Alle zeigen Gold,
  tatsächliche Modellwahl und alle Wahrscheinlichkeiten. Die Evidenzbuttons
  springen direkt zu den annotierten bzw. tatsächlich gewählten Klauseln.
- Kategorien-, Sprach-, Tag- und Ergebnisfilter lassen sich kombinieren. Es gibt
  eigene Filter für falsche Entscheidungen und falsche Evidenz. Eine leere Liste
  entfernt auch den vorherigen Dokument-/Ergebnisinhalt.
- `/` fokussiert die Suche, sofern der Fokus nicht in einem Eingabefeld steht.
  Pfeiltasten in der Fallliste wechseln zwischen Fällen. Neu gerenderte Ziele
  erhalten bewusst den Fokus; Farbzustände haben zusätzliche Textlabels.
- Deep-Links erhalten Suite, Fall und Feld, beispielsweise
  `#explorer?suite=insurance&case=fall_031&field=evidence`. Sprachkontrollfälle
  schalten auf ihren passenden Split um. Back/Forward bleiben nutzbar.
- Das Theme wird, sofern erlaubt, lokal gespeichert. Ohne verfügbaren Browser-
  Speicher funktioniert das Umschalten weiterhin für den offenen Tab.

## Eigene Tests und Modellstatus

Der private Ablauf hat vier Schritte: Datei prüfen, Fälle vorbereiten, lokal
berechnen, Bericht exportieren. Nach dem ausdrücklichen Übernehmen klappt der
Import zu, damit Fallliste und Editor im Mittelpunkt stehen. Er bleibt jederzeit
über seine Überschrift erreichbar. Eine neue Suite ersetzt die geladene erst nach
einer zweiten, sichtbaren Bestätigung. Entfernen hat dieselbe Schutzabfrage;
**Behalten** oder Escape bricht sie ab. Tatsächliches Entfernen leert auch die
Eingabefelder und abgeleiteten DOM-Inhalte, einschließlich versteckter Vorschau.

Eine Liste mit bis zu 500 Fällen lässt sich nach ID/Text durchsuchen und nach
Ausführungsfehlern, Goldabweichungen, fehlenden Goldlabels oder offenen Fällen
filtern. Pfeiltasten, Home und End navigieren in der privaten Fallliste. Eine
geänderte Eingabe erhält einen sichtbaren Hinweis und verwirft frühere Resultate
sofort; vor Start/Export müssen Änderungen validiert oder verworfen werden.

Vor einer Auswertung steht bei Qualitätsmetriken **—**, nicht eine vorgetäuschte
Nullmessung. Die Goldabdeckung bleibt sichtbar. Ein Teillauf nennt bearbeitete,
fehlgeschlagene und offene Fälle; Fehler bleiben im vorgesehenen Nenner. Antworten
vergleichen Modellwahl und Nutzer-Gold nebeneinander, mit den vollständigen
Optionswahrscheinlichkeiten. Goldfreie Felder erhalten keine Richtigkeitswertung.

Der lokale Status trennt **Server**, **Inferenzfreigabe** und **geladenes Modell**.
Ein erreichbarer Python-Server ist kein funktionsfähiges Modell. Die Aktualisierung
liest nur `/api/health`; ungültige/unerreichbare Statusantworten erlauben keine
neue Inferenz. Ein älterer paralleler Statuscheck kann einen neueren nicht
überschreiben. Das Modell wird weiterhin nur bei einer echten, ausdrücklich
gestarteten Anfrage geladen. Es gibt keine automatische Installation und keinen
Modell-/Gerätewechsel im UI.

## Ergebniswahrheit

1. Ausstehende Datensätze zeigen **keine** Scores, Wahrscheinlichkeiten oder
   vorgetäuschten Modellantworten. Goldreferenzen bleiben als solche sichtbar.
2. Abgeschlossene Daten werden zusätzlich im Browser strukturell geprüft:
   Verifikationsstatus, geplante Fallzahlen, jedes Antwortfeld, Optionen,
   Wahrscheinlichkeitsvektoren, Schema-Gültigkeit und Evidenzzuordnung. Die harte
   Hash-/Rohdatenprüfung bleibt im Datenimporter; der Browser ersetzt sie nicht.
3. Eine gespeicherte Antwort gehört nur zu ihrem unveränderten Modellinput.
   Textänderungen, geänderte Regeln und eine geänderte **Fragenreihenfolge**
   invalidieren Replay sofort. Die Vendor-Implementierung erhält die Reihenfolge
   der Fragen, während sie Options-IDs sortiert.
4. Während einer Live-Anfrage besitzt genau diese Anfrage ihren Editorsnapshot.
   Dokumentnavigation ist erlaubt; Suitewechsel, Beispielersetzung und Bearbeitung
   sind gesperrt. Ein älteres oder unvollständiges Ergebnis wird nie angehängt.
5. Ein Fehler zeigt weder alte Antworten noch ein scheinbar plausibles Teilergebnis.
   Es gibt keine simulierte Ersatzinferenz. Ein Tabwechsel beendet eine laufende
   Serverberechnung nicht.
6. Profile kommen vom Server. CPU/ROCm werden erst nach tatsächlichem Laden als
   verwendetes Gerät dargestellt. Es gibt keinen funktionslosen GPU-Umschalter.

## Testen

```sh
# Ohne npm: Logik und unveränderte historische Daten
node --test tests/test_web.mjs

# Zusätzlich: tatsächliche DOM-Interaktionen, ohne Browser/Netzwerksocket/Modell
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

Die reine DOM-Regression verwendet die gepinnte Entwicklungsabhängigkeit
LinkeDOM 0.18.13. Sie prüft tatsächlich gerenderte DOM-Knoten und Events. Die
Testausgaben für Live-/Fehlerszenarien sind ausschließlich ausdrücklich markierte
Testfixtures, nie Messdaten der ausgelieferten Website.

LinkeDOM besitzt keine CSS-Layoutengine. Mobile Bereichszustände, CSS-Breakpoints,
Kontrastwerte und Fokusaufrufe sind modellfrei geprüft; tatsächliche Pixel,
Überlauf, visuelle Fokusringe und Screenreaderverhalten sind damit **nicht**
verifiziert. Der optionale echte Browsertest steht in `tests/test_browser.py`.
Es wurden keine Vorschau-Mockups als Screenshots ausgegeben. Weitere Einzelheiten:
[VALIDATION.md](VALIDATION.md).

Echte Desktop-/Telefonansichten und die README-Galerie werden ausschließlich durch
den [reproduzierbaren Browserlauf](BROWSER_GALLERY.md) erstellt. Seine Existenz ist
noch kein Beleg eines ausgeführten oder bestandenen Browsertests.
