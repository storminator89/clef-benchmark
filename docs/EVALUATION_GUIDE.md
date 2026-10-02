# Evaluation guide: evidence, limits and the next decision

This guide connects the measured results to an evaluation decision. It does not add model measurements or authorize deployment. For a short German/English overview, see the [project brief](PROJECT_BRIEF.md); for commands and the complete result catalogue, start with the [README](../README.md).

## 1. What question does this project answer?

Can one pinned Clef configuration select the reference options for small, explicitly defined German tasks, and can a reviewer reconstruct its successes and failures?

Clef Lab evaluates the native `choice` interface. It separates an input state, explicit instructions, allowed options, reference labels and predictions. A correct option is correctness under that suite's policy. It does not establish that a real financial action is appropriate, that an insurance claim is covered or that a workflow completed successfully.

The six text suites have different task designs. They are **separate studies**, not six folds of a common benchmark. A separate minimal-pair diagnostic now adds 24 pairs / 48 cases. The image experiment and attack-removal diagnostic remain separate reports. A post-hoc probability analysis reuses completed outputs from these nine source suites, with no new inference. No overall accuracy, model leaderboard or cross-suite improvement claim is defined. The workbench gives the pair diagnostic (`#pairs`) and reliability analysis (`#reliability`) their own views.

## 2. Trace a claim to its evidence

For any reported result, follow this chain:

1. **Definition:** read the suite protocol, label meanings, case count and denominator before its percentage.
2. **Reference:** inspect the input and gold rationale. Determine whether missing information or a conflict is itself a valid outcome.
3. **Freeze:** check the pre-inference manifests and recorded changes. The freeze protects the recorded version; it is not proof that an author's judgment is correct.
4. **Execution:** match the request, model revision, runner and completed metadata. Confirm that gold stayed outside model inputs, all planned IDs are present and truncation was rejected.
5. **Output:** inspect the original selected options and complete probability vectors. UI replay is an archived answer, not a new inference.
6. **Score:** reproduce the suite-specific scorer and independent checks. Examine incorrect cases and safety-relevant slices alongside the aggregate.

The [original method](../benchmark/README.md), [finance method](FINANCE_REPRODUCIBILITY.md), [insurance method](../experiments/insurance/METHODOLOGY.md), [bank report](../experiments/bank-support/REPORT.md), [clarification protocol](../experiments/clarification72/PROTOCOL.md) and [minimal-pair protocol](../experiments/minimal_pairs/PROTOCOL.md) document their own scope and artifacts. A later suite may be motivated by earlier errors; freezing it before its own inference does not make the entire research programme prospectively preregistered. The [reliability protocol](../experiments/probability_reliability/PROTOCOL.md) was locked before recomputation but after the original results existed and were available to the authors: its status is explicitly post-hoc and descriptive.

### Who made the data?

These are deliberately constructed, AI-authored synthetic cases and fictional operational rules. Separate AI reviewers checked labels and wording before the corresponding runs; scoring was also checked independently. Neither process is an external human expert panel, blinded human annotation or customer validation. Two AI reviews can share the same blind spots.

New wording is not proof of training-data independence. Familiar patterns may resemble model training material, and a published benchmark may subsequently enter training or tuning data. A future comparative study needs a fresh protected holdout.

## 3. Findings that change an evaluation decision

