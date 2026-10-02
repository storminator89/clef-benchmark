#!/usr/bin/env python3
"""One explicit real Flash9B/CPU-NF4 custom-case HTTP smoke; never a benchmark.

Uses existing pinned weights/environment only. Preparation mode is model-free.
The caller must verify exclusive model ownership and process exit/RAM release.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'scripts'))
import evaluate_custom as custom
from server import Workbench, make_server
from runtime.model_registry import get_model

SUITE = {'schema_version': 1, 'name': 'Synthetic setup/custom HTTP integration smoke', 'cases': [{
    'id': 'synthetic-feature-smoke-001',
    'state': 'Rein synthetischer Test. Regel: Leihgeräte nur mit blauem Schein ausgeben. Für Drucke genügt grün. Eine Person möchte ein Leihgerät und hat nur einen grünen Schein.',
    'questions': {
        'request_kind': {'type': 'choice', 'instructions': 'Was wird angefragt?',
                         'criteria': {'device': 'Ein Leihgerät', 'print': 'Ein Ausdruck'}},
        'permission': {'type': 'choice', 'instructions': 'Ist die genannte Ausgabevoraussetzung erfüllt?',
                       'criteria': {'allowed': 'Voraussetzung erfüllt', 'denied': 'Voraussetzung nicht erfüllt'}},
        'next_step': {'type': 'choice', 'instructions': 'Wähle den regelkonformen nächsten Schritt.',
                      'criteria': {'issue': 'Leihgerät jetzt ausgeben', 'request_blue': 'Zuerst blauen Schein anfordern'}}},
    'gold': {'request_kind': 'device', 'permission': 'denied', 'next_step': 'request_blue'}}]}
SOURCE_FILES = (
    'scripts/smoke_setup_custom.py', 'scripts/evaluate_custom.py', 'server.py',
    'runtime/live_adapter.py', 'runtime/device_profiles.py', 'runtime/model_registry.py',
    'runtime/model_assets.py', 'runtime/check_backend.py', 'runtime/hardware_probe.py',
    'runtime/hardware_estimates.json', 'runtime/setup.py', 'runtime/smoke_ready.py',
    'runtime/joint_schema_model.py', 'runtime/config.json', 'runtime/joint_head_config.json',
    'runtime/requirements_frozen.txt', 'runtime/model_file_manifest.json',
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


class RecordingClient(custom.LocalClient):
    def __init__(self, endpoint):
        super().__init__(endpoint)
        self.exchanges = []

    def request(self, method, path, body=None):
        status, value = super().request(method, path, body)
        self.exchanges.append({'method': method, 'path': path, 'status': status,
                               'body_sha256': hashlib.sha256(body).hexdigest() if body else None})
        return status, value


def verify(report, runtime_status, exchanges):
    case = SUITE['cases'][0]
    row = report['results'][0]
    response = row['response']
    spec = get_model('flash-9b')
    custom.validate_response(case, response, report['model_identity'])
    return {
        'custom_evaluator_completed': report['status'] == 'completed' and row['status'] == 'success',
        'exactly_one_real_http_200_post': [x['status'] for x in exchanges if x['method'] == 'POST'] == [200],
        'request_has_only_state_questions': set(json.loads(custom.encode_request(case))) == {'state', 'questions'},
        'three_fields_in_request_order': list(response['answers']) == list(case['questions']),
        'full_option_ids_and_finite_normalized_probabilities': all(
            set(response['probabilities_unrounded'][field]) == set(question['criteria'])
            and all(isinstance(p, (int, float)) and not isinstance(p, bool) and math.isfinite(p) and 0 <= p <= 1
                    for p in response['probabilities_unrounded'][field].values())
            and abs(sum(response['probabilities_unrounded'][field].values()) - 1) <= 1e-5
            for field, question in case['questions'].items()),
        'actual_identity': response['model_key'] == 'flash-9b' and response['model_id'] == spec['repo_id']
                           and response['revision'] == spec['revision'] and response['runtime']['profile'] == 'cpu-nf4',
        'cold_lazy_load': report['health_before']['runtime_state'] == 'unloaded',
        'state_ready': runtime_status['state'] == 'ready' and report['health_after']['runtime_state'] == 'ready',
        'one_successful_request': runtime_status['successful_requests'] == 1,
        'finite_latency': math.isfinite(response['inference_seconds']) and response['inference_seconds'] > 0
                          and math.isfinite(response['latency_ms']) and response['latency_ms'] > 0
                          and math.isfinite(row['elapsed_seconds']) and row['elapsed_seconds'] > 0,
        'no_truncation': response['truncated'] is False and 0 < response['input_tokens'] <= 2048,
        'excluded_from_benchmarks': report['benchmark_result'] is False and response['benchmark_result'] is False,
        'no_busy_request': report['health_after']['busy'] is False,
    }


def run(model_dir, output):
    import psutil
    available_before = psutil.virtual_memory().available
    if available_before < 7.5 * 1024**3:
        raise RuntimeError('Less than 7.5 GiB available RAM; no model started')
    for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY', 'HF_HUB_DISABLE_IMPLICIT_TOKEN'):
        os.environ[key] = '1'
    sources = {name: digest(ROOT/name) for name in SOURCE_FILES}
    started = now()
    app = Workbench(enabled=True, model_dir=model_dir, profile='cpu-nf4', model_key='flash-9b')
    server = make_server(port=0, app=app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = RecordingClient(f'http://127.0.0.1:{server.server_address[1]}')
        with tempfile.TemporaryDirectory(prefix='clef-synthetic-smoke-') as td:
            report = custom.run_evaluation(custom.new_report(SUITE), client, Path(td)/'report.json')
        if report['status'] != 'completed' or report['results'][0]['status'] != 'success':
            raise RuntimeError('Custom HTTP smoke failed: ' + json.dumps(report.get('run_error') or report['results'][0]['error']))
        runtime = app.runtime.status()
        assertions = verify(report, runtime, client.exchanges)
        assertions['source_files_unchanged_during_run'] = sources == {name: digest(ROOT/name) for name in SOURCE_FILES}
        proof = {
            'schema_version': 1, 'status': 'pass' if all(assertions.values()) else 'failed_assertions',
            'purpose': 'One genuine current-source custom-case HTTP smoke; excluded from every benchmark statistic.',
            'input_origin': 'New assistant-authored short synthetic request, no personal data or historical benchmark input.',
            'benchmark_result': False, 'benchmark_inclusion': False,
            'started_at_utc': started, 'completed_at_utc': now(),
            'assertions': assertions, 'custom_evaluation_report': report, 'http_exchanges': client.exchanges,
            'runtime_status': runtime, 'source_files_sha256': sources,
            'model_manifest_sha256': digest(ROOT/'runtime/model_file_manifest.json'),
            'actual_loaded_vendor_source_sha256': digest(model_dir/'joint_schema_model.py'),
            'scope_limits': ['Uses existing verified weights/environment: no fresh installation or download.',
                             'One HTTP call exercises the same ClefRuntime.infer path used by smoke_ready; no duplicate model load.',
                             'The installer lifecycle remains mock-tested only.',
                             'CPU-BF16, AMD ROCm and 27B remain not hardware-validated.',
                             'No browser visual QA or screenshot evidence.',
                             'Gold labels remain outside the model request; one smoke is not benchmark accuracy evidence.',
                             'Process exit and RAM release are recorded separately by the caller.']}
        with output.open('x', encoding='utf-8') as f:
            json.dump(proof, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')
        print(json.dumps({'status': proof['status'], 'input_tokens': report['results'][0]['response']['input_tokens'],
                          'inference_seconds': report['results'][0]['response']['inference_seconds']}), flush=True)
        return 0 if all(assertions.values()) else 1
    finally:
        server.shutdown(); server.server_close(); thread.join()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--confirm-exclusive-runtime', action='store_true')
    parser.add_argument('--model-dir', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'qa/setup_custom_smoke.json')
    args = parser.parse_args(argv)
    custom.validate_suite(SUITE)
    if not args.run:
        print(json.dumps({'mode': 'prepare_only_no_inference', 'suite': SUITE}, ensure_ascii=False, indent=2)); return 0
    if not args.confirm_exclusive_runtime or args.model_dir is None or not args.model_dir.is_dir():
        parser.error('Run requires --confirm-exclusive-runtime and existing --model-dir')
    if args.output.exists() or not args.output.parent.is_dir():
        parser.error('Output must be new, with an existing parent; historical proofs are never overwritten')
    return run(args.model_dir, args.output)


if __name__ == '__main__':
    raise SystemExit(main())
