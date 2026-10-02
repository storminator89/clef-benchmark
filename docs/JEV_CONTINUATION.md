# Jev: continue only the 793 unattempted cases

The first manual run verified the repository secret and a valid API response. It retained **180 valid cases**, then stopped on one HTTP-200 response that failed the strict response or billing contract. Its exact failed clause is unknown. **793 cases were never sent.** The [independent first-run audit](../execution/jev/first-run-audit/PUBLIC_AUDIT.md) passed 19,032 checks.

This continuation preserves all 181 original prediction records and reservations. It sends only the exact 793 remaining frozen requests, in their original order. **The failed case is not retried; no previously attempted case is resent.** Its technical failure remains in the complete 974-case denominator and remains distinct from a wrong model answer.

## Verified partial results

- Minimal-pair cases: Jev 47/48; Clef 39/48, complete suite
- Clarification cases: Jev 71/72; Clef 64/72, complete suite
- Matched bank-support prefix: Jev 57/60; Clef 51/60; this is only an ordered prefix of 80 cases

Other suites have no Jev result yet. Missing-output zeros in the original scorer are accounting values, not measured errors. The ten-suite comparison remains incomplete. Native probabilities are kept exactly as returned; the first run's values are on a 0.01 grid, not demonstrated high-precision logits. No normalization, repair or substituted billing value is allowed.

## Shared limits

The continuation does **not** start a fresh budget:

- Prior wire attempts: 181, no retries; reserved USD 0.498204672
- Remaining first attempts: 793
- Global ceiling: 1,024 attempts across both runs, including at most 50 retries overall and one per eligible remaining case
- Global local reservation guard: USD 3, based on the dated USD 0.042 per million input-token price
- Prior known-success cost: USD 0.009647022 from 229,691 input tokens; the rejected response's billing is unknown and its full reservation stays charged to the local guard

The first new case must pass the unchanged contract before any later case is sent. Its failure stops immediately without a retry. Later HTTP 429/529 responses may use the original bounded retry allowance. Transport ambiguity or contract/billing failure stops the run. There is no automatic resume or rerun.

These limits govern this reviewed collector, not the provider's account billing. Hosted HTTP latency and local Clef CPU forward timing have different boundaries; do not compute a model-speed ratio. Initial connection-gate overhead is separately disclosed.

## Diagnostics and privacy

A future rejected response records a fixed validation-reason enum and only approved structural facts: known question names, types, counts, Boolean checks and bounded normalization diagnostics. Unknown field names, arbitrary provider strings, raw bodies, headers and exception text are discarded. The validation contract is not relaxed and invalid probabilities are not repaired.

The original first-run files are immutable under [their scientific manifest](../execution/jev/first-run/FILE_SHA256.json). The continuation plan freezes the exact remaining IDs and native request-body digests. All request text, gold labels, original Clef outputs and accepted Jev outputs remain unchanged.

## Manual start

The published manual workflow pins reviewed code commit `5ac03db03857cb3d8945affcd5c769878890f14b`. It is installed and awaiting one explicit start. The workflow requires both default-false approvals, the expected repository and main branch, and the first attempt of a manual dispatch. The secret remains only in the execution step. The repository owner starts the continuation **once** when the published workflow is ready; ordinary pushes and CI never contact the provider.

Concurrency serializes runs but does not prevent a second fresh manual dispatch. The cumulative guard applies to this one continuation plus its fixed predecessor, not to arbitrary future dispatches. Do not click an older initial-run workflow, use Re-run jobs, or launch another continuation. Any further attempt requires reconciling its retained ledger first. Results must be independently audited before reporting the completed comparison. MASSIVE's archived Clef baseline remains pending in the original comparison package until its separate final audit is integrated.
