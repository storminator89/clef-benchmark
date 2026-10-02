# Clef: German minimal-change paired diagnostic

A separate, bounded 24-pair / 48-case experiment across banking, insurance and finance. It tests whether the same pinned native model changes its complete bounded decision when one relevant fact changes, and stays stable when one narrow edit should preserve the outcome.

## What is included

- Explicit fictional rule in every case, German scenario/question, two native fields: action and determination
- Twelve outcome-changing pairs and twelve outcome-invariant pairs, eight pairs per domain
- Exact changed message span, unchanged prefix/suffix hashes, all cases and separated gold
- Frozen inputs, protocol, scorer, source/model/package facts and independent pre-run AI review
- Complete native probabilities/tokens/timings, all errors, paired metrics and independent final verification when execution completes

Read PROTOCOL.md before interpreting scores. This is AI-authored and separately AI-reviewed, with reused schema and generic rule templates. It is not a human-expert holdout or a representative customer sample. Paired observations are dependent. No scores are pooled with prior suites. Bounded choices do not test the quality of generated German clarification questions.

## Runtime

Cloudflare/clef-flash official 9B revision 17f0b0ad64efb65d273590632833508766b2aae6. Experimental CPU NF4 backbone, original BF16 joint head/output embeddings; six threads, batch1, 2048 token cap. The original native runner and model source are preserved. No GPU or native unquantized comparison is claimed.

## Reproduce in a new output directory

1. Create a local runtime directory from reference_runtime, run setup_runtime.sh, and fetch model files with the included pinned download_model.py
2. Verify downloaded hashes using verify_files.py; exact reference package versions must match
3. Run scripts/reproduce.sh with absolute paths to the populated runtime and a new results directory
4. Reproduction must not overwrite this experiment's original predictions or frozen artifacts

The original unmodified runner excludes its unrelated warmup and one first-case repeatability probe from benchmark scores. Its single-case repeat summary is not a general repeatability study. Native option softmax scores are not validated calibrated or joint probabilities.

## Artifact layout

- data: model-visible requests, cases, separated gold, exact paired metadata, schema and design counts
- audit: original and final review evidence, correction history, preflight/scorer tests and independent result checks
- reference_runtime: original model/runner sources, dependency pins and model-file checksums; no weights redistributed
- results: every raw prediction plus case/pair scores, all errors, timing/progress observations and summary
- freeze_manifest.json: immutable pre-inference inputs and code
- provenance/portable_export.json and FILE_SHA256.json: public-export transformations and file integrity

Public scope retains all benchmark cases, outputs, probabilities, errors and forward timings. Redundant development diagnostics, duplicate runtime inventories and operational bookkeeping are outside the public package; provenance does not record private predecessor identities or omission hashes.




## Verified result

39/48 (81.2%) complete cases correct; 17/24 (70.8%) pairs both-correct; 8/12 (66.7%) correct directional flips; 1/12 (8.3%) unjustified invariant changes. Independent score/integrity audit passed.

See [REPORT.md](REPORT.md), [ERRORS.md](ERRORS.md) and [all raw results](results/predictions.jsonl).

## Public verification scope

All 50 frozen scientific files and native results are unchanged. Compact final
verification, complete semantic error review and [method corrections](audit/INDEPENDENT_METHOD.md)
remain available. Redundant development diagnostics and operational bookkeeping
are outside the public package. The public manifest lists only retained files;
no private predecessor identity or omission hash is included.
