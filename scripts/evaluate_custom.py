#!/usr/bin/env python3
"""Validate or sequentially evaluate private custom Clef suites, using only stdlib.

The existing loopback server must already be running. This script never starts a
server, downloads/loads a model, retries an inference, or sends gold labels. A
saved report contains private inputs; keep it out of source control. Resume runs
only pending cases, leaving prior successes and errors unchanged.
"""
from __future__ import annotations

import argparse
import copy
import csv
from datetime import datetime, timezone
import hashlib
import http.client
import io
import json
import math
import os
from pathlib import Path
import re
import signal
import sys
import tempfile
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# server and device_profiles have no ML imports or model-loading side effects.
from server import MAX_BODY, validate_request, validate_result

MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_CASES = 500
MAX_DEPTH = 12
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_REPORT_BYTES = 64 * 1024 * 1024
CASE_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$')
FORBIDDEN_KEYS = {'__proto__', 'prototype', 'constructor'}
REPORT_TYPE = 'custom_suite_evaluation'
RESULT_KEYS = {'id', 'status', 'response', 'error', 'elapsed_seconds'}
IDENTITY_KEYS = {'model_key', 'model_id', 'model', 'revision', 'requested_profile'}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f'Duplicate JSON key: {key}')
        if key in FORBIDDEN_KEYS:
            raise ValueError(f'Unsafe object key: {key}')
        obj[key] = value
    return obj


def check_tree(value, depth=0, max_depth=MAX_DEPTH):
    """Reject unsafe keys, non-finite numbers and invalid Unicode, recursively."""
    if isinstance(value, (dict, list)):
        if depth >= max_depth:
            raise ValueError(f'Maximum nesting depth is {max_depth}')
        if isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(key, str) or key in FORBIDDEN_KEYS:
                    raise ValueError('Object keys must be safe strings')
                check_tree(key, depth + 1, max_depth)
                check_tree(item, depth + 1, max_depth)
        else:
            for item in value:
                check_tree(item, depth + 1, max_depth)
    elif isinstance(value, str):
        try:
            value.encode('utf-8')
        except UnicodeEncodeError as exc:
            raise ValueError('Unpaired Unicode surrogate is not allowed') from exc
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Non-finite JSON numbers are not allowed')


def check_json_depth(text, maximum):
    # Check before json.loads to avoid Python recursion failures on hostile input.
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            if depth > maximum:
                raise ValueError(f'Maximum nesting depth is {maximum}')
        elif char in ']}':
            depth -= 1


def parse_json(text, max_depth=MAX_DEPTH):
    check_json_depth(text, max_depth)
    def bad_constant(value):
        raise ValueError(f'Invalid JSON number: {value}')
    try:
        value = json.loads(text, object_pairs_hook=unique_object,
                           parse_constant=bad_constant)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f'Invalid JSON: {exc}') from exc
    check_tree(value, max_depth=max_depth)
    return value


def read_text(path, maximum=MAX_INPUT_BYTES):
    with Path(path).open('rb') as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError(f'{Path(path).name}: file exceeds {maximum} bytes')
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError(f'{Path(path).name}: expected UTF-8 text') from exc


def wire_request(case):
    """The HTTP contract has exactly these keys; server inserts model internally."""
    return {'state': case['state'], 'questions': case['questions']}