| Observed result | Practical interpretation | Evidence |
|---|---|---|
| Bank support: 228/240 correct fields, but 68/80 complete cases | Report both field and case accuracy. Three mostly correct fields can still create an incorrect workflow | [Bank report](../experiments/bank-support/REPORT.md) |
| Bank critical cases: no missed critical priority or security handoff in 10 examples, but only 8/10 fully correct | Keep critical subgroups and routing errors visible. Ten cases cannot establish a rare-failure rate | [Bank errors](../experiments/bank-support/ERRORS.md) |
| Always predicting `routine` gives 64/80 for bank priority | A high aggregate on an imbalanced field needs a simple reference baseline and error-specific denominators | [Bank report](../experiments/bank-support/REPORT.md) |
| Insurance: 58/60 evidence selections correct; eight of nine wrong decisions still select the right evidence | A plausible citation or evidence choice cannot certify the decision. These are offered evidence sets, not free retrieval or generated legal reasoning | [Insurance report](../experiments/insurance/REPORT.md) |
| Finance: three of four German errors miss a necessary clarification; two wrong choices exceed 92% model probability | A confidence cutoff alone is not an established safeguard. Attack-marked errors without matched clean controls do not isolate an attack's cause | [Finance findings](FINANCE_FINDINGS.md) |
| Clarification: 64/72 fully correct; 4/36 required clarifications missed, 2/36 unnecessary, 1/36 wrong kind | Evaluate both unsafe commitment and unnecessary deferral. Always asking would also fail the task | [Clarification report](../experiments/clarification72/REPORT.md) |
| Clarification: 72/72 structurally valid, but three inconsistent field pairs | Schema validation and semantic consistency are different gates. Raw outputs were not repaired to improve the score | [All clarification errors](../experiments/clarification72/ERRORS.md) |
| Minimal pairs: 39/48 complete cases; 17/24 pairs both correct | A pair is correct only when both fields are correct at both endpoints | [Pair report](../experiments/minimal_pairs/REPORT.md) |
| Minimal pairs: all 12 flip outputs changed, but only 8/12 complete transitions were correct | Sensitivity to an edit does not prove the intended transition; four changes remained incorrect | [Pair protocol and metrics](../experiments/minimal_pairs/PROTOCOL.md) |
| Minimal pairs: 11/12 invariant outputs stable, including two stable-wrong pairs; 9/12 both correct; 1/12 unjustified change | Invariance and correctness answer different questions. Preserve stable errors in the review | [All pair errors](../experiments/minimal_pairs/ERRORS.md) |
| Minimal-pair field scores ≥0.90: 4/36 determinations and 2/7 actions incorrect | The action errors are two dependent endpoints of one invariant pair; the determination errors occupy three pairs. This is not an estimated production risk | [Reliability report](../experiments/probability_reliability/REPORT_DE.md) |

### Read the denominator before interpreting a high score

The later analysis does not contradict the clarification report's five concrete answers. It asks additional, distinct questions:

| Unit and selection at ≥0.90 | Clarification result | Meaning |
|---|---:|---|
| Selected determination field | 0/49 incorrect; 49/72 selected | Includes `unresolved`; says nothing by itself about the action field |
| Selected action field | 0/25 incorrect; 25/72 selected | Includes clarification actions; says nothing by itself about determination |
| Every required field selected, using the minimum field score | 0/21 inexact cases; 21/72 selected | Whole-case score heuristic, including clarification/unresolved outputs |
| Same minimum gate, additionally `answer` and `yes`/`no` | 0/5 wrong concrete answers; 5/72 selected | The earlier report's narrower concrete-only subset |

At the same minimum-score gate the pair suite retains **7/48 whole cases, two inexact**. A minimum is not a calibrated joint correctness probability, and marginal probabilities are not multiplied. The recorded zero-error clarification subsets do not validate safety. At 0.95 no clarification concrete answers qualify; an empty selection has an undefined error rate, not zero risk. [All field thresholds](../experiments/probability_reliability/FIELD_DETAILS.md) and [separate whole-case heuristics](../experiments/probability_reliability/CASE_HEURISTICS.md) retain their own numerators, selected counts and coverage denominators.

### What the reliability analysis actually measures

The **nine source suites, 716 recorded requests and 1,186 field observations are inventory counts only**. The analysis keeps 78 field groups and 64 case groups separate. It never pools fields or suites, even when option IDs match. Older multi-task sources are partitioned by task and language, attack controls also by condition, and image records by kind, language and image/blank condition. All original predictions and gold labels are retained.

