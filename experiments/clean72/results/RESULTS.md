# Clef-Flash: neue saubere deutsche Fälle

Ergebnis: **61/72 (84.72 %) richtig**. Alle 72 geplanten Fälle stehen im Nenner.

11 falsche Entscheidungen; 0 Laufzeit-/Schemafehler. Die Liste `errors` im Scorer erfasst nur Laufzeit-/Schemafehler. Alle falschen Entscheidungen sind vollständig in `decision_errors.jsonl` enthalten.

| Bereich | Richtig |
|---|---:|
| anliegen_priorisierung | 10/12 |
| beitragsrechnung | 6/12 |
| finanzservice_routing | 12/12 |
| rueckfrageplanung | 11/12 |
| unterlagenabgleich | 11/12 |
| vorgangsstand | 11/12 |

## Kontext und Rückfragen

- sufficient: 42/50 richtig
- missing_or_unresolved: 19/22 richtig
- Rückfrage-/Zurückstellungs-Erkennung: Recall 0.8636, Präzision 1.0000
- Unnötige Informationsanforderung bei vollständigem Kontext: 0.0000

## Fehlerbeispiele

### de_clean_rueckfrageplanung_001

Soll: `zeitpunkt`; gewählt: `keine_rueckfrage`; native Konfidenz: 0.8887

Der gewünschte Beginn ist weder genannt noch aus Übergabe bzw. Umzug eindeutig ableitbar.

### de_clean_vorgangsstand_008

Soll: `unterlagen_nachfordern`; gewählt: `einreichung_vorbereiten`; native Konfidenz: 0.7433

Das erforderliche vollständig unterschriebene Formular fehlt wegen der nicht vorhandenen Seite 3.

### de_clean_anliegen_priorisierung_010

Soll: `schadenservice`; gewählt: `bestandsaenderung`; native Konfidenz: 0.6809

Der zuerst gewünschte Status eines konkreten bestehenden Schadens geht an den Schadenservice.

### de_clean_unterlagenabgleich_004

Soll: `konsistent`; gewählt: `abweichung`; native Konfidenz: 0.6417

12 × 12,50 = 150,00; beide Jahresbeträge und Vertragsnummern stimmen überein.

### de_clean_beitragsrechnung_007

Soll: `betrag_c`; gewählt: `betrag_a`; native Konfidenz: 0.5583

438,00 × 73 / 365 = 87,60 Euro.

### de_clean_beitragsrechnung_005

Soll: `betrag_a`; gewählt: `betrag_b`; native Konfidenz: 0.5123

360 × (1 − 0,075) + 12 = 333 + 12 = 345,00 Euro.

## Ausführung und Integrität

- Cloudflare/clef-flash, Revision `17f0b0ad64efb65d273590632833508766b2aae6`
- CPU NF4 backbone, original BF16 joint head and BF16 output embeddings; sechs CPU-Threads, Batch 1, Limit 2.048 Token
- Unveränderter ursprünglicher Text-Runner und virtuelle Umgebung; kein AMD-Adapter, kein Bild-Runner, keine Paketaktualisierung
- Genau ein gewerteter Durchlauf in eingefrorener Reihenfolge; unveränderter fester Warmup und Einzelfall-Wiederholbarkeitscheck des ursprünglichen Runners außerhalb der Wertung
- Vollständige Modell-Dateihashes, eingefrorene Eingaben, Scorer und Gold vor dem Lauf geprüft; eingefrorene Dateien nach dem Lauf unverändert
- 601–710 Eingabetoken, keine Trunkierung; alle nativen Float32-Softmax-Werte ungerundet erhalten
- Median 15.81 s; p95 17.27 s pro Fall. CPU-NF4-Messung, kein Vergleich mit Cloud-/GPU-Latenzen
- Einzelfall-Wiederholbarkeit: {'id': 'de_clean_anliegen_priorisierung_011', 'repeat_max_absolute_probability_difference': 0.0, 'same_choice': True, 'single_case_only': True}

## Grenzen

72 KI-verfasste und vorab unabhängig von einer zweiten KI geprüfte synthetische, gezielt ausgewählte deutsche Bürofälle. Keine echten Kundenkontakte, keine menschliche Fachannotation und keine Produktionsvalidierung. Die Fälle prüfen feste Entscheidungen, keine frei formulierte Beratung. Die native Konfidenz ist keine kalibrierte Zuverlässigkeitsgarantie. Nicht mit früheren Sätzen poolen; Quotenunterschiede sind kein kausaler Manipulationseffekt.

## Dateien und Herkunft

- `predictions.jsonl` und `predictions.metadata.json`: vollständige native Ergebnisse, ungerundete Wahrscheinlichkeiten, Zeiten und Modellkonfiguration
- `scores.json`, `summary.json`, `decision_errors.jsonl`: eingefrorene Auswertung, Kurzmetriken und sämtliche Fehlerfälle
- `run_outcome.json`: Prozessende, einmaliger Hauptlauf, Quellhashes und Ressourcenstand. Ausführliche Start-/Konsolenprotokolle bleiben außerhalb des öffentlichen Exports; `verification.json` dokumentiert die unabhängig kontrollierten Integritätsnachweise.
- `../benchmark/`: vollständige eingefrorene Fälle, Gold, Richtlinien, Audit und Scorer
- Ursprüngliche Modell-Dateien und unveränderter Runner: [`../../../runtime/`](../../../runtime/)
- Offizielle Gewichte: https://huggingface.co/Cloudflare/clef-flash/tree/17f0b0ad64efb65d273590632833508766b2aae6
- Request-SHA256: `3e94e7c8dcda74f58a5402cfe361591da6ee10f818175ec791a3d79856195d84`
- Output-SHA256: `240063f1480ff1a2f69e72f03c9d7a2b04fb337c924ebb6b2941610b4402dc1a`
