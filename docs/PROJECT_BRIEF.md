# Clef Lab: Project brief / Projektprofil

[Deutsch](#deutsch) · [English](#english) · [Methodik und Einsatzgrenzen](EVALUATION_GUIDE.md) · [Workbench starten](../README.md#schnellstart)

## Deutsch

### Executive Summary

**Clef Lab zeigt, wie sich ein KI-Entscheidungsmodell nachvollziehbar evaluieren lässt: von einer expliziten Aufgabenregel über eingefrorene Testfälle bis zur prüfbaren Einzelentscheidung.** Die lokale Open-Source-Workbench untersucht Cloudflare Clef mit seinem nativen Decision Head. Sie erzeugt keine Chatantworten als Ersatz für strukturierte Entscheidungen.

Das Projekt verbindet drei Leistungen: getrennte, reproduzierbar auswertbare Testsuiten; eine Oberfläche für Originaltext, Referenz und vollständige Modellwahrscheinlichkeiten; sowie einen ausdrücklich aktivierten lokalen Testpfad für eigene synthetische Fälle. Die Testdaten und Referenzbegründungen sind KI-verfasst. Separate KI-Prüfungen und nachrechenbare Scorer ergänzen die Qualitätssicherung; sie ersetzen keine menschliche Fachvalidierung.

**Der wichtigste Befund ist, wo eine Entscheidung scheitert.** Im Bank-Support sind 228/240 einzelne Felder korrekt, aber nur 68/80 Anfragen in allen drei Feldern. Bei Versicherungsdokumenten wählt das Modell in acht der neun falschen Entscheidungen trotzdem die richtige angebotene Evidenz. Im gezielten Rückfragetest sind 64/72 Fälle vollständig richtig; vier von 36 notwendigen Rückfragen werden übergangen und drei Feldpaare sind inhaltlich inkonsistent. Diese Befunde begründen weitere beaufsichtigte Tests, keine automatische Ausführung.

Die dokumentierte Modellmessung gilt für **Flash 9B, CPU-NF4 mit originalem BF16-Head**. Vorhandene Ergebnisse lassen sich ohne Modell ansehen und nachrechnen. Ein echter lokaler HTTP-Smoke belegt den Integrationspfad; eine versionierte Chrome-Galerie belegt ausgewählte Desktop-/Mobile-Zustände. Frische Installation, andere Hardwareprofile, 27B, reale Kundenprozesse und wirtschaftlicher Nutzen bleiben gesonderte Nachweise.

Für ein Beratungsprojekt liefert Clef Lab damit ein konkretes Arbeitsmuster: Ziel und Fehlerkosten definieren, Daten und Goldreferenzen trennen, den Test vorab fixieren, Fehler vollständig offenlegen und erst danach über einen begrenzten Pilot entscheiden. Es ist ein unabhängiger Forschungsprototyp mit fiktiven Regeln, kein Kundenreferenzprojekt, Modellranking oder Produktionsnachweis.

### Kurzer Portfolio-Eintrag

**Clef Lab | Transparente Evaluation strukturierter KI-Entscheidungen**

KI-gestützt entwickeltes Open-Source-Projekt für deutsche Routing-, Dokument- und Rückfrageaufgaben mit Cloudflare Clef. Die lokale Workbench verbindet eingefrorene synthetische Tests, reproduzierbare Auswertung und fallweise Fehleranalyse. Originalinputs, Referenzlabels, Modellentscheidungen und ungerundete Wahrscheinlichkeiten bleiben prüfbar. Der Schwerpunkt liegt auf vollständigen Fällen, verpassten Rückfragen und belegten Grenzen. Gemessen wurde Flash 9B im CPU-NF4-Profil; separate KI-Prüfung bedeutet keine menschliche Fachvalidierung. Das Projekt demonstriert Evaluations- und Integrationsarbeit ohne Behauptung von Produktionsreife oder realisiertem Kundennutzen.

## English

### Executive summary

**Clef Lab demonstrates an inspectable evaluation workflow for an AI decision model: explicit task policies, frozen test cases and traceable individual predictions.** The local open-source workbench evaluates Cloudflare Clef through its native decision head. Structured decisions are preserved rather than replaced with generated chat answers.

The project combines separate reproducible evaluation suites, an interface exposing inputs, references and complete model probabilities, and an explicitly enabled local path for testing custom synthetic cases. Test data and reference explanations are AI-authored. Separate AI reviews and independently recomputed scores support quality checks; they do not constitute human domain-expert validation.

**The most useful findings concern failure modes.** In bank support, 228/240 individual fields are correct, while only 68/80 requests have all three fields correct. In the insurance-document suite, eight of nine incorrect decisions still select the correct offered evidence set. In the dedicated clarification test, 64/72 cases are fully correct; four of 36 required clarifications are missed and three output-field pairs are inconsistent. These findings support further supervised evaluation, not autonomous execution.

Recorded model measurements use **Flash 9B on CPU with an NF4 backbone and the original BF16 head**. Saved results can be explored and rescored without a model. A genuine local HTTP smoke test demonstrates the integration path; a versioned Chrome gallery covers selected desktop and mobile-viewport states. Fresh installation, alternative hardware profiles, 27B, real customer workflows and economic benefit require separate evidence.

For consulting work, the project provides a practical process: define the decision and error costs, separate inputs from reference labels, freeze the evaluation, expose every error and then decide whether a bounded pilot is justified. It is an independent research prototype using fictional rules, not a client case study, model leaderboard or production qualification.

### Short portfolio entry

**Clef Lab | Transparent evaluation of structured AI decisions**

An AI-assisted open-source project for German routing, document and clarification tasks using Cloudflare Clef. The local workbench combines frozen synthetic evaluations, reproducible scoring and case-level error analysis. Original inputs, reference labels, model decisions and unrounded probabilities remain inspectable. The focus is complete-case correctness, missed clarifications and evidenced limitations. Measurements use Flash 9B with CPU-NF4; separate AI review is not human expert validation. The project demonstrates evaluation and integration work without claiming production readiness or realized customer value.

## Evidence / Nachweise

These are separate studies with different tasks and denominators. Their percentages are not pooled, ranked or interpreted as changes in model quality.

| Study | Complete-case result | Primary source |
|---|---:|---|
| Bank support: intent, priority, next step | 68/80 | [Report](../experiments/bank-support/REPORT.md), [all errors](../experiments/bank-support/ERRORS.md) |
| Insurance documents: decision and offered evidence | 50/60 | [Report](../experiments/insurance/REPORT.md), [method](../experiments/insurance/METHODOLOGY.md) |
| Clarification: next action and determination | 64/72 | [Report](../experiments/clarification72/REPORT.md), [all errors](../experiments/clarification72/ERRORS.md) |

The remaining suites, language controls and separate image/ablation diagnostics are documented in the [full results overview](../README.md#ergebnisse). The [evaluation guide](EVALUATION_GUIDE.md) separates dataset evidence, software tests, actual model execution and deployment gaps.

Independent project, with no affiliation with or endorsement by Cloudflare. Model weights are obtained separately; see [license and attribution](../README.md#lizenz-und-attribution).
