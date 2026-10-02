# Independent pre-run review

Status: approved for the exact files in `freeze_approval.json`. This is separate AI review, not human-expert validation. The reviewer performed no model load, model inference, or inspection of previous benchmark predictions.

## Exhaustive semantics

All 48 cases, their 144 visible documents, precedence statements, source scopes, dates, facts, questions, plausible-source sets, gold labels, and request payloads were reviewed. The machine-readable case and document review records preserve the visible evidence, individual threshold comparisons, independent source selection, verdicts and hashes. Every current case passes. No case/gold file was edited by the reviewer.

The nine source-uncertain/answer-definite controls are MD012, MD015, MD016, MD028, MD031, MD032, MD044, MD047 and MD048. The three missing-tariff controls safely yield no; the six tied/unknown-version controls safely yield yes. Explicitly scope-excluded distractors never enter their possible-source sets. All twelve unresolved determinations genuinely permit opposing yes/no answers under the supplied facts and complete-source rules.

The source is one complete document. Applicability is resolved before precedence. The visible policy prohibits combining clauses, importing actual contractual rules, or breaking ties by ID, order, length or an inapplicable date. Latest-effective selection uses only versions effective on an allowed event date. Missing publication dates are explicitly immaterial. No hidden rule is needed.

Requests contain only model name, visible state and the shared two-field schema. Expected labels, rationales, metadata and internal document outcomes do not enter the model payload. Logging case IDs are removed by the pinned runner; document IDs remain visible because they are response options. Ja/Nein inside full document rules is task evidence rather than answer-key leakage.

## Review corrections

Round 1 contained 114 documents, mixed document counts, a subtype-fixed source-ID cycle, and unbalanced positions. Its exhaustive records and hashes are retained under `round1/`; the source/gold semantics passed but design/reporting changes were requested. Before inference, the author made all inputs three-document cases with explicit scope exclusions and balanced source IDs and positions within outcome groups. No determination label changed. Current unique-source cases use each ID and each ordinal position nine times, including four yes and five no winners for each.

A source-native check also found that approximate confidence tolerance admitted a non-native rounded value. The primary scorer now requires exact native four-decimal confidence. A report-rendering check found failure when all timing values were unavailable; complete, partial, all-missing and all-invalid reports now render safely. Correction history records these pre-run changes.

## Denominators and scoring

Fixed denominators are 48 cases, 96 field decisions, 27 unique-source cases, 21 ambiguous-source cases, 12 material-clarification cases, 36 definite-answer cases and nine same-answer ambiguous-source controls. Missing or invalid records remain wrong on both fields under full denominators. Clarification categories use the gold determination rather than the misleadingly named unresolved stratum, which intentionally also contains definite-answer controls. Invalid outputs are separately counted and do not masquerade as valid clarification or concrete-answer decisions.

The independent checker does not import the primary scorer. It independently verifies native option sets, finite bounded probabilities, sums, argmax and criterion-order ties, native rounding, exact confidence, token/truncation declarations and telemetry. It independently recomputes every case diagnostic, aggregate, confusion matrix, error evidence and domain/stratum/family/subtype/template slice. Its synthetic suite includes every constant source×determination combination across all 48 cases, missing/malformed cases, duplicate/unexpected IDs, and provenance tampering. All 68 scenarios passed with no differences from the primary scorer where comparison applies. The fourteen provenance scenarios are independent of the scoring comparison and use synthetic metadata only.

The frozen checker also supports actual-run verification of every frozen file, request/runner/encoder hashes, model revision, runtime configuration, packages, start-after-freeze chronology, request/output order, preflight token counts and completed-versus-partial status. Actual result verification remains pending until a run exists.

## Interpretation and remaining limits

These are 48 template-generated instances of sixteen shared archetypes across three domain vocabularies, grouped descriptively into twelve domain×stratum families. They are neither independently written cases nor IID observations, and those twelve families are not independent clusters. All amounts are 400 EUR and each document contains one short threshold rule. The domain, title and template regularities remain deliberate limitations.

There is no paired order intervention. Aggregate balancing does not establish order robustness or a causal effect of document position. No statistical significance, population generalization, real-domain contractual competence, clause composition, generated-answer quality, calibrated probability, production safety or unquantized/GPU equivalence is established. This approval authorizes only the predeclared finite diagnostic under the separate runtime and sequence gates.
