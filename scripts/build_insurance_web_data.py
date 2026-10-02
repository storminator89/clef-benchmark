#!/usr/bin/env python3
"""Import complete, independently verified insurance results, or explicit test-only cases.

The importer never runs inference and never normalizes/rounds model probabilities.
Use --cases-only for an unfrozen development preview with no results or scores.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'Cloudflare/clef-flash'
REVISION = '17f0b0ad64efb65d273590632833508766b2aae6'
OFFICIAL_SOURCE_SHA256 = '0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3'
SPLIT = 'german_insurance_primary'
FIELDS = ('decision', 'evidence')
CASE_COUNT = 60
DOCUMENT_COUNT = 12


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError(f'Missing/unreadable artifact: {path.name}') from exc


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f'Non-finite JSON number: {value}')


def load_json(path, jsonl=False):
    try:
        content = path.read_text(encoding='utf-8')
        parse = lambda text: json.loads(text, object_pairs_hook=unique_object,
                                       parse_constant=reject_constant)
        return [parse(line) for line in content.splitlines() if line.strip()] if jsonl else parse(content)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'Missing or invalid JSON artifact: {path.name}') from exc


def canonical_state(state):
    """Exactly the pinned vendor render(dict) representation (no pretty-printing)."""
    return json.dumps(state, ensure_ascii=False, separators=(',', ':'), sort_keys=True,
                      allow_nan=False)


def number(value, minimum=0):
    return type(value) in (int, float) and math.isfinite(value) and value >= minimum


def index_rows(rows, name, expected_ids=None):
    require(isinstance(rows, list), f'{name} must be an array')
    require(all(isinstance(row, dict) and isinstance(row.get('id'), str) for row in rows),
            f'Invalid {name} rows')
    mapped = {row['id']: row for row in rows}
    require(len(mapped) == len(rows), f'Duplicate {name} ids')
    if expected_ids is not None:
        require(set(mapped) == set(expected_ids), f'Missing or unknown {name} ids')
    return mapped


def input_directory(source, cases_only):
    source = Path(source)
    if (source / 'benchmark.json').is_file():
        return source
    if (source / 'public' / 'benchmark.json').is_file():
        return source / 'public'
    if cases_only and (source / 'benchmark' / 'benchmark.json').is_file():
        return source / 'benchmark'
    raise ValueError('Expected public/benchmark.json and requests.jsonl; candidate benchmark/ is cases-only')


def validate_inputs(benchmark, requests):
    require(isinstance(benchmark, dict), 'Invalid benchmark')
    metadata = benchmark['metadata']
    cases = benchmark['cases']
    documents = benchmark['documents']
    require(metadata.get('case_count') == CASE_COUNT and len(cases) == CASE_COUNT,
            'Expected 60 benchmark cases')
    require(metadata.get('document_count') == DOCUMENT_COUNT and len(documents) == DOCUMENT_COUNT,
            'Expected 12 documents')
    require(metadata.get('synthetic') is True and metadata.get('language') == 'de',
            'Expected synthetic German benchmark')
    require(metadata.get('fields') == list(FIELDS), 'Unexpected benchmark fields')
    areas = metadata['areas']
    require(isinstance(areas, list) and len(areas) == len(set(areas)) == 6,
            'Expected six unique areas')
    bycase = index_rows(cases, 'cases')
    bydoc = index_rows(documents, 'documents')
    byrequest = index_rows(requests, 'requests', bycase)
    require(Counter(c['area'] for c in cases) == Counter({area: 10 for area in areas}),
            'Unexpected area counts')
    require(Counter(c['document_id'] for c in cases) == Counter({key: 5 for key in bydoc}),
            'Unexpected document counts')
    for doc in documents:
        require(doc.get('synthetic') is True and doc.get('area') in areas,
                f'Invalid document {doc["id"]}')
        clauses = index_rows(doc['clauses'], 'clauses')
        require(bool(clauses) and all(isinstance(c.get('text'), str) and c['text'] for c in clauses.values()),
                'Invalid or empty clauses')
    for case in cases:
        cid = case['id']
        doc = bydoc[case['document_id']]
        require(case['area'] == doc['area'], f'Document area mismatch: {cid}')
        require(all(isinstance(case.get(key), str) and case[key] for key in ('scenario', 'claim', 'rationale')),
                f'Missing case text: {cid}')
        require(isinstance(case.get('tags'), list) and all(isinstance(tag, str) for tag in case['tags']),
                f'Invalid tags: {cid}')
        row = byrequest[cid]
        require(set(row) == {'id', 'request'}, f'Unexpected request wrapper: {cid}')
        request = row['request']
        require(set(request) == {'model', 'state', 'questions'} and request['model'] == 'clef-flash',
                f'Invalid native request: {cid}')
        state = request['state']
        require(isinstance(state, dict) and set(state) == {'hinweis', 'unterlagen', 'sachverhalt', 'zu_pruefende_aussage'},
                f'Unexpected state fields: {cid}')
        require(isinstance(state['hinweis'], str) and state['hinweis'], f'Missing synthetic notice: {cid}')
        require(state['unterlagen'] == [{'klausel': c['id'], 'text': c['text']} for c in doc['clauses']],
                f'Request clause mismatch: {cid}')
        require(state['sachverhalt'] == case['scenario'] and state['zu_pruefende_aussage'] == case['claim'],
                f'Request scenario/claim mismatch: {cid}')
        require(case['rationale'] not in canonical_state(request), f'Gold rationale leaked into request: {cid}')
        require(set(request['questions']) == set(FIELDS), f'Partial question schema: {cid}')
        require(set(case['decision_options']) == {'ja', 'nein', 'offen', 'konflikt'}, f'Invalid decision options: {cid}')
        options = case['evidence_options']
        clause_ids = {c['id'] for c in doc['clauses']}
        require(isinstance(options, dict) and len(options) == 5, f'Expected five evidence options: {cid}')
        require(all(isinstance(value, list) and value and len(value) == len(set(value)) and set(value) <= clause_ids
                    for value in options.values()), f'Invalid evidence clause references: {cid}')
        require(len({tuple(sorted(value)) for value in options.values()}) == 5,
                f'Duplicate evidence option: {cid}')
        require(len({len(value) for value in options.values()}) == 1, f'Unequal evidence option sizes: {cid}')
        for field in FIELDS:
            question = request['questions'][field]
            require(set(question) == {'type', 'instructions', 'criteria'} and question['type'] == 'choice'
                    and isinstance(question['instructions'], str) and question['instructions'],
                    f'Invalid native question: {cid}/{field}')
            criteria = case['decision_options'] if field == 'decision' else {key: ', '.join(value) for key, value in options.items()}
            require(question['criteria'] == criteria, f'Question options mismatch: {cid}/{field}')
            require(case['expected'][field] in criteria, f'Invalid gold option: {cid}/{field}')
        require(set(case['expected']['evidence_clauses']) == set(options[case['expected']['evidence']]),
                f'Gold evidence clauses mismatch: {cid}')
        accepted = case['expected'].get('accepted_evidence', [case['expected']['evidence']])
        require(isinstance(accepted, list) and accepted and set(accepted) <= set(options)
                and case['expected']['evidence'] in accepted, f'Invalid accepted evidence: {cid}')
    return byrequest


def aggregate(rows):
    count = len(rows)
    result = {'cases': count}
    for field in (*FIELDS, 'exact_case'):
        correct = sum(row['correct'][field] for row in rows)
        result[field] = {'correct': correct, 'total': count, 'accuracy': correct / count if count else None}
    correct = sum(row['correct']['decision'] + row['correct']['evidence'] for row in rows)
    result['field_accuracy'] = {'correct': correct, 'total': count * 2,
                                'accuracy': correct / (count * 2) if count else None}
    return result


def recompute(benchmark, raw):
    """Independent consistency check; only raw field vectors feed the UI result."""
    byraw = index_rows(raw, 'predictions', [case['id'] for case in benchmark['cases']])
    rows = []
    for case in benchmark['cases']:
        cid = case['id']
        pred = byraw[cid]
        require(set(pred['answers']) == set(pred['probabilities_unrounded']) == set(FIELDS),
                f'Partial or extra result fields: {cid}')
        require(pred.get('truncated') is False, f'Truncated prediction: {cid}')
        require(type(pred.get('input_tokens')) is int and 0 < pred['input_tokens'] <= 2048,
                f'Invalid token count: {cid}')
        require(number(pred.get('inference_seconds')) and number(pred.get('encode_seconds'))
                and number(pred.get('latency_ms')), f'Invalid timing: {cid}')
        require(pred['latency_ms'] == pred['inference_seconds'] * 1000, f'Latency mismatch: {cid}')
        for field in FIELDS:
            probs = pred['probabilities_unrounded'][field]
            options = case[f'{field}_options']
            answer = pred['answers'][field]
            require(isinstance(probs, dict) and set(probs) == set(options), f'Probability option mismatch: {cid}/{field}')
            require(all(number(value) and value <= 1 for value in probs.values()) and abs(sum(probs.values()) - 1) < 1e-5,
                    f'Invalid probability vector: {cid}/{field}')
            require(isinstance(answer, dict) and answer.get('choice') in options, f'Invalid answer: {cid}/{field}')
            expected_choice = max(options, key=probs.__getitem__)
            expected_answer = {'type': 'choice', 'choice': expected_choice,
                               'confidence': round(probs[expected_choice], 4),
                               'probabilities': {key: round(probs[key], 4) for key in options}}
            require(answer == expected_answer, f'Answer schema or vendor rounding mismatch: {cid}/{field}')
        actual = {field: pred['answers'][field]['choice'] for field in FIELDS}
        correct = {'decision': actual['decision'] == case['expected']['decision'],
                   'evidence': actual['evidence'] in case['expected'].get('accepted_evidence', [case['expected']['evidence']])}
        correct['exact_case'] = all(correct.values())
        rows.append({'id': cid, 'document_id': case['document_id'], 'area': case['area'], 'tags': case['tags'],
                     'expected': case['expected'], 'actual': actual, 'actual_evidence_clauses': case['evidence_options'][actual['evidence']],
                     'correct': correct, 'answers': pred['answers'], 'probabilities': pred['probabilities_unrounded'],
                     'input_tokens': pred['input_tokens'], 'truncated': pred['truncated'],
                     'inference_seconds': pred['inference_seconds'], 'encode_seconds': pred['encode_seconds'],
                     'rss_bytes': pred.get('rss_bytes')})
    summary = aggregate(rows)
    summary['decision_label_distribution'] = dict(Counter(case['expected']['decision'] for case in benchmark['cases']))
    summary['decision_majority_baseline'] = max(summary['decision_label_distribution'].values()) / len(rows)
    summary['evidence_uniform_random_baseline'] = 1 / 5
    summary['evidence_option_distribution'] = dict(Counter(case['expected']['evidence'] for case in benchmark['cases']))
    summary['evidence_position_majority_baseline'] = max(summary['evidence_option_distribution'].values()) / len(rows)
    summary['exact_case_majority_pair_baseline'] = max(Counter((case['expected']['decision'], case['expected']['evidence']) for case in benchmark['cases']).values()) / len(rows)
    summary['decision_balanced_accuracy'] = statistics.mean(
        sum(row['correct']['decision'] for row in rows if row['expected']['decision'] == label)
        / sum(row['expected']['decision'] == label for row in rows) for label in summary['decision_label_distribution'])
    summary['high_confidence_errors'] = {field: [
        {'id': row['id'], 'choice': row['actual'][field], 'confidence': max(row['probabilities'][field].values())}
        for row in rows if not row['correct'][field] and max(row['probabilities'][field].values()) >= .9] for field in FIELDS}
    times = sorted(row['inference_seconds'] for row in rows)
    summary['latency_seconds'] = {'median': statistics.median(times), 'p95_nearest_rank': times[math.ceil(len(times) * .95) - 1],
                                  'min': min(times), 'max': max(times), 'total': sum(times)}
    summary['tokens'] = {'min': min(row['input_tokens'] for row in rows), 'median': statistics.median(row['input_tokens'] for row in rows),
                         'max': max(row['input_tokens'] for row in rows), 'truncated_cases': 0}
    return {'summary': summary, 'cases': rows,
            'by_area': {area: aggregate([row for row in rows if row['area'] == area]) for area in benchmark['metadata']['areas']},
            'by_document': {doc['id']: aggregate([row for row in rows if row['document_id'] == doc['id']]) for doc in benchmark['documents']},
            'by_decision_label': {label: aggregate([row for row in rows if row['expected']['decision'] == label]) for label in summary['decision_label_distribution']},
            'date_version_subset': aggregate([row for row in rows if 'date_version_application' in row['tags']]),
            'without_date_version_subset': aggregate([row for row in rows if 'date_version_application' not in row['tags']])}


def build(source, cases_only=False):
    try:
        return _build(source, cases_only)
    except (KeyError, TypeError, IndexError, AttributeError, ZeroDivisionError) as exc:
        raise ValueError(f'Malformed insurance artifact: {exc}') from exc


def _build(source, cases_only=False):
    base = input_directory(source, cases_only)
    benchmark = load_json(base / 'benchmark.json')
    requests = load_json(base / 'requests.jsonl', jsonl=True)
    byrequest = validate_inputs(benchmark, requests)
    metadata = benchmark['metadata']
    cases = []
    for original in benchmark['cases']:
        request = byrequest[original['id']]['request']
        case = copy.deepcopy(original)
        # Never trust result-like keys on a source case, even in preview mode.
        for key in ('result', 'latency_ms', 'input_tokens'):
            case.pop(key, None)
        case.update(category=original['area'], split=SPLIT, input=canonical_state(request['state']),
                    questions=copy.deepcopy(request['questions']), gold_rationale=original['rationale'], title=original['claim'])
        cases.append(case)
    payload = {'status': 'test_data_only', 'schema_version': 2,
               'suite': {'id': 'insurance', 'label': 'Versicherungsdokumente', 'primary_split': SPLIT,
                         'categories': {area: area for area in metadata['areas']},
                         'splits': {SPLIT: 'Deutsch · synthetische Versicherungsunterlagen'},
                         'n': CASE_COUNT, 'primary_n': CASE_COUNT, 'random_order_seed': metadata['seed']},
               'metadata': copy.deepcopy(metadata), 'documents': copy.deepcopy(benchmark['documents']), 'cases': cases,
               'verification': {'status': 'pending', 'reason': 'cases_only_no_model_results'},
               'run_metadata': {},
               'source_artifacts': {name: digest(base / name) for name in ('benchmark.json', 'requests.jsonl')}}
    if cases_only:
        return payload
    gate = load_json(base / 'verification.json')
    require(gate.get('status') == 'verified' and isinstance(gate.get('verified_at'), str) and gate['verified_at'],
            'Independent completed verification is missing')
    require(gate.get('case_count') == CASE_COUNT and gate.get('field_count') == CASE_COUNT * 2,
            'Independent verification is incomplete')
    require(gate.get('pre_inference_audit') == gate.get('post_inference_audit') == 'pass'
            and gate.get('no_truncation') is True and gate.get('single_primary_run') is True,
            'Independent audit gates did not pass')
    artifacts = ('benchmark.json', 'requests.jsonl', 'results.json', 'predictions.jsonl', 'predictions.metadata.json')
    for name in artifacts:
        require(gate.get('input_hashes', {}).get(name) == digest(base / name), f'Independent verification hash mismatch: {name}')
    results = load_json(base / 'results.json')
    raw = load_json(base / 'predictions.jsonl', jsonl=True)
    meta = results['run_metadata']
    require(results.get('status') == 'completed' and meta.get('status') == 'completed'
            and meta.get('started_at') and meta.get('completed_at'), 'Incomplete inference results')
    require(meta.get('model') == MODEL and meta.get('revision') == REVISION, 'Unexpected model identity')
    require(meta.get('source_code_sha256') == OFFICIAL_SOURCE_SHA256, 'Native model source mismatch')
    require(meta.get('request_count') == CASE_COUNT and meta.get('requests_sha256') == digest(base / 'requests.jsonl'),
            'Run does not match requests')
    require([row.get('id') for row in raw] == [row['id'] for row in requests] == meta.get('request_order_ids'),
            'Missing, duplicate, unknown or reordered predictions')
    require(meta.get('max_length') == 2048 and meta.get('benchmark_requests_only_no_gold') is True,
            'Unexpected inference request settings')
    require(results.get('benchmark') == metadata, 'Result benchmark metadata mismatch')
    for key, name in (('benchmark', 'benchmark.json'), ('predictions', 'predictions.jsonl')):
        require(results.get('input_hashes', {}).get(key) == digest(base / name), f'Result source hash mismatch: {key}')
    metadata_path = base / 'predictions.metadata.json'
    require(load_json(metadata_path) == meta, 'Embedded run metadata mismatch')
    require(results.get('input_hashes', {}).get('metadata') == digest(metadata_path), 'Result metadata hash mismatch')
    fresh = recompute(benchmark, raw)
    for key, value in fresh.items():
        require(canonical_state(results.get(key)) == canonical_state(value), f'Saved results differ from raw recomputation: {key}')
    byraw = index_rows(raw, 'predictions')
    byscore = index_rows(results['cases'], 'scores', byraw)
    for case in cases:
        row = byraw[case['id']]
        score = byscore[case['id']]
        case['result'] = {'fields': {field: {'prediction': score['actual'][field],
                                            'correct': score['correct'][field],
                                            'probabilities': copy.deepcopy(row['probabilities_unrounded'][field]),
                                            'schema_valid': True} for field in FIELDS},
                          'correct': score['correct']['exact_case'], 'schema_valid': True,
                          'actual_evidence_clauses': copy.deepcopy(score['actual_evidence_clauses'])}
        case['latency_ms'] = row['latency_ms']
        case['input_tokens'] = row['input_tokens']
    payload.update(status='completed', model=MODEL, revision=REVISION, run_metadata=meta, verification=gate,
                   **{key: value for key, value in fresh.items() if key != 'cases'})
    payload['source_artifacts'] = {name: digest(base / name) for name in (*artifacts, 'verification.json')}
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'experiments/insurance')
    parser.add_argument('--out', type=Path, default=ROOT / 'web/data/insurance.json')
    parser.add_argument('--cases-only', action='store_true')
    args = parser.parse_args()
    payload = build(args.source, args.cases_only)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(args.out.suffix + '.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(args.out)
    print(json.dumps({'status': payload['status'], 'suite': 'insurance', 'cases': len(payload['cases']), 'file': str(args.out)}))


if __name__ == '__main__':
    main()
