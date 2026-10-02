# Custom German retail-bank support pilot

80 newly authored, fictional German support messages, three native Clef choice fields per case: intent, priority and next support step. This is a deliberately stratified pilot of workflow classification. It is **not BANKING77**, a real-ticket corpus, a representative bank-traffic sample or an evaluation of financial advice. Do not compare its scores numerically with vendor BANKING77/Jev results or pool it with other suites.

The main result belongs in `REPORT.md`; every whole-case mismatch belongs in `ERRORS.md`. Full predictions, unrounded option probabilities, token counts, latencies and observed process memory are retained in `results/`. All labels and model-visible rules are frozen before inference. No bank transaction, account modification, card block, eligibility decision or customer communication is executed.

## Layout

- `data/requests.jsonl`: label-free native requests; only these enter the model
- `data/gold.jsonl`: ID-aligned three-field gold, scored in a separate process
- `data/cases.jsonl`: original synthetic messages, gold, rationale and clarification target
- `data/metadata.jsonl`: topic, linguistic style, answerability and rationale; never input to the model
- `data/policy.json`: the exact fictional support policy and native field definitions
- `data/design_summary.json`: exact topic/label/style counts, not prevalence estimates
- `audit/`: full initial and revised independent pre-inference review, encoding cap checks and scorer checks
- `freeze_manifest.json`: exact pre-inference hashes
- `scripts/`: construction, validation, freeze, score and reproduction helpers
- `reference_runtime/`: pinned public Clef inference/download sources and dependencies; weights and virtual environment excluded
- `SOURCES.md`: primary topic-inspiration sources and boundaries

The ten design groups have eight cases each. Gold intents are not balanced: 9 access/TAN, 9 account/documents, 9 cards, 8 cash, 7 direct debits, 8 fees, 10 security, 8 standing orders, 8 transfers and 4 unclear. Priorities are 10 critical, 6 urgent and 64 routine. Next steps are 14 clarification, 31 guidance, 10 security handoff and 25 specialist review. Linguistic strata are 40 plain, 8 colloquial/typo, 15 negation/context, 12 uncertain and 5 multi-intent. These are primary descriptive tags, not all mutually absent linguistic properties.

One deliberately designed policy edge case (`bank_ambiguous_multi_07`) asks clarification between equal-ranked routes while global priority remains urgent. The explicit fictional rule, rather than an asserted universal bank practice, determines its gold. The custom taxonomy groups many service questions broadly and is not a complete bank intent taxonomy.

## Runtime

Pinned official model: [Cloudflare/clef-flash](https://huggingface.co/Cloudflare/clef-flash/tree/17f0b0ad64efb65d273590632833508766b2aae6), revision `17f0b0ad64efb65d273590632833508766b2aae6`. Original native schema head and original lexical output embeddings remain BF16; backbone uses experimental CPU NF4 with double quantization and BF16 compute. Batch size 1; six threads; 2048-token cap; no generation-based replacement. Torch 2.11.0+cpu, Transformers 5.10.2, bitsandbytes 0.50.2. This is not vendor stock BF16/GPU inference.

The official English wrapper remains unchanged; messages and task instructions are German, native option IDs are English. This tests bounded choices, not the wording or usefulness of an actual generated German answer. The `clarification_target` is an author-provided explanation for audit/UI, not a model-generated question.

## Reproduce without overwriting the recorded run

Use Python 3.12 on a suitable CPU machine with sufficient disk and RAM. The original main runner refuses to overwrite predictions.

1. From `reference_runtime/`, run `bash setup_runtime.sh`
2. Run `venv/bin/python download_model.py` and `venv/bin/python verify_files.py`
3. From this pilot directory, run `python scripts/validate.py`
4. Run `scripts/reproduce.sh /absolute/path/to/reference_runtime /absolute/path/to/a/new/results-directory`

Model weights are downloaded from the exact upstream revision and verified against retained hashes. Download/setup is not part of inference latency. The single main run contains 80 scored cases, plus an unrelated technical warmup and one first-case repeatability probe excluded from all quality and latency aggregates. No prompt retuning, label repair, model selection, retry averaging or test-case cherry-picking is permitted under the original result identity.

Scores are descriptive for this exact frozen set. Even a perfect score on ten safety-critical cases would not establish rare-event safety. Gold was independently checked by a separate AI reviewer who could see the labels; it is not blinded human annotation or expert banking validation. No real customer records, genuine identifiers, credentials, account balances, terms or statutory deadlines are included.

## Public provenance boundary

This public package retains every frozen benchmark input/source file and every
scored prediction, unrounded probability vector, final metric and independent
score check. It retains the model revision, quantization, package versions,
thread/token settings and per-case CPU timing methodology needed to interpret
this run. It intentionally omits nonfrozen restoration/host/filesystem
diagnostics, historical restoration smoke comparisons and raw process/host
resource telemetry. Those private diagnostics are not part of the public
reproducibility claim. The omissions and changed nonfrozen documentation are
explicitly recorded in `provenance/portable_export.json`; no scored case, gold
label, model-visible rule or measurement was repaired or selected away.

`scripts/export_public.py` copies only the files already included in this
reviewed public manifest. A new run or newly added diagnostic files need a
separate publication review rather than automatic inclusion.
