# Jev × Clef: frozen native-decision comparison

**Prepared, not executed. No Jev result, ranking, billed API call or credential use is included.**

This self-contained package compares the versioned **TypeSafe Jev `jev-1.13.0`** service against archived **Cloudflare/clef-flash `17f0b0ad64efb65d273590632833508766b2aae6`**, CPU NF4 backbone with original BF16 decision head/output embeddings. It is intended for `experiments/jev_comparison/` in Clef Lab after review and authorization. The workflow is a deliberately inactive template.

## Scope and cost

| Suite | Requests | Interpretation |
|---|---:|---|
| Original text | 180 | 120 German primary; 30 English controls; 30 German-input/English-schema diagnostics |
| Finance | 100 | 80 German primary; 20 English controls |
| clean72 | 72 | German synthetic primary |
| Bank support | 80 | German synthetic, three fields |
| Insurance | 60 | German synthetic; five related cases per document |
| Clarification | 72 | German synthetic, two fields |
| Minimal pairs | 48 | 24 dependent pairs; retain flip/invariant diagnostics |
| Attack removal | 14 | Seven attack/clean pairs; attack payloads repeat seven prior primary requests |
| Multidocument | 48 | 12 families and 16 shared cross-domain templates, two fields |
| MASSIVE de-DE | 300 | Frozen official-test slice; 60 options, 59 gold-supported labels |
| **Operational inventory only** | **974** | **1,362 questions; no combined accuracy, independent-sample claim or overall ranking** |

The 90 original image requests are **not comparable**: Jev has no native image input. No images are copied or forwarded, and no OCR replacement is made. Probability-reliability analysis reuses these text outputs rather than generating another suite of API calls. Superseded pilots, setup probes and private user cases are outside scope.

