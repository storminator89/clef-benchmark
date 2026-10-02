# Scorer 1.1 audit copy

Created 2026-10-02 during inference, before this reviewer inspected any model predictions. Authorized as a separate robustness fix and additive analysis. The frozen benchmark data, policy, gold, selection, thresholds, and `benchmark/score.py` v1.0 are unchanged.

## Changes

- `qa/score_v1_1.py` is a separate copy of frozen v1.0, with its data directory pointing at `benchmark/`.
- Malformed top-level response, `answers`, and `decision` objects now become invalid response records rather than raising an AttributeError. Missing outputs remain missing. No latency or confidence is invented for malformed records.
- Output-file rows must have a nonempty string ID. Unassignable malformed rows fail with an explicit ValueError; duplicate and unknown IDs remain rejected.
- Existing complete-case `paired` metrics are unchanged. New `paired_all_planned` metrics use all 30 planned pairs, counting invalid/missing/runtime-error halves as incorrect. Both the number valid on both halves and the number with any invalid/missing half are explicit. This additive reliability-sensitive analysis does not replace the frozen valid-both result.
- `scoring_version` is now `1.1`. Accuracy, strict accuracy, class support, F1, calibration, ECE bins, thresholds, abstention grouping, clipping and latency formulas are unchanged.

## Reproduction

Run `python qa/test_score_v1_1.py` for synthetic-only tests. Ten tests pass, including null/list/scalar answer envelopes, correct/wrong/missing labels, malformed probabilities, strict schema, Brier range and NLL clip, ECE, deferral, planned/complete-case pair denominators, exact McNemar, and a complete 180-record synthetic regression against v1.0. The synthetic regression matches every original report field except version.

Run `python qa/score_v1_1.py PATH_TO_FINAL_PREDICTIONS --out PATH_TO_REPORT` only on completed final predictions. The separate final-result audit will record any effect on real records; this document does not imply those records have yet been inspected.