def encode_request(case):
    return json.dumps(wire_request(case), ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def blank_text(value):
    """Use the union of Python and ECMAScript whitespace for blank-only text."""
    return isinstance(value, str) and all(char.isspace() or char == '\ufeff' for char in value)


def validate_suite(value):
    check_tree(value)
    if not isinstance(value, dict) or set(value) != {'schema_version', 'name', 'cases'}:
        raise ValueError('Suite requires exactly schema_version, name and cases')
    if isinstance(value['schema_version'], bool) or value['schema_version'] != 1:
        raise ValueError('schema_version must be the integer 1')
    if not isinstance(value['name'], str) or blank_text(value['name']) or len(value['name']) > 200:
        raise ValueError('Suite name must contain 1–200 characters and not be blank')
    if not isinstance(value['cases'], list) or not 1 <= len(value['cases']) <= MAX_CASES:
        raise ValueError(f'Suite must contain 1–{MAX_CASES} cases')
    seen = set()
    for index, case in enumerate(value['cases'], 1):
        label = f'Case {index}'
        if not isinstance(case, dict) or not {'id', 'state', 'questions'} <= set(case) or set(case) - {'id', 'state', 'questions', 'gold'}:
            raise ValueError(f'{label}: expected id, state, questions and optional gold only')
        if not isinstance(case['id'], str) or not CASE_ID.fullmatch(case['id']):
            raise ValueError(f'{label}: invalid safe case ID (1–64 ASCII characters)')
        if case['id'] in seen:
            raise ValueError(f'{label}: duplicate case ID {case["id"]}')
        seen.add(case['id'])
        try:
            validate_request(wire_request(case))
        except (ValueError, TypeError) as exc:
            raise ValueError(f'{label} ({case["id"]}): {exc}') from exc
        if blank_text(case['state']) or any(blank_text(question['instructions']) or any(blank_text(description) for description in question['criteria'].values()) for question in case['questions'].values()):
            raise ValueError(f'{label}: state, instructions and descriptions cannot contain only whitespace')
        if len(encode_request(case)) > MAX_BODY:
            raise ValueError(f'{label}: serialized HTTP request exceeds {MAX_BODY} bytes')
        if 'gold' in case:
            gold = case['gold']
            if not isinstance(gold, dict):
                raise ValueError(f'{label}: gold must be an object')
            for field, choice in gold.items():
                if field not in case['questions'] or not isinstance(choice, str) or choice not in case['questions'][field]['criteria']:
                    raise ValueError(f'{label}: gold must reference existing fields and choices')
    return {'schema_version': 1, 'name': value['name'], 'cases': value['cases']}



def check_csv_syntax(text):
    # csv.reader(strict=True) still accepts a quote in an unquoted field; reject
    # that ambiguity to match the browser importer rather than silently repair it.
    quoted, closed, at_start = False, False, True
    index = 0
    while index < len(text):
        char = text[index]
        if quoted:
            if char == '"':
                if index + 1 < len(text) and text[index + 1] == '"':
                    index += 1
                else:
                    quoted, closed = False, True
        elif char in ',\r\n':
            closed, at_start = False, True
        elif closed:
            raise ValueError('Invalid CSV: text after closing quote')
        elif char == '"':
            if not at_start:
                raise ValueError('Invalid CSV: unexpected quote in unquoted field')
            quoted, at_start = True, False
        else:
            at_start = False
        index += 1
    if quoted:
        raise ValueError('Invalid CSV: unclosed quoted field')


def load_suite(path, file_format='auto', spec=None):
    path = Path(path)
    if file_format == 'auto':
        file_format = {'.json': 'json', '.jsonl': 'jsonl', '.ndjson': 'jsonl', '.csv': 'csv'}.get(path.suffix.lower())
        if not file_format:
            raise ValueError('Unknown extension; pass --format json, jsonl or csv')
    if file_format != 'csv' and spec is not None:
        raise ValueError('--spec is only valid for CSV input')
    text = read_text(path)
    if file_format == 'json':
        return validate_suite(parse_json(text))
    if file_format == 'jsonl':
        # splitlines would silently treat U+2028 inside a JSON string as a row.
        lines = re.split(r'\r\n|\n|\r', text)
        if lines and lines[-1] == '':
            lines.pop()
        if not 1 <= len(lines) <= MAX_CASES:
            raise ValueError(f'JSONL requires 1–{MAX_CASES} rows')
        cases = []
        for number, line in enumerate(lines, 1):
            if not line.strip():
                raise ValueError(f'JSONL row {number}: blank rows are not allowed')
            try:
                cases.append(parse_json(line))
            except ValueError as exc:
                raise ValueError(f'JSONL row {number}: {exc}') from exc
    elif file_format == 'csv':
        if spec is None:
            raise ValueError('CSV input requires --spec with schema_version and questions')
        questions_spec = parse_json(read_text(spec))
        if not isinstance(questions_spec, dict) or set(questions_spec) != {'schema_version', 'questions'} or isinstance(questions_spec['schema_version'], bool) or questions_spec['schema_version'] != 1:
            raise ValueError('CSV spec requires exactly schema_version:1 and questions')
        questions = questions_spec['questions']
        validate_request({'state': 'CSV schema validation', 'questions': questions})
        check_csv_syntax(text)
        reader = csv.reader(io.StringIO(text, newline=''), strict=True)
        try:
            header = next(reader, None)
            if not header or len(set(header)) != len(header):
                raise ValueError('CSV requires a header without duplicate columns')
            allowed = {'id', 'state'} | {f'gold.{field}' for field in questions}
            if not {'id', 'state'} <= set(header) or set(header) - allowed:
                raise ValueError('CSV columns must be id, state and optional gold.FIELD columns')
            cases = []
            for record_number, row in enumerate(reader, 2):
                if len(row) != len(header):
                    raise ValueError(f'CSV record {record_number}: blank row or wrong column count')
                record = dict(zip(header, row))
                case = {'id': record['id'], 'state': record['state'], 'questions': copy.deepcopy(questions)}
                gold = {field: record[f'gold.{field}'] for field in questions
                        if f'gold.{field}' in record and record[f'gold.{field}'] != ''}
                if gold:
                    case['gold'] = gold
                cases.append(case)
                if len(cases) > MAX_CASES:
                    raise ValueError(f'CSV exceeds {MAX_CASES} cases')
        except csv.Error as exc:
            raise ValueError(f'Invalid CSV: {exc}') from exc
    else:
        raise ValueError(f'Unknown format: {file_format}')
    return validate_suite({'schema_version': 1, 'name': path.stem, 'cases': cases})


def suite_fingerprint(suite):
    """Preserve meaningful question insertion order alongside sorted-key JSON."""
    wrapper = {'suite': suite, 'question_order': [list(case['questions']) for case in suite['cases']]}
    canonical = json.dumps(wrapper, sort_keys=True, ensure_ascii=False,
                           separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(canonical).hexdigest()


def probability(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def validate_response(case, response, identity=None):
    try:
        validate_result(wire_request(case), response)
    except (RuntimeError, TypeError) as exc:
        raise ValueError(str(exc)) from exc
    if response.get('source') != 'live_local_inference' or response.get('benchmark_result') is not False or response.get('truncated') is not False:
        raise ValueError('Response must identify a new local, non-benchmark, untruncated inference')
    if any(not isinstance(response.get(key), str) or not response[key].strip() for key in ('model_key', 'model_id', 'model', 'revision', 'requested_profile')):
        raise ValueError('Response lacks model identity or revision')
    if type(response.get('input_tokens')) is not int or not 0 < response['input_tokens'] <= 2048:
        raise ValueError('Response lacks a valid input token count')
    latency = response.get('latency_ms')
    if isinstance(latency, bool) or not isinstance(latency, (int, float)) or not math.isfinite(latency) or latency < 0:
        raise ValueError('Response lacks valid finite, non-negative forward latency')
    if not isinstance(response.get('runtime'), dict) or not response['runtime']:
        raise ValueError('Response lacks actual runtime metadata')
    if not isinstance(response['runtime'].get('profile'), str) or not response['runtime']['profile'].strip():
        raise ValueError('Response lacks its actual runtime profile')
    if identity is not None and (any(response[key] != identity[key] for key in IDENTITY_KEYS)
                                 or response['runtime']['profile'] != identity['requested_profile']):
        raise ValueError('Response model, revision or runtime profile differs from the pinned run identity')
    if any(response['runtime'].get(key) != response[key] for key in ('model_key', 'model_id', 'revision')):
        raise ValueError('Response runtime model identity differs from its top-level identity')
    if response['runtime']['profile'] != response['requested_profile']:
        raise ValueError('Response runtime profile differs from the requested profile')
    for key in ('device', 'precision'):
        if not isinstance(response.get(key), str) or not response[key] or response['runtime'].get(key) != response[key]:
            raise ValueError(f'Response lacks consistent actual {key} metadata')
    for field, question in case['questions'].items():
        answer = response['answers'][field]
        if set(answer) != {'type', 'choice', 'confidence', 'probabilities'}:
            raise ValueError(f'{field}: incomplete native choice answer')
        rounded = answer['probabilities']
        unrounded = response['probabilities_unrounded'][field]
        if not isinstance(rounded, dict) or set(rounded) != set(question['criteria']) or not all(probability(item) for item in rounded.values()):
            raise ValueError(f'{field}: incomplete or invalid native probabilities')
        # Native probabilities are rounded to four decimals; twelve classes may
        # introduce up to 0.0006 aggregate rounding error.
        if abs(sum(rounded.values()) - 1) > 0.00061:
            raise ValueError(f'{field}: native probabilities do not sum to one')
        if any(abs(rounded[key] - unrounded[key]) > 0.000051 for key in rounded):
            raise ValueError(f'{field}: native and unrounded probabilities disagree')
        choice = answer['choice']
        if not probability(answer['confidence']) or abs(answer['confidence'] - rounded[choice]) > 0.000001:
            raise ValueError(f'{field}: invalid native confidence')
        if unrounded[choice] < max(unrounded.values()) - 1e-7:
            raise ValueError(f'{field}: selected choice is not the highest-probability option')
    return response


def ratio(correct, total):
    return correct / total if total else None


def summarize(suite, results):
    by_id = {result['id']: result for result in results}
    summary = dict.fromkeys(('cases_total', 'cases_succeeded', 'cases_failed', 'cases_pending',
                            'fields_total', 'labelled_fields', 'unlabelled_fields',
                            'evaluated_labelled_fields', 'correct_labelled_fields',
                            'fully_labelled_cases', 'evaluated_fully_labelled_cases',
                            'correct_fully_labelled_cases'), 0)
    by_field = {}
    for case in suite['cases']:
        result = by_id.get(case['id'], {'status': 'pending'})
        successful = result['status'] == 'success'
        summary['cases_total'] += 1
        summary[{'success': 'cases_succeeded', 'error': 'cases_failed', 'pending': 'cases_pending'}[result['status']]] += 1
        gold = case.get('gold', {})
        summary['fields_total'] += len(case['questions'])
        summary['labelled_fields'] += len(gold)
        summary['unlabelled_fields'] += len(case['questions']) - len(gold)
        all_correct = successful
        for field in case['questions']:
            group = by_field.setdefault(field, {'labelled': 0, 'evaluated': 0, 'correct': 0})
            if field not in gold:
                continue
            group['labelled'] += 1
            correct = successful and result['response']['answers'][field]['choice'] == gold[field]
            group['evaluated'] += int(successful)
            group['correct'] += int(correct)
            summary['evaluated_labelled_fields'] += int(successful)
            summary['correct_labelled_fields'] += int(correct)
            all_correct = all_correct and correct
        if len(gold) == len(case['questions']):
            summary['fully_labelled_cases'] += 1
            summary['evaluated_fully_labelled_cases'] += int(successful)
            summary['correct_fully_labelled_cases'] += int(all_correct)
    summary['field_accuracy'] = ratio(summary['correct_labelled_fields'], summary['labelled_fields'])
    summary['field_coverage'] = ratio(summary['evaluated_labelled_fields'], summary['labelled_fields'])
    summary['case_accuracy'] = ratio(summary['correct_fully_labelled_cases'], summary['fully_labelled_cases'])
    summary['case_coverage'] = ratio(summary['evaluated_fully_labelled_cases'], summary['fully_labelled_cases'])
    for group in by_field.values():
        group['accuracy'] = ratio(group['correct'], group['labelled'])
        group['coverage'] = ratio(group['evaluated'], group['labelled'])
    summary['completion_coverage'] = ratio(summary['cases_succeeded'] + summary['cases_failed'], summary['cases_total'])
    summary['prediction_coverage'] = ratio(summary['cases_succeeded'], summary['cases_total'])
    summary['gold_coverage'] = ratio(summary['labelled_fields'], summary['fields_total'])
    summary['by_field'] = by_field
    return summary


def new_report(suite):
    suite = validate_suite(copy.deepcopy(suite))
    now = utc_now()
    report = {'schema_version': 1, 'report_type': REPORT_TYPE, 'benchmark_result': False,
              'suite': suite, 'suite_sha256': suite_fingerprint(suite),
              'created_at': now, 'updated_at': now, 'status': 'validated',
              'result_provenance': 'local_execution',
              'endpoint': None, 'health_before': None, 'health_after': None, 'model_identity': None, 'model_identity_sha256': None,
              'results': [{'id': case['id'], 'status': 'pending', 'response': None,
                           'error': None, 'elapsed_seconds': None} for case in suite['cases']]}
    report['summary'] = summarize(suite, report['results'])
    return report


def load_resume(path, suite):
    report = parse_json(read_text(path, MAX_REPORT_BYTES), max_depth=32)
    if not isinstance(report, dict) or type(report.get('schema_version')) is not int or report['schema_version'] != 1 or report.get('report_type') != REPORT_TYPE or report.get('benchmark_result') is not False:
        raise ValueError('Resume file is not a custom evaluation report v1')
    embedded = validate_suite(report.get('suite'))
    fingerprint = suite_fingerprint(suite)
    if report.get('suite_sha256') != fingerprint or suite_fingerprint(embedded) != fingerprint:
        raise ValueError('Resume fingerprint mismatch: input content or question order changed')
    results = report.get('results')
    if not isinstance(results, list) or len(results) != len(suite['cases']):
        raise ValueError('Resume results must contain every suite case')
    identity = report.get('model_identity')
    if identity is not None:
        validate_identity(identity)
        if report.get('model_identity_sha256') != model_identity_fingerprint(fingerprint, identity):
            raise ValueError('Resume model identity fingerprint mismatch')
    elif report.get('model_identity_sha256') is not None:
        raise ValueError('Resume identity fingerprint has no model identity')
    if any(isinstance(row, dict) and row.get('status') != 'pending' for row in results) and identity is None:
        raise ValueError('Resume report has attempted cases but no pinned model identity')
    for case, result in zip(suite['cases'], results):
        if not isinstance(result, dict) or set(result) != RESULT_KEYS or result['id'] != case['id']:
            raise ValueError('Resume results must match case IDs and order exactly')
        if result['status'] not in {'pending', 'success', 'error'}:
            raise ValueError('Invalid resume case status')
        elapsed = result['elapsed_seconds']
        if elapsed is not None and (not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or not math.isfinite(elapsed) or elapsed < 0):
            raise ValueError('Invalid resume duration')
        if result['status'] == 'success':
            validate_response(case, result['response'], identity)
            if result['error'] is not None:
                raise ValueError('Successful resume result cannot contain an error')
        elif result['status'] == 'pending':
            if result['response'] is not None or result['error'] is not None or elapsed is not None:
                raise ValueError('Pending resume result contains an attempted response')
        elif not isinstance(result['error'], dict) or not isinstance(result['error'].get('message'), str):
            raise ValueError('Failed resume result must retain its error')
    # Never trust a report's saved summary, status, or benchmark designation.
    restored = new_report(suite)
    # Structurally valid saved responses are still user-supplied, never verified.
    restored['result_provenance'] = 'user_supplied_resume_plus_local_execution'
    restored['results'] = results
    for key in ('created_at', 'endpoint', 'health_before', 'health_after', 'model_identity', 'model_identity_sha256'):
        if key in report:
            restored[key] = report[key]
    restored['summary'] = summarize(suite, results)
    return restored



def validate_identity(identity):
    if not isinstance(identity, dict) or set(identity) != IDENTITY_KEYS or any(not isinstance(value, str) or not value.strip() for value in identity.values()):
        raise ValueError('Model identity requires model_key, model_id, model, revision and requested_profile')
    return identity



def model_identity_fingerprint(suite_sha256, identity):
    canonical = json.dumps({'suite_sha256': suite_sha256, 'model_identity': identity},
                           sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def identity_from_health(health):
    return validate_identity({key: health.get(key) for key in IDENTITY_KEYS})


def parse_endpoint(endpoint):
    try:
        parts = urlsplit(endpoint)
        port = 80 if parts.port is None else parts.port
    except ValueError as exc:
        raise ValueError('Invalid loopback endpoint') from exc
    if (parts.scheme != 'http' or parts.hostname not in {'127.0.0.1', 'localhost', '::1'}
            or parts.username is not None or parts.password is not None
            or parts.path not in {'', '/'} or parts.query or parts.fragment
            or any(char.isspace() for char in endpoint) or not 1 <= port <= 65535):
        raise ValueError('Endpoint must be an HTTP loopback origin (127.0.0.1, localhost or [::1])')
    host = parts.hostname
    normalized = f'http://{"[::1]" if host == "::1" else host}:{port}'
    return host, port, normalized


class LocalClient:
    def __init__(self, endpoint, timeout=1800):
        self.host, self.port, self.endpoint = parse_endpoint(endpoint)
        self.timeout = timeout

    def request(self, method, path, body=None):
        # http.client ignores proxy environment variables and never follows a
        # redirect; only our fixed health/infer paths are used.
        connection = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
        headers = {'Accept': 'application/json'}
        if body is not None:
            headers.update({'Content-Type': 'application/json', 'X-Clef-Request': '1'})
        try:
            connection.request(method, path, body, headers)
            response = connection.getresponse()
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError('HTTP response exceeds 1 MiB; response not accepted')
            try:
                text = raw.decode('utf-8-sig')
                value = parse_json(text, max_depth=24)
            except (ValueError, UnicodeDecodeError):
                # Invalid bytes are represented losslessly; never invent JSON.
                value = {'invalid_response_utf8_hex': raw.hex()}
            return response.status, value
        finally:
            connection.close()

    def health(self):
        status, value = self.request('GET', '/api/health')
        if status != 200 or not isinstance(value, dict) or type(value.get('inference_enabled')) is not bool or type(value.get('busy')) is not bool:
            raise ValueError(f'Invalid health response (HTTP {status}): {value}')
        return value


class StopFlag:
    def __init__(self):
        self.requested = False

    def handle(self, _signum, _frame):
        self.requested = True
        print('Stopping after the current request. Pending cases will be preserved.', file=sys.stderr, flush=True)


def atomic_private_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError('Refusing to replace an output symlink')
    descriptor, temporary = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        os.chmod(temporary, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def escape_csv(value):
    text = '' if value is None else str(value)
    if text.startswith(('\t', '\r', '\n')) or re.match(r'^[\s\ufeff]*[=+\-@]', text):
        return "'" + text
    return text


def report_csv(report):
    output = io.StringIO(newline='')
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(('id', 'field', 'status', 'gold', 'prediction', 'correct',
                     'forward_ms', 'elapsed_seconds', 'device', 'precision', 'model', 'revision', 'requested_profile', 'error'))
    for case, result in zip(report['suite']['cases'], report['results']):
        for field in case['questions']:
            gold = case.get('gold', {}).get(field)
            successful = result['status'] == 'success'
            response = result['response'] if isinstance(result['response'], dict) else {}
            answer = response['answers'][field] if successful else {}
            correct = ('true' if successful and answer['choice'] == gold else 'false') if gold is not None else ''
            runtime = response.get('runtime') if isinstance(response.get('runtime'), dict) else {}
            row = (case['id'], field, result['status'], gold, answer.get('choice'), correct,
                   response.get('latency_ms'), result['elapsed_seconds'], runtime.get('device'),
                   runtime.get('precision'), response.get('model'), response.get('revision'),
                   runtime.get('profile'), result['error'].get('message') if result['error'] else '')
            writer.writerow([escape_csv(value) for value in row])
    return '\ufeff' + output.getvalue()


def save_report(report, output, csv_output=None):
    report['updated_at'] = utc_now()
    report['summary'] = summarize(report['suite'], report['results'])
    atomic_private_write(output, json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    if csv_output is not None:
        atomic_private_write(csv_output, report_csv(report))


def run_evaluation(report, client, output, csv_output=None, stop=None):
    stop = stop or StopFlag()
    report['endpoint'] = client.endpoint
    report['status'] = 'running'
    # Saving before any network I/O also checks the output is writable first.
    save_report(report, output, csv_output)
    if not any(result['status'] == 'pending' for result in report['results']):
        report['status'] = 'completed'
        save_report(report, output, csv_output)
        return report
    try:
        health = client.health()
        report['health_before'] = health
        if not health['inference_enabled'] or health['busy']:
            raise ValueError('Local inference is disabled or busy; no cases were submitted')
        identity = identity_from_health(health)
        if report['model_identity'] is not None and report['model_identity'] != identity:
            raise ValueError('Backend model, revision or requested profile changed; no cases were submitted')
        report['model_identity'] = identity
        report['model_identity_sha256'] = model_identity_fingerprint(report['suite_sha256'], identity)
    except (OSError, ValueError, http.client.HTTPException) as exc:
        report['status'] = 'blocked'
        report['run_error'] = {'kind': 'health', 'message': str(exc)}
        save_report(report, output, csv_output)
        return report
    report.pop('run_error', None)
    save_report(report, output, csv_output)
    for case, result in zip(report['suite']['cases'], report['results']):
        if stop.requested:
            break
        if result['status'] != 'pending':
            continue
        # A hard process kill cannot leave this request looking unattempted.
        # The marker is replaced once a response arrives; if it survives a
        # crash, resume preserves the uncertain result instead of retrying it.
        result['status'] = 'error'
        result['error'] = {'kind': 'in_flight', 'message': 'A request was about to be submitted, but no completed response has been saved. It may have reached the server; it will not be retried automatically.'}
        result['elapsed_seconds'] = 0.0
        save_report(report, output, csv_output)
        started = time.perf_counter()
        response = None
        try:
            status, response = client.request('POST', '/api/infer', encode_request(case))
            result['response'] = response
            if status != 200:
                result['status'] = 'error'
                result['error'] = {'kind': 'http', 'http_status': status,
                                   'message': f'Inference returned HTTP {status}', 'body': response}
                if status not in {400, 413, 422}:
                    report['status'] = 'blocked'
            else:
                validate_response(case, response, report['model_identity'])
                result['status'] = 'success'
                result['error'] = None
        except KeyboardInterrupt:
            stop.requested = True
            result['status'] = 'error'
            result['error'] = {'kind': 'interrupted', 'message': 'Request interrupted; it may have reached the server. No response was accepted, and it will not be retried automatically.'}
        except (OSError, ValueError, TypeError, http.client.HTTPException) as exc:
            result['status'] = 'error'
            result['error'] = {'kind': 'response' if response is not None else 'network', 'message': str(exc)}
            report['status'] = 'blocked'
        finally:
            result['elapsed_seconds'] = time.perf_counter() - started
            save_report(report, output, csv_output)
        print(f'{case["id"]}: {result["status"]}', file=sys.stderr, flush=True)
        if report['status'] == 'blocked':
            break
    if report['status'] != 'blocked':
        report['status'] = 'interrupted' if stop.requested and any(row['status'] == 'pending' for row in report['results']) else 'completed'
    try:
        report['health_after'] = client.health()
    except (OSError, ValueError, http.client.HTTPException) as exc:
        report['health_after_error'] = {'kind': 'health', 'message': str(exc)}
    save_report(report, output, csv_output)
    return report


def reserve_output(path, may_replace=False):
    path = Path(path)
    if path.is_symlink() or (path.exists() and not may_replace):
        raise ValueError(f'Output already exists or is a symlink: {path}. Choose a new path or use --resume.')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.exists():
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(descriptor)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Private JSON, JSONL or CSV suite')
    parser.add_argument('--format', choices=('auto', 'json', 'jsonl', 'csv'), default='auto')
    parser.add_argument('--spec', type=Path, help='CSV question-spec JSON')
    parser.add_argument('--output', type=Path, help='Private JSON report (default: user_runs/INPUT.report.json)')
    parser.add_argument('--csv-output', type=Path, help='Optional formula-escaped per-field CSV report')
    parser.add_argument('--endpoint', default='http://127.0.0.1:8765')
    parser.add_argument('--validate-only', action='store_true', help='Validate and write report without any HTTP requests')
    parser.add_argument('--resume', type=Path, help='Resume pending cases from a fingerprint-matching JSON report')
    parser.add_argument('--timeout', type=float, default=1800, help='Per-request timeout in seconds (default: 1800)')
    args = parser.parse_args(argv)
    try:
        if not math.isfinite(args.timeout) or args.timeout <= 0:
            raise ValueError('--timeout must be finite and positive')
        if args.validate_only and args.resume:
            raise ValueError('--validate-only cannot be combined with --resume')
        client = LocalClient(args.endpoint, args.timeout)
        suite = load_suite(args.input, args.format, args.spec)
        report = load_resume(args.resume, suite) if args.resume else new_report(suite)
        output = args.output or args.resume or Path('user_runs') / f'{args.input.stem}.report.json'
        outputs = [output] + ([args.csv_output] if args.csv_output else [])
        forbidden = {args.input.resolve()} | ({args.spec.resolve()} if args.spec else set())
        if len({path.resolve() for path in outputs}) != len(outputs) or any(path.resolve() in forbidden for path in outputs):
            raise ValueError('Input, spec, JSON output and CSV output must be different files')
        if args.resume and args.csv_output and args.csv_output.resolve() == args.resume.resolve():
            raise ValueError('CSV output cannot replace the resume report')
        if args.resume and report['endpoint'] is not None and parse_endpoint(report['endpoint'])[2] != client.endpoint:
            raise ValueError('Resume endpoint changed; pass the original loopback --endpoint')
        # Check every path before reserving any, avoiding partial output on a
        # predictable conflict. Only the explicitly selected resume report may
        # be replaced, plus its explicitly selected CSV export.
        for path in outputs:
            allowed = bool(args.resume and (path == args.csv_output or path.resolve() == args.resume.resolve()))
            if path.is_symlink() or (path.exists() and not allowed):
                raise ValueError(f'Output already exists or is a symlink: {path}')
        for path in outputs:
            reserve_output(path, may_replace=bool(args.resume))
        if args.validate_only:
            save_report(report, output, args.csv_output)
        else:
            stop = StopFlag()
            signals = [signal.SIGINT]
            if hasattr(signal, 'SIGTERM'):
                signals.append(signal.SIGTERM)
            old_handlers = {}
            try:
                for signum in signals:
                    old_handlers[signum] = signal.signal(signum, stop.handle)
                run_evaluation(report, client, output, args.csv_output, stop)
            finally:
                for signum, old_handler in old_handlers.items():
                    signal.signal(signum, old_handler)
        print(f'{report["status"]}: {len(suite["cases"])} cases; report {output}')
        if report['status'] == 'interrupted':
            return 130
        if report['status'] == 'blocked' or report['summary']['cases_failed']:
            return 1
        return 0
    except (OSError, ValueError, TypeError, csv.Error) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
