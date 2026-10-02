#!/usr/bin/env bash
# Separate finance experiment; original benchmark results are never overwritten.
set -euo pipefail
cd -- "$(dirname -- "$0")"
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6
export HF_HOME="$PWD/hf_cache"
venv/bin/python download_model.py
venv/bin/python ../scripts/verify_model_download.py
venv/bin/python guard_run.py venv/bin/python run_clef.py \
  --requests ../finance_benchmark/requests.jsonl --output reproduced_finance_predictions.jsonl
venv/bin/python ../finance_benchmark/score.py reproduced_finance_predictions.jsonl --out reproduced_finance_scores.json
