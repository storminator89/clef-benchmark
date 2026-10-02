# Bank-Kundensupport in der Workbench

Die eigenständige Suite `bank-support` verwendet den Split
`german_bank_support_primary`. Ihre 80 deutschsprachigen Fälle sind synthetisch;
auch die mitgelieferte Servicerichtlinie ist fiktiv. Es werden keine echten
Kundendaten verwendet und keine Bankvorgänge ausgeführt.

## Drei getrennte Auswahlfelder

- `intent`: Anliegen erkennen
- `priority`: Priorität anhand der mitgelieferten Regeln bestimmen
- `next_step`: nächsten Bearbeitungsschritt aus festen Optionen auswählen

Die Oberfläche zeigt pro Feld Sollreferenz, tatsächliche Modellwahl und sämtliche
unveränderten Modellwahrscheinlichkeiten. Die Referenzbegründung ist eine
Goldannotation, keine vom Modell erzeugte Erklärung. Nachricht und mitgelieferte
Servicerichtlinie stehen als getrennte Abschnitte im Dokumentbereich; zusätzlich
bleiben der exakte Nachrichtentext (`state`) und sämtliche nativen
Feldanweisungen inklusive Auswahloptionen einsehbar. Die Regeln werden dem
Modell in den Feldanweisungen bereitgestellt, nicht als Zusatz im Nachrichtentext.

## Nenner und Vergleichbarkeit

Jede Feldgenauigkeit hat den Nenner 80. Ein Fall gilt nur dann als vollständig
richtig, wenn alle drei Felder richtig sind. Der Kategorienvergleich zählt
vollständig richtige Fälle. Kein Mittelwert über die Felder wird als
Fallgenauigkeit ausgegeben und kein Ergebnis wird mit früheren Suiten gepoolt.
Die wenigen synthetischen Beispiele sind keine repräsentative Messung realer
Bankanfragen, seltene Fehlpriorisierungen können damit nicht zuverlässig
quantifiziert werden. Diese Suite misst weder freie Antwortqualität noch eine
sichere automatische Bearbeitung.

## Ergebnis- und Replay-Grenzen

Die Browserprüfung verlangt alle 80 Fälle, die vollständige native Feldfolge
`intent`, `priority`, `next_step`, gültige Optionen, Goldwerte, Resultate und
Wahrscheinlichkeitsvektoren. Ausstehende Ergebnisse dürfen keine Scores oder
Modellantworten enthalten. Vor der Veröffentlichung prüft der Datenimporter
zusätzlich die finalen Quellen und ihre Hashes; eine Browserprüfung ersetzt diese
Quellenprüfung nicht.

Gespeicherter Replay gilt nur für den unveränderten Text und die unveränderte
Feldreihenfolge. Änderungen an Nachricht, Richtlinie oder Schema löschen die
Anzeige des alten Ergebnisses. Während einer neuen Live-Anfrage bleibt deren
Editorsnapshot gesperrt; Navigation im Explorer verändert diesen Snapshot nicht.
Eine unvollständige Drei-Feld-Antwort wird insgesamt zurückgewiesen.

Die bestehenden lokalen CPU-/AMD-Profile, Token- und Größenlimits bleiben
unverändert. Das Öffnen der Suite führt keine Inferenz aus.

## Prüfung

Die Node-Tests enthalten explizite, ausschließlich testlokale Drei-Feld-Fixtures
für Rendering, Kennzahlen, Datenzulassung, Filter, Replay und unterbrochene
Navigation. Diese Fixtures sind keine Benchmark-Ergebnisse. Die DOM-Prüfung hat
keine Layoutengine und verifiziert weder Pixel noch Smartphone-Überlauf. Die
bereits dokumentierte Grenze der visuellen Browserprüfung bleibt bestehen.

## Priorisierung und Eskalation

Neben der Feldgenauigkeit zeigt die Oberfläche Fehlpriorisierungen mit expliziten
Nennern: kritische Fälle unterhalb `critical`, kritische Fälle ohne
`security_handoff`, dringende Fälle fälschlich als `routine`, unnötig als
`critical` eingestufte Fälle und unnötige Security-Handoffs. Unnötige Eskalationen
bedeuten genau: Gold `guidance`/`clarify`, Modell
`specialist_review`/`security_handoff`. Ein tatsächlich prüfungsbedürftiger
Fachstellenfall wird damit nicht pauschal als unnötige Eskalation gezählt.

Die Prioritäts-Goldverteilung enthält 10 kritische, 6 dringende und 64
Routinefälle. Immer `routine` zu wählen ergäbe bereits 64/80 = 80 %
Prioritätsgenauigkeit. Diese Baseline und die Fehlergruppen gehören deshalb zur
Interpretation; eine hohe Gesamtquote allein belegt keine sichere Priorisierung.
Die Verteilung ist gestaltet und sagt nichts über reale Bank-Traffic-Anteile aus.

## Reproduzierbarer Import

Die abgeschlossene öffentliche Exportstruktur liegt unter
`experiments/bank-support/`. Der Import akzeptiert ausschließlich diesen
vorab eingefrorenen Test und einen vollständig abgeschlossenen, unabhängig
geprüften Lauf:

```sh
python scripts/build_bank_web_data.py
python scripts/check_bank_support.py
```

Die Zulassung kontrolliert den vollständigen Exportmanifest, alle ursprünglichen
Freeze-Hashes, Modellrevision und unveränderten Runner, CPU-Konfiguration,
chronologische Reihenfolge, Request-IDs und Tokenmessung. Der finale unabhängige
Prüfbericht ist an die tatsächlichen Input-, Rohresultat-, Metadaten-, Summary-
und Fehlerdateien gebunden. Alte oder unvollständige QA-Berichte werden abgelehnt.
Zusätzlich berechnet der Importer Feldmetriken, exakte Fälle, Konfusionsmatrizen
und sämtliche Safety-Fallmengen direkt aus ungerundeten Vektoren neu.

Die vollständige Prüfung führt beide Scorer modellfrei erneut aus. Sie prüft
außerdem alle 80 echten Request-Bodys gegen den bestehenden lokalen API-Vertrag
und bewahrt 212 frühere Daten-/Laufzeitdateien bytegleich. Es werden keine
vorherigen Messwerte ersetzt, keine Inferenz gestartet und keine Modellgewichte
benötigt.
