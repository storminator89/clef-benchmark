# Final 520-case Jev continuation: validation protocol v2

**Recovery revision 2026-10-03:** the collector, auditor and activation code are newly reconstructed and independently reviewed. The original uncommitted code was unavailable after an execution-workspace reset; it is not represented as recovered. The raw seven-file second-run archive and the 520-request plan were recovered byte-for-byte from verified artifacts and uploaded Git blobs.

This preparation is inert until a separately reviewed immutable code commit is activated. It makes no provider request during ordinary CI or offline planning.

## Frozen history and scope

The two stopped manual runs retain 454 attempted cases: 452 strict-valid results and two technical failures, with no retries. Original case 455, `finance100/de_finance_contract_service_005`, is the first new request. Exactly 520 frozen requests remain: finance26, insurance60, clean72, attack14, multidoc48 and MASSIVE300. Every request, source/gold file, archived Clef result and original validator/scorer remains unchanged. Every historical prediction, reservation and diagnostic byte is preserved, including failed cases181 and454. Neither failed case is retried or reconstructed.

The cumulative 454 prior reservations consume USD1.249640448 under the local guard. Existing known-success usage is437597 input tokens, USD0.018379074 at the frozen dated rate. The same USD3, 1024-total-attempt and50-retry ceilings cover all three runs; completing974 initial attempts reserves USD2.680946688, and using all1024 permitted attempts reserves USD2.818572288. This is a local reservation guard, not a provider-enforced account cap or invoice.

## Explicit protocol evolution

The frozen strict validator still defines scored-valid responses, including its local probability-sum tolerance1e-5. This tolerance is not presented as a documented provider guarantee. In v2, the collector checks provider model and billing first and inspects every requested field. Only a response whose sole failure is finite, in-range native probabilities summing outside that tolerance may continue as a quarantined case.

Its main prediction remains `failed`; its allowlisted original native numeric values are retained in `flagged_native.jsonl`, together with each sum/deviation, native choice/confidence, validated usage and request/response digest links. No normalization, rounding, label repair or promotion to valid occurs. Flags are excluded from strict probability and paired-valid scoring. Known-success cost remains strict-success-only; retained flagged usage is disclosed separately. The two historical rejected vectors were discarded and cannot be backfilled.

Wrong model, missing/invalid/excess-capacity billing, malformed JSON, other schema/choice/confidence failures, authentication errors, uncertain transport, unexpected local errors and budget exhaustion halt. Only the original bounded429/529 retry policy applies, never to the first new case, a validation failure or ambiguous transport. New reservations are persisted before transmission. Output reuse, automatic resume and automatic rerun are prohibited.

## Verification and scoring

`python3 scripts/run_jev_final_continuation.py` verifies the exact predecessor and prints the520-case plan without reading credentials or making network calls.

`python3 scripts/audit_jev_final_continuation.py --run OUTPUT` checks historical byte prefixes, request order and hashes, reservations/completions, eligible retries, fatal-stop semantics, strict native values, mandatory quarantined data, diagnostics, connection gate and counters. It rejects unfinished/unsettled reservations. It hashes all six collector artifacts. HTTP body hashes are linkage evidence; discarded raw bodies cannot be rehashed.

The activated template requires that audit before invoking the unchanged frozen scorer. The completed native MASSIVE baseline and its offline overlay are unavailable in this recovery revision, so the frozen MASSIVE baseline remains pending_owner_final_audit. No missing Clef prediction is reconstructed from a score or report. Hosted Jev observations may still be collected for those 300 cases, but a paired MASSIVE comparison remains unavailable. Scoring output stays separate from the immutable initial comparison archive. Missing all-expected zeros indicate coverage accounting; they are not observed model errors. Valid-only results condition on strict-valid observed cases. No pooled probability metric, model-speed ratio or production-safety claim is supported.

## Two-stage activation

Stage A publishes an inert workflow with no credential reference or provider command, plus pinned collector/auditor/template/plan/history and offline tests. The original activation metadata remains historical; current state is in the separate v2 activation record.

Stage B replaces only the current workflow and v2 activation state after StageA's full immutable commit SHA and CI have been verified. The workflow checks out that reviewed SHA, has two default-false manual approvals, a first-attempt/main/repository guard, no push/PR/schedule trigger, and one secret-scoped collection step. Audit and sanitized artifact retention run even after a halt. The repository owner dispatches once after review; never use Re-run jobs or an older793/974 workflow. A subsequent dispatch requires reconciling its ledger and a new explicit plan first.

The sanitized raw workflow artifact is retained for seven days. Download and verify it promptly; the repository archive and a separate preserved delivery remain the durable evidence. Workflow artifacts are not themselves permanent storage.
