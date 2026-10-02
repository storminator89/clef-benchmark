# Jev: bounded manual execution

Status: execution code prepared; no live request or secret verification has been recorded yet. The immutable [preparation bundle](../experiments/jev_comparison/README.md) remains unchanged and describes its original preparation state.

The next activation commit installs the reviewed template as a **manual-only** GitHub workflow. It checks out the preceding, reviewed code commit by its full immutable SHA. Pushes, pull requests, schedules, reruns and arbitrary refs cannot execute this comparison.

## One explicit start

The repository owner starts **Jev verified frozen comparison** on `main` once, with both approval boxes selected:

- `approve_public_data`: send the 974 frozen public/synthetic text requests to TypeSafe
- `approve_api_three_usd`: allow one run, at most 1,024 wire attempts, with a local USD 3 reservation guard

The user supplies `JEV_API_KEY` through GitHub Actions repository secrets themselves. The workflow never prints the value, request headers, error bodies or exception text. A missing or malformed secret stops before any API call. The public signal is only `secret_present`.

The **first existing frozen case** is the connection check. It consumes one normal reservation and is retained as the first prediction, without an extra probe or duplicate. Any first-response HTTP, transport, model-version, schema, probability or billing-validation failure stops immediately. A validated response permits the remaining cases in the same process and ledger. Successful authentication alone is not a model-quality result.

## Limits and retained evidence

- Fixed HTTPS endpoint `https://api.typesafe.ai/v1/systemone`; pinned service ID `jev-1.13.0`
- TLS verification, redirects refused, proxy discovery disabled; no alternate endpoint
- 974 initial requests; at most 50 retries globally and one per case, only for later HTTP 429/529 responses; no automatic retry on the initial connection check
- At most 1,024 total wire attempts; reservation persisted before each send; interruptions and unknown billing are not blindly retried
- Standard GitHub runner, read-only repository permission, serial execution, 45-minute timeout
- Explicit sanitized artifact allowlist; one-day artifact retention; no raw environment, headers, secret, provider error body or model weights

The unchanged runner summarizes a failed first connection as a transport/contract halt; `connection_check.json` provides its more specific safe HTTP/validation status. A failed run remains incomplete. **Do not use Re-run jobs or start again without reviewing the retained attempts and remaining budget.**

## Price and data handling

Official documentation was checked on 2026-10-02: [model and price](https://docs.typesafe.ai/models), [API contract](https://docs.typesafe.ai/api), [data handling](https://docs.typesafe.ai/legal). Jev 1.13 is listed at USD 0.042 per million input tokens with free output. The runner conservatively reserves 65,536 input tokens per attempt against the documented 64k capacity; 1,024 such reservations total USD 2.818572288. The USD 3 guard is local and depends on those dated terms; it is **not a provider-enforced account spending cap**. No top-up, subscription or paid runner is configured.

The provider says it does not train on customer requests or responses. Enterprise zero retention is a separate offering; this project does not claim this account has it. Only the already reviewed public/synthetic benchmark text is sent, never private customer documents. The workflow uses an existing account and secret; it does not accept a new agreement or create credentials.

## Interpretation

No Jev score is available until real outputs are retained and independently audited. Existing Clef vectors are unchanged. MASSIVE300's Clef baseline remains pending its owner's final audit; generating Jev outputs cannot make that comparison complete. Native probability vectors, per-field/suite denominators and dependent families stay separate. Hosted HTTP latency cannot be presented as equivalent to Clef CPU forward time. The first case additionally includes connection-gate validation and safe-status persistence in its recorded request duration; this is explicitly marked in the run summary.

The new wrapper's tests use mock responses only. Their successful connection signals are software-test fixtures, not evidence that a real key or endpoint has been verified.
