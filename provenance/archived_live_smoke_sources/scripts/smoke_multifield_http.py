#!/usr/bin/env python3
"""One opt-in, real CPU-NF4 HTTP smoke; never part of any benchmark score.

Without --run this only validates and prints the fresh synthetic request. A real
run requires a locally installed pinned runtime, existing weights, and explicit
confirmation that earlier inference has exited and released memory. No download,
installation, browser, alternate host, or inference retry is performed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import http.client
from importlib.metadata import version
import json
from pathlib import Path
import platform
import resource
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server import MAX_BODY, Workbench, make_server, validate_request, validate_result
from runtime.live_adapter import EXPECTED_FILES, MODEL_ID, REVISION, SOURCE_SHA256

REQUEST = {
    'state': (
        'Vollständig synthetischer Funktionstest, kein realer Vorgang. '
        'Fiktive Materialausgabe. K1: Zur Ausgabe von Leihgeräten ist ein blauer '
        'Berechtigungsschein erforderlich. K2: Für Papierausdrucke genügt ein grüner '
        'Berechtigungsschein. Sachverhalt: Eine Person möchte ein Leihgerät erhalten '
        'und zeigt ausschließlich einen grünen Berechtigungsschein. '
        'Zu prüfende Aussage: Die genannte Voraussetzung für die Leihgeräteausgabe ist erfüllt.'
    ),
    'questions': {
        'decision': {
            'type': 'choice',
            'instructions': 'Prüfe die Aussage ausschließlich anhand der ausdrücklich genannten fiktiven Regeln und des Sachverhalts.',
            'criteria': {
                'ja': 'Die genannte Voraussetzung ist erfüllt.',
                'nein': 'Die genannte Voraussetzung ist nicht erfüllt.',
                'offen': 'Der Text reicht nicht aus, um die Aussage zu beurteilen.',
                'konflikt': 'Die Angaben widersprechen sich und erlauben keine eindeutige Beurteilung.',
            },
        },
        'evidence': {
            'type': 'choice',
            'instructions': 'Welche Fundstelle enthält die für die Prüfung der Leihgeräteausgabe entscheidende Regel?',
            'criteria': {
                'b1': 'K1: Blauer Berechtigungsschein für Leihgeräte.',
                'b2': 'K2: Grüner Berechtigungsschein für Papierausdrucke.',
                'b3': 'Keine passende Fundstelle vorhanden.',
            },
        },
    },
}
# These labels stay outside the HTTP request and model input.
EXPECTED_ANSWERS = {'decision': 'nein', 'evidence': 'b1'}
SOURCE_FILES = (
    'scripts/smoke_multifield_http.py', 'server.py', 'runtime/live_adapter.py',
    'runtime/device_profiles.py', 'runtime/joint_schema_model.py',
    'runtime/config.json', 'runtime/joint_head_config.json',
    'runtime/requirements_frozen.txt', 'runtime/model_file_manifest.json',
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def request_bytes():
    validate_request(REQUEST)
    encoded = json.dumps(REQUEST, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    if len(encoded) > MAX_BODY:
        raise ValueError('Smoke request exceeds the HTTP body limit')
    return encoded


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_environment():
    return {
        'python': platform.python_version(),
        'system': platform.system(),
        'machine': platform.machine(),
        'packages': {name: version(name) for name in (
            'torch', 'torchvision', 'transformers', 'bitsandbytes',
            'tokenizers', 'psutil', 'accelerate', 'safetensors',
        )},
    }


def exchange(port, method, path, body=None):
    # The origin/headers go through the real server checks. No direct infer call.
    headers = {'Origin': f'http://127.0.0.1:{port}'}
    if body is not None:
        headers.update({'Content-Type': 'application/json', 'X-Clef-Request': '1'})
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=1800)
    started = time.perf_counter()
    try:
        connection.request(method, path, body, headers)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), json.loads(response.read()), time.perf_counter() - started
    finally:
        connection.close()


def verify_response(response, before, after, runtime_status, headers):
    validate_result(REQUEST, response)
    return {
        'http_status_200': True,
        'source_is_live_local_inference': response.get('source') == 'live_local_inference',
        'both_questions_in_request_order': list(response['answers']) == list(REQUEST['questions']),
        'every_option_has_unrounded_probability': all(
            set(response['probabilities_unrounded'][name]) == set(question['criteria'])
            for name, question in REQUEST['questions'].items()),
        'native_answers_have_complete_fields': all(
            set(answer) == {'type', 'choice', 'confidence', 'probabilities'}
            for answer in response['answers'].values()),
        'native_answers_have_all_options': all(
            isinstance(response['answers'][name].get('probabilities'), dict)
            and set(response['answers'][name]['probabilities']) == set(question['criteria'])
            for name, question in REQUEST['questions'].items()),
        'decision_matches_prespecified_expectation': response['answers']['decision']['choice'] == EXPECTED_ANSWERS['decision'],
        'evidence_matches_prespecified_expectation': response['answers']['evidence']['choice'] == EXPECTED_ANSWERS['evidence'],
        'nothing_truncated': response.get('truncated') is False,
        'within_2048_token_limit': type(response.get('input_tokens')) is int and 0 < response['input_tokens'] <= 2048,
        'not_a_benchmark_result': response.get('benchmark_result') is False,
        'correct_model_and_revision': response.get('model') == MODEL_ID and response.get('revision') == REVISION,
        'cold_start_was_lazy': before.get('model_loaded') is False and before.get('runtime_state') == 'unloaded',
        'actual_runtime_is_ready': after.get('model_loaded') is True and after.get('runtime_state') == 'ready',
        'first_call_loaded_model': response.get('first_call_after_load') is True,
        'exactly_one_successful_request': runtime_status.get('successful_requests') == 1,
        'cpu_nf4_profile_verified': response.get('device') == 'cpu' and response.get('runtime', {}).get('profile') == 'cpu-nf4'
                                    and response['runtime'].get('quantization') == 'nf4-double',
        'memory_and_token_configuration': runtime_status.get('threads') == 6 and runtime_status.get('max_length') == 2048,
        'no_request_left_busy': after.get('busy') is False,
        'security_headers_preserved': headers.get('Cache-Control') == 'no-store'
                                      and headers.get('X-Content-Type-Options') == 'nosniff'
                                      and "connect-src 'self'" in headers.get('Content-Security-Policy', '')
                                      and 'Access-Control-Allow-Origin' not in headers,
    }


def run_smoke(model_dir, output):
    """Caller must have confirmed prior process exit and memory release."""
    import psutil
    body = request_bytes()
    available_before = psutil.virtual_memory().available
    if available_before < 7.5 * 1024**3:
        raise RuntimeError('Less than 7.5 GiB available RAM; real smoke not started')
    if digest(model_dir / 'joint_schema_model.py') != SOURCE_SHA256:
        raise RuntimeError('Existing pinned vendor source differs; real smoke not started')
    environment = public_environment()
    source_hashes = {name: digest(ROOT / name) for name in SOURCE_FILES}
    started_at = utc_now()
    started = time.perf_counter()
    app = Workbench(enabled=True, model_dir=model_dir, profile='cpu-nf4')
    server = make_server(port=0, app=app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        if server.server_address[0] != '127.0.0.1':
            raise RuntimeError('Smoke server did not bind loopback')
        status_before, _, before, _ = exchange(port, 'GET', '/api/health')
        if status_before != 200 or app.runtime is not None:
            raise RuntimeError('Initial health/lazy-load check failed')
        print('Starting exactly one real local CPU-NF4 multiquestion HTTP request.', flush=True)
        status, headers, response, http_seconds = exchange(port, 'POST', '/api/infer', body)
        status_after, _, after, _ = exchange(port, 'GET', '/api/health')
        if status != 200 or status_after != 200:
            raise RuntimeError(f'Real smoke HTTP status: inference={status}, health={status_after}; no successful evidence written')
        runtime_status = app.runtime.status()
        assertions = verify_response(response, before, after, runtime_status, headers)
        assertions['source_files_unchanged_during_run'] = source_hashes == {
            name: digest(ROOT / name) for name in SOURCE_FILES}
        evidence = {
            'schema_version': 1,
            'status': 'pass' if all(assertions.values()) else 'failed_assertions',
            'purpose': 'One real new-input multiquestion HTTP integration smoke; excluded from every benchmark score.',
            'input_origin': 'Fresh assistant-authored synthetic material-desk scenario created only for this HTTP smoke; not an insurance benchmark case, replay, or test-double output.',
            'benchmark_inclusion': False,
            'started_at_utc': started_at,
            'completed_at_utc': utc_now(),
            'request': REQUEST,
            'request_serialization': 'UTF-8 JSON, ensure_ascii=False, compact separators, insertion order retained',
            'request_body_bytes': len(body),
            'request_body_sha256': hashlib.sha256(body).hexdigest(),
            'expected_answers_not_sent_to_model': EXPECTED_ANSWERS,
            'response': response,
            'assertions': assertions,
            'health_before': before,
            'health_after': after,
            'runtime_status': runtime_status,
            'http': {'method': 'POST', 'path': '/api/infer', 'loopback_only': True,
                     'status': status, 'headers': headers, 'elapsed_seconds': http_seconds},
            'total_elapsed_seconds': time.perf_counter() - started,
            'environment': environment,
            'source_files_sha256': source_hashes,
            'inference_configuration': {'profile': 'cpu-nf4', 'threads': 6, 'batch_size': 1,
                                        'max_length': 2048, 'seed': 20261002,
                                        'backbone_quantization': 'NF4, double quantization',
                                        'compute_dtype': 'bfloat16',
                                        'joint_head_and_output_embeddings_dtype': 'bfloat16'},
            'model': {'id': MODEL_ID, 'revision': REVISION,
                      'actual_loaded_vendor_source_sha256': digest(model_dir / 'joint_schema_model.py'),
                      'verified_release_files': EXPECTED_FILES},
            'resources': {'available_ram_before_bytes': available_before,
                          'available_ram_after_response_bytes': psutil.virtual_memory().available,
                          'process_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024},
            'scope_limits': ['One cold-start request; no throughput or general quality claim.',
                             'Actual CPU-NF4 execution only; AMD ROCm remains model-free-tested.',
                             'Expected labels were never transmitted to the model.',
                             'Process exit and subsequent RAM release must be verified by the invoking caller.'],
        }
        # No model directory, executable path, command line, hostname, or raw log
        # is included. Refuse replacement of earlier evidence.
        with output.open('x', encoding='utf-8') as stream:
            json.dump(evidence, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
        print(json.dumps({'status': evidence['status'], 'input_tokens': response['input_tokens'],
                          'answers': {name: answer['choice'] for name, answer in response['answers'].items()},
                          'inference_seconds': response['inference_seconds'],
                          'http_elapsed_seconds': http_seconds}, ensure_ascii=False), flush=True)
        return 0 if all(assertions.values()) else 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='Explicitly execute one real local model request')
    parser.add_argument('--confirm-exclusive-runtime', action='store_true',
                        help='Confirm earlier inference has exited and released RAM; never run in parallel')
    parser.add_argument('--model-dir', type=Path, help='Existing pinned local model directory; never downloaded')
    parser.add_argument('--output', type=Path, default=ROOT / 'qa/live_multifield_smoke.json',
                        help='New sanitized evidence file; an existing file is never overwritten')
    args = parser.parse_args(argv)
    body = request_bytes()
    if not args.run:
        print(json.dumps({'mode': 'prepare_only_no_inference', 'request': REQUEST,
                          'expected_answers_not_sent_to_model': EXPECTED_ANSWERS,
                          'body_bytes': len(body), 'body_sha256': hashlib.sha256(body).hexdigest()},
                         ensure_ascii=False, indent=2))
        return 0
    if not args.confirm_exclusive_runtime:
        parser.error('--run requires --confirm-exclusive-runtime after prior inference has exited and freed RAM')
    if args.model_dir is None or not args.model_dir.is_dir():
        parser.error('--run requires an existing --model-dir')
    if args.output.exists():
        parser.error('Evidence already exists; choose a new --output instead of overwriting it')
    if not args.output.parent.is_dir():
        parser.error('Output parent directory must already exist')
    return run_smoke(args.model_dir, args.output)


if __name__ == '__main__':
    raise SystemExit(main())
