# Clef: HuggingFace-Bildtest mit deutschen Fragen

Stand: 2. Oktober 2026. Separater Pilot neben den früheren Texttests; diese bleiben unverändert.

## Ergebnis

Der vollständige Lauf ist mit Exit 0 abgeschlossen: 90 von 90 Vorhersagen, keine Kürzungen, echte Vision-Aufrufe bei allen Requests und unveränderte eingefrorene Inputs.

| Aufgabe mit deutschen Fragen | Richtige Quellenlabels | Mehrheit ohne Bild |
| --- | ---: | ---: |
| Diagrammart | 27/30 (90 %) | 10 % |
| Anzahl Legenden-Einträge | 30/30 (100 %) | 36,7 % |
| Belegart | 20/20 (100 %) | 80 % |
| Ausdrücklicher Steuerhinweis | 19/20 (95 %) | 60 % |
| Bruttosummen-Intervall | 18/20 (90 %) | 20 % |

Alle Aufgaben eines Bildes stimmen bei 27/30 Diagrammen und 17/20 Belegen mit den Quellenlabels überein. **Wichtige Testgrenze:** Alle drei Diagrammtyp-Abweichungen sind Säulen-plus-Linie gegen die Option „Senkrechte Säulen mit zwei y-Achsen“. Die betroffenen Bilder besitzen tatsächlich beide Merkmale. Diese im Nachhinein erkannte Überschneidung der Optionsbeschreibungen begrenzt die Aussagekraft der strikten 27/30; sie belegt nicht drei eindeutige visuelle Erkennungsfehler. Gold und Resultate werden nicht nachträglich umgeschrieben.

Bei zwei Gutschriften wurde ein negativer Gesamtbetrag einer positiven Betragsklasse zugeordnet (80,4 % beziehungsweise 85,9 % Konfidenz). Ein ausdrücklicher Kleinunternehmer-Hinweis wurde verfehlt. Kein Primärfehler hatte mindestens 90 % Konfidenz; das ersetzt keine Kalibrierungs- oder Sicherheitsprüfung.

Auf denselben gepaarten zehn Diagrammen liefern deutsche Fragen 19/20 richtige Feldentscheidungen, englische 19/20 und weiße Bilder nur 1/20. Bei zehn gepaarten Belegen sind es 27/30, 28/30 und 12/30. Das stützt eine echte Abhängigkeit vom Bildinhalt; die erzwungene Auswahl ohne Enthaltungsoption ist kein Test einer sicheren Ablehnung unlesbarer Bilder. 49/50 gepaarte deutsche/englische Entscheidungen sind identisch; für einen allgemeinen Sprachvergleich ist die Stichprobe zu klein.

Gemessene Median-Latenz: 37,73 Sekunden pro Diagramm und 36,79 Sekunden pro Beleg, nach separatem Aufwärmen; Peak-RSS 6,49 GiB. Diese CPU-NF4-Messung ist nicht auf eine Radeon-/ROCm- oder Hersteller-GPU-Konfiguration übertragbar.


## Gegenstand

- 30 synthetische Diagramme aus dem offiziellen Testsplit von `YuukiAsuna/synthetic_chart`: eine durch SHA-256 deterministisch ausgewählte Datei pro Diagrammtyp × Schwierigkeitsgrad (10 × 3)
- 20 synthetische **deutsche** Rechnungen/Gutschriften aus der öffentlichen Belege-Vorschau: 8 reguläre, 5 Kleinunternehmer-, 3 Reverse-Charge- und 4 Gutschrift-Fälle; 12 Fotos, 6 Scans, 2 saubere Renderings
- Insgesamt 120 Primärentscheidungen: Diagrammart und Anzahl Legenden-Einträge; Dokumentart, ausdrücklicher Steuerhinweis und Bruttosummen-Intervall
- 20 identische Bilder zusätzlich mit englischen Fragen sowie dieselben 20 mit weißen Bildflächen und deutschen Fragen: insgesamt 90 Vorwärtsläufe

Die Diagramme haben englische Bildbeschriftungen. Deutsche Aufgabenformulierungen machen daraus **keinen deutschen Bilddatensatz**. Die Belege sind dagegen tatsächlich deutschsprachige, künstlich erzeugte Bilder. Es gibt für diese 40-Belege-Vorschau keinen offiziellen Testsplit.

## Sicherungen vor dem Hauptlauf

Alle 50 Bilder und 120 Referenzentscheidungen wurden unabhängig direkt anhand der Bildpunkte kontrolliert, ohne Modellvorhersagen zu lesen. Zwei unpräzise Diagramm-Optionsbeschreibungen wurden vorab korrigiert. Fälle, Referenzlabels, Aufgaben, Auswertungscode und Bilder sind vor Inferenz per Hash eingefroren. Die sechs Scorer-Tests prüfen vollständige, fehlerhafte und ungültige Ausgaben. Alle 90 Requests wurden auf vollständige Kodierung geprüft: 1.119–1.400 Tokens, keine Kürzung.

