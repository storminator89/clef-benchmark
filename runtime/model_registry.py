"""Explicit pinned model choices. No downloads, imports of ML packages or fallback."""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = 'flash-9b'
MODEL_KEYS = ('flash-9b', 'clef-27b')
_MODELS = {
    'flash-9b': {
        'key': 'flash-9b', 'repo_id': 'Cloudflare/clef-flash', 'api_model': 'clef-flash',
        'revision': '17f0b0ad64efb65d273590632833508766b2aae6', 'model_size': '9B',
        'manifest': 'model_file_manifest.json', 'default_model_dir': 'runtime/model',
        'source_sha256': '0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3',
        'vocab_size': 248320, 'hidden_size': 4096,
        'min_ram_gib': {'cpu-nf4': 7.5, 'cpu-bf16': 28, 'rocm-bf16': 2, 'rocm-fp16': 2},
        'min_gpu_free_gib': 22,
        'validation': 'cpu_nf4_tested_linux_x86_64_other_profiles_prepared',
    },
    'clef-27b': {
        'key': 'clef-27b', 'repo_id': 'Cloudflare/clef', 'api_model': 'clef',
        'revision': '2f3de3dd85f379784083b0814d997ab627200f0c', 'model_size': '27B',
        'manifest': 'models/clef-27b/manifest.json', 'default_model_dir': 'runtime/model-clef-27b',
        'source_sha256': '0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3',
        'vocab_size': 248320, 'hidden_size': 5120,
        'min_ram_gib': {'cpu-nf4': 24, 'cpu-bf16': 68, 'rocm-bf16': 4, 'rocm-fp16': 4},
        'min_gpu_free_gib': 60,
        'validation': 'all_profiles_prepared_not_hardware_validated',
    },
}


def get_model(key=DEFAULT_MODEL):
    if key not in _MODELS:
        raise ValueError('model must be one of ' + ', '.join(MODEL_KEYS))
    return copy.deepcopy(_MODELS[key])


def model_manifest(key=DEFAULT_MODEL):
    return json.loads((ROOT / get_model(key)['manifest']).read_text(encoding='utf-8'))


def validation_status(model_key, profile):
    return ('tested_linux_x86_64' if model_key == DEFAULT_MODEL and profile == 'cpu-nf4'
            else 'prepared_not_hardware_validated')
