# Final pre-inference review

## Decision

**Approved for freeze: all 24 final pairs and all 48 gold endpoints pass.** Every final case was reread after the prospective corrections. All bounded-span, unchanged-component, metadata, request construction, case/pair identity, schema-order, and gold checks pass. The reviewer did not load a model or observe benchmark outputs. Prediction files are absent at approval.

This is a separate AI review of AI-authored data, with author gold and rationales visible. Manual rule application is recorded per endpoint; the review is not gold-blind, human-expert validation, or an independent expert holdout. The exact prior two-field schema, option IDs, and generic rule templates are reused and disclosed. New scenario text does not establish training-data novelty.

## Final data assessment

`pre_inference_review.jsonl` contains all 24 pair IDs, all 48 case IDs, independently derived gold objects, per-case reasons, changed-span and unchanged-component assessments, ambiguity/leakage decisions, mechanical results, and exact SHA256 hashes of each final dataset file. Each verdict is pass. The accompanying summary and final snapshot retain the exact inspected bytes.

The final set has 12 flips (six yes/no reversals and six answer/clarify transitions) and 12 invariants (six irrelevant-text, three within-region fact, and three short-circuit controls). There are eight pairs per domain. Final determination gold counts are 19 yes, 17 no, and 12 unresolved. Action counts remain 36 answer and four for each clarification action.

All pairs change one documented contiguous span. The rule, question, schema/option order, prefix, and suffix remain identical between endpoints. Character offsets are zero-based Unicode-character offsets. Reconstructed messages, unchanged-text hashes, case/file ordering, and duplicated gold copies match exactly. No case belongs to multiple pairs and none is missing.

Closed-rule interpretations are sound: threshold inclusivity is explicit; unknown is distinct from confirmed absence; ambiguous targets have differing candidate results; equal-rank conflicts have no unstated precedence; and a false necessary conjunct makes an unrelated unknown irrelevant. Irrelevant text is explicitly identified by the supplied rule. The base-tariff applicability correction removes the only material alternate reading found in round 1.

## Prospective corrections and provenance

The original round-1 snapshot and its 23-pass/1-correction verdict remain intact. Comparison of original and final pair records found exactly the five pair IDs in `correction_history.json`, and its original-snapshot hash matches the retained file:

1. Rebalancing: explicitly establish Basistarif in both unchanged prefixes; retain the 30→29 and yes→no gold
2. Towing: equal-rank 25/12 reports become 25/25 by changing only the second report; conflict→no
3. Equipment: certificate present becomes unknown; yes→ask_fact
4. Baggage: weight 19→20 stays within the inclusive cap; yes/yes
5. Voucher: age 89→90 stays within the inclusive cap; yes/yes

The latter four are declared pre-inference coverage refinements, not repairs justified by observed scores. No model outputs were consulted. All final endpoints were separately rederived after these changes.

## Scorer and metric review

Static review covered the final primary scorer, dataset validator, synthetic self-tests, protocol, source disclosure, dataset builder, token preflight, runtime verifier, RAM guard, freeze script, reproduction script, native runner, and the native choice conversion function. The reviewer made no dataset or production-script edits.

The final scorer implements:

- Case exactness /48 and pair both-correct /24 using complete action/determination outputs
- Directional flip success /12 requiring both complete gold endpoints, intentionally identical to both-correct on the flip subset
- Separate wrong-valid and invalid/missing flip-transition counts
- Valid unequal invariant outputs as unjustified change /12, with a separately reported valid-pair conditional denominator
- Invalid/missing invariant pairs as failed invariance, never as stability
- Stable-but-wrong pairs separately from correct stable pairs
- Fixed denominators on missing rows, and rejection rather than arbitrary selection of duplicate/unexpected IDs

Native validation checks complete unrounded option maps, finite normalized numeric probabilities, exact criterion-order argmax tie-breaking, complete native rounded maps equal to round(unrounded, 4), scalar confidence within the explicitly declared 0.00011 tolerance, tokens/cap/truncation, and finite nonnegative telemetry. Booleans are not accepted as numeric evidence. Entire invalid cases receive no correctness credit. The scalar confidence tolerance is intentionally distinct from exact rounded-map validation, matching the protocol.

The author's 24 synthetic tests pass. The reviewer additionally ran **30 separate black-box CLI tests**, comparing metrics with a separately written counting oracle and without importing the primary scorer. All 30 pass. They include no predictions, reversed flip directions, constant outputs, single-field failures, stable wrong invariants, missing endpoints, identically invalid endpoints, duplicate/unexpected IDs, malformed native fields, numeric booleans, rounded-map failures, confidence tolerance, and exact tie behavior. These fixtures are synthetic software tests, not model predictions. The test evidence binds its scorer and dataset hashes.

## Freeze and execution review

The tokenizer-only report is for the final requests SHA256, contains all 48 case IDs, reports exact uncapped-versus-2048-cap token equality, and records lengths from 673 to 730 tokens. No case is truncated. The runtime verification report binds the pinned model/source files, native runner SHA256, and exact package versions and states that no model was loaded. This reviewer inspected the verification code and its recorded evidence; the author performed the full weight-file hashing.

The freeze script validates reviewer approval against the currently present bytes, validates preflight and test status, and unions every approved evidence file into the freeze manifest. This includes the original round-1 snapshot and review generators. The reproduction script verifies that manifest, runner/model hashes, and recorded package versions before executing under the RAM guard. It rejects an existing predictions file. Bash syntax validation passes. The approval file binds all current data, pre-inference scripts, reference runtime files, protocol/source disclosure, review/correction evidence, license evidence, and recorded runtime verification.

Approval is to freeze these exact files, not permission to alter them after observing predictions. A separate post-run integrity/scoring review remains required. No runtime quality or latency result is claimed by this pre-inference review.

## Remaining limits

- This is a small purposive deterministic diagnostic with reused schema/templates, not a representative sample or independent test of broad financial-domain performance
- Pair members are dependent; no independent-case significance claim is supported
- Subtype×domain cells contain one pair, except irrelevant-text cells with two. Clarification transition polarities are improved but not perfectly balanced across three domains
- Within-region invariants now cover both yes/yes and no/no. Short-circuit controls necessarily remain no/no under these conjunctions
- Explicitly declared irrelevance makes the distractor controls relatively easy; it does not test discovery of latent irrelevance
- Stable wrong answers are a genuine possible outcome and must stay visible alongside pair correctness
- Native bounded choices do not measure generated German explanation/question quality. Marginal scores are not calibrated or joint probabilities
- Experimental CPU NF4 results must not be described as stock unquantized or GPU performance

`freeze_approval.json` is the operative exact-file approval. Future post-run helpers and outputs are outside this pre-inference review.
