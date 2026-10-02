#!/usr/bin/env python3
"""Independent post-run integrity/metric checker; standard library only.

Written after inference started but before inspecting predictions. Never imports the
primary scorer or any model library. Actual-result reads require --completed-run.
The original pre-inference audit and manifest are read-only inputs.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import statistics

FIELDS = ('action', 'determination')
CLARIFY = {'ask_fact', 'ask_target', 'resolve_conflict'}
OPTIONS = {'action': {'answer'} | CLARIFY, 'determination': {'yes', 'no', 'unresolved'}}
THRESHOLDS = (0.80, 0.90, 0.95)
EXPECTED_COUNT = 72
EXPECTED_FREEZE_SHA256 = '8eeb30bec0e06776298509328323e6fa2d7849e0d2ff75d03eb922edcf692f6a'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric(value):
    return type(value) in (int, float) and math.isfinite(value)


def ratio(numerator, denominator):
    return {'numerator': numerator, 'denominator': denominator,
            'rate': numerator / denominator if denominator else None}


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    low = int(position)
    return ordered[low] + (ordered[min(low + 1, len(ordered) - 1)] - ordered[low]) * (position - low)


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timezone required')
    return parsed


class Findings:
    def __init__(self):
        self.items = []

    def require(self, condition, location, detail):
        if not condition:
            self.items.append({'location': location, 'detail': detail})
        return bool(condition)

    def json(self, root, name, rows=False):
        try:
            text = (root / name).read_text(encoding='utf-8')
            if rows:
                return [json.loads(line) for line in text.splitlines() if line.strip()]
            return json.loads(text)
        except (OSError, ValueError, TypeError):
            self.require(False, name, 'missing, unreadable, or malformed JSON')
            return None

    def compare(self, expected, actual, location):
        if isinstance(expected, dict):
            if not self.require(isinstance(actual, dict), location, 'expected an object'):
                return
            self.require(set(expected) == set(actual), location, 'object keys differ')
            for key in expected:
                if key in actual:
                    self.compare(expected[key], actual[key], f'{location}.{key}')
        elif isinstance(expected, list):
            if not self.require(isinstance(actual, list) and len(expected) == len(actual), location, 'list type or length differs'):
                return
            for index, (left, right) in enumerate(zip(expected, actual)):
                self.compare(left, right, f'{location}[{index}]')
        elif numeric(expected) and numeric(actual):
            self.require(math.isclose(expected, actual, rel_tol=1e-12, abs_tol=1e-12), location, 'numeric value differs')
        else:
            self.require(type(expected) is type(actual) and expected == actual, location, 'value differs')


def unique_rows(rows, name, findings):
    result = {}
    if not findings.require(isinstance(rows, list), name, 'expected JSONL records'):
        return result
    for index, row in enumerate(rows):
        loc = f'{name}[{index}]'
        if not findings.require(isinstance(row, dict) and isinstance(row.get('id'), str), loc, 'record must have a string ID'):
            continue
        ident = row['id']
        if not findings.require(ident not in result, loc, 'duplicate ID'):
            continue
        result[ident] = row
    return result


def inspect_prediction(row, request, expected_tokens):
    """Validate a prediction without trusting its selected answer or confidence."""
    issues = []
    selected = {}
    choices = {field: None for field in FIELDS}
    if row is None:
        return choices, selected, ['missing_prediction']
    def require(condition, detail):
        if not condition:
            issues.append(detail)
    require(type(row.get('input_tokens')) is int and 0 < row['input_tokens'] <= 2048, 'invalid_input_tokens')
    require(row.get('input_tokens') == expected_tokens, 'tokens_differ_from_frozen_preflight')
    require(row.get('truncated') is False, 'truncation_not_explicitly_false')
    answers = row.get('answers')
    probabilities = row.get('probabilities_unrounded')
    require(isinstance(answers, dict) and set(answers) == set(FIELDS), 'invalid_answer_fields')
    require(isinstance(probabilities, dict) and set(probabilities) == set(FIELDS), 'invalid_probability_fields')
    if isinstance(answers, dict) and isinstance(probabilities, dict):
        for field in FIELDS:
            answer = answers.get(field)
            scores = probabilities.get(field)
            if not isinstance(answer, dict) or not isinstance(scores, dict):
                issues.append(f'{field}:invalid_answer_or_scores')
                continue
            options = set(request['questions'][field]['criteria'])
            choice = answer.get('choice')
            require(answer.get('type') == 'choice' and isinstance(choice, str) and choice in options,
                    f'{field}:invalid_choice')
            require(set(scores) == options, f'{field}:probability_options_differ')
            score_values_valid = all(numeric(value) and 0 <= value <= 1 for value in scores.values())
            require(score_values_valid, f'{field}:invalid_probability')
            if score_values_valid:
                require(abs(sum(scores.values()) - 1.0) < 1e-5, f'{field}:probability_sum')
                if isinstance(choice, str) and choice in scores:
                    require(scores[choice] == max(scores.values()), f'{field}:choice_not_argmax')
                    confidence = answer.get('confidence')
                    require(numeric(confidence) and abs(confidence - scores[choice]) <= 0.00011,
                            f'{field}:confidence_not_selected_score')
                    choices[field] = choice
                    selected[field] = scores[choice]
    for name in ('encode_seconds', 'inference_seconds', 'total_seconds', 'rss_bytes'):
        require(numeric(row.get(name)) and row[name] >= 0, f'invalid_{name}')
    if issues:
        return {field: None for field in FIELDS}, {}, issues
    return choices, selected, []


def recompute(cases, requests, predictions, token_counts):
    """Metric computation independent of the primary scorer implementation."""
    events = {name: [] for name in (
        'invalid_or_missing', 'missed_required_clarifications',
        'required_clarifications_not_successfully_requested', 'excess_clarifications',
        'wrong_clarification_kind', 'inconsistent_fields', 'substantive_answer_cases',
        'risky_wrong_answers')}
    for threshold in THRESHOLDS:
        events[f'confident_answers_{threshold}'] = []
        events[f'confident_wrong_answers_{threshold}'] = []
    records = []
    confusion = {field: defaultdict(Counter) for field in FIELDS}
    valid_rows = []
    for case in cases:
        ident = case['id']
        gold = case['expected']
        row = predictions.get(ident)
        actual, scores, issues = inspect_prediction(row, requests[ident]['request'], token_counts[ident])
        valid = len(issues) == 0
        correct = {field: gold[field] == actual[field] for field in FIELDS}
        exact = all(correct.values())
        required = gold['action'] in CLARIFY
        asked = valid and actual['action'] in CLARIFY
        answered = valid and actual['action'] == 'answer'
        concrete = answered and actual['determination'] in ('yes', 'no')
        risky = concrete and (required or actual['determination'] != gold['determination'])
        if valid:
            valid_rows.append(row)
        else:
            events['invalid_or_missing'].append(ident)
        flags = {
            'missed_required_clarifications': required and answered,
            'required_clarifications_not_successfully_requested': required and not asked,
            'excess_clarifications': not required and asked,
            'wrong_clarification_kind': required and asked and actual['action'] != gold['action'],
            'inconsistent_fields': valid and ((answered and actual['determination'] == 'unresolved') or
                                             (asked and actual['determination'] in ('yes', 'no'))),
            'substantive_answer_cases': concrete,
            'risky_wrong_answers': risky,
        }
        for name, flag in flags.items():
            if flag:
                events[name].append(ident)
        for threshold in THRESHOLDS:
            if concrete and scores['action'] >= threshold and scores['determination'] >= threshold:
                events[f'confident_answers_{threshold}'].append(ident)
                if risky:
                    events[f'confident_wrong_answers_{threshold}'].append(ident)
        for field in FIELDS:
            confusion[field][gold[field]][actual[field] or '__invalid__'] += 1
        records.append({
            'id': ident, 'valid': valid, 'expected': gold, 'predicted': actual,
            'field_correct': correct, 'all_fields_exact': exact, 'selected_probabilities': scores,
            'required_clarification': required, 'model_requested_clarification': asked,
            'risky_wrong_answer': risky, 'technical_issues': issues,
        })
    total = len(cases)
    required_total = sum(case['expected']['action'] in CLARIFY for case in cases)
    answerable = total - required_total
    metrics = {field: ratio(sum(row['field_correct'][field] for row in records), total) for field in FIELDS}
    metrics['all_fields_exact'] = ratio(sum(row['all_fields_exact'] for row in records), total)
    metrics['all_field_decisions'] = ratio(sum(sum(row['field_correct'].values()) for row in records), total * 2)
    count = lambda name: len(events[name])
    behavior = {name: ratio(count(name), denominator) for name, denominator in (
        ('missed_required_clarifications', required_total),
        ('required_clarifications_not_successfully_requested', required_total),
        ('excess_clarifications', answerable), ('wrong_clarification_kind', required_total))}
    behavior['risky_wrong_answers_all_cases'] = ratio(count('risky_wrong_answers'), total)
    behavior['risky_wrong_answers_among_substantive'] = ratio(count('risky_wrong_answers'), count('substantive_answer_cases'))
    high = {}
    for threshold in THRESHOLDS:
        confident = count(f'confident_answers_{threshold}')
        wrong = count(f'confident_wrong_answers_{threshold}')
        high[str(threshold)] = {'confident_answers': confident, 'confident_wrong': wrong,
                               'wrong_rate_among_confident': ratio(wrong, confident)}
    grouped = {}
    for attribute in ('domain', 'stratum', 'family'):
        groups = defaultdict(list)
        for case, record in zip(cases, records):
            groups[case[attribute]].append(record)
        grouped[attribute] = {}
        for name, group in groups.items():
            grouped[attribute][name] = {'cases': len(group),
                'all_fields_exact': ratio(sum(item['all_fields_exact'] for item in group), len(group)),
                **{field: ratio(sum(item['field_correct'][field] for item in group), len(group)) for field in FIELDS}}
    forwards = [row['inference_seconds'] for row in valid_rows]
    tokens = [row['input_tokens'] for row in valid_rows]
    missing = sum(case['id'] not in predictions for case in cases)
    return {
        'suite_id': 'clarification', 'case_count': total, 'field_count': 2,
        'metrics': metrics,
        'denominators': {'clarification_required': required_total, 'answerable': answerable,
                         'valid_cases': len(valid_rows), 'substantive_answers': count('substantive_answer_cases')},
        'behavior_rates': behavior, 'high_confidence': high,
        'events': {name: {'count': len(ids), 'ids': ids} for name, ids in events.items()},
        'confusion_matrices': {field: {gold: dict(values) for gold, values in matrix.items()}
                               for field, matrix in confusion.items()},
        'strata': grouped,
        'technical': {'recorded_predictions': len(predictions), 'valid_cases': len(valid_rows),
                      'missing_predictions': missing, 'invalid_existing_predictions': count('invalid_or_missing') - missing,
                      'input_tokens_min': min(tokens, default=None), 'input_tokens_max': max(tokens, default=None),
                      'forward_seconds_median': statistics.median(forwards) if forwards else None,
                      'forward_seconds_p95': percentile(forwards, .95), 'forward_seconds_total': sum(forwards),
                      'peak_observed_rss_bytes': max((row['rss_bytes'] for row in valid_rows), default=None)},
    }, records


def check(root, *, completed_authorized=False, expected_manifest_sha=EXPECTED_FREEZE_SHA256):
    root = Path(root)
    findings = Findings()
    report = {'checker_schema_version': 1, 'reviewer_identity_type': 'independent_ai_reviewer_task',
              'checker_prepared_without_actual_predictions': True,
              'primary_scorer_imported': False, 'model_loaded': False,
              'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'passed': False, 'prediction_count': None, 'mismatches': findings.items,
              'predictions_sha256': None, 'summary_sha256': None, 'errors_sha256': None,
              'freeze_manifest_sha256': None, 'checker_sha256': sha256(Path(__file__)),
              'recomputed_metrics': None, 'error_ids': [], 'case_scores': []}
    if not findings.require(completed_authorized, 'completion_gate', 'explicit completed-run authorization required'):
        return report
    # Completion gates precede any access to predictions, summary, or errors.
    metadata = findings.json(root, 'results/predictions.metadata.json')
    outcome = findings.json(root, 'results/run_outcome.json')
    metadata_valid = isinstance(metadata, dict) and metadata.get('status') == 'completed' and isinstance(metadata.get('completed_at'), str)
    outcome_valid = isinstance(outcome, dict) and type(outcome.get('exit_code')) is int and outcome['exit_code'] == 0
    findings.require(metadata_valid, 'results/predictions.metadata.json', 'completed metadata required')
    findings.require(outcome_valid, 'results/run_outcome.json', 'actual process exit_code 0 required')
    if not metadata_valid or not outcome_valid:
        return report
    manifest = findings.json(root, 'freeze_manifest.json')
    if not isinstance(manifest, dict):
        return report
    report['freeze_manifest_sha256'] = sha256(root / 'freeze_manifest.json')
    if not findings.require(report['freeze_manifest_sha256'] == expected_manifest_sha, 'freeze_manifest.json', 'manifest differs from independently pinned pre-result hash'):
        return report
    frozen = manifest.get('files', {})
    if not findings.require(isinstance(frozen, dict) and bool(frozen), 'freeze_manifest.json', 'nonempty frozen file map required'):
        return report
    essential = {'PROTOCOL.md', 'data/cases.jsonl', 'data/gold.jsonl', 'data/requests.jsonl', 'data/policy.json',
                 'audit/encoding_preflight.json', 'audit/freeze_approval.json', 'scripts/build_dataset.py',
                 'scripts/score.py', 'reference_runtime/run_clef.py', 'reference_runtime/joint_schema_model.py'}
    findings.require(essential <= set(frozen), 'freeze_manifest.json', 'essential frozen files missing')
    verified = 0
    for name, digest in frozen.items():
        rel = PurePosixPath(name)
        if not findings.require(not rel.is_absolute() and '..' not in rel.parts, 'freeze_manifest.json', 'unsafe file path'):
            continue
        try:
            match = sha256(root / name) == digest
        except OSError:
            match = False
        if findings.require(match, name, 'frozen SHA-256 mismatch or missing file'):
            verified += 1
    report['frozen_files_verified'] = verified
    if findings.items:
        return report
    cases = findings.json(root, 'data/cases.jsonl', rows=True)
    gold = findings.json(root, 'data/gold.jsonl', rows=True)
    requests = findings.json(root, 'data/requests.jsonl', rows=True)
    policy = findings.json(root, 'data/policy.json')
    preflight = findings.json(root, 'audit/encoding_preflight.json')
    if any(item is None for item in (cases, gold, requests, policy, preflight)):
        return report
    case_map = unique_rows(cases, 'data/cases.jsonl', findings)
    gold_map = unique_rows(gold, 'data/gold.jsonl', findings)
    request_map = unique_rows(requests, 'data/requests.jsonl', findings)
    preflight_map = unique_rows(preflight.get('cases'), 'audit/encoding_preflight.json.cases', findings)
    ids = list(case_map)
    for name, rows in (('cases', case_map), ('gold', gold_map), ('requests', request_map), ('preflight', preflight_map)):
        findings.require(len(rows) == EXPECTED_COUNT and list(rows) == ids, name, '72 identical ordered IDs required')
    findings.require(manifest.get('case_count') == EXPECTED_COUNT, 'freeze_manifest.json', 'case count must be 72')
    if findings.items:
        return report
    requests_digest = sha256(root / 'data/requests.jsonl')
    for case in cases:
        ident = case['id']
        findings.compare(case['expected'], gold_map[ident]['expected'], f'data/gold.jsonl.{ident}')
        payload = request_map[ident]['request']
        findings.require(set(payload) == {'model', 'state', 'questions'}, f'data/requests.jsonl.{ident}', 'payload must contain only model/state/questions')
        expected_state = f"Fiktive Testregel:\n{case['rule']}\n\nSynthetische Anfrage und Unterlagen:\n{case['message']}\n\nZu beurteilende Eigenschaft:\n{case['question']}"
        findings.require(payload['state'] == expected_state, f'data/requests.jsonl.{ident}', 'state differs from reviewed case')
        findings.compare(policy['questions'], payload['questions'], f'data/requests.jsonl.{ident}.questions')
        for field in FIELDS:
            findings.require(set(payload['questions'][field]['criteria']) == OPTIONS[field], f'data/policy.json.{field}', 'unexpected options')
        findings.require(preflight_map[ident].get('truncated') is False, f'audit/encoding_preflight.json.{ident}', 'preflight truncation must be false')
    findings.require(preflight.get('requests_sha256') == requests_digest and preflight.get('count') == EXPECTED_COUNT,
                     'audit/encoding_preflight.json', 'preflight request hash/count mismatch')
    meta_expectations = {'request_count': EXPECTED_COUNT, 'request_order_ids': ids, 'requests_sha256': requests_digest,
                        'revision': manifest.get('revision'), 'source_code_sha256': frozen['reference_runtime/joint_schema_model.py'],
                        'runner_sha256': frozen['reference_runtime/run_clef.py'], 'max_length': 2048,
                        'threads': 6, 'batch_size': 1, 'device': 'cpu', 'dtype': 'bfloat16', 'benchmark_requests_only_no_gold': True}
    for key, value in meta_expectations.items():
        findings.compare(value, metadata.get(key), f'results/predictions.metadata.json.{key}')
    packages = metadata.get('packages')
    if not isinstance(packages, dict):
        findings.require(False, 'results/predictions.metadata.json.packages', 'package versions must be an object')
        packages = {}
    for package, version in {'torch': '2.11.0+cpu', 'transformers': '5.10.2', 'bitsandbytes': '0.50.2'}.items():
        findings.require(packages.get(package) == version, f'results/predictions.metadata.json.packages.{package}', 'version differs from frozen protocol')
    try:
        chronology = timestamp(manifest['frozen_at_utc']) <= timestamp(metadata['started_at']) <= timestamp(metadata['completed_at']) <= timestamp(outcome['finished_at_utc'])
    except (AttributeError, KeyError, TypeError, ValueError):
        chronology = False
    findings.require(chronology, 'completion_chronology', 'require freeze <= start <= completion <= process exit with explicit timezones')
    predictions = findings.json(root, 'results/predictions.jsonl', rows=True)
    summary = findings.json(root, 'results/summary.json')
    errors = findings.json(root, 'results/errors.jsonl', rows=True)
    for key, name in (('predictions_sha256', 'results/predictions.jsonl'), ('summary_sha256', 'results/summary.json'), ('errors_sha256', 'results/errors.jsonl')):
        try:
            report[key] = sha256(root / name)
        except OSError:
            pass
    if predictions is None or summary is None or errors is None:
        return report
    if not findings.require(isinstance(summary, dict), 'results/summary.json', 'summary must be an object'):
        return report
    if not findings.require(isinstance(predictions, list), 'results/predictions.jsonl', 'predictions must be a list of records'):
        return report
    report['prediction_count'] = len(predictions)
    prediction_map = unique_rows(predictions, 'results/predictions.jsonl', findings)
    findings.require(len(predictions) == EXPECTED_COUNT and len(prediction_map) == EXPECTED_COUNT, 'results/predictions.jsonl', 'exactly 72 unique predictions required')
    findings.require(list(prediction_map) == ids, 'results/predictions.jsonl', 'prediction IDs or order differ from frozen requests')
    recomputed, records = recompute(cases, request_map, prediction_map, {key: row['input_tokens'] for key, row in preflight_map.items()})
    report['recomputed_metrics'] = recomputed
    report['case_scores'] = records
    report['error_ids'] = [row['id'] for row in records if not row['all_fields_exact']]
    findings.require(not recomputed['events']['invalid_or_missing']['count'], 'results/predictions.jsonl', 'one or more predictions fail technical validation')
    for key, value in recomputed.items():
        findings.compare(value, summary.get(key), f'results/summary.json.{key}')
    provenance = {'requests_sha256': requests_digest, 'gold_sha256': sha256(root / 'data/gold.jsonl'),
                  'predictions_sha256': report['predictions_sha256']}
    findings.compare(provenance, summary.get('provenance'), 'results/summary.json.provenance')
    error_map = unique_rows(errors, 'results/errors.jsonl', findings)
    findings.require(list(error_map) == report['error_ids'], 'results/errors.jsonl', 'error IDs/order differ from recomputation')
    for record in records:
        ident = record['id']
        if record['all_fields_exact'] or ident not in error_map:
            continue
        actual_error = error_map[ident]
        for key, value in record.items():
            # Invalid records already fail validation; distinct implementations need not use identical diagnostics.
            if key != 'technical_issues':
                findings.compare(value, actual_error.get(key), f'results/errors.jsonl.{ident}.{key}')
        for key in ('domain', 'family', 'stratum', 'rule', 'message', 'question', 'rationale', 'clarification_target'):
            findings.compare(case_map[ident][key], actual_error.get(key), f'results/errors.jsonl.{ident}.{key}')
        probabilities = prediction_map.get(ident, {}).get('probabilities_unrounded')
        findings.compare(probabilities, actual_error.get('probabilities_unrounded'), f'results/errors.jsonl.{ident}.probabilities_unrounded')
    report['passed'] = len(findings.items) == 0
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--completed-run', action='store_true', help='Confirm that the author authorized checking the completed actual run')
    args = parser.parse_args()
    report = check(args.root, completed_authorized=args.completed_run)
    destination = args.root / 'audit/independent_result_check.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('passed', 'prediction_count', 'mismatches')}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
