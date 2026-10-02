# Local Clef-flash execution record

## Identity and official source

- Official model: https://huggingface.co/Cloudflare/clef-flash
- Pinned revision: `17f0b0ad64efb65d273590632833508766b2aae6`
- Source code: `joint_schema_model.py`, SHA-256 `0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3`
- Backbone checkpoint: 9,409,813,744 parameters, 18,819,627,488 tensor bytes (official index)
- Separate original joint schema head is essential; ordinary chat generation or GGUF backbone-only generation is not equivalent Clef inference

## Environment

CPU-only Linux x86-64, 9 visible CPUs, AMD EPYC 9V74, 9.7 GiB system RAM, no swap, no detected NVIDIA GPU. Public hardware facts are in `provenance/environment.json`; the full system snapshot is intentionally omitted. No paid API, account creation, remote GPU or user computer used.

## Experimental configuration

Official model loader unmodified; `load_release_model(device='cpu', dtype=torch.bfloat16, quantization_config=...)` forwards a Transformers BitsAndBytesConfig into its standard Qwen3.5 loader. Backbone Linear weights quantized on load to NF4 with double quantization and BF16 compute. Output embedding (`lm_head`) kept BF16 because the original Clef head directly indexes it to form its lexical prior. The original joint head is loaded strictly from official safetensors and kept BF16. This is an experimental CPU quantization, not vendor-tested stock BF16/H200 inference, and quality/performance must not be represented as the vendor configuration.

Torch 2.11.0+cpu, Transformers 5.10.2, bitsandbytes 0.50.2. Exact package freeze recorded separately. Missing optional GPU/custom fast kernels use standard Torch fallbacks; no unrelated model substitutes the Clef checkpoint.

## Validation

Before the 19GB model download, standalone NF4 CPU and miniature Qwen3.5 forward tests passed. These tests establish runtime compatibility only, not Clef accuracy. The first tiny synthetic configuration had a 2-wide linear layer that is incompatible with the CPU 32-wide packer; the revised fixture uses the real model's 32 value heads and passed. Setup/debug logs are intentionally omitted from this public package; these compatibility tests are distinct from the recorded model benchmark.

Actual inference uses the official encoder, collation, ClefModel forward and answer conversion. Every input is encoded a second time without a practical length cap, and equality is asserted to prevent silent truncation. All predictions retain unrounded probabilities, token counts and measured forward latency. Model-load time and a separate technical warmup are excluded from benchmark latency. The official internal wrapper remains English even when state, instruction and descriptions are German.

The runner reads only label-free requests and rejects top-level expected/gold/label fields. Labels and benchmark construction are maintained separately. No tuning against test answers is performed.

## Running

Run the commands in this section from the repository’s `runtime/` directory. For the complete public layout and paths, see `docs/REPRODUCIBILITY.md` from the repository root.

1. Run `bash setup_runtime.sh` using Python 3.12 to create the venv and install pinned requirements from their official registries
2. `python download_model.py` downloads the fixed official revision
3. `python guard_run.py python run_clef.py --requests ../benchmark/requests.jsonl --output predictions.jsonl`

Alternatively, after setup, run `bash reproduce.sh`; it saves separate reproduced predictions and scores and never overwrites the original result.

Use the venv's Python for both guard and runner. Set OMP_NUM_THREADS=6 and MKL_NUM_THREADS=6. Read the completed metadata in `results/run_metadata.json` and `results/finance/run_metadata.json` (repository-root paths) before interpreting published outputs. Reproduction logs are generated locally; original setup/debug logs are not included. The guard logs RAM and stops unsafe memory pressure. Incomplete runs are not benchmark success.

## Completed measurements, 2026-10-02

Both independently frozen runs completed with process exit code 0, no missing predictions and no truncated input. The same runner source SHA-256 (`d06f85b922e1e4d0e905a1ddc8846aedcafa93c29f502f48b1529a36a9eb5906`) and model configuration were used. The original benchmark was not rerun or altered after scoring.

- General pilot: 116/120 German choices correct (96.67%), 29/30 English controls, 29/30 mixed-schema diagnostics. All 180 outputs schema-valid. German forward latency median 10.180 s, p95 11.440 s; overall 180-case median 9.803 s. Peak process RSS 6.629 GiB. See `results/summary.json` (repository-root path).
- Separate finance/broker pilot: 76/80 German choices correct (95.0%), 18/20 English controls. All 100 outputs schema-valid. German forward latency median 11.469 s, p95 13.667 s; overall 100-case median 11.306 s. Peak process RSS 6.658 GiB. See `results/finance/summary.json` (repository-root path).
- Each run repeated its first request once after completion as a narrowly scoped repeatability check: probabilities were bit-identical. This does not establish cross-platform determinism.
- A separate, new-input `live_adapter.py` test passed (proof: `qa/live_adapter_smoke.json` (repository-root path)); it is excluded from all benchmark metrics.

The finance pilot uses fictional explicit workflow rules. It is not an investment-advice, underwriting, eligibility, legal-compliance or production-safety test. Three of its four German mistakes chose a concrete route where the reference required clarification; two mistakes had confidence above 92%. Confidence is not a safety gate. All quality claims are limited to these small synthetic purposive datasets and this experimental quantized runtime.

To reproduce the finance pilot separately, run `bash reproduce_finance.sh` after setup. Do not merge its case counts with the original pilot when interpreting domain performance.
