# Weniger Text, klarere Prüfung

Die Oberfläche verwendet kurze deutsche Titel, feste Symbole mit sichtbarer Beschriftung und Details zum Aufklappen. Regeltext, Referenz und Modellantwort bleiben vollständig. Fehler, fehlende Ergebnisse, lokale Datenschutzgrenzen und die Bedeutung der Nenner stehen weiterhin am jeweiligen Bedienpunkt.

## Was sich geändert hat

- Direkte Seitentitel statt rhetorischer Überschriften: „Fälle prüfen“, „Minimalpaare“, „Score & Fehler“
- Kleinere Überschriften und Abstände; weniger dekorative Nummern und wiederholte Hinweisboxen
- Methodik in nativen, per Tastatur bedienbaren Details; relevante Gruppen- und Fehlerhinweise bleiben sichtbar
- Konsistente lokale SVG-Symbole neben Text, ohne externe Icon-Bibliothek oder reine Rätsel-Buttons
- Eine siebte Ergebnis-Suite mit vollständiger Vorrangregel und drei Dokumenten; Quellenauswahl und Feststellung getrennt geprüft

## Messbarer Textumfang

Die Zählung nutzt gerenderten DOM-Text ohne geschlossene Detailinhalte, versteckten Text, Icons und nicht ausgewählte Optionen. Sie beschreibt die beiden konkreten Standardansichten, keine allgemeine Lesbarkeits- oder Usability-Studie.

| Ansicht | Vorher | Nachher |
|---|---:|---:|
| Paar-Kopfbereich | 27 Wörter | 9 Wörter |
| Score-Kopfbereich | 25 Wörter | 10 Wörter |
| Standard-Paaransicht | 448 Wörter | 375 Wörter |
| Standard-Scoreansicht | 534 Wörter | 402 Wörter |

Alle unveränderten wissenschaftlichen Daten bleiben bytegleich. Der UI-Umbau verbessert weder retrospektiv Modellantworten noch Benchmarkwerte.

## Vorher: versionierte echte Aufnahmen

Die alten Aufnahmen bleiben unverändert. Sie zeigen den früheren Stand `a21344f8c1d3ebc848a753c88f90ae257c36608d`:

[Minimalpaare vorher](screenshots/paired-reliability/screenshots/minimal-pairs-comparison-light.png) · [Scoreansicht vorher](screenshots/paired-reliability/screenshots/reliability-determination-light.png)

Der aktuelle Browsernachweis wird gesondert an seinen exakten Quellstand gebunden. Ein Screenshot belegt nur den sichtbaren Zustand; Interaktionsprüfungen, modellfreie Softwaretests und wissenschaftliche Inferenz bleiben unterschiedliche Nachweise.
