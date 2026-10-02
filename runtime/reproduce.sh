#!/usr/bin/env bash
# Run from a copy of the complete benchmark bundle. Refuses to overwrite results.
set -euo pipefail
cd -- "$(dirname -- "$0")"
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6
export HF_HOME="$PWD/hf_cache"
venv/bin/python download_model.py
venv/bin/python verify_files.py
venv/bin/python guard_run.py venv/bin/python run_clef.py \
  --requests ../benchmark/requests.jsonl --output reproduced_predictions.jsonl
venv/bin/python ../qa/score_v1_1.py reproduced_predictions.jsonl --out reproduced_scores.json
