# Mehrere Dokumente: Quelle und Entscheidung

Die Auswahl **Mehrere Dokumente** öffnet die abgeschlossene eigenständige Suite `multidoc` mit 48 Fällen. Der Explorer zeigt die gesamte Vorrangregel, alle drei Dokumente in Originalreihenfolge, bekannte Fakten und die Frage. Filter, Einzelprüfung, Ergebnisübersicht und gespeicherter Replay bleiben auf diese Suite begrenzt.

## Was wird bewertet?

Zwei native Felder: `source` wählt D1, D2, D3 oder `not_unique`; `determination` wählt yes, no oder unresolved. **42/48 Quellen** und **24/48 Feststellungen** sind richtig; **24/48 Fälle** stimmen in beiden Feldern. Die 24 Fehler und alle nativen Optionswahrscheinlichkeiten bleiben unverändert sichtbar.

Eine unklare Quelle erfordert nicht automatisch eine offene Antwort. Wenn alle möglichen Quellen dasselbe Ergebnis liefern, ist `not_unique` mit yes/no erlaubt. Neun Kontrollfälle prüfen diese Unterscheidung; sechs sind vollständig richtig. Die gemessenen 15 inkonsistenten Feldpaare folgen der vorab festgelegten, fallbezogenen Regel und werden nicht nachträglich repariert.

## Grenzen

- 48 KI-verfasste, separat KI-geprüfte Fälle mit vollständigen fiktiven Regeln; keine menschliche Fachvalidierung oder echte Vertragsauslegung
- Zwölf Familien und 16 wiederverwendete Vorlagen; die Fälle sind abhängig
- Ein vollständiges maßgebliches Dokument wählen, keine Kombination partieller Klauseln oder freie Antwortqualität
- Ausgewogene Dokument-IDs/Positionen, aber kein gepaarter Reihenfolgewechsel: keine kausale Robustheitsaussage
- Experimentelle CPU-NF4-Ausführung mit originalem BF16-Head; kein GPU- oder unquantisierter Vergleich
- Native marginale Optionscores sind keine kalibrierte oder gemeinsame Korrektheitswahrscheinlichkeit

## Reproduktion

`build_multidoc_web_data.py` prüft den exakten öffentlichen Export, den Vorab-Freeze, vollständige IDs und unveränderte native Vektoren. Scorer und unabhängige Gegenprüfung werden ohne Modell erneut ausgeführt. `check_multidoc.py` schützt außerdem die bisherigen wissenschaftlichen Artefakte. Die UI-Datei ist nur eine deterministische Ableitung; eingefrorene Inputs und Ergebnisse bleiben im Experimentordner.

[Bericht](../experiments/multidoc48/REPORT.md) · [Alle Fehler](../experiments/multidoc48/ERRORS.md) · [Vorab-Protokoll](../experiments/multidoc48/PROTOCOL.md)
