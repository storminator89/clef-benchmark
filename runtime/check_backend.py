"""Check a requested backend without downloading or loading a Clef model.

Run from the repository root: python -m runtime.check_backend --profile rocm-bf16
The optional --test-kernel allocates only a tiny tensor, never model weights.
"""
from __future__ import annotations

import argparse
import json
import sys

from runtime.device_profiles import PROFILES, dtype_for_profile, resolve_profile


def check(torch, profile, device_index=0, test_kernel=False):
    info = resolve_profile(torch, profile, device_index)
    info['model_loaded'] = False
    info['kernel_test'] = 'not_run'
    if test_kernel:
        # This is a backend smoke only, not a test of Clef/Qwen operator coverage.
        with torch.inference_mode():
            value = torch.ones((16, 16), device=info['device'], dtype=dtype_for_profile(torch, profile))
            result = value @ value
            if profile != 'cpu-nf4':
                torch.cuda.synchronize(info['device'])
            if not bool(torch.isfinite(result).all().item()) or float(result[0, 0].item()) != 16.0:
                raise RuntimeError('The selected backend returned an invalid matrix multiplication result')
        info['kernel_test'] = 'passed_tiny_matmul_only'
    return info


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=PROFILES, default='rocm-bf16')
    parser.add_argument('--device-index', type=int, default=0)
    parser.add_argument('--test-kernel', action='store_true', help='Run a tiny matrix multiplication; no model load')
    args = parser.parse_args(argv)
    try:
        import torch
        result = check(torch, args.profile, args.device_index, args.test_kernel)
    except Exception as error:
        print(json.dumps({'status': 'unavailable', 'requested_profile': args.profile,
                          'error': f'{type(error).__name__}: {error}', 'model_loaded': False}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    print(json.dumps({'status': 'backend_detected', **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
