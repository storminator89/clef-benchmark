"""Explicit actual-model synthetic smoke. Never a benchmark accuracy result."""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import json
import os
from pathlib import Path
import sys
import time

from runtime.device_profiles import PROFILES
from runtime.live_adapter import ClefRuntime
from runtime.model_registry import DEFAULT_MODEL, MODEL_KEYS


def smoke(model_dir, profile, device_index=0, threads=6, model_key=DEFAULT_MODEL):
    # Weights/configuration must already be local and pinned for this command.
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
    runtime = ClefRuntime(model_dir, threads=threads, profile=profile, device_index=device_index, model_key=model_key)
    request = {'state': 'This is a synthetic setup check. The package has not shipped. Change the delivery address.',
               'questions': {'department': {'type': 'choice', 'instructions': 'Select the department.',
                             'criteria': {'shipping': 'Delivery and package addresses', 'billing': 'Bills and refunds'}}}}
    started = time.perf_counter()
    with redirect_stdout(sys.stderr):
        response = runtime.infer(request)
    status = runtime.status()
    if status['state'] != 'ready' or response.get('benchmark_result') is not False or response.get('truncated') is not False:
        raise RuntimeError('Runtime did not reach the expected verified model state')
    if response['runtime']['profile'] != profile or set(response['probabilities_unrounded']['department']) != {'shipping', 'billing'}:
        raise RuntimeError('Runtime profile or decision options changed unexpectedly')
    return {'status': 'model_smoke_passed', 'benchmark_result': False, 'model_loaded': True,
            'purpose': 'One synthetic schema-valid forward pass; no accuracy or speed claim',
            'elapsed_seconds': time.perf_counter() - started, 'runtime': status,
            'response': response, 'process_model_released_on_exit': True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--profile', choices=PROFILES, default='cpu-nf4')
    parser.add_argument('--model', choices=MODEL_KEYS, default=DEFAULT_MODEL)
    parser.add_argument('--device-index', type=int, default=0)
    parser.add_argument('--threads', type=int, default=6)
    args = parser.parse_args(argv)
    try:
        result = smoke(args.model_dir, args.profile, args.device_index, args.threads, args.model)
    except Exception as error:
        print(json.dumps({'status': 'smoke_failed', 'error': f'{type(error).__name__}: {error}',
                          'benchmark_result': False}))
        return 6
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
