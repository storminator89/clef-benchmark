# Pre-inference review, round 1

## Decision

**Data review: 23 pairs pass, 1 pair requires a wording correction before freeze.** All 24 pairs (48 cases) were read and separately checked. All mechanical consistency, bounded-span, unchanged-component, gold-consistency, schema-order, and request-separation checks pass. No model was loaded, run, or queried for this review. Final freeze approval is withheld pending the correction and protocol/scorer review.

This is a separately performed **AI review of an AI-authored set**. The reviewer saw author gold and rationales, so this was not a gold-blind adjudication. It is not a human review, independent expert validation, or untouched holdout. Manual case-by-case rule application was recorded rather than merely checking the author's gold copies against each other.

## Required correction

`pair_rebalance_interval`: the rule's “im Basistarif” limits the rule to the base tariff, but neither message nor the question explicitly establishes that tariff. The intended labels, answer/yes at 30 days and answer/no at 29 days, are sound under the intended tariff scope. A reader could instead treat applicability as an unprovided fact. Add unchanged “Es gilt der Basistarif.” to both messages, or explicitly scope the question to the base tariff. Keep the 30→29 changed span and both gold endpoints. This is a prospective ambiguity fix, not an outcome-driven relabeling.

The round-1 snapshot and original hashes are retained. The author should rebuild and the reviewer should confirm the revised bytes before approving a freeze.

## Pair and case review

The accompanying `pre_inference_review_round1.jsonl` contains one record per pair with both case IDs, separately derived gold for both endpoints, per-case reasoning, the single changed fact/span, each unchanged component, alternate-reading assessment, leakage assessment, mechanical results, a pass/fail verdict, and the complete dataset-file SHA256 map.

All declared changed spans reconstruct both messages using exactly one shared prefix and suffix. Character offsets are zero-based Python Unicode-character offsets, not byte offsets. The supplied prefix/suffix hashes are correct. All pairs keep the rule, question, model-facing question schema and option order, message prefix, and message suffix identical. Facts outside the bounded span remain unchanged.

All 48 gold objects agree across case, gold, and pair files and with independently applied intended rules. There are no duplicate or missing case or pair IDs, and each case belongs to exactly one pair. Case, request, metadata, and gold row orders match. There are 12 flips and 12 invariants, with eight pairs in each of banking, insurance, and finance.

### Interpretation checks

- Inclusive threshold wording supports all six yes/no reversals. The theft case already supplies fully calculated elapsed hours, avoiding clock/date conventions. Decimal price-step arithmetic in the limit-order control is exact and unambiguous
- Unknown, explicitly absent, and present prerequisite statuses are meaningfully distinct. Clarification is required only when the missing fact affects the result
- Ambiguous targets have two explicit candidates with different results. Naming a candidate resolves only the referent. The irrelevant report-title edit explicitly leaves the target unselected
- Conflicting records describe the same target, have equal rank, and do not state a correction or chronological priority. Reconciliation or introducing a conflict changes exactly one reported value
- All short-circuit controls retain an explicitly false necessary condition while changing another fact from unknown to satisfied. Answer/no is therefore required on both sides
- The six irrelevant-text pairs explicitly declare the edited attribute irrelevant and do not change a reference needed by the question

## Leakage and difficulty limits

Requests contain exactly an outer ID and an inner request with model, state, and questions. The state reconstructs only the rule, case message, and question. Expected labels, rationales, pair kind/subtype, side, and transition metadata are not included in the model-facing request. Static inspection of the runner confirms outer IDs are retained for association but not passed to `encode_record`; only state/model/questions enter its input. The shared schema's English option IDs and German definitions are intentional task instructions, not answer-key leakage.

The exact clarification72 two-field schema and generic rule families are reused, as disclosed by the author. The new texts have not been checked against the model's training data; no unseen-training-data claim is possible. Cross-benchmark template familiarity and these highly explicit closed rules limit any generalization claim.

Balance limitations should remain visible in reporting:

- All three clarify→answer flips end in yes; all three answer→clarify flips start from no. The direction and resolved polarity are confounded
- All within-region numeric controls use two failing values above an upper bound; all short-circuit controls have no/no gold. These are useful controls but do not cover every same-region outcome
- Irrelevance is explicitly stated in the rules, so these primarily measure instruction-following under easy irrelevant edits rather than discovery of unstated irrelevance
- There is one pair per scenario family and only 24 pairs. A perfect run would support this narrow deterministic set, not a robust domain-wide performance claim

## Metric expectations for the pending scorer review

- Both endpoints exactly correct: fixed denominator 24 pairs
- Correct directional transition on flip pairs: fixed denominator 12 flips, requiring both complete action/determination objects to match their respective gold endpoints; this is mathematically flip-subset both-correct, not an independent aggregate
- Unjustified output change on invariants: fixed denominator 12 invariants, counting valid endpoint outputs that differ. Invalid pairs must be reported separately and never credited as stability
- Exact case accuracy: fixed denominator 48 cases
- Preserve counts beside rates. Equality of wrong outputs may show invariance but is not correctness; pair exactness must remain visible beside stability

## Provenance

Exact original dataset hashes are in every JSONL review row and `pre_inference_review_round1_summary.json`. `round1_review_snapshot.json` retains the original inspected file contents and hash map. `write_round1_review.py` records the manually specified gold derivations and reproducible mechanical checks. None of these files edits the source dataset.
