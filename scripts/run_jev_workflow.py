#!/usr/bin/env python3
"""Manually approved Jev run, with the first frozen case as a fail-closed probe.

No extra request: the successful probe remains the first prediction and uses the
same reservation ledger as the remaining cases. The frozen runner is unchanged.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'experiments/jev_comparison'
spec = importlib.util.spec_from_file_location('frozen_jev_runner', BUNDLE / 'scripts/jev_runner.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def require_manual_context(env):
    expected = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'storminator89/clef-benchmark',
                'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REF': 'refs/heads/main',
                'GITHUB_RUN_ATTEMPT': '1'}
    if any(env.get(key) != value for key, value in expected.items()):
        raise runner.ContractError('Only a first manual main-branch run is permitted')


class FirstCaseGate:
    """Only safe status metadata is persisted; error bodies/headers are never kept."""
    def __init__(self, transport, destination):
        self.transport = transport
        self.destination = destination
        self.first = True

    def __call__(self, body):
        if not self.first:
            return self.transport(body)
        self.first = False
        result = {'secret_present': True, 'connection_valid': False,
                  'probe_is_first_frozen_case': True, 'extra_requests': 0}
        try:
            status, raw, delay = self.transport(body)
            result['http_status'] = status
            if status != 200:
                result['status'] = 'first_request_http_failure'
                raise runner.ContractError('First request failed')
            runner.validate_response(json.loads(body), json.loads(raw))
            result.update(status='valid', connection_valid=True)
            return status, raw, delay
        except Exception:
            result.setdefault('status', 'first_request_transport_or_contract_failure')
            raise runner.ContractError('First request did not validate') from None
        finally:
            runner.write(self.destination, result)
            print(json.dumps(result), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--approval', choices=['one-pass-public-text-974'])
    parser.add_argument('--approved-api-usd', type=runner.Decimal)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.execute:
        runner.write(args.output, runner.make_plan(BUNDLE))
        return 0
    if args.approval != 'one-pass-public-text-974' or args.approved_api_usd != runner.MAX_USD:
        raise runner.ContractError('Exact bounded approval required')
    require_manual_context(os.environ)
    # Verify the public code/input lock before reading a credential.
    import subprocess
    subprocess.run([sys.executable, str(BUNDLE / 'scripts/check_bundle.py')], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   env={k: os.environ[k] for k in os.environ if k != 'JEV_API_KEY'})
    token = os.environ.get('JEV_API_KEY', '')
    present = bool(token)
    print(json.dumps({'secret_present': present}), flush=True)
    if not present or any(c.isspace() for c in token):
        raise runner.ContractError('Missing or malformed repository secret')
    transport = FirstCaseGate(runner.HttpTransport(token), args.output / 'connection_check.json')
    outcome = runner.run(BUNDLE, args.output, args.approved_api_usd, transport)
    outcome['first_case_latency_note'] = ('The first case request_seconds additionally includes connection-gate validation and safe-status persistence; subsequent cases use the frozen runner timing definition.')
    runner.write(args.output / 'run_summary.json', outcome)
    print(json.dumps({k: outcome[k] for k in ['status', 'completed_cases', 'failed_cases',
                     'remaining_cases', 'wire_attempts_reserved', 'capacity_reserved_usd',
                     'known_success_cost_usd']}), flush=True)
    return 0 if outcome['status'] == 'complete' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({'status': 'blocked', 'error_type': type(error).__name__}), flush=True)
        sys.exit(2)
