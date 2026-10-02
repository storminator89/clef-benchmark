# Independent review: PASS

The scientific contents, metrics, reports, and public-scope checks pass independent review. The complete-file integrity manifest must also pass after any packaging change.

## Independence and checks

The independent formulas and synthetic tests were implemented before inspecting real predictions or the primary metric implementation. Real-source scoring began only after the announced source lock. The independent calculator never imports a primary implementation, never reads derived normalized rows as scoring input, and performs no model inference, fitting, clipping, renormalization, label changes, or threshold tuning.

- Source lock: `c02c5378121b67c91706c3f2edcff45b50224f2b752bbb6188849ec9f329bff4`
- All 73 locked scientific source/protocol/inventory files rehashed before and after the independent computation
- Nine suites, 716 requests, 1,186 field observations, 78 separate field groups and 64 separate case groups
- 65,127 independent source, grouping, metric, item, denominator and context comparisons passed
- All 124 field disagreements with frozen gold verified, including native unrounded vectors, saved choices, source gold, original input context and case metadata
- No missing, extra, duplicate, invalid or truncated records; no exact maximum-score ties in the real records
- 15 independently authored synthetic tests and all 20 primary synthetic tests rerun successfully
- 3,749 report assertions passed: all 780 bin rows, 468 field-threshold rows, 384 case-threshold rows, 124 error sections and 20 errors with selected score at least .90

Every Brier, NLL, confidence mean, bin, ECE, fixed risk/coverage threshold and tie-aware error AUROC agrees with the independent recomputation. Undefined and infinite cases were tested synthetically; no real gold probability equals zero. Native choices are retained without retie-breaking. Whole-case minimum scores are described only as heuristics.

## Required denominator and dependence checks

The minimal-pair action errors at .90 are two endpoints of one invariant pair. Its four high-score determination errors occupy three pairs. These are dependent observations.

Clarification at .90 retains 25 action fields and 49 determination fields; the all-case minimum-score gate retains 21 cases, all exact. Adding the earlier concrete-only condition retains five cases. The report clearly distinguishes these denominators. Finance and attack-ablation high-score repeats have identical recorded native vectors and are identified as repeated scenarios.

## Report and provenance review

The full human-readable error inventory preserves every field disagreement with frozen gold. For chart-type observations, the overlapping bar_line/vbar2 option descriptions limit interpretation: a recorded gold mismatch alone does not establish a semantic visual-recognition failure. Blank-image targets also remain relative to the original-image gold. All original native outputs remain available at the referenced relative scientific files and IDs. Local frozen-gold/overlapping-option warnings appear before values in all three chart-type field groups, all three chart case groups and all 13 chart-type error sections. Every blank error has an adjacent diagnostic warning, and the summary total is explicitly gold-relative. The Markdown bin-header delimiter issue found during review was corrected. Package versions, model revision, request hashes, runtime caps, thread and batch settings agree with recorded metadata.

The supplementary model/runtime references are clearly labeled as post-computation documentation, outside the unchanged source lock. The supplied model and joint-head configurations match their public reference-manifest sizes and hashes; all manifest entries use the recorded model revision. Frozen package lists contain package versions rather than local installation locations. Model weights are not redistributed.

No private execution locations, host identifiers, process identifiers or private omission lineage were found in the reviewed text artifacts. Compiled Python caches are excluded from the public deliverable. This review did not reacquire source image pixels, independently relabel images, reload model weights, or reproduce original inference. Recorded image/blank gold caveats, AI-authored labels, intentional sampling, dependent families and CPU-NF4 limitations remain explicit.

## Recheck

Use `PYTHONDONTWRITEBYTECODE=1` when running the supplied tests and audit scripts. `audit/recompute.py` recomputes from original sources; `audit/audit_reports.py` checks report values and context. `scripts/verify_artifact.py` verifies the final complete file set and byte hashes without model inference. Rebuilding or modifying any file requires a fresh integrity-manifest verification before release.