Official input price checked 2026-10-02: **USD 0.042 per million input tokens; output free** ([TypeSafe models](https://docs.typesafe.ai/models)). The 974 request bodies total 2,400,319 UTF-8 JSON bytes. A deliberately approximate 2–4 bytes/token illustration gives **600,080–1,200,160 tokens, about USD 0.025–0.050 for one pass**. This is not an official tokenizer, interval or quotation; serialization and internal overhead may differ. Per-suite estimates and seven exact repeats are in `qa/offline_plan.json`.

Proposed live limits:

- One pass, 974 cases; at most one retry per case and 50 retries across the run
- At most 1,024 wire attempts, including failures and ambiguous outcomes
- USD 3 local API reservation ceiling; no account signup, top-up, paid CI or subscription
- Reserve the 65,536-token capacity reservation (a conservative interpretation of the documented “64k” limit) × the dated price before every attempt: USD 0.002752512/attempt, **USD 2.818572288 for all 1,024 attempts**
- Sequential, at least 1.05 seconds between starts; 90-second request timeout; only 429/529 eligible for one bounded retry; no automatic transport/SDK retries
- Fail closed on changed model version, malformed probabilities, missing/invalid usage, usage above reserved capacity, authentication/schema errors, redirects or ambiguous transport failure

This is a **local count/reservation safeguard, not a provider-enforced account spending limit**. Provider price changes, accounting of failures, taxes/minimum charges and hidden overhead have not been contractually verified. Actual successful `usage.input_tokens` is recorded and reconciled at the dated rate. Unknown failures retain their full reservation. Reconfirm the official price and account terms before activation; use a provider-side limit if available. No guarantee is made about free or billable GitHub runner use.

## Reproducible protocol

1. Verify all 68 retained scientific/provenance file hashes and the separate code/manifest lock before evaluation. The original 61 multidocument and 56 MASSIVE frozen files also passed source checks; compact public provenance retains the result without operational inventories.
2. Use each exact frozen request in its original per-suite order. The **only request-content change is `model: clef-flash` → `model: jev-1.13.0`**. Preserve state JSON shape, all text, field names/order, all option keys/order/descriptions, primitive and instructions. No translation, added examples, schema repair, injected abstention option, token-probability approximation or outcome-based adaptation.
3. Each original case remains one request with its original native parallel questions. Do not pack different cases into one state, feed preceding model answers forward, or condition questions on other outputs. Provider internals/tokenization can differ; this is equality of supplied task content, not equality of internal serialization.
4. Keep gold separate from inference. Only `model`, `state` and `questions` can reach the network. Collector never opens gold; offline scorer consumes independently frozen labels later. Insurance and MASSIVE gold are mechanically normalized for the scorer; original gold-bearing source records and hashes are retained. No label is inferred from Jev or Clef predictions.
5. Preserve every native class probability, selected choice, vendor confidence, returned model ID, token usage, request/response SHA-256 and attempt timing. Never renormalize, round or fabricate missing distributions. Exact response bytes are hashed, not stored; validated native fields retain their numerical precision. Unknown fields, headers and raw error bodies are excluded from artifacts.
6. Report expected, valid, failed and missing counts. An interrupted/partial run stays partial. No automatic resume, automatic workflow rerun, or silent second full run. A new run requires fresh bounded authorization.
7. Keep each suite and control split separate. Report exact-case and field accuracy, paired both-right/Clef-only/Jev-only/both-wrong counts and agreement. Calibration groups remain split by suite/partition/category/field/option set. Use native selected-option probability for fixed risk/coverage thresholds, multiclass sum-Brier, NLL and 10 equal-width-bin ECE. Exact zero gold probability yields infinite NLL explicitly, not epsilon-clipped apparent finiteness. No uncertainty interval or independent-sample significance claim is attached to the dependent synthetic cases.
8. Minimal-pair output retains both-endpoint correctness, changes/stability and stable-wrong pairs. Attack-removal pairs retain recovery/regression and unchanged choices; English/mixed-schema control pairs retain correctness and cross-language agreement. MASSIVE reports 300 primary cases, 59 gold-supported macro-F1 and separate fixed-60 macro-F1, plus predeclared 285/284 exact-overlap sensitivities. Public training-contamination overlap remains unknown.

**Important confidence mismatch:** Jev Choice confidence is `(p_max − 1/n) / (1 − 1/n)`. Historical Clef `confidence` is a rounded selected-option probability. They are retained separately and are not compared using the same numeric confidence threshold. Native probability vectors support the common analysis ([TypeSafe confidence](https://docs.typesafe.ai/confidence)).

**Latency limitation:** Clef’s historical `inference_seconds` is a local CPU-NF4 forward-pass measurement. Jev `request_seconds` covers hosted HTTP submission through full body receipt, including transport, provider queuing and computation; case end-to-end time additionally includes validation and retry/backoff. These have different hardware, precision and timing boundaries. The report gives separate medians/p95, without a model-speed ratio or apples-to-apples claim. Jev exposes a versioned service ID; an immutable weight hash and serving hardware are unavailable.

## Offline checks

Python 3.12+, standard library only; no model or dependency installation needed.

```sh
python3 scripts/check_bundle.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/jev_runner.py --output qa/offline_plan.json
```

The 23 tests exercise mocked HTTP responses, invalid vectors/billing, redirects, safe logging, token reservations, one-retry behavior, leakage guards, native preservation, source hashes, exact-control counts and incomplete-run scoring. Mocks and empty-result tests create temporary files only; they do not constitute Jev observations. No live service behavior has been verified.

## Secure activation, after explicit approval

1. Review this package and publish its code/data commit through the authorized repository writer. Publication is not performed by this preparation.
2. In the inactive `workflow/jev-comparison.yml.in`, replace `REVIEWED_CODE_COMMIT_SHA` with that **immutable, reviewed 40-character code commit**. Put the activated workflow on main in a separate reviewed commit. Its checkout and upload actions are pinned to verified official release SHAs. Do not check out user-controlled dispatch refs.
3. The user enters an API key directly in GitHub: repository **Settings → Secrets and variables → Actions → New repository secret**, name `JEV_API_KEY`. Never place it in chat, dispatch inputs, code, arguments or an artifact. The assistant does not enter or retrieve it.
4. Explicitly approve transmission of this frozen public/synthetic scope and the finite one-pass USD 3 API guard. Both manual-dispatch approval inputs default to false. The secret is injected only into the live execution step; preflight, tests, scorer and artifact uploader do not receive it. No PR, push, fork or schedule trigger exists. Reruns are blocked and overlapping executions serialize.
5. Review sanitized output artifacts. They retain only the explicit evidence allowlist for seven days, never requests, headers, environment dumps or error bodies. Repository write access still allows malicious workflows to obtain repository secrets; manual dispatch and masking alone are not isolation boundaries. For stronger access control, configure a protected GitHub environment yourself after deciding its permissions.

Official setup and security references: [GitHub secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets), [secure workflow use](https://docs.github.com/en/actions/reference/security/secure-use), [manual dispatch](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch).

## Baseline completeness and rights

The first nine suites have complete archived Clef baselines. **MASSIVE’s final Clef comparison is pending its owner’s completion and independent audit.** No partial MASSIVE predictions were copied or scored. The frozen 300 Jev inputs can be evaluated once authorized; the later audited Clef baseline must be imported and pinned through a reviewed manifest update before final head-to-head scoring.

Synthetic source data is Apache-2.0. MASSIVE is Amazon’s public CC-BY-4.0 dataset; license and source attribution are included, and the upstream input utterances are unchanged. This narrow preparation has not approved forwarding licensed source images or any private customer data. See `NOTICE`, `LICENSE`, `licenses/MASSIVE-CC-BY-4.0.txt`, and `inputs/massive300/SOURCES.md`.

TypeSafe states it does not train Jev on customer requests/responses. Ordinary retention duration is not confirmed; enterprise ZDR is not assumed ([TypeSafe legal](https://docs.typesafe.ai/legal)). An existing account and authorized credential are prerequisites. No new agreement, account, payment or expanded access is accepted here. This is research on public/synthetic fixtures, not a deployment decision or finance/insurance advice.

## Publication scope

The repository integration curates non-scientific preparation metadata. Frozen requests, gold, native Clef predictions and option probabilities are unchanged. Public model/profile provenance and the input/code locks remain; operational diagnostics and redundant development inventories are outside this package. The historical source commit is retained, while the integration base is recorded separately. A new offline review covers this curated package.
