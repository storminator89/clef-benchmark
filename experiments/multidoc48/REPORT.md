# German multi-document precedence: finite-set results

## Main results

- Both fields exact: 24/48 (50.0%)
- Source choice: 42/48 (87.5%)
- Determination: 24/48 (50.0%)
- Correct field decisions: 66/96 (68.8%)

## Source selection and clarification

- unique_source_correct: 21/27 (77.8%)
- wrong_concrete_source: 4/27 (14.8%)
- unnecessary_source_uncertainty: 2/27 (7.4%)
- ambiguous_source_correct: 21/21 (100.0%)
- invented_unique_source: 0/21 (0.0%)
- same_answer_ambiguous_source_exact: 6/9 (66.7%)
- missed: 8/12 (66.7%)
- excess: 8/36 (22.2%)
- wrong_definite_answer_on_answerable: 8/36 (22.2%)
- invalid_on_required: 0/12 (0.0%)
- invalid_on_answerable: 0/36 (0.0%)
- same_answer_control_excess: 3/9 (33.3%)

- Field-pair inconsistencies: 15/48 (31.2%)

This inconsistency rule allows an uncertain source with a definite answer whenever all plausible sources agree. The nine controls are explicitly scored separately. A wrong source is not evidence of a unique psychological failure mechanism.

## Domain and precedence strata

- domain / insurance: exact 10/16 (62.5%); source 15/16 (93.8%); determination 10/16 (62.5%); invalid/missing 0
- domain / banking: exact 7/16 (43.8%); source 13/16 (81.2%); determination 7/16 (43.8%); invalid/missing 0
- domain / finance: exact 7/16 (43.8%); source 14/16 (87.5%); determination 7/16 (43.8%); invalid/missing 0
- stratum / scope: exact 5/12 (41.7%); source 12/12 (100.0%); determination 5/12 (41.7%); invalid/missing 0
- stratum / unresolved: exact 6/12 (50.0%); source 12/12 (100.0%); determination 6/12 (50.0%); invalid/missing 0
- stratum / effective_date: exact 6/12 (50.0%); source 9/12 (75.0%); determination 6/12 (50.0%); invalid/missing 0
- stratum / authority: exact 7/12 (58.3%); source 9/12 (75.0%); determination 7/12 (58.3%); invalid/missing 0

## Execution and integrity

- Recorded 48/48; valid 48/48; missing 0; invalid existing 0
- Input tokens: 888–953; exact full/cap equality enforced before and during inference
- Forward time: median 27.319 s; interpolated p95 32.417 s; sum 1313.246 s
- Maximum observed scored-case process RSS: 6055006208 bytes
- Native load time: 57.31906165699911 s; run status: completed
- Frozen before inference: 2026-10-02T16:07:28.638145+00:00; native run started: 2026-10-02T16:09:16.783583+00:00
- Model revision: 17f0b0ad64efb65d273590632833508766b2aae6
- CPU NF4 backbone; original BF16 joint head and output embeddings; six threads; batch one; cap2048
- Unrelated warmup and post-run first-case probe excluded from metrics
- Every error and all native option scores remain available in results/errors.jsonl and results/predictions.jsonl

## Interpretation limits

These are 48 purposefully AI-authored and separately AI-reviewed cases, not human-expert validation or a representative customer sample. Sixteen templates are reused across three domains; twelve domain×stratum families are not independent clusters. Domain/template/family strata remain in the machine-readable summary. No population interval or significance estimate is claimed.

The task selects one complete rule and a bounded outcome. It does not test composing partial clauses, generated German answer quality, real contractual interpretation or customer actions. Eighteen yes, eighteen no and twelve material clarification cases are deliberately balanced; nine more have ambiguous source but a definite answer. Document IDs and positions are balanced across unique-source outcomes; no matched order-swap intervention occurred, so causal order robustness is not established.

Marginal native option scores are not calibrated or joint probabilities. This is an experimental CPU NF4 result, without GPU/native-precision claims. Different earlier schemas and datasets are not pooled or treated as a before/after model improvement. Private environment diagnostics are omitted from the public artifact.