Der Inferenzprozess liest nur Fragen und Bilddateien. Quell-IDs, Dateinamen, OCR-Transkripte, Metadaten und Goldlabels gelangen nicht in den Modelltext. Der offizielle Processor erzeugt echte `pixel_values`; ein Beobachtungshook protokolliert pro Request den tatsächlichen Aufruf des Vision-Encoders. Weiße Kontrollbilder haben dieselbe Originalgröße wie ihre Gegenstücke.

## Rechenkonfiguration

Modell: `Cloudflare/clef-flash`, Revision `17f0b0ad64efb65d273590632833508766b2aae6`.

CPU-only, Batch 1, sechs Threads. Sprach-Linear-Layer NF4 mit Double Quantization und BF16-Berechnung. Originaler Vision-Encoder, Original-Joint-Head und Ausgabe-Embedding bleiben BF16. Die offizielle `joint_schema_model.py` wird unverändert genutzt. Das ist eine experimentelle CPU-Konfiguration und kein Hersteller-H200/BF16-Benchmark.

Warum der Vision-Encoder BF16 bleibt: Die 4-Bit-CPU-Packroutine der installierten bitsandbytes-Version passt nicht zu den Vision-MLP-Dimensionen (4304). Der Ausschluss `model.visual` wurde geprüft; null Vision-Linear4bit-Module und BF16 aller Vision-Parameter werden vor dem Lauf verlangt. Das BF16-Visionmodell stammt direkt aus dem unveränderten offiziellen Checkpoint.

Auflösung: offizieller Processor, mindestens 65.536 und höchstens 786.432 Bildpunkte, Seitenverhältnis erhalten. Keine Ausschnitte, zusätzliche OCR, Rotation oder Bildoptimierung. Die Größenrundung folgt dem offiziellen Patchraster. Ein separates, nicht gewertetes Bild wärmt den Visionpfad auf; Lade- und Aufwärmzeiten zählen nicht als Benchmark-Latenz.

## Auswertung

Exakte Übereinstimmung des zulässigen Options-IDs. Ergebnisse getrennt nach Datensatz und Feld; zusätzlich Anteil vollständig richtiger Bilder, Klassen-Balanced-Accuracy und Mehrheitsklassen-Baseline. Englisch und Weißbild werden nur auf denselben gepaarten Teilmengen verglichen. Schema-Validität ist ein getrenntes technisches Maß.

Ein hoher Softmax-Wert ist keine Garantie. Fehler mit mindestens 90 % Konfidenz werden gesondert ausgewiesen. Die Kontrollbilder prüfen, ob die Vorhersage von Bildinhalt abhängt; sie beweisen keine vollständige kausale Interpretation oder Robustheit gegen andere Bildstörungen.

## Grenzen

Kleine, gezielt geschichtete synthetische Stichprobe. Trainingskontamination ist unbekannt. Aufgaben umfassen überwiegend Erkennung und begrenzte Klassifikation, keine freie Volltext-OCR, Rechnungsprüfung, Anlageberatung, komplexe Finanzmathematik oder Produktionsfreigabe. Einige Diagramme haben inhaltlich unplausible Titel/Achsen und abgeschnittene Legendentexte; die zu zählenden Einträge sind sichtbar. Vier Kleinunternehmer-Belege zeigen widersprüchliche Steuersätze in Positionszeilen; die Frage verlangt ausdrücklich den sichtbaren §19-Fußnotenhinweis. Es wird Bildinhalt erkannt, keine steuerrechtliche Gültigkeit bewertet.

## Dateistruktur

- `benchmark/`: eingefrorene Fälle, Requests, Gold, Paarungen, Regeln und Hashmanifest
- `scripts/`: gepinnter Download, deterministischer Aufbau, Processor-Preflight, offizielle Vision-Inferenz, RAM-Wächter und unabhängige Auswertung
- `results/`: unbearbeitete Vorhersagen, Tensor-/Encoder-Nachweise, Laufmetadaten und spätere Scores
- `qa/`: Vorab-Pixelaudit, Kodierungsprüfung, Scorer-Tests und Download-Reproduktionsprüfung
- `provenance/`, `licenses/`, `NOTICE`: Versionen, Prüfwerte und Lizenznachweise

Rohbilddateien und vollständige ursprüngliche Beleglabels werden nicht mit dem Ergebnis-Paket verbreitet. Der Bericht enthält lediglich zwei gekennzeichnete Ausschnitte als dokumentarische Abbildungen der negativen Gesamtsummen; dies ist mit der ausdrücklichen Abbildungsfreigabe und Belege-Attribution gedeckt. Die Quellbeschaffung ist reproduzierbar und verweist auf feste HuggingFace-Versionen. Siehe `REPRODUCE.md`.
