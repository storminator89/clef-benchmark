#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")/.." && pwd)
RUNTIME=${1:?Usage: reproduce.sh /absolute/runtime /absolute/new-results-directory}
RESULTS=${2:?Usage: reproduce.sh /absolute/runtime /absolute/new-results-directory}
[[ "$RUNTIME" = /* && "$RESULTS" = /* ]] || { echo 'Use absolute paths' >&2; exit 2; }
mkdir -p "$RESULTS"
[[ ! -e "$RESULTS/predictions.jsonl" ]] || { echo 'Refusing to overwrite predictions' >&2; exit 2; }
PY="$RUNTIME/venv/bin/python"
"$PY" "$HERE/scripts/validate.py"
"$PY" - "$HERE" "$RUNTIME" <<'PY'
from pathlib import Path
import sys,json,hashlib,importlib.metadata
h,r=map(Path,sys.argv[1:]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in json.loads((h/'freeze_manifest.json').read_text())['files'].items():assert sha(h/path)==digest,path
for name in ['run_clef.py','joint_schema_model.py']:assert sha(r/name)==sha(h/'reference_runtime'/name),name
for name,facts in json.loads((h/'reference_runtime/model_file_manifest.json').read_text()).items():
 p=r/'model'/name;d=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024**2),b''):d.update(chunk)
 assert p.stat().st_size==facts['bytes'] and d.hexdigest()==facts['sha256'],name
for name,version in json.loads((h/'provenance/runtime_verified_before_run.json').read_text())['packages'].items():assert importlib.metadata.version(name)==version,name
PY
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 HF_HUB_OFFLINE=1
"$PY" "$HERE/scripts/guard_run.py" "$PY" "$RUNTIME/run_clef.py" --requests "$HERE/data/requests.jsonl" --output "$RESULTS/predictions.jsonl" --threads 6 --max-length 2048
"$PY" "$HERE/scripts/score.py" --data "$HERE/data" --results "$RESULTS"
