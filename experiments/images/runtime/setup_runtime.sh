#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
python3 -m venv venv
venv/bin/python -m pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu 'torch==2.11.0' 'torchvision==0.26.0'
venv/bin/python -m pip install --no-cache-dir -r requirements_frozen.txt
