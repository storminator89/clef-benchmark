# Reproducing the German Clef benchmark

This is a research snapshot dated 2026-10-02, not a production qualification.
This page documents the original general-purpose benchmark. The separately
versioned [finance/insurance extension](FINANCE_REPRODUCIBILITY.md) has its own data, freeze, scoring and results;
its cases must not be pooled into the original 120-case German primary score.
The frozen benchmark and saved model responses are separate from the interactive
workbench. Browsing the workbench or replaying a saved answer does not run Clef.

## Original benchmark scope and provenance

- 120 synthetic German primary scenarios, 30 selected English translations, and
  30 German-input/English-schema diagnostic variants: 180 original requests in total
- Six separate decision taxonomies; one native `choice` question per request
- Model: [Cloudflare/clef-flash](https://huggingface.co/Cloudflare/clef-flash),
  revision `17f0b0ad64efb65d273590632833508766b2aae6`
- Native encoder, forward pass, original joint head and answer conversion;
  no substitute chat-generation model and no API-call baseline
- CPU NF4 backbone, double quantization, BF16 compute, original BF16 joint head
  and BF16 output embeddings; batch 1, 6 Torch threads, seed 20261002
- Python 3.12.14, Linux x86-64, AMD EPYC 9V74, 9 visible CPUs,
  10,451,464,192 bytes reported system RAM, no swap and no detected NVIDIA GPU
- The original official wrapper prompt remains English. “German” refers to the
  state, task instructions and answer descriptions, not every internal token

The run is an experimental resource-constrained configuration. Its accuracy and
latency must not be presented as stock BF16/H200, API, or larger Clef results.
Hardware and dependencies affect execution; exact cross-platform bitwise model
reproducibility is not promised. The recorded repeatability probe covers one case.

## Validate without downloading a model

From the repository root, using Python 3.12:

```sh
python3 scripts/check_project.py
```

This verifies frozen hashes, benchmark structure and scorer synthetic regression
checks. When final results are present it independently recomputes both scorers
in a temporary directory, compares the published reports and verifies every
record's ID, probability consistency and non-truncation flag. It does not execute
an ML model. The synthetic scorer fixtures are software tests, not model results.

Run the lightweight UI tests separately as documented in the root README.

## Re-run real inference

Allow approximately 20 GB for the official release plus the Python environment
and several GB of disk headroom. No weights are stored in this repository. The
original run used a CPU configuration close to its RAM limit; avoid other large
jobs and inspect the guard before changing its thresholds. Running on other
hardware is a new experimental configuration and should be labeled as such.

```sh
bash runtime/setup_runtime.sh
runtime/venv/bin/python runtime/download_model.py
python3 scripts/verify_model_download.py
bash runtime/reproduce.sh
```

The setup uses PyTorch's official CPU wheel index and pinned dependencies in
`runtime/requirements_frozen.txt`. The downloader resolves the exact 40-character
revision, not the moving main branch. It obtains executable official model code;
review it before running. `scripts/verify_model_download.py` checks every release
file against the saved SHA-256/size manifest before inference. The original
`runtime/verify_files.py` additionally checks the downloaded Hugging Face commit
and LFS hashes. It refreshes the local model-file manifest; the package check
will detect a changed tracked manifest.

`reproduce.sh` writes `runtime/reproduced_predictions.jsonl`, accompanying
metadata, and `runtime/reproduced_scores.json`; it refuses to overwrite an
existing predictions file. It never replaces the published `results/` snapshot.
Retain a completed metadata file before interpreting a run. Do not combine partial
outputs with a different revision or configuration. This command may take tens
of minutes on comparable CPU hardware and consumes no paid API.

The runner never reads gold labels. It asserts equality between bounded and
unbounded encoded inputs to reject truncation. Its separate technical warm-up,
model loading and token encoding are excluded from `latency_ms`, which is measured
forward-pass time. Encoding and total measured per-case time are separate fields.

## Re-score a completed run

```sh
python3 benchmark/score.py runtime/reproduced_predictions.jsonl --out runtime/reproduced_scores_v1_0.json
python3 qa/score_v1_1.py runtime/reproduced_predictions.jsonl --out runtime/reproduced_scores_v1_1.json
```

`benchmark/score.py` is the frozen v1.0 scorer. `qa/score_v1_1.py` is a separately
identified robustness revision prepared before predictions were inspected. It
handles malformed answer envelopes and adds an all-30-planned paired analysis;
it does not change existing metric definitions. See the [changelog](../qa/scorer_v1_1_changelog.md).

Primary accuracy uses all 120 planned German cases. Missing, errored or invalid
outputs count as incorrect. Overall macro-F1 averages the six category macro-F1s,
not incompatible classes pooled across tasks. Calibration uses multiclass Brier
sum, NLL clipped at 1e-12 and five equal-width ECE bins. Paired comparisons use
only the 30 deliberately selected triplets, never all 120 German versus 30 English.

## Rebuild the data safely

The hand-authored cases are embedded in `benchmark/build_benchmark.py`.
It writes beside itself; do not run it over the published frozen snapshot.
Copy that script into a new directory, run it there, and compare resulting data
hashes to `benchmark/freeze_manifest.json`. The timestamped freeze manifest is
a separate pre-inference record, not regenerated by that command.

## Public artifact mapping

- `benchmark/`: original frozen files, byte-identical, including methodology
- `runtime/`: original reproduction scripts, pinned packages, official source
  and lightweight model/configuration manifests; no weights or environment
- `results/predictions.jsonl`: complete original 180 raw model predictions
- `results/run_metadata.json`: original completed-run metadata
- `results/scores_*.json`: explicit public derivatives of score reports, with
  `outputs_file` changed to `results/predictions.jsonl` only
- `results/verification.json`: independent final-result verification
- `results/summary.json`: compact original-run summary, formerly
  `runtime/result_summary.json`; regenerated by `scripts/summarize_results.py`
- `provenance/environment.json`: necessary hardware/software facts extracted
  from the original machine snapshot, with the transformation documented
- `provenance/curation_manifest.json`: source and public SHA-256 hashes and every
  transformation; original run records are never silently rewritten
- `reports/`: final reviewed German PDF/DOCX report when available

`docs/EXECUTION.md` preserves the final execution record; its references to
`environment_before.json`, logs or original result locations describe original
run artifacts. Public equivalents and intentionally excluded files are listed
above and in the curation manifest. `runtime/finance_summary.json` maps to
`results/finance/summary.json`, and `runtime/live_adapter_smoke.json` maps to
`qa/live_adapter_smoke.json`. Installation/debug logs, raw conversations,
private research notes, credentials, caches and model weights are excluded.

## Limits

These newly authored AI-generated cases had a separate AI label/translation
review before freeze, not independent human annotation. The dataset is small,
balanced and synthetic rather than representative German traffic. The 30 pairs
are purposive, not random; exploratory McNemar p-values do not establish a general
language effect. No evaluation of free-form German writing, multimodal ability,
long contexts, actual tools, finetuning or production safety is claimed. Six
injection examples are not a security certification. Public release also creates
future training-data contamination risk.

## Sources and license

The upstream [model card at the exact revision](https://huggingface.co/Cloudflare/clef-flash/blob/17f0b0ad64efb65d273590632833508766b2aae6/README.md),
[official Clef interface documentation](https://developers.cloudflare.com/workers-ai/models/clef/),
and [Cloudflare announcement](https://blog.cloudflare.com/clef-decision-models/)
are distinct from the findings of this independent benchmark. A verbatim model
card is preserved in `docs/UPSTREAM_MODEL_CARD.md`. The official model source
and release use Apache-2.0; the original license is included in `licenses/`.
See the root LICENSE and NOTICE for this project's licensing and attribution.
