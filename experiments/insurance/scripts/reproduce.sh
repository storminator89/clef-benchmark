#!/usr/bin/env bash
# A separate environment; never upgrade an existing shared environment.
set -euo pipefail
cd -- "$(dirname -- "$0")"
python3.12 -m venv venv
venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch==2.11.0
venv/bin/pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements_frozen.txt
venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download
from pathlib import Path
import shutil
snapshot_download('Cloudflare/clef-flash',revision='17f0b0ad64efb65d273590632833508766b2aae6',local_dir='model')
shutil.copyfile('model/joint_schema_model.py','joint_schema_model.py')
PY
venv/bin/python verify_files.py
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6
venv/bin/python check_encoding.py --model-dir model --requests ../benchmark/requests.jsonl --output ../qa/reproduced_encoding.json
venv/bin/python guard_run.py --log ../results/reproduced_resources.jsonl venv/bin/python run_clef.py --requests ../benchmark/requests.jsonl --output ../results/reproduced_predictions.jsonl --max-length 2048
venv/bin/python score_results.py --benchmark ../benchmark/benchmark.json --predictions ../results/reproduced_predictions.jsonl --metadata ../results/reproduced_predictions.metadata.json --output ../results/reproduced_results.json
