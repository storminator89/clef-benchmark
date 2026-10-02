# Jev frozen comparison: independent audit of the halted first run

## Outcome

The retained evidence is internally consistent and independently reproducible. **The planned 974-case run did not complete.** It stopped after 180 validated cases and one rejected HTTP-200 response; 793 cases were never attempted. No retry or extra probe request occurred.

- [Manual run 37056885572](https://github.com/storminator89/clef-benchmark/actions/runs/37056885572), first attempt, 2 October 2026
- Collector interval: 19:52:12.969–19:55:23.050 UTC
- Reviewed code pin: `851a2b649826f47d7a1fe8aad2bf06a0590754fd`
- Workflow commit: `e50f98a21244506f7d69dd4e3b50dff0f074522a`
- Frozen manifest SHA-256: `c41b9b4308c692b64dc85c05d279c62faf74f7d24034a1e4ffaf651ec27d2386`
- Hosted model ID in every accepted response: `jev-1.13.0`; an immutable serving-weight hash is unavailable
- Archived Clef baseline: `Cloudflare/clef-flash`, revision `17f0b0ad64efb65d273590632833508766b2aae6`, CPU NF4 backbone with original BF16 decision head/output embeddings

This audit examined the supplied frozen source and ten sanitized artifact files offline. It did not contact the provider, inspect workflow logs, run a model, change the collector, resume the run or dispatch another run. Run/workflow commit identity was supplied with artifact acquisition; the audit independently verified the frozen local source hashes and retained evidence.

## Coverage and exact-case results

Exact-case correctness requires every native field to match the frozen gold label.

| Cohort | Valid Jev cases | Jev exact correct | Clef exact correct on the same cases | Status |
|---|---:|---:|---:|---|
| Minimal pairs | 48/48 | 47/48 (97.92%) | 39/48 (81.25%) | Complete suite |
| Clarification | 72/72 | 71/72 (98.61%) | 64/72 (88.89%) | Complete suite |
| Bank support, validated prefix | 60/80 | 57/60 (95.00%) | 51/60 (85.00%) | Partial, ordered prefix |

The bank-support suite has one additional failed response and 19 unattempted cases. Its complete archived Clef result is 68/80, but that denominator must not be presented as a matched comparison against Jev's 57/60. The observed 60-case prefix was determined by frozen order and the failure stop, not a complete sample of the suite.

Original text (180), finance (100), insurance (60), clean72 (72), attack removal (14), multidocument (48), and MASSIVE (300) have **no Jev observations**. Zero-valued “accuracy_all_expected” entries in the frozen machine-readable scorer reflect missing-result accounting, not observed errors or measured model accuracy. No result or ranking is asserted for these suites. MASSIVE's archived Clef baseline also remains pending its final independent audit.

Paired exact-case counts, ordered as both correct / Clef only / Jev only / both wrong:

- Minimal pairs: 39 / 0 / 8 / 1
- Clarification: 64 / 0 / 7 / 1
- Bank-support validated prefix: 49 / 2 / 8 / 1

Within the minimal-pair diagnostics, Jev was correct at both endpoints of all 12 flip pairs and 11 of 12 invariant pairs; Clef was correct at both endpoints of 8 flip and 9 invariant pairs. Jev had no stable-wrong pair; Clef had two. These paired and synthetic observations are dependent, so no independent-sample significance or uncertainty claim is attached.

## What was verified

The final audit passed **19,032 checks with zero detected inconsistencies**. The sole run-level warning is incompleteness.

- All 68 frozen scientific/provenance files and six code/manifest lock entries matched their SHA-256 commitments
- Frozen inventory: 974 requests, 1,362 native questions, ten suites; 674 complete archived Clef baseline cases, plus the pending MASSIVE cohort
- Gold identities, native field names, option labels and baseline validity were checked
- Every retained request-body hash matches the exact original request serialized with only the model ID replaced; source-request hashes, identities and frozen order match
- The reservation/completion ledger is sequential; each prediction and failed record reconciles to exactly one attempt, with no retries, duplicates, missing completions or unaccounted valid responses
- All 420 accepted native fields have the exact option keys, finite bounded probabilities summing within the frozen tolerance, an argmax choice, bounded native confidence, and valid token usage; duplicated retained vectors agree
- All retained prediction and attempt records satisfy their explicit field allowlists
- An independently implemented scorer reproduces partitions, case decisions, per-group probability metrics, special diagnostics and latency summaries
- Running the unchanged frozen scorer offline reproduces all five uploaded scoring files **byte-for-byte**

The auditor itself was exercised with five offline tests: complete mock data, a first-gate HTTP failure, reordered records, tampered counters/vector duplication, and duplicate/non-finite JSON rejection. These fixtures are clearly separated from the hosted results and are not observations.

Response SHA-256 values agree between prediction and ledger records. Raw response bodies were deliberately not retained, so their bytes cannot now be rehashed or independently revalidated beyond the sanitized native fields. Request hashes demonstrate consistency with the reviewed collector's exact intended payload; they are not an independent packet capture.

## Why it stopped

Attempt 181, `bank_support80/bank_access_tan_01`, received HTTP 200 in approximately 0.1206 seconds, then was classified `invalid_response_or_billing`. Its recorded response SHA-256 is `172e974af58c60baa0913544373987706006dc6bb81b94877a5d99bbc6834d45`.

The response body and the specific validation exception were intentionally discarded. Consequently, the failing clause **cannot be identified from retained evidence**. Possible static failure classes include invalid response JSON, a model/answer/primitive mismatch, a probability-vector or argmax failure, an invalid confidence value, or missing/invalid/excess-capacity usage. HTTP 200 is evidenced; this is not a demonstrated network failure, nor an observed wrong answer.

The failed source request uses exactly the same three-question schema as all other bank-support requests, and its transformed JSON body is 5,624 UTF-8 bytes. There is no new input schema at this boundary. That observation does not establish why the provider response failed.

All 1,860 retained Jev probability values lie on a 0.01 grid. Coarse emitted probabilities make the collector's strict sum tolerance one possible issue to investigate in a separately reviewed future diagnostic design; the discarded response prevents confirming that explanation. No distribution was normalized, repaired or substituted in this audit.

The initial connection gate succeeded and reused the first frozen case. Its stricter error mapping did not cause the stop at attempt 181. More generally, a failed first gate would map HTTP/contract errors to a generic transport error, so its own safe status must be consulted before labeling such a failure.

## Error nuance and probability interpretation

The five validated Jev exact-case errors are interpretable against the frozen rules:

1. `pair_limit_order_price_step_a`: asked for a missing trading-window fact even though the failed price-step condition already makes the conjunction false. Clef made the same error
2. `clarify_statement_download_02`: correctly chose to ask which account statement was meant, but simultaneously returned a definite “yes” despite one possible account being closed. This is a cross-field inconsistency, not a failure to recognize target ambiguity
3. `bank_transfers_07`: requested clarification for a general “where is the scheduled-transfer function?” question whose gold next step is guidance
4. `bank_transfers_02`: chose security handoff for an explicitly self-authorized transfer to the wrong recipient, where the synthetic policy requires specialist review. Clef was correct on this case
5. `bank_transfers_06`: treated an uncertain, possibly unsent duplicate transfer as urgent; the synthetic rule requires an already-sent transfer for that priority. Clef made the same priority error

On the same 60 validated bank cases, field correctness is Jev versus Clef: intent 60/60 versus 57/60; priority 59/60 versus 57/60; next step 58/60 versus 57/60. The supplemental matched-prefix file recomputes each field's probability metrics on those same identities. The original frozen field-metric file retains Clef's 80-case denominator and Jev's 60-case denominator and must be interpreted accordingly.

“Unrounded” in the retained Jev data means **unchanged from the API**. It does not establish access to higher-precision probabilities or logits. Native confidence differs by as much as 0.02 from the documented formula recomputed from emitted probabilities. The cause is not established; confidence was kept separately, and shared risk thresholds use selected-option probability. No observed gold label has zero probability, so the observed group NLLs are finite. ECE, Brier, NLL and coverage/risk remain separated by suite, split, category, field and option set; none is pooled across suites.

## Budget and limits

The ledger reserves 181 attempts × USD 0.002752512 = **USD 0.498204672**, within the USD 3 local guard. The 180 accepted responses report **229,691 input tokens**, corresponding to **USD 0.009647022** at the frozen dated rate of USD 0.042 per million input tokens. The rejected response's usage is unknown and its full reservation remains accounted for. These figures are local reservation and known-success arithmetic, not a provider invoice or a provider-enforced spending ceiling.

Jev timings measure hosted HTTP request/body receipt, including transport and queueing. The first case also includes connection-gate validation and status persistence. Clef's historical times measure local CPU forward passes. No model-speed ratio or apples-to-apples latency claim is supported.

This halted single pass supports descriptive results for two completed synthetic suites and one partial prefix. It does not support an overall winner, a complete ten-suite benchmark, training-contamination conclusions, production readiness, or financial/insurance safety claims.
