#!/usr/bin/env python3
"""NEWREVISION recovery implementation: 520 never-attempted frozen cases.

This is newly authored code, not recovery of the missing earlier collector.

Default: offline verification only, without reading credentials. Historical files,
scientific inputs and the original response validator are never rewritten. There
is no output-directory resume, failed-case replay, automatic restart or warm-up.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import signal
import time

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'experiments/jev_comparison'
FIRST_RUN = ROOT / 'execution/jev/second-run'
PLAN = ROOT / 'execution/jev/final_continuation_plan.json'
RUNNER_SHA256 = '0cbd708b644944da642c645b09b2820266259e8233c1b73de2278d27fe56f733'
BUNDLE_LOCK_SHA256 = 'c62021bbcb33b94c653cc9649d7d06dcbdf1633d4dc7b7f19dee2db2cb8be2f4'
MANIFEST_SHA256 = 'c41b9b4308c692b64dc85c05d279c62faf74f7d24034a1e4ffaf651ec27d2386'
FIRST_RUN_LOCK_SHA256 = '16eba9a3e8e89bf4666567d07eb937cdd0d7c74ecec5866c937cb7c831d759b0'
PLAN_SHA256 = '7bb0133d6d8dcb4d977b19e6ab59b2eae83250be56053055fd6a905eb7cb32a9'
APPROVAL = 'continue-unattempted-public-text-520-validation-v2'
PRIOR_ATTEMPTS = 454
PRIOR_COMPLETED = 452
PRIOR_FAILED = 2
PRIOR_INPUT_TOKENS = 437597
CONTINUATION_CASES = 520
FIRST_RUN_FILES = {'SOURCE.json', 'attempts.jsonl', 'connection_check.json',
                   'predictions.jsonl', 'run_summary.json', 'validation_diagnostics.jsonl'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


# Execute no imported benchmark code before its immutable source pin passes.
_runner_path = BUNDLE / 'scripts/jev_runner.py'
if _runner_path.is_symlink() or sha(_runner_path.read_bytes()) != RUNNER_SHA256:
    raise ValueError('Frozen runner checksum mismatch')
_spec = importlib.util.spec_from_file_location('continuation_frozen_jev_runner', _runner_path)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)


def require(condition, message):
    if not condition:
        raise runner.ContractError(message)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def locked_file(root, name):
    path = root / name
    require(not root.is_symlink() and not path.is_symlink() and path.is_file(),
            'Expected ordinary locked file')
    require(all(not p.is_symlink() for p in path.parents if p != root.parent),
            'Symlink in locked input path')
    return path.read_bytes()


def verify_bundle(bundle):
    lock_bytes = locked_file(bundle, 'FILE_SHA256.json')
    require(sha(lock_bytes) == BUNDLE_LOCK_SHA256, 'Frozen bundle lock mismatch')
    lock = json.loads(lock_bytes)
    actual = {p.relative_to(bundle).as_posix() for p in bundle.rglob('*')
              if p.is_file() and p.name != 'FILE_SHA256.json' and '__pycache__' not in p.parts}
    require(set(lock) == actual, 'Frozen bundle file set mismatch')
    for name, digest in lock.items():
        require(sha(locked_file(bundle, name)) == digest, 'Frozen bundle file mismatch')
    require(sha(locked_file(bundle, 'manifest.json')) == MANIFEST_SHA256,
            'Frozen manifest mismatch')
    _, requests = runner.load_requests(bundle)
    require(len(requests) == 974 and len({(r['suite'], r['id']) for r in requests}) == 974,
            'Frozen request scope mismatch')
    return requests


def read_json_lines(data):
    require(data.endswith(b'\n'), 'Historical JSONL terminator missing')
    lines = data.splitlines()
    require(all(lines), 'Historical JSONL contains empty lines')
    return [json.loads(line) for line in lines]


def verify_prior(first_run, requests):
    lock_bytes = locked_file(first_run, 'FILE_SHA256.json')
    require(sha(lock_bytes) == FIRST_RUN_LOCK_SHA256, 'Historical lock mismatch')
    hashes = json.loads(lock_bytes)
    require(set(hashes) == FIRST_RUN_FILES, 'Historical allowlist mismatch')
    require({p.name for p in first_run.iterdir()} == FIRST_RUN_FILES | {'FILE_SHA256.json'},
            'Historical file set mismatch')
    data = {}
    for name, digest in hashes.items():
        data[name] = locked_file(first_run, name)
        require(sha(data[name]) == digest, 'Historical file checksum mismatch')
    predictions = read_json_lines(data['predictions.jsonl'])
    events = read_json_lines(data['attempts.jsonl'])
    require(len(predictions) == PRIOR_ATTEMPTS and len(events) == PRIOR_ATTEMPTS * 2,
            'Historical prefix length mismatch')
    tokens = 0
    for index, (record, request) in enumerate(zip(predictions, requests), 1):
        identity = (request['suite'], request['id'])
        body_hash = sha(runner.dumps(request['request']).encode())
        require((record['suite'], record['id']) == identity and record['attempt_count'] == 1,
                'Historical prediction order or attempt mismatch')
        reservation, completion = events[2 * (index - 1):2 * index]
        require(reservation['event'] == 'reserved' and reservation['attempt'] == index
                and reservation['case_attempt'] == 1 and reservation['retry'] is False
                and (reservation['suite'], reservation['id']) == identity
                and reservation['request_body_sha256'] == body_hash
                and reservation['reserved_usd'] == str(runner.RESERVE),
                'Historical reservation reconciliation failed')
        expected_status = 'valid' if index not in (181, 454) else 'invalid_response_or_billing'
        require(completion['event'] == 'completed' and completion['attempt'] == index
                and completion['http_status'] == 200 and completion['status'] == expected_status,
                'Historical completion reconciliation failed')
        if index not in (181, 454):
            require(record['status'] == 'valid' and record['request_body_sha256'] == body_hash
                    and record['source_request_sha256'] == request['source_request_sha256']
                    and record['response_body_sha256'] == completion['response_body_sha256'],
                    'Historical valid response provenance mismatch')
            native = runner.validate_response(request['request'], {
                'model': record['provider_model'], 'answers': record['answers'], 'usage': record['usage']})
            require(record['probabilities_unrounded'] == {
                k: a['probabilities'] for k, a in native['answers'].items()}
                and record['input_tokens'] == native['usage']['input_tokens'],
                'Historical probabilities or billing mismatch')
            tokens += native['usage']['input_tokens']
        else:
            require(identity == {181: ('bank_support80', 'bank_access_tan_01'),
                                 454: ('finance100', 'de_finance_advice_escalation_005')}[index]
                    and record['status'] == 'failed' and record['error_code'] == expected_status
                    and not ({'answers', 'usage', 'input_tokens', 'probabilities_unrounded'} & set(record)),
                    'Historical final technical failure changed')
    require(tokens == PRIOR_INPUT_TOKENS, 'Historical token total mismatch')
    summary = json.loads(data['run_summary.json'])
    expected = {'status': 'halted', 'planned_cases': 974, 'completed_cases': PRIOR_COMPLETED,
                'failed_cases': PRIOR_FAILED, 'remaining_cases': CONTINUATION_CASES,
                'wire_attempts_reserved': PRIOR_ATTEMPTS, 'retry_attempts': 0,
                'capacity_reserved_usd': '1.249640448', 'known_success_input_tokens': PRIOR_INPUT_TOKENS,
                'known_success_cost_usd': '0.018379074', 'cap_usd': '3',
                'manifest_sha256': MANIFEST_SHA256, 'halt_reason': 'invalid_response_or_billing'}
    require(all(summary.get(k) == v for k, v in expected.items()), 'Historical summary mismatch')
    source = json.loads(data['SOURCE.json'])
    require(source['workflow_run_id'] == 37061364247 and source['prior_wire_attempts'] == PRIOR_ATTEMPTS
            and source['prior_retries'] == 0 and source['completed'] == PRIOR_COMPLETED
            and source['failed'] == PRIOR_FAILED and source['unattempted'] == CONTINUATION_CASES,
            'Historical source mismatch')
    check = json.loads(data['connection_check.json'])
    require(check['connection_valid'] is True and check['extra_requests'] == 0,
            'Historical connection metadata mismatch')
    return data, hashes


def build_plan(requests, hashes):
    remaining = requests[PRIOR_ATTEMPTS:]
    return {
        'schema_version': 2,
        'validation_version': 'v2-strict-scoring-quarantine-sum-only',
        'flagged_vectors_are_strict_scoring_failures': True,
        'renormalization_permitted': False,
        'status': 'offline_plan_no_network_no_credential_read',
        'approval': APPROVAL,
        'prior_workflow_run_id': 37061364247,
        'first_run_file_lock_sha256': FIRST_RUN_LOCK_SHA256,
        'first_run_files_sha256': hashes,
        'frozen_manifest_sha256': MANIFEST_SHA256,
        'frozen_runner_sha256': RUNNER_SHA256,
        'endpoint': runner.ENDPOINT,
        'model': runner.MODEL,
        'original_denominator': 974,
        'prior_completed_cases': PRIOR_COMPLETED,
        'prior_failed_cases': PRIOR_FAILED,
        'prior_wire_attempts_reserved': PRIOR_ATTEMPTS,
        'prior_retry_attempts': 0,
        'prior_known_success_input_tokens': PRIOR_INPUT_TOKENS,
        'prior_known_success_cost_usd': '0.018379074',
        'prior_capacity_reserved_usd': '1.249640448',
        'continuation_initial_requests': CONTINUATION_CASES,
        'first_continuation_case_is_gate': True,
        'gate_requires_model_and_billing_not_probability_sum': True,
        'first_continuation_case_retries': 0,
        'retry_previously_attempted_cases': False,
        'copy_historical_prediction_and_ledger_prefix_bytes': True,
        'max_total_attempts_including_prior': runner.MAX_ATTEMPTS,
        'max_global_retries_including_prior': runner.MAX_RETRIES,
        'max_retries_per_new_case': 1,
        'retryable_http_statuses': sorted(runner.RETRYABLE),
        'max_api_usd_including_prior': str(runner.MAX_USD),
        'reserved_usd_per_attempt': str(runner.RESERVE),
        'all_1024_attempts_capacity_reservation_usd': str(runner.RESERVE * runner.MAX_ATTEMPTS),
        'unknown_billing_reservations_never_refunded': True,
        'requests': [{'original_case_number': i, 'suite': r['suite'], 'id': r['id'],
                      'request_body_sha256': sha(runner.dumps(r['request']).encode()),
                      'source_request_sha256': r['source_request_sha256']}
                     for i, r in enumerate(remaining, PRIOR_ATTEMPTS + 1)],
    }


def prepare(bundle=BUNDLE, first_run=FIRST_RUN, plan_path=PLAN):
    requests = verify_bundle(bundle)
    data, hashes = verify_prior(first_run, requests)
    plan_bytes = locked_file(plan_path.parent, plan_path.name)
    require(sha(plan_bytes) == PLAN_SHA256, 'Continuation plan checksum mismatch')
    require(plan_bytes == encoded(build_plan(requests, hashes)), 'Continuation plan scope mismatch')
    return requests, data, json.loads(plan_bytes)


def require_manual_context(env):
    expected = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'storminator89/clef-benchmark',
                'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REF': 'refs/heads/main',
                'GITHUB_RUN_ATTEMPT': '1'}
    require(all(env.get(key) == value for key, value in expected.items()),
            'Only a first manual main-branch continuation is permitted')


# These are exact clauses in the unchanged, pinned validator, never provider text.
CONTRACT_CODES = {
    'Missing or unexpected provider model version': 'provider_model_mismatch',
    'Answer fields mismatch': 'answer_fields_mismatch',
    'Response primitive mismatch': 'response_primitive_mismatch',
    'Probability option keys mismatch': 'probability_option_keys_mismatch',
    'Invalid native probability': 'invalid_native_probability',
    'Probability sum outside tolerance': 'probability_sum_outside_tolerance',
    'Choice is not a native maximum': 'choice_not_native_maximum',
    'Invalid native confidence': 'invalid_native_confidence',
    'Missing or invalid billing units': 'billing_units_missing_or_invalid',
    'Usage exceeds documented capacity reservation': 'usage_exceeds_capacity',
}


def safe_finite(value):
    try:
        return runner.finite(value)
    except (OverflowError, ValueError, TypeError):
        return False


def structural_diagnostic(request, response, code):
    """Whitelist only: no external strings, values, unknown names or error text."""
    require(code in set(CONTRACT_CODES.values()) | {'invalid_json', 'unexpected_validation_exception'},
            'Unknown diagnostic enum')
    result = {'contract_code': code, 'json_object': isinstance(response, dict),
              'expected_answer_fields_count': len(request['questions'])}
    obj = response if isinstance(response, dict) else {}
    answers = obj.get('answers')
    result.update(model_present='model' in obj, model_matches_expected=obj.get('model') == runner.MODEL,
                  answers_object=isinstance(answers, dict))
    known = request['questions']
    if isinstance(answers, dict):
        result.update(answer_fields_count=len(answers),
                      missing_answer_fields_count=len(set(known) - set(answers)),
                      unexpected_answer_fields_count=len(set(answers) - set(known)))
    fields = {}
    for name, question in known.items():
        a = answers.get(name) if isinstance(answers, dict) else None
        entry = {'present': isinstance(answers, dict) and name in answers,
                 'answer_object': isinstance(a, dict)}
        if isinstance(a, dict):
            p = a.get('probabilities')
            entry.update(primitive_is_choice=a.get('type') == 'choice',
                         probabilities_object=isinstance(p, dict),
                         confidence_valid=safe_finite(a.get('confidence')) and 0 <= a['confidence'] <= 1)
            if isinstance(p, dict):
                options = question['criteria']
                entry.update(expected_options_count=len(options), probability_options_count=len(p),
                             missing_options_count=len(set(options) - set(p)),
                             unexpected_options_count=len(set(p) - set(options)))
                exact = set(p) == set(options)
                numeric = exact and all(safe_finite(p[k]) and 0 <= p[k] <= 1 for k in options)
                entry['known_probabilities_finite_in_range'] = numeric
                if numeric:
                    entry['normalization_within_tolerance'] = abs(math.fsum(p[k] for k in options) - 1) <= 1e-5
                    choice = a.get('choice')
                    entry['choice_is_known_option'] = isinstance(choice, str) and choice in options
                    entry['choice_is_native_maximum'] = (entry['choice_is_known_option']
                                                         and p[choice] == max(p.values()))
        fields[name] = entry
    result['expected_fields'] = fields
    usage = obj.get('usage')
    billing = {'usage_object': isinstance(usage, dict)}
    for name in ('input_tokens', 'output_tokens'):
        value = usage.get(name) if isinstance(usage, dict) else None
        valid = type(value) is int and value >= 0
        billing[name + '_valid_nonnegative_integer'] = valid
        if name == 'input_tokens':
            billing['input_tokens_within_reserved_capacity'] = valid and value <= runner.CAPACITY
    result['billing_validity'] = billing
    return result


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def validate_with_diagnostic(request, raw):
    """Validate ALL contracts before accepting a sum-only quarantine.

    No value is normalized, rounded, repaired or replaced. The original pinned
    validator is still the authority for strictly eligible observations.
    """
    response = None
    try:
        require(isinstance(raw, bytes) and len(raw) <= 2_000_000, 'Invalid JSON body')
        response = json.loads(raw, object_pairs_hook=_unique_object,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError, TypeError, RecursionError, runner.ContractError):
        return None, structural_diagnostic(request, None, 'invalid_json')
    try:
        require(isinstance(response, dict) and response.get('model') == runner.MODEL,
                'Missing or unexpected provider model version')
        answers = response.get('answers')
        require(isinstance(answers, dict) and set(answers) == set(request['questions']),
                'Answer fields mismatch')
        sums = {}
        clean = {}
        for field, question in request['questions'].items():
            a = answers[field]
            require(isinstance(a, dict) and a.get('type') == 'choice', 'Response primitive mismatch')
            p = a.get('probabilities')
            require(isinstance(p, dict) and set(p) == set(question['criteria']),
                    'Probability option keys mismatch')
            require(all(safe_finite(v) and 0 <= v <= 1 for v in p.values()), 'Invalid native probability')
            choice = a.get('choice')
            require(isinstance(choice, str) and choice in p and p[choice] == max(p.values()),
                    'Choice is not a native maximum')
            require(safe_finite(a.get('confidence')) and 0 <= a['confidence'] <= 1,
                    'Invalid native confidence')
            total = math.fsum(p.values())
            sums[field] = {'native_sum': total, 'absolute_deviation': abs(total - 1),
                           'normalization_within_tolerance': abs(total - 1) <= 1e-5}
            clean[field] = {key: a[key] for key in ('type', 'choice', 'probabilities', 'confidence')}
        usage = response.get('usage')
        require(isinstance(usage, dict) and all(type(usage.get(k)) is int and usage[k] >= 0
                for k in ('input_tokens', 'output_tokens')), 'Missing or invalid billing units')
        require(usage['input_tokens'] <= runner.CAPACITY, 'Usage exceeds documented capacity reservation')
        native = {'model': response['model'], 'answers': clean,
                  'usage': {k: usage[k] for k in ('input_tokens', 'output_tokens')}}
        if all(entry['normalization_within_tolerance'] for entry in sums.values()):
            return runner.validate_response(request, response), None
        diagnostic = structural_diagnostic(request, response, 'probability_sum_outside_tolerance')
        diagnostic.update(sum_only_deviation=True, strict_scoring_eligible=False,
                          probability_sums=sums)
        return native, diagnostic
    except runner.ContractError as error:
        code = CONTRACT_CODES.get(str(error), 'unexpected_validation_exception')
    except Exception:
        code = 'unexpected_validation_exception'
    return None, structural_diagnostic(request, response, code)


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class BoundedHttpTransport(runner.HttpTransport):
    """Hard wall-clock bound, including slow response trickles (Linux CI only)."""
    def __call__(self, body):
        require(hasattr(signal, 'setitimer'), 'Hard request deadline unavailable')
        def expire(signum, frame):
            raise TimeoutError('Request deadline')
        previous = signal.signal(signal.SIGALRM, expire)
        signal.setitimer(signal.ITIMER_REAL, 95)
        try:
            return super().__call__(body)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)


class ContinuationLedger(runner.Ledger):
    def __init__(self, cap):
        super().__init__(cap)
        require(runner.RESERVE * PRIOR_ATTEMPTS <= self.cap, 'Prior reservations exceed approved cap')
        self.attempts = PRIOR_ATTEMPTS
        self.retries = 0
        self.known_input_tokens = PRIOR_INPUT_TOKENS


def append(stream, value):
    stream.write((runner.dumps(value) + '\n').encode())
    stream.flush()
    os.fsync(stream.fileno())


def run(out, cap, transport, *, bundle=BUNDLE, first_run=FIRST_RUN, plan_path=PLAN,
        sleep=time.sleep, now=time.perf_counter):
    requests, prior, plan = prepare(bundle, first_run, plan_path)
    ledger = ContinuationLedger(cap)
    require(not out.exists() and not out.is_symlink(), 'New output directory required; no resume')
    require(all(not parent.is_symlink() for parent in out.parents),
            'Symlink in output path')
    target = out.resolve()
    for protected in (bundle, first_run, ROOT / 'execution/jev/first-run'):
        require(target != protected.resolve() and protected.resolve() not in target.parents,
                'Output must not modify frozen or historical directories')
    out.mkdir(parents=True)
    # Persist the new directory entry as well as its later ledger files.
    for parent in out.parents:
        fsync_directory(parent)
    summary = {
        'collector_revision': 'newrevision-rebuilt-2026-10-03',
        'validation_version': 'v2-strict-scoring-quarantine-sum-only',
        'flagged_vectors_are_strict_scoring_failures': True,
        'renormalization_permitted': False,
        'current_flagged_native_cases': 0, 'flagged_native_input_tokens': 0,
        'massive_baseline_status': 'pending_missing_offline_overlay',
        'status': 'running', 'started_utc': runner.stamp(), 'endpoint': runner.ENDPOINT,
        'requested_model': runner.MODEL, 'manifest_sha256': MANIFEST_SHA256,
        'continuation_plan_sha256': PLAN_SHA256, 'first_run_file_lock_sha256': FIRST_RUN_LOCK_SHA256,
        'prior_workflow_run_id': 37061364247, 'planned_cases': 974,
        'continuation_planned_cases': CONTINUATION_CASES,
        'prior_completed_cases': PRIOR_COMPLETED, 'prior_failed_cases': PRIOR_FAILED,
        'prior_remaining_cases': CONTINUATION_CASES, 'prior_wire_attempts_reserved': PRIOR_ATTEMPTS,
        'prior_retry_attempts': 0, 'prior_capacity_reserved_usd': '1.249640448',
        'prior_known_success_input_tokens': PRIOR_INPUT_TOKENS,
        'prior_known_success_cost_usd': '0.018379074',
        'current_completed_cases': 0, 'current_failed_cases': 0,
        'current_transport_calls_started': 0, 'completed_cases': PRIOR_COMPLETED, 'failed_cases': PRIOR_FAILED,
        'remaining_cases': CONTINUATION_CASES, 'prior_failed_cases_retried': 0,
        'provider_immutable_weight_hash': None,
        'provider_revision_semantics': 'Versioned service ID only; no public immutable weight checksum',
        'latency_definition': 'HTTP submission through complete body read; per-case total also includes validation and retries/backoff. Network-hosted service, not comparable to Clef CPU forward-only latency.',
        'historical_first_case_latency_note': json.loads(prior['run_summary.json'])['first_case_latency_note'],
        'first_case_latency_note': 'First continuation response is fully validated once; only sum deviations are quarantined, without an extra request. request_seconds excludes validation and connection-check persistence. case_end_to_end_seconds ends after validation and before connection-check persistence.',
        'billing_caveat': 'Known-success usage only; failures and interrupted reservations retain full capacity reservation. This is a local guard, not a provider-enforced account limit.',
    }
    gate = {'connection_valid': False, 'probe_is_first_unattempted_case': True, 'extra_requests': 0,
            'original_case_number': 455, 'status': 'not_attempted'}
    halt = None
    last_start = None
    run_started = now()

    def update_summary():
        summary.update(ledger.status())
        summary['current_wire_attempts_reserved'] = ledger.attempts - PRIOR_ATTEMPTS
        summary['current_retry_attempts'] = ledger.retries
        summary['current_capacity_reserved_usd'] = str(runner.RESERVE * (ledger.attempts - PRIOR_ATTEMPTS))
        summary['current_known_success_input_tokens'] = ledger.known_input_tokens - PRIOR_INPUT_TOKENS
        summary['current_known_success_cost_usd'] = str(runner.Decimal(summary['current_known_success_input_tokens']) * runner.PRICE / 1000000)
        summary['completed_cases'] = PRIOR_COMPLETED + summary['current_completed_cases']
        summary['failed_cases'] = PRIOR_FAILED + summary['current_failed_cases']
        summary['remaining_cases'] = 974 - summary['completed_cases'] - summary['failed_cases']
        summary['attempt_reservations_without_valid_billing'] = ledger.attempts - summary['completed_cases']
        summary['flagged_native_cost_usd'] = str(runner.Decimal(summary['flagged_native_input_tokens']) * runner.PRICE / 1000000)
        summary['attempt_reservations_without_valid_billing'] -= summary['current_flagged_native_cases']
        runner.write(out / 'run_summary.json', summary)

    with (out / 'attempts.jsonl').open('xb') as attempts, \
            (out / 'predictions.jsonl').open('xb') as predictions, \
            (out / 'validation_diagnostics.jsonl').open('xb') as diagnostics, \
            (out / 'flagged_native.jsonl').open('xb') as flagged:
        attempts.write(prior['attempts.jsonl'])
        attempts.flush()
        os.fsync(attempts.fileno())
        predictions.write(prior['predictions.jsonl'])
        predictions.flush()
        os.fsync(predictions.fileno())
        diagnostics.write(prior['validation_diagnostics.jsonl'])
        diagnostics.flush()
        os.fsync(diagnostics.fileno())
        fsync_directory(out)
        runner.write(out / 'connection_check.json', gate)
        update_summary()
        try:
            for index, request in enumerate(requests[PRIOR_ATTEMPTS:]):
                if now() - run_started >= 7200:
                    halt = 'total_time_limit'
                    break
                body = runner.dumps(request['request']).encode()
                body_hash = sha(body)
                approved = plan['requests'][index]
                require((request['suite'], request['id'], body_hash) ==
                        (approved['suite'], approved['id'], approved['request_body_sha256']),
                        'Continuation request differs from locked plan')
                case_start = now()
                case_attempts = 0
                last_error = None
                diagnostic = None
                for retry in (False, True):
                    if retry and ledger.retries >= runner.MAX_RETRIES:
                        break
                    if last_start is not None:
                        sleep(max(0, 1.05 - (now() - last_start)))
                    if now() - run_started >= 7200:
                        halt = 'total_time_limit'
                        break
                    try:
                        ledger.reserve(retry)
                    except runner.BudgetError:
                        halt = 'local_budget_or_attempt_limit'
                        break
                    case_attempts += 1
                    append(attempts, {'suite': request['suite'], 'id': request['id'],
                                     'attempt': ledger.attempts, 'case_attempt': case_attempts,
                                     'retry': retry, 'started_utc': runner.stamp(),
                                     'request_body_sha256': body_hash,
                                     'reserved_usd': str(runner.RESERVE), 'event': 'reserved'})
                    last_start = now()
                    summary['current_transport_calls_started'] += 1
                    try:
                        status, raw, retry_after = transport(body)
                        require(type(status) is int and 100 <= status <= 599
                                and isinstance(raw, bytes)
                                and (retry_after is None or (safe_finite(retry_after) and retry_after >= 0)),
                                'Unexpected transport contract')
                    except Exception:
                        elapsed = now() - last_start
                        last_error = halt = 'transport_failure_unknown_billing'
                        append(attempts, {'attempt': ledger.attempts, 'event': 'completed',
                                          'status': last_error, 'request_seconds': elapsed})
                        if index == 0:
                            gate['status'] = 'first_request_transport_failure'
                            runner.write(out / 'connection_check.json', gate)
                        break
                    elapsed = now() - last_start
                    event = {'attempt': ledger.attempts, 'event': 'completed',
                             'http_status': status, 'request_seconds': elapsed}
                    if status == 200:
                        native, diagnostic = validate_with_diagnostic(request['request'], raw)
                        if native is None:
                            last_error = halt = 'invalid_response_or_billing'
                            event.update(status=last_error, diagnostic=diagnostic, response_body_sha256=sha(raw))
                            append(diagnostics, {'suite': request['suite'], 'id': request['id'],
                                                 'attempt': ledger.attempts, 'diagnostic': diagnostic})
                        elif diagnostic is not None:
                            # A fully checked sum-only deviation is a technical failure, never a score.
                            last_error = 'probability_sum_outside_tolerance'
                            event.update(status='flagged_native', strict_scoring_eligible=False,
                                         diagnostic=diagnostic, response_body_sha256=sha(raw))
                            append(flagged, {
                                'suite': request['suite'], 'id': request['id'],
                                'attempt': ledger.attempts, 'attempt_count': case_attempts,
                                'status': 'flagged_native', 'strict_scoring_eligible': False,
                                'provider_model': native['model'], 'answers': native['answers'],
                                'probabilities_unrounded': {k: a['probabilities'] for k, a in native['answers'].items()},
                                'usage': native['usage'], 'input_tokens': native['usage']['input_tokens'],
                                'request_body_sha256': body_hash, 'response_body_sha256': sha(raw),
                                'source_request_sha256': request['source_request_sha256'],
                                'diagnostic': diagnostic, 'request_seconds': elapsed,
                                'case_end_to_end_seconds': now() - case_start})
                            append(diagnostics, {'suite': request['suite'], 'id': request['id'],
                                                 'attempt': ledger.attempts, 'diagnostic': diagnostic})
                            summary['current_flagged_native_cases'] += 1
                            summary['flagged_native_input_tokens'] += native['usage']['input_tokens']
                        else:
                            ledger.known_input_tokens += native['usage']['input_tokens']
                            event.update(status='valid', response_body_sha256=sha(raw))
                            append(predictions, {
                                'suite': request['suite'], 'id': request['id'], 'status': 'valid',
                                'provider_model': native['model'], 'answers': native['answers'],
                                'probabilities_unrounded': {k: a['probabilities'] for k, a in native['answers'].items()},
                                'usage': native['usage'], 'input_tokens': native['usage']['input_tokens'],
                                'request_seconds': elapsed, 'case_end_to_end_seconds': now() - case_start,
                                'attempt_count': case_attempts, 'request_body_sha256': body_hash,
                                'source_request_sha256': request['source_request_sha256'],
                                'response_body_sha256': sha(raw),
                                'truncation': 'not_reported_by_provider; no client truncation'})
                            summary['current_completed_cases'] += 1
                            last_error = None
                        append(attempts, event)
                        if index == 0:
                            gate.update(connection_valid=native is not None, http_status=status,
                                        status=('flagged_native' if diagnostic is not None else 'valid') if native is not None else 'first_request_contract_failure')
                            if diagnostic is not None:
                                gate['diagnostic'] = diagnostic
                            runner.write(out / 'connection_check.json', gate)
                        break
                    last_error = 'http_' + str(status)
                    event['status'] = last_error
                    append(attempts, event)
                    if index == 0:
                        halt = last_error
                        gate.update(status='first_request_http_failure', http_status=status)
                        runner.write(out / 'connection_check.json', gate)
                        break
                    if status not in runner.RETRYABLE:
                        halt = last_error
                        break
                    if retry:
                        break
                    if retry_after is not None and retry_after > 120:
                        halt = 'retry_after_exceeds_bounded_wait'
                        break
                    if ledger.retries < runner.MAX_RETRIES:
                        sleep(max(2.0, retry_after or 0))
                if last_error and case_attempts:
                    record = {'suite': request['suite'], 'id': request['id'], 'status': 'failed',
                              'error_code': last_error, 'attempt_count': case_attempts,
                              'strict_scoring_eligible': False,
                              'case_end_to_end_seconds': now() - case_start}
                    if diagnostic is not None:
                        record['diagnostic'] = diagnostic
                    append(predictions, record)
                    summary['current_failed_cases'] += 1
                update_summary()
                if halt:
                    break
            summary['status'] = 'halted' if halt else 'completed_with_failures'
        except Exception:
            # Unexpected local exceptions are never serialized or automatically retried.
            summary['status'] = 'halted'
            halt = 'unexpected_local_failure'
        finally:
            summary.update(halt_reason=halt, ended_utc=runner.stamp())
            update_summary()
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--approval', choices=[APPROVAL])
    parser.add_argument('--approved-api-usd', type=runner.Decimal)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    _, _, plan = prepare()
    if not args.execute:
        if args.output is not None:
            with args.output.open('xb') as stream:
                stream.write(encoded(plan))
        else:
            print(json.dumps(plan, indent=2))
        return 0
    require(args.approval == APPROVAL and args.approved_api_usd == runner.MAX_USD,
            'Exact continuation scope and shared 3 USD approval required')
    require(args.output is not None and not args.output.exists() and not args.output.is_symlink(),
            'New output directory required; no resume')
    require_manual_context(os.environ)
    # No credential, inherited PYTHONPATH or arbitrary parent environment enters preflight.
    child_env = {'PYTHONDONTWRITEBYTECODE': '1'}
    subprocess.run([sys.executable, str(BUNDLE / 'scripts/check_bundle.py')], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=child_env)
    token = os.environ.get('JEV_API_KEY', '')
    require(bool(token) and not any(c.isspace() for c in token), 'Missing or malformed repository secret')
    outcome = run(args.output, args.approved_api_usd, BoundedHttpTransport(token))
    print(json.dumps({k: outcome[k] for k in (
        'status', 'completed_cases', 'failed_cases', 'remaining_cases',
        'current_completed_cases', 'current_failed_cases', 'current_wire_attempts_reserved',
        'wire_attempts_reserved', 'retry_attempts', 'capacity_reserved_usd', 'known_success_cost_usd')}))
    return 0 if outcome['remaining_cases'] == 0 and outcome['status'] == 'completed_with_failures' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        print(json.dumps({'status': 'blocked', 'error_code': 'preflight_or_execution_guard_failed'}))
        sys.exit(2)
