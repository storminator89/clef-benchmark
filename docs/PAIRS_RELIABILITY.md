# Minimal pairs and probability reliability / Minimalpaare und Score-Zuverlässigkeit

[Deutsch](#deutsch) · [English](#english) · [Project brief](PROJECT_BRIEF.md) · [Evaluation guide](EVALUATION_GUIDE.md) · [Workbench](../README.md#schnellstart)

Two separate completed studies extend the existing results: a new paired inference diagnostic and a post-hoc analysis of already recorded probabilities. They have different purposes and evidence boundaries. The workbench opens them separately at `#pairs` and `#reliability`. Neither is a pooled leaderboard, a production qualification or a new visual-browser pass.

## Deutsch

### Was lässt sich damit zeigen?

**Eine kleine Änderung ist nur dann richtig verarbeitet, wenn die Entscheidung auf beiden Seiten stimmt. Ein hoher Optionscore allein ist keine abgesicherte Freigaberegel.** Die neuen Ergebnisse machen beide Fragen anhand vollständig einsehbarer synthetischer Fälle überprüfbar.

Für Berater und Interessenten ist der Nutzen ein konkreter Evaluationsablauf: fachliche Soll-Änderung festlegen, Antworten und Referenzen auf beiden Seiten vergleichen, Fehler samt Scores sichtbar lassen und die nächste Prüfung daraus ableiten. Reale Kundenwirkung, Wirtschaftlichkeit und sichere automatische Verarbeitung wurden nicht gemessen.

### 1. Minimalpaare: vollständige Übergänge statt bloßer Reaktion

Die Diagnose enthält **24 Situationen mit je zwei Varianten, also 48 Fälle**: acht Paare je Banking, Versicherung und Finanzen. Zwölf Edits sollen das Ergebnis ändern, zwölf es erhalten. Genau eine zusammenhängende Textstelle wird geändert; unveränderte Regel, Frage, Optionsschema und Textumgebung sind dokumentiert. Die Modelleingabe enthält weder Gold noch Paarinformation. Beide Varianten wurden als separate, zustandslose Requests einmal ausgeführt.

Die Felder sind `action` (`answer`, `ask_fact`, `ask_target`, `resolve_conflict`) und `determination` (`yes`, `no`, `unresolved`). Schema und allgemeine Regelmuster werden aus clarification72 wiederverwendet; die 24 Situationen und Regeltexte sind neu. Vor Inferenz wurden Inputs, Gold, Paarmetadaten, Scorer und Protokoll fixiert und separat KI-geprüft. Das ist keine menschliche Fachprüfung.

| Maß | Ergebnis | Was als Erfolg zählt |
|---|---:|---|
| Vollständiger Fall | **39/48** | Beide Felder dieses Falls entsprechen Gold |
| Vollständiges Paar | **17/24** | Beide Felder beider Varianten entsprechen Gold |
| Richtiger vollständiger Wechsel | **8/12** | Beide Endpunkte des gewünschten Wechsels sind richtig |
| Beobachtete Änderung bei Wechselpaaren | **12/12** | Mindestens ein Feld ändert sich; vier Übergänge sind dennoch falsch |
| Unbegründete Änderung bei invarianten Paaren | **1/12** | Gültige Ausgaben unterscheiden sich trotz gleichem Soll |
| Stabile invariante Paare | **11/12** | Beide gültigen Ausgaben sind gleich; zwei Paare sind stabil falsch |
| Invariante Paare vollständig richtig | **9/12** | Stabilität und beide Referenzentscheidungen stimmen |

Alle 48 Antworten sind technisch gültig und ungekürzt. Die Feldwerte sind separat 40/48 richtige Aktionen und 42/48 richtige Feststellungen; sie ersetzen weder Fall- noch Paargenauigkeit. Abhängige Endpunkte und wiederverwendete Muster erlauben keine naive unabhängige Stichprobenrechnung oder allgemeine kausale Aussage.

**Zwei anschauliche Fehler:** Eine irrelevante Änderung am Berichtstitel lässt zweimal `answer / yes` bestehen, obwohl der Zielbericht ungeklärt bleibt. Ein anderer Fall verletzt bereits den nötigen Preisschritt; dennoch bewirkt ein unbekanntes Handelsfenster eine unnötige Rückfrage statt des schon feststehenden Neins. Stabilität kann einen Fehler erhalten, und eine Änderung kann auf die falsche Information reagieren.

[Paarprotokoll](../experiments/minimal_pairs/PROTOCOL.md) · [Ergebnisse](../experiments/minimal_pairs/REPORT.md) · [Alle Fehler](../experiments/minimal_pairs/ERRORS.md) · [Originalvorhersagen](../experiments/minimal_pairs/results/predictions.jsonl)

### 2. Hohe Scores: feste Schwellen, getrennte Feldgruppen

Die Wahrscheinlichkeitsanalyse ist **post-hoc und deskriptiv**. Die Benchmarkausgänge existierten und waren den Autoren zugänglich, bevor das Analyseprotokoll und die Quellen für die Neuberechnung gehasht wurden. Es gab keine neue Inferenz, angepasste Kalibrierung, Schwellenoptimierung oder Umetikettierung.

**Neun Quellsuiten, 716 Requests und 1.186 Feldbeobachtungen sind nur Inventarzahlen.** Ergebnisse bleiben in 78 Feldgruppen und 64 Fallgruppen getrennt. Es gibt keine gemeinsame Genauigkeit und keine Pooling-Regel über Suiten oder Felder, auch nicht bei identischen Optionsnamen. Aufgaben, Sprachen, Bild-/Blank- und Attack-/Clean-Bedingungen bleiben nach Protokoll getrennt.

| Ausgewählter Feldscore ≥0,90 | Fehler / ausgewählte Felder | Abdeckung |
|---|---:|---:|
| Minimalpaare: Feststellung | **4/36** | 36/48 |
| Minimalpaare: Aktion | **2/7** | 7/48 |
| Rückfragen: Feststellung | **0/49** | 49/72 |
| Rückfragen: Aktion | **0/25** | 25/72 |

Die zwei Aktionsfehler im Paartest sind **die beiden Endpunkte desselben invarianten Paares**; die vier Feststellungsfehler verteilen sich auf drei Paare. Sie sind keine unabhängigen Sicherheitsereignisse. Auch die verwandten Rückfragefälle sind keine unabhängige Produktionsstichprobe. Null beobachtete Fehler in solchen Teilmengen belegen weder Sicherheit noch Kalibrierung.

Die Analyse weist klassenweise summierten Brier (0–2-Konvention), NLL in nats, zehn gleich breite Score-Bins, ECE und Fehler/Abdeckung an den festen Schwellen **0,50 / 0,70 / 0,80 / 0,90 / 0,95 / 0,99** aus. Kleine Bins, Klassenmix und Optionszahl beeinflussen die Größen. Daraus entsteht keine bereinigte Rangliste. Leere Bins und leere Auswahlen haben undefinierte Kennwerte; NLL würde bei Gold-Wahrscheinlichkeit null unendlich, nicht durch Clipping künstlich endlich.

### 3. Warum 49, 25, 21 und 5 gleichzeitig richtig sind

In clarification72 betrachten die ersten zwei Zahlen **je ein Feld**. 49 Feststellungen beziehungsweise 25 Aktionen erreichen 0,90. Bei der **Minimumscore-Heuristik für ganze Fälle** müssen dagegen beide ausgewählten Feldscores mindestens 0,90 sein: Das trifft auf 21/72 Fälle zu, alle 21 sind vollständig richtig. Die zusätzliche Bedingung einer **konkreten Antwort** (`answer` zusammen mit `yes` oder `no`) lässt davon nur fünf Fälle übrig. Daher berichtet die ursprüngliche konkrete Analyse 0/5 Fehler bei 5/72 Abdeckung.

Im Minimalpaartest wählt dasselbe Fallminimum **7/48 Fälle** aus, davon **zwei nicht vollständig richtig**. Das Minimum ist eine Auswahlheuristik, keine gemeinsame Korrektheitswahrscheinlichkeit. Marginale Wahrscheinlichkeiten werden nicht multipliziert. Bei einer leeren Auswahl, etwa den konkreten Rückfrageantworten ab 0,95, ist die Fehlerquote undefiniert. Eine im Nachhinein günstig aussehende Schwelle wäre auf unabhängigen Daten neu zu prüfen.

### 4. Grenzen bleiben direkt bei den Daten sichtbar

- **Abhängigkeiten:** Paarendpunkte, zwölf Rückfrage-Regelfamilien, fünf Versicherungsfälle je Dokument, Sprachvarianten und Bildkontrollen teilen Informationen. Die Ablation verwendet sieben Finance-Szenarien erneut; wiederholte hohe Fehler sind keine neuen unabhängigen Ereignisse
- **Falllokale Evidenz:** Versicherungsoptionen `b1`–`b5` bezeichnen je Fall angebotene Klauselmengen. Ein Slot ist keine über alle Fälle konstante semantische Klasse
- **Bild-Gold:** `bar_line`/`vbar2` haben dokumentiert überlappende Beschreibungen. Eine Abweichung von unverändertem Gold belegt daher nicht automatisch einen eindeutig validierten Erkennungsfehler
- **Blank-Diagnostik:** Leere Bildkontrollen behalten die Referenz des Originalbilds, dessen Inhalt fehlt. Ihre Abweichungen dürfen nicht als gewöhnliche Fehler beantwortbarer Bildfälle dargestellt werden
- **Quellbilder:** Die 50 Originalbilder sind nicht im portablen Paket. Diese Neuberechnung brauchte keine Pixel und behauptet weder eine neue Bild-/Goldprüfung noch einen erneuten Vision-Lauf. Steuerfußnoten-Labels beziehen sich auf die gedruckte Fußnote, Betragsklassen auf den vorzeichenbehafteten Gesamtbetrag
- **Geltungsbereich:** Kleine, gezielt konstruierte, überwiegend KI-verfasste und KI-geprüfte Tests; keine menschliche Fachvalidierung, Populationsschätzung, rechtliche/finanzielle Validierung oder Produktionsfreigabe

### Nächster sinnvoller Nachweis

1. Einen abgegrenzten Prozess, seine Fachregeln, schädliche Fehler und menschliche Entscheidungsverantwortung festlegen
2. Neue Situationen und Paarfamilien fachlich unabhängig annotieren; verwandte Fälle gemeinsam auf Entwicklungs- und unangetastete Testdaten aufteilen
3. Eine Review-Regel auf Entwicklungsdaten festlegen und einfrieren. Auf dem unangetasteten Test vollständige Fälle, korrekte Übergänge, stabile Fehler, Abdeckung und übersehene kritische Fehler messen
4. In einem autorisierten Shadow-Test ohne reale Folgeaktionen prüfen, ob Menschen Fehler erkennen, welche Arbeit die Prüfung verursacht und wie technische Ausfälle behandelt werden

Dies ist ein Vorschlag für neue Evidenz, kein bereits durchgeführter Kundenpilot oder bestätigter Sicherheitsmechanismus.

## English

### What do these additions establish?

**A response to one edit is correct only when both endpoint decisions are correct. A high native option score alone is not a validated release rule.** These additions make both questions inspectable using complete synthetic examples.

For a consultant or prospective client, the useful deliverable is a reproducible evaluation method: specify the intended change, compare both endpoints against references, retain errors and scores, and decide what to test next. Customer impact, economic benefit and safe autonomous operation have not been measured.

### 1. Paired correctness and stability

The completed diagnostic has **24 new situations / 48 cases**, eight pairs each in banking, insurance and finance. Twelve edits should change the outcome and twelve should preserve it. One documented contiguous text span changes; rules, question, options and surrounding text remain fixed. Each endpoint was run as a separate stateless request without gold or pair information. Inputs, references and scoring were frozen and separately AI-reviewed before inference. The schema and generic rule patterns are reused from clarification72; this is not a human-expert holdout.

- **39/48 complete cases** and **17/24 both-correct pairs**
- **8/12 correct full transitions**, although **all 12** flip pairs changed their outputs; four changes remained wrong
- **1/12 unjustified invariant changes**; **11/12 stable invariant pairs**, including **two stable-wrong pairs**; **9/12 invariant pairs both correct**
- All 48 outputs technically valid and untruncated; action accuracy 40/48 and determination accuracy 42/48 remain separate from complete-case and pair accuracy

One invariant pair keeps the same incorrect `answer / yes` after an irrelevant report-title edit even though the target report is unresolved. Another changes its decision when an unknown trading window becomes open, despite an invalid price increment already determining `no`. These bounded examples distinguish useful sensitivity, unjustified changes and stable errors. Dependent endpoints and reused patterns do not establish a general causal effect or population error rate.

### 2. Descriptive probability reliability

This is **post-hoc analysis of existing outcomes**, not a held-out calibration study. Sources and protocol were locked before recomputation, after the benchmark outcomes were available. No new inference, fitted calibration, threshold tuning or relabeling occurred.

**Nine source suites, 716 requests and 1,186 field observations are inventory counts only.** The 78 field groups and 64 case groups remain separate. Fields and suites are never pooled, including those with matching option IDs. Task, language and image/blank or attack/clean partitions retain their original meaning.

At field score ≥0.90, minimal pairs have **4/36 incorrect determinations** (36/48 selected) and **2/7 incorrect actions** (7/48 selected). Both action errors are endpoints of **one invariant pair**; the determination errors occupy three pairs. Clarification has **0/49 determination errors** and **0/25 action errors**, selecting 49/72 and 25/72 fields respectively. These dependent, intentionally constructed subsets do not estimate production risk; zero observed errors does not establish safety.

Each group reports class-summed Brier (0–2 convention), NLL in nats, ten equal-width bins, ECE and error/coverage at fixed thresholds **0.50 / 0.70 / 0.80 / 0.90 / 0.95 / 0.99**. Option counts, class mix and small bins limit comparisons. Empty-bin statistics and empty-selection risk are undefined; a zero gold probability would yield infinite NLL rather than clipping. No score becomes a calibrated safety guarantee or task ranking.

### 3. Field, whole-case and concrete-only denominators

The clarification counts **49** and **25** filter one field at a time. Requiring **every selected field score** to reach 0.90, using their minimum, retains **21/72 cases**, all exact. Also requiring a **concrete answer** (`answer` plus `yes` or `no`) retains only **5/72**, the earlier report's 0/5-error subset. These are different selection rules, not conflicting results.

The same whole-case minimum selects **7/48 minimal-pair cases**, **two inexact**. The minimum is a score heuristic, not a joint probability of correctness; marginal probabilities are not multiplied. At 0.95 no clarification concrete answers qualify, so their error rate is undefined. Choosing a favorable threshold after viewing these results would still require separate development and untouched evaluation data.

### 4. Preserve the local caveats

Pair members, rule families, document families, language variants and image controls are dependent. Attack ablation reuses seven finance scenarios; repeated high-score failures are not independent incidents. Insurance evidence slots name case-local offered clause sets, not stable semantic classes.

For images, `bar_line`/`vbar2` descriptions overlap: disagreement with frozen gold alone need not establish a uniquely validated visual-recognition error. Blank controls retain original-image gold while withholding the original content, so their mismatches are diagnostic rather than ordinary answerable-image failures. The 50 source images are not bundled and were not reacquired or relabeled for this reanalysis; no new vision inference was performed. Invoice tax-footnote labels concern the printed footnote, and amount bands use the signed total. These warnings remain local to the relevant groups and errors in the source reports.

All results describe small, deliberately authored sets with predominantly AI-authored/AI-reviewed references. There is no human-expert validation, representative population estimate, legal or financial validity study, production qualification or measured customer return.

### A useful next evaluation

Agree one bounded process, its rules, error costs and human decision owner. Independently annotate new situations and pair families with domain experts; keep related cases together when splitting development and untouched evaluation data. Define and freeze any review policy on development data, then measure complete cases, correct transitions, stable errors, coverage, missed harmful errors and review workload on the untouched set. An authorized shadow-mode study should perform no real downstream actions and explicitly test human error detection and technical failure handling. This is proposed work, not an existing client deployment or proven safeguard.

## Evidence, runtime and reproduction / Nachweise

- [Minimal-pair protocol](../experiments/minimal_pairs/PROTOCOL.md), [report](../experiments/minimal_pairs/REPORT.md), [all errors](../experiments/minimal_pairs/ERRORS.md) and [artifact/reproduction guide](../experiments/minimal_pairs/README.md)
- [Reliability protocol](../experiments/probability_reliability/PROTOCOL.md), [German report](../experiments/probability_reliability/REPORT_DE.md), [source inventory](../experiments/probability_reliability/SOURCE_INVENTORY.json), [all field details](../experiments/probability_reliability/FIELD_DETAILS.md), [whole-case heuristics](../experiments/probability_reliability/CASE_HEURISTICS.md) and [all gold-relative field disagreements](../experiments/probability_reliability/ERRORS.md)
- [Independent reliability review](../experiments/probability_reliability/audit/INDEPENDENT_REVIEW.md): source-based metric recomputation and report checks; it did not reproduce original model inference or independently relabel images

Recorded text inference uses Cloudflare/clef-flash revision `17f0b0ad64efb65d273590632833508766b2aae6`, CPU-NF4 backbone and original BF16 joint head/output embeddings, six threads, batch one and a 2,048-token cap. The original image run uses its own 4,096-token cap and BF16 vision encoder. No GPU, unquantized-precision, OCR or 27B equivalence is implied. The minimal-pair forward median is 17.298 seconds, excluding model load, unrelated warm-up and a single-case repeat probe; this is not an end-to-end service latency or general determinism study.

Reliability recomputation uses the Python standard library and needs no model or original image pixels. Run the supplied verification/tests from the corresponding experiment directory, following its README; write any reproduced metrics to a new output directory. Do not overwrite frozen inputs, raw outputs, source locks or original derived results. Recomputable arithmetic supports traceability; it does not independently establish the truth of the reference labels.

The historical five-suite and clarification Chrome galleries keep their original source commits, labels and hashes. They do not visually verify the later pair/reliability views. Scientific artifact audits, model-free integration tests and a real visual browser pass are separate evidence levels.
