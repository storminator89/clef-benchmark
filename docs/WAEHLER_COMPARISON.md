# Clef, Jev und Wähler

## Ergebnisse im direkten Vergleich

Ein Fall ist nur richtig, wenn **alle geforderten Felder** richtig sind. Der Nenner bleibt je Testgruppe für alle drei Modelle gleich.

| Testgruppe | Clef richtig | Jev richtig | Wähler richtig |
|---|---:|---:|---:|
| Allgemeine Entscheidungen | 116/120 | 119/120 | 118/120 |
| Finanzen und Makler | 76/80 | 78/80 | 77/80 |
| Büroentscheidungen · clean72 | 61/72 | 67/72 | 62/72 |
| Bank-Kundensupport | 68/80 | 75/80 | 61/80 |
| Versicherungsdokumente | 50/60 | 56/60 | 48/60 |
| Rückfragen statt Raten | 64/72 | 71/72 | 59/72 |
| Minimalpaare · einzelne Fälle | 39/48 | 47/48 | 41/48 |
| Mehrere Dokumente | 24/48 | 44/48 | 19/48 |

Bei Jev fehlt im Bank- und Finanztest jeweils eine auswertbare Antwort. Diese Fälle bleiben im Nenner und zählen nicht als richtig.

Die Ergebnisse gelten für diese Aufgaben und Modellprofile. Kleine synthetische und teils abhängige Fälle sowie unterschiedliche Quantisierung und Hardware begrenzen die Übertragbarkeit.

### Modelle und Auswertung

Wähler 4B lief lokal mit Q8-Gewichten, acht CPU-Threads und nativer Kalibrierung. Clef Flash 9B lief im CPU-NF4-Profil mit BF16-Decision-Head; Jev 1.13.0 über eine gehostete API. Die Profile unterscheiden sich in Größe, Quantisierung und Ausführungsumgebung. Die Messung isoliert deshalb keinen Architektur- oder Quantisierungseffekt; lokale Forward-Zeiten und HTTP-Latenzen sind kein fairer Geschwindigkeitsvergleich.

Verglichen werden dieselben 580 vorab fixierten deutschen Fälle in acht getrennten Gruppen mit 968 Choice-Feldern. Maßgeblich sind die nativen Entscheidungen: Nur vollständig richtige Fälle zählen. Fehlende oder strukturell ungültige Antworten bleiben im geplanten Nenner. Reine Abweichungen der Wahrscheinlichkeitssumme werden separat diagnostiziert, nicht ausgeschlossen oder nachträglich normalisiert. Es gibt keine gepoolte Gesamtrangliste.

Wähler-Revision: `aeb171ee8ddd951cd8b4ee61cc0ed818d6b22cd8`; Modell-SHA-256: `7d9a13c147ed69e7b7f3e83c5f4034043936ba83aae3993dbbe436b885d84989`; JevAlt: `c0d443cba86e7f1e2545db79a37d546027ac321c`. Weitere Prüfsummen stehen in `comparison.json`. Die historischen Clef-/Jev-Ergebnisse bleiben unverändert.

## Fälle und Reproduktion

Alle 580 Fälle lassen sich in der [lokalen Web-App](http://127.0.0.1:8765/#studies?study=wahler580) nach Testgruppe und Modellergebnis filtern. Originaleingabe, Referenz, native Auswahl und vollständige Optionscores bleiben je Modell einsehbar.

- [Fallweise Vergleichsdaten](../studies/wahler580/cases.jsonl)
- [Exakte Eingaben, native Antworten, Scorer und Modellkonfiguration](../studies/wahler580/evidence/README.md)
- [Gruppenergebnisse und Profile](../studies/wahler580/comparison.json)

Vom Repository-Hauptverzeichnis, ohne Modell oder Netzwerk:

```bash
python3 studies/wahler580/evidence/recompute.py --evidence studies/wahler580/evidence
python3 scripts/build_study_web_data.py --check
python3 scripts/generate_evaluation_charts.py --check
```

Die synthetischen Labels wurden separat KI-geprüft, nicht durch ein unabhängiges menschliches Fachpanel validiert. Testgruppen und abhängige Fälle werden nicht zu einer Gesamtrangliste zusammengefasst. Der [historische Jev-Vergleich](JEV_COMPARISON.md) enthält zusätzliche Gruppen außerhalb dieser 580 Fälle.

## Modellquellen und Laufprofil

- [Wähler-Gewichte, gepinnte Revision](https://huggingface.co/mertkayacs/Wahler-4B-GGUF/tree/aeb171ee8ddd951cd8b4ee61cc0ed818d6b22cd8): `Wahler-4B-Q8_0.gguf`.
- [JevAlt, gepinnter Quellstand](https://github.com/mertkayacs/jevalt/tree/c0d443cba86e7f1e2545db79a37d546027ac321c) und [native API](https://github.com/mertkayacs/jevalt/blob/c0d443cba86e7f1e2545db79a37d546027ac321c/docs/api.md).
- Python 3.12.14, llama-cpp-python 0.3.36, CPU mit acht Threads, Kontext 8192, Batch 512, keine GPU-Layer, mmap deaktiviert und Repacking aktiviert.
- Die Kalibrierungsdatei stammt aus derselben gepinnten Modellrevision. Native automatische Spracherkennung: Deutsch; Choice-Temperatur 1.1128. Kein Sprach- oder Coverage-Override und keine nachträgliche Anpassung.
- Alle Requests passten ohne Kürzung in den Kontext. Die nativen Tokenzahlen lagen zwischen 433 und 1445; zusätzlich waren 512 Tokens Reserve vorgesehen.

Die gespeicherten Modell-, Kalibrierungs-, Tokenizer- und Konfigurationshashes stehen in [provenance.json](../studies/wahler580/evidence/provenance.json). Die obigen Replay-Befehle reproduzieren die Auswertung unabhängig von einer Modellinstallation. Ein frischer Modelllauf muss Gewichte, Runtime und Kalibrierung explizit auf diese Revisionen festlegen; der Standard-CLI-Abruf allein stellt diese Pins nicht sicher.
