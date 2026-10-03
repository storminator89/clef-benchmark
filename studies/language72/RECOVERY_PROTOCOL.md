# Stage 7: recovered-input execution record, 2026-10-03

## Identity and evidence limits

The previous workspace is no longer present. This package is a new recovery/evaluation record, not a recreation of the old 48-file freeze or its missing original logs. Seventy-two model-visible request bytes were reconstructed from this task's retained authoring text and unchanged public schema. Their SHA-256 exactly matches the previously recorded value `0a5d7e070afdb17c10ee8fd4c74c321aafd3ee8197dcd0ef7d2d253d816c2e12`. The seed-20261007 first36-request segment also matches its historical hash `975748f859d7dececef5df26eeb0b6b3c4ab2c1f229bc23ef294e48327b47ec0`. Hash matching establishes request-byte identity; it does not restore unavailable evidence.

Reconstructed gold/pairs and new scoring/evaluation code receive fresh independent AI review before a new freeze. No original scientific result exists: both historical attempts completed loading but were SIGKILLed before a completed technical warmup or scored output. The known historical facts are retained separately with explicit source and uncertainty, never represented as recovered raw logs. Historical prefreeze test counts describe the previous work, not validation of newly written code.

## Testable recovery rationale

The official project CPU-NF4 profile requires at least7.5GiB currently available memory and recommends8GiB. The first historical attempt admitted approximately6.89GiB under an older6.5GiB guard. The current clean environment reports approximately8.7GiB available. This provides a specific testable resource-admission improvement, not a proven explanation for SIGKILL. Cgroup memory-event files were absent in the previous namespace and kernel logs were denied; no memory/security controls are changed or bypassed.

Retain the original Cloudflare/clef-flash revision `17f0b0ad64efb65d273590632833508766b2aae6`, pinned native runner SHA `d06f85b922e1e4d0e905a1ddc8846aedcafa93c29f502f48b1529a36a9eb5906`, encoder SHA `0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3`, package versions, CPU NF4 double-quantized backbone, BF16 compute/head/output embeddings, six threads, batch1, cap2048 and seed20261002. No alternate backend, truncated input, changed model, prompt tuning or lower precision is introduced. Environment timing is separately identified; do not equate it to the prior machine's timing.

## Gates and bounded execution

1. Verify exact request hashes, fresh semantic/pair review, scorer plus independent synthetic tests, all model/source hashes and installed package pins, and tokenizer full/capped equality. Measure disk before19.08GB official model download; account for installed dependencies and at least3GB remaining reserve. Save a separate recovery bundle to persistent Library before model inference.
2. Before every model load require at least8GiB available RAM, no existing native model runner, and exclusive ownership of the local model window.
3. Run exactly one technical warmup-only probe by giving the unchanged native runner an empty request file. It still executes its built-in144-token warmup; no scored benchmark request is included. Bound this probe to8minutes with2-second resource sampling. Stop owned child on RSS>8.3GiB, available memory<0.75GiB or elapsed bound; retain every event/outcome. The original runner must finish successfully, emit a valid warmup result with144tokens/no truncation, and release model RAM before proceeding. A failed probe does not authorize repeated blind probes.
4. If the probe passes, execute the unchanged72 scientific requests in original seeded order as two36-request segments. Each segment uses an owned supported exec session, same model/configuration, no overwrite,40-minute bound and same resource guards. Save flush/fsync checkpoints. After each completed segment persist its outputs before proceeding. Warmups and native first-case-repeat summaries are separate from all scored denominators. The native repeat does not expose its full separate probability/timing row; same_choice compares entire rounded answer objects, not selected labels alone.
5. Preserve every failed/partial attempt. Never rerun completed scored IDs for selection; any incomplete continuation must lock only uncompleted IDs before running. Verify original request bytes after execution. Independently recompute final metrics and review all errors before publishing.

## Fixed finite-set metrics

- Case exactness/action/determination: /72 unique requests; invariant subset/60; ambiguity subset/12; each invariant view/12. Missing or assignable invalid output counts incorrect.
- Invariant both-correct/stable/stable-but-wrong/observed unjustified change/invalid-pair/failed-invariance: /48 pairs, per transformation/12, domain/16. Conditional valid-pair rate is additional and clearly labeled.
- Loss: correct canonical→incorrect variant /48; improvement reverse /48; conditional loss among correct-canonical pair endpoints (NA when zero). Shared canonical appears in four comparisons and is executed only once.
- Ambiguity directional both-correct: /6, each subtype/3; a mere output change is not enough.
- All five views correct per base: /12 clusters. Domain cells have four clusters, only one base tests conflict resolution; no population inference or naive independent-pair significance.
- Fixed high-score gate min(selected unrounded action,determination)≥.90: wrong-and-selected/72 and/selected, with subset denominators/60 and/12. Also separately report per-field errors using own marginal gates and within the min-score case gate. These are uncalibrated marginals, not a joint safety probability.
- Technical coverage: recorded/valid/missing/invalid unique requests and complete pairs. Timing uses unique main requests only, excluding loads/warmups/repeat probes.

Validate native fields, exact option membership, original criteria-order argmax ties, finite nonboolean probabilities in[0,1], unrounded sum error<1e-5, four-decimal maps/confidence exactly round(raw,4), latency-ms consistency<1e-5, exact preflight token counts and truncated=false. Encoded option IDs are lexical; that does not replace criteria-order native tie handling. Duplicate/unexpected IDs, ambiguous JSON keys or unassignable parsing failures stop ingestion. Raw evidence is retained unchanged.

Synthetic, purposive, AI-authored/AI-reviewed German variants do not establish authentic-user prevalence, dialect performance, expert-human validity, financial advice quality or production safety. Jev remains a separate future supplement outside its frozen974-request plan. No image experiment is resumed.
