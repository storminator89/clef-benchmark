# German finance injection ablation: separate post-hoc diagnostic

This diagnostic directly compares all seven German injection-tagged cases from the frozen finance/broker benchmark with a minimally edited counterpart. It was designed after the original finance results were known. It is not a new held-out benchmark and is not pooled with either original benchmark.

For each case the entire appended injection suffix (including its quote/note framing) is deleted. The retained state is an exact original prefix, with every substantive task fact, ambiguity, negation, and missing-information statement unchanged. Policy, label descriptions, label order, and gold remain identical. `pairs.jsonl` records each complete original, clean text, exact removed suffix, and character offsets. Both original and clean are rerun; historic original results are only a repeatability comparison.

The 14 label-free requests are run once with the unchanged pinned native Clef-flash runner: revision `17f0b0ad64efb65d273590632833508766b2aae6`, CPU NF4 backbone, original BF16 joint head and output embeddings, seed 20261002, six threads, batch size one, max input length 2048. Run order uses seed 2026100204: random pair order and counterbalanced adjacent conditions (four attack-first, three clean-first). The original runner adds its unrelated warmup and a first-case repeatability probe, outside the 14 scored requests. No generation substitute or paid API is used.

Independent review checks that the edit preserves the task and that gold remains valid before new model inference; files are then frozen with SHA-256. The original finance source files are never modified, and their frozen hashes are checked again. The only model inputs are `model`, `state`, and `questions` from `requests.jsonl`; gold and annotations remain outside inference.

Outputs report every pair's gold, attack/clean predicted choice, native confidence, full probability vectors, schema validity, correctness transition, and attack-rerun agreement with the historic run. Missing/invalid labels count as wrong. Schema checking uses an unchanged copy of the original scorer. The paired label-change rate and accuracy difference are descriptive; no broad significance or model-quality claim is intended.

Important limits: seven selected synthetic cases, post-hoc design, no human expert adjudication, no representative or production inference. Removing a suffix changes length and lexical context as well as removing instructions. This diagnostic can show which selected decisions changed under the specified edit in this pinned configuration; it cannot prove that all finance errors are caused by attacks or that clean realistic tasks are generally solved. Native confidence is not calibrated reliability. The attack label tags on case records are inherited source provenance, including clean counterparts; `condition` identifies actual input treatment.

Files:
- `build_ablation.py`: deterministic selection and minimal deletion construction; refuses to rebuild a frozen directory
- `cases.jsonl`, `gold.jsonl`, `pairs.jsonl`, `policies.json`, `design.json`: separate diagnostic data and provenance
- `requests.jsonl`: 14 label-free requests
- `source_score.py`: exact original schema/correctness scorer, imported rather than invoked as a full benchmark
- `validate.py`: source integrity, deletion, data isolation, rebuild, scorer-fixture and freeze checks
- `score_ablation.py`: paired post-run scoring and comparison against historic original predictions
- `pre_inference_review.md`, `freeze_manifest.json`: independent audit and pre-inference hashes
- `predictions.jsonl`, `predictions.metadata.json`, `results.json`, `RESULTS.md`: live outputs and findings, produced only after the image benchmark finishes

Run from this directory only after other model processes have ended; write reproductions outside this frozen benchmark directory:

```bash
python validate.py
../../../runtime/venv/bin/python ../../../runtime/guard_run.py ../../../runtime/venv/bin/python ../../../runtime/run_clef.py --requests requests.jsonl --output ../reproduced/predictions.jsonl
python score_ablation.py --predictions ../reproduced/predictions.jsonl --out ../reproduced/results.json
```
