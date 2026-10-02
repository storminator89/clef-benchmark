# Independent review of completed clarification results

## Audit verdict

**PASS:** completed metadata and actual shell exit 0 verified; 72 unique ordered predictions; all 72 technically valid; all frozen file hashes unchanged; model-request hash, tokenizer preflight counts and per-case token counts agree. No truncation (689–757 tokens). Independently recomputed metrics, full error records and error IDs agree with summary.json and errors.jsonl. A separate exact comparison also confirms all 72 case_scores.jsonl records equal the independent reconstruction. No prediction, frozen data, protocol, primary scorer, or pre-inference audit was modified.

The checker was prepared and its 15 synthetic tests passed before actual predictions were inspected. It imports no primary scorer or model library. It independently pins the pre-result freeze-manifest hash. The reviewer is AI, not a human expert, and previously performed the gold-aware pre-inference review. The original signed pre-inference review remains immutable; this is a separate post-result review.

## Headline findings

- Joint exactness: 64/72 (88.9%); action 65/72 (90.3%); determination 66/72 (91.7%). The descriptive 131/144 field decisions are dependent, not 144 independent cases.
- Required clarification: missed 4/36 (11.1%); one additional case asked the wrong kind. All four missed actions occur among ambiguous-target examples.
- Unnecessary clarification: 2/36 answerable cases (5.6%).
- Three inconsistent action/determination pairs.
- Four risky concrete answers: 4/72 overall (5.6%) and 4/37 concrete model answers (10.8%). Three are unsupported concrete determinations for unspecified targets; one is a false yes despite a definitively failed condition. This set differs from the four missed-clarification cases because one missed clarification still returned unresolved.
- All eight joint errors fall in two strata: ambiguous_target 7/12 correct; sufficient_despite_omission 9/12 correct. The other four strata each score 12/12.
- Within sufficient_despite_omission, all six positive cases with irrelevant missing details pass; only three of six negative cases requiring a failed-condition shortcut pass. This is a descriptive subgroup observation, not a separately pre-registered inferential comparison.

## Marginal-score reporting

Zero risky concrete errors meet BOTH selected-score thresholds. Report the coverage with that observation:

- At 0.80: 0/23 errors among qualifying concrete answers (23/37 concrete answers covered).
- At 0.90: 0/5 (5/37 covered).
- At 0.95: no qualifying concrete answers; error rate is undefined, not 0%.

This does not establish calibration, low real-world risk, or a validated confidence-based release rule. Scores are uncalibrated marginals rather than a joint correctness probability. A wrong action can have a score above 0.80 while the other field is below it; therefore do not paraphrase the both-field result as an absence of all high-scored wrong decisions. Do not select a new threshold after seeing this test and claim held-out validation.

## Every wrong case

### clarify_order_cancellation_02

Gold: ask_target / unresolved. Prediction: ask_fact / no. Selected marginal scores: action 0.47160098; determination 0.48461920.

The two identified orders have different outcomes. ask_fact is the wrong clarification kind, and pairing any clarification action with no is inconsistent under the specified schema. This is not a risky concrete answer under the frozen metric because the selected action was not answer.

### clarify_savings_fee_02

Gold: ask_target / unresolved. Prediction: answer / yes. Selected marginal scores: action 0.70225608; determination 0.61716157.

The two plans use different funds and have opposite outcomes; the target remains unspecified. A concrete yes is unsupported.

### clarify_statement_download_02

Gold: ask_target / unresolved. Prediction: answer / yes. Selected marginal scores: action 0.86421001; determination 0.74171108.

The two statements belong to open versus closed accounts and have opposite outcomes; the target remains unspecified. A concrete yes is unsupported. Its action score alone is 0.8642, but the selected determination score is 0.7417, so the fixed both-score 0.80 criterion is not met.

### clarify_bicycle_theft_02

Gold: ask_target / unresolved. Prediction: answer / no. Selected marginal scores: action 0.57672417; determination 0.62016672.

