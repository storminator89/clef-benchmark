# Clef Lab: Project brief / Projektprofil

[Deutsch](#deutsch) · [English](#english) · [Minimalpaare und Score-Zuverlässigkeit](PAIRS_RELIABILITY.md) · [Methodik und Einsatzgrenzen](EVALUATION_GUIDE.md) · [Workbench starten](../README.md#schnellstart)

## Deutsch

### Executive Summary

**Clef Lab zeigt, wie sich ein KI-Entscheidungsmodell nachvollziehbar evaluieren lässt: von einer expliziten Aufgabenregel über eingefrorene Testfälle bis zur prüfbaren Einzelentscheidung.** Die lokale Open-Source-Workbench untersucht Cloudflare Clef mit seinem nativen Decision Head. Sie erzeugt keine Chatantworten als Ersatz für strukturierte Entscheidungen.

Das Projekt verbindet drei Leistungen: getrennte, reproduzierbar auswertbare Testsuiten; eine Oberfläche für Originaltext, Referenz und vollständige Modellwahrscheinlichkeiten; sowie einen ausdrücklich aktivierten lokalen Testpfad für eigene synthetische Fälle. Die Testdaten und Referenzbegründungen sind KI-verfasst. Separate KI-Prüfungen und nachrechenbare Scorer ergänzen die Qualitätssicherung; sie ersetzen keine menschliche Fachvalidierung.

**Der wichtigste Befund ist, wo eine Entscheidung scheitert.** Im Bank-Support sind 228/240 einzelne Felder korrekt, aber nur 68/80 Anfragen in allen drei Feldern. Bei Versicherungsdokumenten wählt das Modell in acht der neun falschen Entscheidungen trotzdem die richtige angebotene Evidenz. Im gezielten Rückfragetest sind 64/72 Fälle vollständig richtig; vier von 36 notwendigen Rückfragen werden übergangen und drei Feldpaare sind inhaltlich inkonsistent. Diese Befunde begründen weitere beaufsichtigte Tests, keine automatische Ausführung.

Die dokumentierte Modellmessung gilt für **Flash 9B, CPU-NF4 mit originalem BF16-Head**. Vorhandene Ergebnisse lassen sich ohne Modell ansehen und nachrechnen. Ein echter lokaler HTTP-Smoke belegt den Integrationspfad; eine versionierte Chrome-Galerie belegt ausgewählte Desktop-/Mobile-Zustände. Frische Installation, andere Hardwareprofile, 27B, reale Kundenprozesse und wirtschaftlicher Nutzen bleiben gesonderte Nachweise.

Für ein Beratungsprojekt liefert Clef Lab damit ein konkretes Arbeitsmuster: Ziel und Fehlerkosten definieren, Daten und Goldreferenzen trennen, den Test vorab fixieren, Fehler vollständig offenlegen und erst danach über einen begrenzten Pilot entscheiden. Es ist ein unabhängiger Forschungsprototyp mit fiktiven Regeln, kein Kundenreferenzprojekt, Modellranking oder Produktionsnachweis.

### Neue Befunde: eine Änderung, zwei Entscheidungen

Die abgeschlossene **Minimalpaardiagnostik** ergänzt die bisherigen Suiten um 24 neue Situationen mit je zwei Varianten. Je Paar wird eine dokumentierte Textstelle verändert; zwölf Änderungen sollen die Entscheidung ändern, zwölf sollen sie erhalten. **39/48 Fälle** und **17/24 Paare** sind vollständig richtig. Alle zwölf gewünschten Wechsel verändern die Ausgabe, doch nur **8/12** treffen beide Referenzentscheidungen. Von zwölf invarianten Paaren bleiben elf stabil, darunter zwei stabil falsche; neun sind auf beiden Seiten richtig. Ein Paar ändert sich unbegründet.

Für ein Kundengespräch ist diese Unterscheidung entscheidend: Reagiert ein System auf die richtige Information, und ist das Ergebnis vor und nach der Änderung korrekt? Bloße Reaktion oder Stabilität reichen als Qualitätsnachweis nicht aus. Die Paare sind abhängig, Schema und allgemeine Regelmuster werden aus dem Rückfragetest wiederverwendet. Das begrenzte Design liefert überprüfbare Fehlerbeispiele, keine allgemeine kausale Wirkungsschätzung.

Die separate **Wahrscheinlichkeitsanalyse** untersucht bereits aufgezeichnete Ergebnisse post-hoc, mit festen Schwellen und ohne neue Inferenz oder angepasste Kalibrierung. Im Paartest bleiben bei Feldscore ≥0,90 **4/36 Feststellungen** und **2/7 Aktionen** falsch; beide Aktionsfehler stammen aus demselben invarianten Paar. Die Rückfragesuite hat an dieser Schwelle 0/49 Feststellungs- und 0/25 Aktionsfehler. Weder diese Nullen noch ein hoher Score belegen Sicherheit.

Die neun Quellsuiten mit 716 Requests und 1.186 Feldbeobachtungen sind ein **Inventar**, kein gemeinsamer Leistungswert oder unabhängiger Stichprobenumfang. Feldschwellen und Auswahl ganzer Fälle bleiben getrennt. So qualifizieren sich in der Rückfragesuite bei einem Minimum beider Feldscores ≥0,90 21/72 Fälle, aber mit der zusätzlichen Bedingung „konkrete Antwort“ nur 5/72. Bild-/Blank-Gruppen behalten ihre lokalen Gold- und Annotationsgrenzen. Es gibt keine menschliche Fach-, Populations- oder Produktionsvalidierung.

**Sinnvoller nächster Schritt:** Für einen klar begrenzten Anwendungsfall Regeln und Fehlerkosten mit Fachverantwortlichen festlegen, neue Paarfamilien unabhängig fachlich annotieren und eine Review-Regel auf getrennten Entwicklungs- und unangetasteten Testdaten prüfen. Gemessen werden vollständige Fälle, korrekte Übergänge, stabil falsche Antworten, Abdeckung und übersehene Fehler. Automatische Kunden- oder Finanzhandlungen sind daraus nicht abgeleitet. [Befunde und Methodik im Detail](PAIRS_RELIABILITY.md#deutsch)

### Mehrere Dokumente und vorbereiteter Modellvergleich

In der neuen Multidokument-Suite findet Clef **42/48 Quellen** korrekt, entscheidet aber nur **24/48 Fälle** vollständig richtig. Acht von zwölf notwendigen Klärungen werden übergangen. Das macht eine wichtige Prüfgrenze sichtbar: Eine passende Quelle bestätigt noch keine richtige Schlussfolgerung. Die 48 fiktiven Fälle teilen 16 Vorlagen und zwölf Familien; sie liefern keine repräsentative Risikoschätzung.

Ein separater Jev-Vergleich wartet auf den expliziten manuellen Start. 974 öffentliche/synthetische Textanfragen sind eingefroren; die Offline-Mocks sind keine Modellmessung. Es gibt keine Jev-Ergebnisse. [Multidokumente](MULTIDOC_UI_DATA.md) · [Start und Grenzen](JEV_EXECUTION.md)

### Kurzer Portfolio-Eintrag

**Clef Lab | Transparente Evaluation strukturierter KI-Entscheidungen**

KI-gestützt entwickeltes Open-Source-Projekt für deutsche Routing-, Dokument- und Rückfrageaufgaben mit Cloudflare Clef. Die lokale Workbench verbindet eingefrorene synthetische Tests, reproduzierbare Auswertung und fallweise Fehleranalyse. Eine separate Minimalpaardiagnostik prüft korrekte Änderungen und stabile Fehler; eine post-hoc Scoreanalyse legt auch hoch bewertete Fehlentscheidungen offen. Originalinputs, Referenzlabels, Modellentscheidungen und ungerundete Wahrscheinlichkeiten bleiben prüfbar. Gemessen wurde Flash 9B im CPU-NF4-Profil; separate KI-Prüfung bedeutet keine menschliche Fachvalidierung. Das Projekt demonstriert Evaluations- und Integrationsarbeit ohne Behauptung von Produktionsreife oder realisiertem Kundennutzen.

## English

### Multi-document finding and comparison readiness

The new multi-document test selects the correct source in **42/48 cases**, but only **24/48 cases** are completely correct. Eight of twelve material clarification needs are missed. Correct source selection therefore does not certify the conclusion. Sixteen reused templates and twelve families limit the 48 fictional cases; no population risk estimate follows.

A separate Jev comparison awaits an explicit manual start: 974 frozen public/synthetic text requests and offline mocks, with no Jev observations. The final MASSIVE Clef baseline remains pending in that package. [Multi-document study](MULTIDOC_UI_DATA.md) · [Execution limits](JEV_EXECUTION.md)

### Executive summary

**Clef Lab demonstrates an inspectable evaluation workflow for an AI decision model: explicit task policies, frozen test cases and traceable individual predictions.** The local open-source workbench evaluates Cloudflare Clef through its native decision head. Structured decisions are preserved rather than replaced with generated chat answers.

The project combines separate reproducible evaluation suites, an interface exposing inputs, references and complete model probabilities, and an explicitly enabled local path for testing custom synthetic cases. Test data and reference explanations are AI-authored. Separate AI reviews and independently recomputed scores support quality checks; they do not constitute human domain-expert validation.

**The most useful findings concern failure modes.** In bank support, 228/240 individual fields are correct, while only 68/80 requests have all three fields correct. In the insurance-document suite, eight of nine incorrect decisions still select the correct offered evidence set. In the dedicated clarification test, 64/72 cases are fully correct; four of 36 required clarifications are missed and three output-field pairs are inconsistent. These findings support further supervised evaluation, not autonomous execution.

Recorded model measurements use **Flash 9B on CPU with an NF4 backbone and the original BF16 head**. Saved results can be explored and rescored without a model. A genuine local HTTP smoke test demonstrates the integration path; a versioned Chrome gallery covers selected desktop and mobile-viewport states. Fresh installation, alternative hardware profiles, 27B, real customer workflows and economic benefit require separate evidence.

For consulting work, the project provides a practical process: define the decision and error costs, separate inputs from reference labels, freeze the evaluation, expose every error and then decide whether a bounded pilot is justified. It is an independent research prototype using fictional rules, not a client case study, model leaderboard or production qualification.

### New findings: one edit, two decisions

The completed **minimal-pair diagnostic** adds 24 new situations with two variants each. Each pair changes one documented text span; twelve edits should change the outcome and twelve should preserve it. **39/48 cases** and **17/24 pairs** are fully correct. All twelve intended flips change the output, but only **8/12** match both reference endpoints. Eleven of twelve invariant pairs remain stable, including two that are stably wrong; nine are correct at both endpoints. One changes without justification.

For a prospective engagement, the useful question is whether the system responds to the relevant information and reaches the correct decision on both sides of an edit. Response or stability alone cannot establish quality. Pair members are dependent, and the schema and generic rule patterns are reused from clarification. This bounded design exposes inspectable failure examples; it does not estimate a general causal effect.

The separate **probability-reliability analysis** describes previously recorded outputs post-hoc, using fixed thresholds without new inference or fitted calibration. At selected field score ≥0.90, the pair suite still has **4/36 incorrect determinations** and **2/7 incorrect actions**; both action errors are endpoints of the same invariant pair. Clarification records 0/49 determination errors and 0/25 action errors at that threshold. Neither those zeros nor a high score establishes safety.

Nine source suites, 716 requests and 1,186 field observations form an **inventory**, not an overall performance score or independent sample size. Field thresholds and whole-case selection remain separate. In clarification, a minimum across both selected field scores ≥0.90 retains 21/72 cases; additionally requiring a concrete answer retains only 5/72. Image/blank groups retain their local gold and annotation limitations. No human-expert, population or production validation is claimed.

**A useful next step:** Agree the rules and error costs for one bounded use case with domain owners, independently annotate new pair families, and evaluate a review policy using separate development and untouched test data. Measure complete cases, correct transitions, stable wrong answers, coverage and missed errors. These results do not authorize automated customer or financial actions. [Detailed findings and method](PAIRS_RELIABILITY.md#english)

### Short portfolio entry

**Clef Lab | Transparent evaluation of structured AI decisions**

An AI-assisted open-source project for German routing, document and clarification tasks using Cloudflare Clef. The local workbench combines frozen synthetic evaluations, reproducible scoring and case-level error analysis. A separate minimal-pair diagnostic tests correct changes and stable errors; a post-hoc score analysis also exposes high-score mistakes. Original inputs, reference labels, model decisions and unrounded probabilities remain inspectable. Measurements use Flash 9B with CPU-NF4; separate AI review is not human expert validation. The project demonstrates evaluation and integration work without claiming production readiness or realized customer value.

## Evidence / Nachweise

These are separate studies with different tasks and denominators. Their percentages are not pooled, ranked or interpreted as changes in model quality.

| Study | Complete-case result | Primary source |
|---|---:|---|
| Bank support: intent, priority, next step | 68/80 | [Report](../experiments/bank-support/REPORT.md), [all errors](../experiments/bank-support/ERRORS.md) |
| Insurance documents: decision and offered evidence | 50/60 | [Report](../experiments/insurance/REPORT.md), [method](../experiments/insurance/METHODOLOGY.md) |
| Clarification: next action and determination | 64/72 | [Report](../experiments/clarification72/REPORT.md), [all errors](../experiments/clarification72/ERRORS.md) |
| Minimal pairs: next action and determination | 39/48 cases; 17/24 pairs | [Report](../experiments/minimal_pairs/REPORT.md), [all errors](../experiments/minimal_pairs/ERRORS.md) |

The [reliability report](../experiments/probability_reliability/REPORT_DE.md), [field details](../experiments/probability_reliability/FIELD_DETAILS.md) and [separate case heuristics](../experiments/probability_reliability/CASE_HEURISTICS.md) describe existing outputs; they add no inference study or pooled score. The remaining suites, language controls and separate image/ablation diagnostics are documented in the [full results overview](../README.md#ergebnisse). The [evaluation guide](EVALUATION_GUIDE.md) separates dataset evidence, software tests, actual model execution and deployment gaps. Historical Chrome galleries retain their original source versions and do not cover the later pair/reliability views.

Independent project, with no affiliation with or endorsement by Cloudflare. Model weights are obtained separately; see [license and attribution](../README.md#lizenz-und-attribution).
