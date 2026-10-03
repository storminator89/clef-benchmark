# Clef German language variants: independently checked result

64/72 unique requests fully correct;40/48 invariant pairs correct at both endpoints;6/48 invariant output changes, comprising5 improvements and1 wrong-to-other-wrong transition. No correct canonical endpoint became wrong. Two invariant pairs remained stably wrong. Separate ambiguity-changing controls:3/6 pairs both correct.

All eight errors concern an unspecified target. This is a deliberately constructed AI-reviewed sample, not a population, dialect or safety estimate. Read REPORT_DE.md and ERRORS.md before interpreting percentages. Native decisions and every option probability are retained unchanged.

This is a new recovered execution record: original72 request bytes match their historical SHA-256, but the old full preparation archive and historical raw failure logs were not recovered. No historical result was invented. The current two completed segments, warmups and independent checks are retained. Private operational diagnostics are omitted from this public package and its manifests.

## Read and verify

- data/: complete fictional rules/messages, gold, pairs and exact native requests
- results/predictions.jsonl:72 native rows, byte-preserving segment assembly
- scored/: fixed-denominator case/pair/cluster metrics and every error
- runtime_results/: exact native metadata/predictions, curated completed outcomes and sampled RSS/timings
- runtime/: original pinned public source/config/package/model-hash references; no weights
- evidence/: actual tokenization, package/model verification, synthetic test evidence and concise independent final result
- public_scientific_freeze.json: only retained pre-inference scientific files
- PUBLIC_MANIFEST.json: all retained public files; manifest itself excluded

Model-free checks:

    python scripts/verify_public.py
    python scripts/score.py --predictions results/predictions.jsonl --output fresh_scores

Use a new scoring output directory. Exact original model setup uses official CPU package pins and the immutable upstream revision, with adequate available RAM and disk. Never overwrite recorded predictions. Runtime timing belongs to this recovered environment; it is not a controlled precision comparison. Publication/repository integration is a separate coordinator action.
