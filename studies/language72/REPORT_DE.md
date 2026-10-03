# Deutsche Sprachvarianten: Ergebnisse der wiederhergestellten Ausführung

## Kernergebnis

Vollständig richtige Entscheidungen: **64/72 (88.9 %)**. Bei bedeutungsgleichen Varianten sind **40/48 (83.3 %)** Paare an beiden Endpunkten richtig. **2/48 (4.2 %)** Paare bleiben stabil falsch; Stabilität allein ist daher kein Erfolgsmaß.

## Getrennte Nenner

| Messgröße | Ergebnis |
|---|---:|
| Alle Fälle, beide Felder richtig | 64/72 (88.9 %) |
| Aktion richtig | 66/72 (91.7 %) |
| Feststellung richtig | 67/72 (93.1 %) |
| Invariante Eingaben, vollständig richtig | 55/60 (91.7 %) |
| Ambiguitätskontroll-Eingaben, vollständig richtig | 9/12 (75.0 %) |
| Invariante Paare, beide richtig | 40/48 (83.3 %) |
| Unbegründeter Wechsel bei invarianten Paaren | 6/48 (12.5 %) |
| Stabil falsche invariante Paare | 2/48 (4.2 %) |
| Verlust: korrekte Basis, falsche Variante | 0/48 (0.0 %) |
| Verbesserung: falsche Basis, korrekte Variante | 5/48 (10.4 %) |
| Alle fünf Ansichten eines Basisfalls richtig | 10/12 (83.3 %) |
| Ambiguitätskontroll-Paare, korrekter voller Richtungswechsel | 3/6 (50.0 %) |

Die 48 invarianten Vergleiche verwenden zwölf gemeinsame Basisantworten jeweils viermal. Sie ergeben 60 unterschiedliche Eingaben. Sechs zusätzliche Kontrollpaare ergeben zwölf weitere Eingaben. Insgesamt wurden 72 unterschiedliche Hauptanfragen gestellt; 54 Paare sind keine 108 unabhängigen Modellaufrufe.

## Ausdrucksformen

| Ansicht | Fälle vollständig richtig |
|---|---:|
| canonical | 10/12 (83.3 %) |
| typo | 11/12 (91.7 %) |
| compact_colloquial | 12/12 (100.0 %) |
| abbreviation | 12/12 (100.0 %) |
| de_en_mix | 10/12 (83.3 %) |

| Transformation | Beide Endpunkte richtig | Unbegründete Änderung | Stabil falsch |
|---|---:|---:|---:|
| typo | 10/12 (83.3 %) | 1/12 (8.3 %) | 1/12 (8.3 %) |
| compact_colloquial | 10/12 (83.3 %) | 2/12 (16.7 %) | 0/12 (0.0 %) |
| abbreviation | 10/12 (83.3 %) | 2/12 (16.7 %) | 0/12 (0.0 %) |
| de_en_mix | 10/12 (83.3 %) | 1/12 (8.3 %) | 1/12 (8.3 %) |

## Domänen

| Domäne | Fälle vollständig richtig | Invariante Paare beide richtig |
|---|---:|---:|
| banking | 20/24 (83.3 %) | 12/16 (75.0 %) |
| insurance | 23/24 (95.8 %) | 16/16 (100.0 %) |
| finance | 21/24 (87.5 %) | 12/16 (75.0 %) |

## Was die Fehler tatsächlich zeigen

Die nachträgliche Fehlerdurchsicht zeigt ein enges Muster: Alle acht Abweichungen betreffen Fälle, in denen zwischen zwei möglichen Zielobjekten mit verschiedenen Ergebnissen geklärt werden muss. In dieser Gruppe sind 5/13 Fälle vollständig richtig; die übrigen 59/59 Fälle sind vollständig richtig. Dies ist eine deskriptive, nachträgliche Untergruppenbeschreibung, keine zusätzliche repräsentative Messung.

Von 13 nötigen Zielrückfragen verfehlt das Aktionsfeld sechs; bei zwei weiteren Fällen fordert es die Zielklärung an, gibt aber gleichzeitig eine konkrete negative Feststellung aus. Insgesamt enthalten fünf Fälle widersprüchliche Aktion-/Feststellungs-Kombinationen. Alle drei Kontrollen, in denen das ausdrückliche Ziel entfernt wurde, blieben fälschlich bei answer/no; die drei Kontrollen mit fehlender Sachangabe wechseln dagegen korrekt zur Rückfrage.

