#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")/.." && pwd)
RUNTIME=${1:?Usage: reproduce.sh /absolute/runtime /absolute/new-results-dir}
RESULTS=${2:?Usage: reproduce.sh /absolute/runtime /absolute/new-results-dir}
[[ "$RUNTIME" = /* && "$RESULTS" = /* ]] || { echo 'Use absolute paths' >&2; exit 2; }
mkdir -p "$RESULTS"
[[ ! -e "$RESULTS/predictions.jsonl" ]] || { echo 'Refusing to overwrite predictions' >&2; exit 2; }
PY="$RUNTIME/venv/bin/python"
"$PY" "$HERE/scripts/validate.py"
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 HF_HUB_OFFLINE=1
"$PY" "$HERE/scripts/guard_run.py" "$PY" "$RUNTIME/run_clef.py" --requests "$HERE/data/requests.jsonl" --output "$RESULTS/predictions.jsonl" --threads 6 --max-length 2048
"$PY" "$HERE/scripts/score.py" --data "$HERE/data" --results "$RESULTS"