The protocol fixes thresholds at 0.50, 0.70, 0.80, 0.90, 0.95 and 0.99. Each field group reports class-summed multiclass Brier (0–2 convention), NLL using the natural logarithm, ten equal-width score bins, ECE and error/coverage counts. NLL would be infinite at zero gold probability rather than clipped. Empty-bin statistics and empty-selection risk remain undefined. These descriptive measures do not establish a calibrated model or justify selecting a production threshold from the same observations. No fitting, new inference, relabeling or threshold optimization was performed.

**Keep the image limitations beside the image numbers.** The documented `bar_line`/`vbar2` chart-type descriptions overlap, so a frozen-gold mismatch need not establish a uniquely validated visual-recognition error. Blank controls keep the original-image gold while removing the original content; their mismatches are diagnostic, not ordinary answerable-image errors. The 50 original image files are not bundled, and this reanalysis did not reacquire pixels, relabel images or rerun vision inference. Invoice tax-footnote labels refer to the printed footnote and amount bands to the signed total. Insurance evidence slots are likewise case-local offered clause sets, not stable semantic classes. See the [source inventory](../experiments/probability_reliability/SOURCE_INVENTORY.json) and locally qualified [field details](../experiments/probability_reliability/FIELD_DETAILS.md).

### Multi-document precedence

The additional 48-case study scores native source and determination fields separately: **42/48 source choices**, **24/48 determinations**, **24/48 complete cases**. Eight of twelve required clarifications are missed; eight of 36 answerable cases are unnecessarily unresolved. The nine same-answer ambiguous-source controls explicitly permit `not_unique` with a definite answer; six are fully correct. All 24 errors and 15 case-defined inconsistent field pairs remain recorded.

Twelve families and 16 cross-domain templates create dependence. Balanced IDs/positions do not replace a matched order-swap intervention, which was not run. This finite-set test chooses a complete fictional rule; it does not compose clauses or interpret actual contracts. [Report](../experiments/multidoc48/REPORT.md)

The [Jev preparation package](JEV_PREPARATION.md) remains frozen. Its separately reviewed [manual workflow](JEV_EXECUTION.md) awaits an explicit start. Mock checks, frozen requests and a published workflow do not establish hosted-model accuracy, latency, billing or a valid key. No API run or ranking is included.

## 4. Uncertainty and comparisons

- **Sampling:** all percentages describe their fixed constructed sets. They do not estimate a real bank's ticket mix or a client's error rate.
- **Dependence:** insurance has five cases per document; clarification has related cases within twelve rule families; minimal pairs have two dependent endpoints and reuse the clarification schema and generic rule patterns. Fields within a case, language variants, image/blank controls and related templates are not independent observations. Attack-ablation sources reuse seven finance scenarios; high-score repeats are not new independent incidents. Do not attach naive binomial confidence intervals to pooled decisions. A future study should define the sampling unit and use a design-appropriate uncertainty analysis.
- **Language:** compare only the same paired scenarios. The original study has 30 selected pairs; finance has 20. A whole German test versus selected English controls is not a language comparison. Class coverage also limits finance's all-label English macro-F1.
- **Model scores:** probabilities are observable model outputs, not validated real-world error probabilities. Fixed-bin ECE is sensitive to group and bin size; Brier/NLL also depend on the option set and class mix. Different scores across suites are not a model ranking. Any threshold selected on these observations would require a separate validation set, untouched test set and explicit coverage/error tradeoff.
- **Repeated measurement:** a successful one-case repeatability probe does not demonstrate multi-run stability. Hash-identical derived files demonstrate artifact reproducibility, not bitwise model outputs on every device.
- **Latency:** CPU forward time excludes loading and other separately recorded stages. It is not an API service-level objective. The bank median of 40.88 seconds and clarification median of 20.77 seconds use different inputs; their difference is not a causal optimization result.
- **Value:** no measured customer satisfaction, staff time saved, total operating cost, ROI, fairness or legal/compliance outcome is reported. Such claims require a purpose-built evaluation.