Die sechs Änderungen zwischen invarianten Paaren sind daher nicht sechs Verschlechterungen durch Sprache: fünf Varianten korrigieren eine bereits falsche Basisentscheidung, eine ändert ein falsches Feldpaar in ein anderes falsches Feldpaar. Keine der 40 Paarverwendungen einer vollständig richtigen Basis wird durch die Variante falsch. Dass kompakte Formulierungen und Abkürzungen hier jeweils 12/12 erreichen, belegt keine allgemeine Überlegenheit dieser Schreibweisen: Es sind dieselben zwölf konstruierten Basen.

## Hohe Scores

Bei min(Aktionsscore, Feststellungsscore) ≥0,90 werden 21/72 (29.2 %) Fälle ausgewählt. Davon sind 0/21 (0.0 %) nicht vollständig richtig; bezogen auf alle Fälle sind es 0/72 (0.0 %).
Die Schwelle war vorab festgelegt. Die ungerundeten marginalen Scores sind weder kalibriert noch eine gemeinsame Fehlerwahrscheinlichkeit. Die Feldselektion ist von der Zwei-Feld-Fallselektion zu unterscheiden.

| Feld | Eigene ≥0,90-Selektion | Fehler unter eigener Auswahl | Fehler innerhalb der Zwei-Feld-Auswahl |
|---|---:|---:|---:|
| action | 22/72 (30.6 %) | 0/22 (0.0 %) | 0/21 (0.0 %) |
| determination | 59/72 (81.9 %) | 1/59 (1.7 %) | 0/21 (0.0 %) |

## Technische Vollständigkeit und Laufzeit

Gültige native Ausgaben: 72/72 (100.0 %); fehlend: 0; vorhandene ungültige Ausgaben: 0. Vollständige Paare: 54/54 (100.0 %).
Die 72 Hauptaufrufe benötigen im Mittel 14.520 Sekunden reinen Forward (Median 14.428, Minimum 13.009, Maximum 17.195). Laden, Probe, Aufwärmen und Wiederholungsprüfungen sind darin nicht enthalten.
Ein technischer Warmup-only-Probelauf und zwei Hauptsegmente wurden getrennt ausgeführt. Bei vollständigem Erfolg sind dies drei Ladevorgänge und insgesamt 77 native Forward-Aufrufe: 72 Hauptfälle sowie eine Probe, zwei segmentinterne Warmups und zwei Wiederholungsprüfungen. Der unveränderte native Runner speichert von jeder Wiederholung nur eine Zusammenfassung, keine eigene vollständige Wahrscheinlichkeits-/Zeitzeile; same_choice vergleicht komplette gerundete Antwortobjekte.

| Ausführung | Ladezeit (s) | Warmup-Forward (s) | Prozess-Maximum RSS (Bytes) |
|---|---:|---:|---:|
| probe | 53.403 | 10.141 | 7036891136 |
| segment01 | 51.772 | 10.660 | 7037956096 |
| segment02 | 53.819 | 11.894 | 6806298624 |

## Herkunft, Wiederherstellung und Grenzen

Die 72 Modelleingaben und das erste Segment stimmen bytegenau mit ihren zuvor aufgezeichneten SHA-256-Werten überein. Neue Gold-/Paar-Metadaten und Auswertungscode wurden erneut unabhängig KI-geprüft und vor der neuen Inferenz eingefroren. Die ursprünglichen vollständigen 48 Vorbereitungsdateien und Rohlogs der beiden vorherigen SIGKILL-Versuche waren nach dem Workspace-Verlust nicht wiederherstellbar. Bekannte historische Fakten sind als solche gekennzeichnet; fehlende Belege wurden nicht erfunden.
Die früheren Versuche lieferten keine bewerteten Ausgaben. Der neue Lauf verwendet dasselbe gepinnte Modell, dieselben nativen Skripte und numerischen Einstellungen, aber eine neu aufgebaute Umgebung und mindestens 8 GiB verfügbaren Speicher vor jedem Laden. Ein erfolgreicher neuer Lauf beweist nicht rückwirkend die Ursache der früheren Abbrüche. Laufzeiten verschiedener Umgebungen dürfen nicht als reine Präzisions-/Thread-Effekte verglichen werden.
Die konstruierten deutschen Varianten sind keine repräsentative Nutzungsstichprobe oder Dialektstudie. Geteilte Basen erzeugen abhängige Vergleiche; es werden keine naiven Signifikanztests oder Aussagen zur Produktionssicherheit abgeleitet. Die Regeln sind fiktiv. KI-Review ersetzt keine menschliche Fachprüfung. Sämtliche Abweichungen bleiben mit Regel, Nachricht, Gold, nativen Entscheidungen und vollständigen Scores in ERRORS.md und scored/errors.jsonl erhalten.

Die unabhängige Endprüfung und ihr genauer Status werden separat in evidence dokumentiert. Dieses Dokument allein ist keine Veröffentlichungsfreigabe.