The attached versus unattached bicycles have opposite outcomes; the target remains unspecified. A concrete no is unsupported.

### clarify_device_damage_02

Gold: ask_target / unresolved. Prediction: answer / unresolved. Selected marginal scores: action 0.80517209; determination 0.51044625.

The in-contract versus after-contract cases have opposite outcomes. unresolved is the correct determination, but answer is the wrong action, producing an inconsistent pair. Count this as a missed clarification action, not a concrete risky yes/no.

### clarify_savings_fee_06

Gold: answer / no. Prediction: ask_fact / no. Selected marginal scores: action 0.64023364; determination 0.60259771.

Kiesel is excluded regardless of the unknown rate. no is correct, but asking for a fact is unnecessary and inconsistent with this determined conclusion under the prescribed schema.

### clarify_depot_statement_fee_06

Gold: answer / no. Prediction: ask_fact / unresolved. Selected marginal scores: action 0.85348195; determination 0.62319726.

Paper delivery is explicitly disqualifying regardless of the unknown account age. Both the extra factual question and unresolved determination are wrong.

### clarify_giro_fee_06

Gold: answer / no. Prediction: answer / yes. Selected marginal scores: action 0.61863303; determination 0.47741711.

No salary was received, and the rule explicitly excludes other incoming payments. The result must be no regardless of mailbox status. The concrete yes is a rule-application error. Choices alone do not establish its internal cause.

## Interpretation limits

The error labels remain defensible under the frozen fictional rules; there is no reason to revise gold after observing these predictions. These are small, purposefully balanced, overtly signposted, related two-conjunct scenarios. No population generalization, domain competence claim, statistical significance claim, or generated-German-question quality claim follows. In particular, do not conclude that the model always selects the first listed target: the concrete target errors include both yes and no.

Performance is for the specified CPU NF4 backbone with the original BF16 head/output embeddings, not a stock BF16/GPU run. The single repeatability probe reproduces only the first case, including its wrong prediction; it does not establish full-suite or cross-platform repeatability. All 72 measured forward latencies are retained: median 20.775 seconds, p95 25.304 seconds, total 1511.017 seconds. These exclude loading, warmup and the repeatability probe. Distinguish maximum sampled per-prediction RSS (6,152,990,720 bytes) from process maximum RSS reported in metadata (6,681,849,856 bytes).

## Verified artifacts

- `audit/independent_result_check.json`: `59b8a99d78df5336ff0f132acd943a4d5631cd0b247ece83b900f42ee1622d64`
- `audit/independent_checker_self_tests.json`: `5b3969ebf40de60135a0e67f9d3a9013d6d5ffe299ea1f15b359a0a4fdf4bf0b`
- `results/predictions.jsonl`: `94256dd1931c19e73404bd9f84cc48f2593799a8622d685a90748f871ef769f4`
- `results/summary.json`: `cd2fd9ac42b30e15c5227e318f56e88db747e19f8469a6f91e79dc455665e0a3`
- `results/errors.jsonl`: `3c0d02c56583babeff33f589ab75c1d0364e61bc515e3e97788090ca0deb72e2`
- `results/case_scores.jsonl`: `e9b42c1bd430fd5225a03e7d366fc9baf876d3e80911181cefd14138cfe82464`
- `results/predictions.metadata.json`: `af2f331c590c87209b0e7142316850cc19139ba9b611a7ce94f4b5bec3b12361`
- `results/run_outcome.json`: `e4be90c57d39152a9687045e769ce74dcca09ad4b011aede8658931c5fcfcb9d`
- `freeze_manifest.json`: `8eeb30bec0e06776298509328323e6fa2d7849e0d2ff75d03eb922edcf692f6a`
- `scripts/independent_result_check.py`: `c28786b53d7abee67c999e1e136482c4fa0ac430cb0d89e93c160da88c4c1707`
