# Independent post-inference audit

**Status: PASS**

Separate AI reviewer. Independent metric recomputation; no import or execution of score_results.score; no model inference.

60 cases, 120 fields, 1811 checks; 0 blockers.

## Independently recomputed result

- Decision: 51/60 (85,0 %)
- Evidence: 58/60 (96,7 %)
- Exact case: 50/60 (83,3 %)
- Balanced decision accuracy: 89,1 %
- Decision-majority baseline: 45,0 %
- Evidence-position-majority baseline: 33,3 %
- Uniform random evidence baseline: 20,0 %
- Most-common decision/evidence pair baseline: 18,3 %

## High-confidence errors (raw maximum ≥ 0.9)

- decision: none
- evidence: none

## Verification

Per-case grading, all group totals, baselines, balanced accuracy, latency/token summaries, raw probability normalization, official-order argmax, rounding, metadata, source hashes, no truncation, terminal completion/exit code, and all frozen input hashes were checked independently. Full check records and source hashes are in the adjacent JSON.

## Blockers

None.

## Limits

- No model predictions were read until completion gates passed.
- All frozen files are rehashed; large backbone weight files were not rehashed again by this independent validator. Their pre-run revision/hash manifest is frozen.
- Original joint-head file is independently hashed and its BF16 header and parameter count checked. Runtime output-embedding dtype is supported by the hash-verified runner assertion and successful completion, not a second live-memory read.
- Single-case repeatability probe is not broad determinism evidence.
- AI QA is not external human or insurance/legal expert review.

## Interpretation checks

- 8 of 9 wrong decisions still selected the correct evidence
- Date/version subset: 1/3 (33,3 %) decisions, 3/3 (100,0 %) evidence selections
- True conflicts recognized: 3/3; additional false-conflict predictions: fall_029, fall_050
- No observed ≥90% field error is not evidence that softmax values are calibrated