## 5. What was actually tested?

Evidence is versioned. A later UI, model, installer or schema change needs its own relevant checks; a historical pass does not transfer automatically.

| Layer | Evidence established | Boundary / remaining work |
|---|---|---|
| Recorded model quality | Completed, frozen Flash-9B CPU-NF4 suite outputs with per-case probabilities and separate scores | Synthetic tasks only; no BF16/GPU equivalence, 27B result or representative customer holdout |
| Deterministic scoring and imports | Integrity gates, independent rescoring and byte-identical dataset rebuilds; [validation record](VALIDATION.md) | Software checks do not independently validate domain truth |
| Minimal-pair diagnostic | 48 archived native predictions, unchanged pre-inference freeze and separate final score/integrity audit; [report](../experiments/minimal_pairs/REPORT.md) | 24 authored pairs, dependent endpoints and reused rule patterns; no representative or human-expert validation |
| Probability reliability | Post-hoc recomputation from locked original sources and independently implemented metric checks; [review](../experiments/probability_reliability/audit/INDEPENDENT_REVIEW.md) | No fresh inference, fitted calibration, independent population sample or production threshold validation; local image/gold caveats remain |
| Public UI at source commit `3b5b374` | Eight real Chrome check groups, 17 source/hash-verified PNGs, desktop plus 320/390-CSS-pixel states, light/dark; [publication evidence](../qa/browser_gallery_publication.json) | Five-suite capture; later clarification UI is outside it. No physical-device, cross-browser or screenreader certification |
| Clarification72 UI at source commit `ce636994` | [Real Chrome capture](https://github.com/storminator89/clef-benchmark/actions/runs/37029702253): ten check groups and 21 hash-verified PNGs; all six suites and 320/390-CSS-pixel clarification panels | Four clarification PNGs visually reviewed; no physical-device, screenreader, cross-browser or new inference claim |
| Pair and reliability UI at source commit `a21344f8` | [Real Chrome capture](https://github.com/storminator89/clef-benchmark/actions/runs/37041382266): 12 check groups and 30 hash-verified PNGs; all 78 separate field groups, desktop/320/390px, light/dark and keyboard access to horizontal table columns | Nine diagnostic PNGs visually inspected; no physical-device, screenreader, cross-browser or new inference claim. Historical galleries retain their own sources |
| Concise UI and multidoc source `4289d761` | [Sandboxed Chrome capture](https://github.com/storminator89/clef-benchmark/actions/runs/37048924234): 14 check groups, 34 source/hash-verified PNGs, five selected for publication; seven suites and 320/390px flows | First narrow-title regression corrected and rerun; selected-state visual review, no physical-device or screenreader certification |
| Software release `b084dc17` | [Exact-commit CI passed](https://github.com/storminator89/clef-benchmark/actions/runs/37022682017); recorded 254 Python and 99 JS/DOM tests, three integrity gates; [versioned review](https://github.com/storminator89/clef-benchmark/blob/b084dc17e8e285e0eef20e00af07fae76d371ec2/qa/ui_polish_review.json) | Snapshot counts, not a test count for later releases; mock tests are not real model executions |
| Custom-case live integration | One real local HTTP request, three fields, no gold in request, actual Flash-9B CPU-NF4 load, no truncation; [smoke](../qa/setup_custom_smoke.json) and [completion](../qa/setup_custom_smoke_completion.json) | Existing environment/weights; one smoke, not accuracy evidence or a load test. Browser capture ran without inference |
| New setup lifecycle | Planning, validation and simulated installer-step tests; [setup contract](AGENT_SETUP.md) | No demonstrated fresh end-to-end installation with the new installer |
| Other hardware/model profiles | Documented selection, resource estimates and guards; [hardware guide](HARDWARE.md) | CPU-BF16, AMD ROCm and every 27B combination lack full hardware/model validation here |
| Local data handling | Explicit local execution, gold separation, no automatic publication and documented input/export behaviour; [custom-case contract](CUSTOM_CASES.md) | Not a security certification, retention policy or approval to process real sensitive data; gitignore is not encryption |
| Operational adoption | A reviewable experimental workflow | No client deployment, human expert gold validation, production SLA, ROI study or compliance certification |

Use the current README and exact-commit CI for later integration status. Additional model-free tests do not retrospectively change frozen benchmark measurements.

## 6. A responsible next step for a financial-services use case

The following is a **proposed supervised evaluation plan**, not functionality already implemented or a deployment recommendation. Continue using synthetic data in this public demonstration. Real sensitive information would require a separately approved environment and data-governance process.

### Candidate scope and human ownership

| Candidate for an offline or shadow-mode study | Model's bounded role | Human-owned boundary |
|---|---|---|
| Incoming service-ticket routing | Suggest an intent and next review queue under an agreed policy | Reviewer confirms the route; the demo sends nothing to a real queue |
| Completeness and clarification checks | Suggest whether a fact, target or contradiction needs resolution | Reviewer decides the question and customer response; no collection of credentials or secret codes |
| Document-review assistance | Compare a claim with supplied synthetic clauses and offered evidence | Qualified reviewer interprets real terms and makes any consequential determination |
| Security-sensitive support triage | Flag a case for an established human security process | No automated card block, account action, transfer, eligibility, refund or investment decision |

### Before measuring

Agree a single decision contract: input boundary, allowable outputs, rule owner, harmful errors and who can override a suggestion. Have domain experts create and adjudicate reference labels without seeing model predictions. Keep separate development and untouched evaluation sets; split related customers, documents or rule families together to avoid leakage. Define anticipated missing/ambiguous inputs and preserve them in the test.

Predefine acceptance criteria with the accountable business and risk owners. There is no universal safe accuracy target in this repository. Report counts and denominators for complete cases, required handoffs missed, unnecessary handoffs, unresolved/ambiguous cases, contradictions and execution failures. Include simple majority/rule baselines and the existing human workflow where legitimately measurable. Evaluate decision quality and review workload together.

For a paired extension, have domain experts define the exact relevant edit, expected transition and outcome-preserving controls before inference. Keep both members and related rule families in the same data split. Score complete endpoints, both-correct pairs, correct full transitions, unjustified changes and stable-wrong pairs; never count an arbitrary output change as success. Reserve new situations for the untouched evaluation rather than repeating only published failures.

For a score-based review policy, first define the decision unit and which errors require human review. Develop any calibration or threshold choice on separate data, freeze it, then measure coverage, complete-case errors, harmful-error misses and reviewer workload on the untouched set. Include missing/invalid outputs and failure handling. Human domain adjudication, representative sampling and the exact deployment configuration are new evidence requirements, not properties supplied by this public reanalysis. [German/English pair and reliability briefing](PAIRS_RELIABILITY.md)

### Before any assisted pilot

1. Run in shadow mode with **no downstream actions**. Preserve all errors, not only successful examples.
2. Test a separately defined review policy for ambiguity, contradictions, unsupported inputs and failures. Deterministic safeguards, if added, need separate before/after results; do not silently rewrite the native benchmark outputs.
3. Measure whether reviewers detect model mistakes, how long review takes and how often they override suggestions. A human-in-the-loop label alone is not evidence that the loop works.
4. Validate the exact chosen model, precision and hardware. Report cold-start, end-to-end latency, concurrency limits, memory and failure recovery separately from pure forward time.
5. Require an accountable owner, explicit release criteria, a rollback path and a new evaluation after policy/model changes. Define monitoring with appropriate privacy and retention limits before collecting operational records.

Until those conditions have their own evidence, the defensible conclusion remains: **inspectable experimental results and a reusable evaluation workflow; real-world suitability still to be established.**
