#!/usr/bin/env python3
"""Admission and deterministic UI export for the final QA-gated bank-support run.

No inference, model imports, probability rounding or missing-answer repairs.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('intent', 'priority', 'next_step')
COUNT = 80
SPLIT = 'german_bank_support_primary'
REVISION = '17f0b0ad64efb65d273590632833508766b2aae6'
FROZEN_REQUESTS_SHA256 = 'a4ee04381c9d98e7d0365d487fadbe54a6f8c0e3dd751c1a08ebab14c0919562'
FROZEN_MANIFEST_SHA256 = '11e895f000ada7286dc8ae5fabd00b63a862f81e57de1692ff86990e72a895d3'
OFFICIAL_SOURCE_SHA256 = '0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3'
CHECKER_SHA256 = 'cd05206420d058056d323027326aa37cde7e43020c85fe8ccbe30b08ffa6ec6b'
RUNNER_SHA256 = 'd06f85b922e1e4d0e905a1ddc8846aedcafa93c29f502f48b1529a36a9eb5906'
CATEGORIES = {
    'cards': 'Karten', 'transfers': 'Überweisungen', 'standing_orders': 'Daueraufträge',
    'direct_debits': 'Lastschriften', 'access_tan': 'Zugang & TAN', 'fees': 'Bankgebühren',
    'security': 'Sicherheitsanliegen', 'cash': 'Bargeld & Automaten',
    'account_documents': 'Konto & Dokumente', 'ambiguous_multi': 'Mehrere / unklare Anliegen',
}
PRIORITIES = {'critical', 'urgent', 'routine'}
STEPS = {'security_handoff', 'specialist_review', 'clarify', 'guidance'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, f'Duplicate JSON key: {key}')
        value[key] = item
    return value


def load(path, lines=False):
    def reject(value):
        raise ValueError(f'Non-finite JSON number: {value}')
    parse = lambda text: json.loads(text, object_pairs_hook=unique, parse_constant=reject)
    content = Path(path).read_text(encoding='utf-8')
    return [parse(line) for line in content.splitlines() if line.strip()] if lines else parse(content)


def rows_by_id(rows, name):
    require(isinstance(rows, list) and len(rows) == COUNT, f'Expected 80 {name} rows')
    require(all(isinstance(r, dict) and isinstance(r.get('id'), str) for r in rows), f'Invalid {name} rows')
    result = {r['id']: r for r in rows}
    require(len(result) == len(rows), f'Duplicate {name} IDs')
    return result


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def validate_inputs(cases, requests, gold, policy, design):
    C, R, G = (rows_by_id(rows, name) for rows, name in
               ((cases, 'cases'), (requests, 'requests'), (gold, 'gold')))
    require(list(C) == list(R) == list(G), 'Input ID/order mismatch')
    require(list(policy['questions']) == list(FIELDS), 'Wrong native field order')
    require(set(policy['questions']['priority']['criteria']) == PRIORITIES, 'Wrong priorities')
    require(set(policy['questions']['next_step']['criteria']) == STEPS, 'Wrong next-step options')
    require(len(policy['questions']['intent']['criteria']) == 10, 'Expected ten intent options')
    for c in cases:
        cid = c['id']; req = R[cid]
        require(set(req) == {'id', 'request'}, f'Extra inference wrapper fields: {cid}')
        request = req['request']
        require(set(request) == {'model', 'state', 'questions'} and request['model'] == 'clef-flash', f'Invalid request: {cid}')
        require(request['state'] == 'Synthetische Kundennachricht:\n' + c['message'], f'Message/state mismatch: {cid}')
        require(request['questions'] == policy['questions'], f'Supplied policy/schema differs: {cid}')
        require(list(request['questions']) == list(FIELDS), f'Field order differs: {cid}')
        require(c['expected'] == G[cid]['expected'] and set(c['expected']) == set(FIELDS), f'Gold mismatch: {cid}')
        require(c['topic'] in CATEGORIES, f'Unknown topic: {cid}')
        require(isinstance(c['rationale'], str) and c['rationale'], f'Missing gold rationale: {cid}')
        require(c['rationale'] not in json.dumps(request, ensure_ascii=False), f'Gold rationale leaked: {cid}')
        require(len(request['state']) <= 6000 and len(json.dumps(request, ensure_ascii=False).encode()) <= 32768, f'Request exceeds live limits: {cid}')
        for f in FIELDS:
            q = request['questions'][f]
            require(set(q) == {'type', 'instructions', 'criteria'} and q['type'] == 'choice', f'Invalid choice schema: {cid}/{f}')
            require(isinstance(q['instructions'], str) and 0 < len(q['instructions']) <= 4000, f'Invalid instructions: {cid}/{f}')
            require(2 <= len(q['criteria']) <= 12 and c['expected'][f] in q['criteria'], f'Invalid options/gold: {cid}/{f}')
            require(all(isinstance(v, str) and 0 < len(v) <= 300 for v in q['criteria'].values()), f'Invalid criteria: {cid}/{f}')
        require((c['expected']['next_step'] == 'clarify') == (c['answerability'] == 'clarification_needed') == bool(c['clarification_target']), f'Clarification annotation mismatch: {cid}')
        require((c['expected']['priority'] == 'critical') == (c['expected']['next_step'] == 'security_handoff'), f'Critical annotation mismatch: {cid}')
    require(design['case_count'] == COUNT and design['total_field_decisions'] == COUNT * 3
            and design['not_representative_traffic_sample'] is True and design['banking77'] is False,
            'Wrong pilot scope/counts')
    require(design['topic_counts'] == dict(Counter(c['topic'] for c in cases)), 'Topic counts differ')
    require(design['gold_label_counts'] == {f: dict(Counter(c['expected'][f] for c in cases)) for f in FIELDS}, 'Gold label counts differ')
    return R


def metric(correct, total):
    return {'correct': correct, 'total': total, 'accuracy': correct / total if total else None}


def recompute(cases, requests, raw):
    """Independent, strict consistency check of raw vectors and safety-case sets."""
    P = rows_by_id(raw, 'predictions')
    R = rows_by_id(requests, 'requests')
    require(list(P) == list(R) == [c['id'] for c in cases], 'Prediction order/ID mismatch')
    totals = Counter(); safety = defaultdict(list); result = {}; confusion = {f: defaultdict(Counter) for f in FIELDS}
    safety_keys = ('critical_cases', 'critical_priority_misses', 'critical_handoff_misses',
        'critical_safety_case_errors', 'urgent_cases', 'urgent_undertriage',
        'unnecessary_critical_priority', 'unnecessary_security_handoffs',
        'non_escalation_reference_cases', 'unnecessary_escalations', 'missed_clarifications')
    for c in cases:
        cid = c['id']; p = P[cid]; g = c['expected']; fields = {}; actual = {}
        require(set(p['answers']) == set(p['probabilities_unrounded']) == set(FIELDS), f'Missing/extra result fields: {cid}')
        require(p.get('truncated') is False and type(p.get('input_tokens')) is int and 0 < p['input_tokens'] <= 2048, f'Truncated/invalid token count: {cid}')
        require(all(number(p.get(k)) for k in ('inference_seconds', 'encode_seconds', 'latency_ms', 'rss_bytes')), f'Invalid timing/memory: {cid}')
        require(p['latency_ms'] == 1000 * p['inference_seconds'], f'Latency mismatch: {cid}')
        for f in FIELDS:
            options = R[cid]['request']['questions'][f]['criteria']; probs = p['probabilities_unrounded'][f]; a = p['answers'][f]
            require(isinstance(probs, dict) and set(probs) == set(options), f'Incomplete probability vector: {cid}/{f}')
            require(all(number(v) and v <= 1 for v in probs.values()) and abs(sum(probs.values()) - 1) < 1e-5, f'Invalid probabilities: {cid}/{f}')
            require(a.get('type') == 'choice' and a.get('choice') in options and probs[a['choice']] == max(probs.values()), f'Invalid native choice/argmax: {cid}/{f}')
            require(number(a.get('confidence')) and isinstance(a.get('probabilities'), dict)
                    and all(number(v) for v in a['probabilities'].values()), f'Non-numeric rounded answer: {cid}/{f}')
            require(a == {'type': 'choice', 'choice': a['choice'], 'confidence': round(probs[a['choice']], 4),
                          'probabilities': {k: round(v, 4) for k, v in probs.items()}}, f'Vendor answer/rounding mismatch: {cid}/{f}')
            actual[f] = a['choice']; correct = actual[f] == g[f]; totals[f] += correct
            confusion[f][g[f]][actual[f]] += 1
            fields[f] = {'prediction': actual[f], 'correct': correct, 'schema_valid': True, 'probabilities': probs}
        exact = all(fields[f]['correct'] for f in FIELDS); totals['all_fields_exact'] += exact
        result[cid] = {'fields': fields, 'correct': exact, 'schema_valid': True}
        conditions = {
            'critical_cases': g['priority'] == 'critical',
            'critical_priority_misses': g['priority'] == 'critical' and actual['priority'] != 'critical',
            'critical_handoff_misses': g['priority'] == 'critical' and actual['next_step'] != 'security_handoff',
            'critical_safety_case_errors': g['priority'] == 'critical' and (actual['priority'] != 'critical' or actual['next_step'] != 'security_handoff'),
            'urgent_cases': g['priority'] == 'urgent',
            'urgent_undertriage': g['priority'] == 'urgent' and actual['priority'] == 'routine',
            'unnecessary_critical_priority': g['priority'] != 'critical' and actual['priority'] == 'critical',
            'unnecessary_security_handoffs': g['next_step'] != 'security_handoff' and actual['next_step'] == 'security_handoff',
            'non_escalation_reference_cases': g['next_step'] in ('guidance', 'clarify'),
            'unnecessary_escalations': g['next_step'] in ('guidance', 'clarify') and actual['next_step'] in ('specialist_review', 'security_handoff'),
            'missed_clarifications': g['next_step'] == 'clarify' and actual['next_step'] != 'clarify',
        }
        for key, value in conditions.items():
            if value: safety[key].append(cid)
    metrics = {f: metric(totals[f], COUNT) for f in (*FIELDS, 'all_fields_exact')}
    metrics['all_field_decisions'] = metric(sum(totals[f] for f in FIELDS), COUNT * 3)
    return {'metrics': metrics, 'safety': {key: {'count': len(safety[key]), 'ids': safety[key]} for key in safety_keys},
            'confusion_matrices': {f: {g: dict(v) for g, v in values.items()} for f, values in confusion.items()},
            'results': result}


def make_dataset(cases, requests, raw, policy, summary, verification):
    """Convert only source data that has already passed the admission gate."""
    computed = recompute(cases, requests, raw)
    for key in ('metrics', 'safety', 'confusion_matrices'):
        require(derived_equal(computed[key], summary[key]), f'Independent {key} recomputation differs')
    require(summary['case_count'] == COUNT and summary['field_count'] == 3
            and summary['suite_id'] == 'bank-support' and summary['split'] == SPLIT,
            'Wrong summary scope')
    require(summary['errors_count'] == COUNT - computed['metrics']['all_fields_exact']['correct'], 'Wrong error count')
    P = rows_by_id(raw, 'predictions'); R = rows_by_id(requests, 'requests')
    service_policy = '\n\n'.join(policy['questions'][f]['instructions'] for f in FIELDS)
    rows = []
    for c in cases:
        cid = c['id']; p = P[cid]; request = R[cid]['request']
        rows.append({
            'id': cid, 'title': c['message'], 'split': SPLIT, 'category': c['topic'],
            'tags': [c['style'], c['answerability']], 'synthetic': True, 'manipulation': False,
            'message': c['message'], 'service_policy': service_policy, 'input': request['state'],
            'questions': request['questions'], 'expected': c['expected'], 'gold_rationale': c['rationale'],
            'clarification_target': c['clarification_target'], 'style': c['style'], 'answerability': c['answerability'],
            'input_tokens': p['input_tokens'], 'latency_ms': p['latency_ms'], 'result': computed['results'][cid],
        })
    return {
        'status': 'completed',
        'suite': {'id': 'bank-support', 'title': 'Bank-Kundensupport', 'primary_split': SPLIT,
                  'splits': {SPLIT: 'Deutsch · Bank-Kundensupport'}, 'categories': CATEGORIES,
                  'synthetic': True, 'not_representative_traffic_sample': True,
                  'scope': 'Eigener deutscher Support-Pilot; 80 gestaltete Fälle nach fiktiver Servicerichtlinie, kein BANKING77'},
        'model': {'name': 'Cloudflare/clef-flash', 'revision': REVISION,
                  'configuration': 'Experimental CPU NF4 backbone with original BF16 joint head'},
        'verification': {'status': 'pass', 'n_present': COUNT,
                         'source': 'experiments/bank-support/audit/independent_score_check.json',
                         'independent_raw_metric_recomputation': True},
        'summary': summary, 'cases': rows,
    }


def relative_file(source, name):
    path = Path(name)
    require(not path.is_absolute() and '..' not in path.parts and str(path) == name, 'Unsafe artifact path')
    target = source / path
    require(target.is_file() and not target.is_symlink() and target.resolve().is_relative_to(source.resolve()), f'Missing/unsafe artifact: {name}')
    return target


def derived_equal(expected, actual):
    """Match independently derived floats within 1e-12; IDs/counts/types stay exact.

    This is only for recomputed summaries, never for source hashes or raw vectors.
    Equivalent percentile arithmetic can differ in its final floating-point bit.
    """
    if isinstance(expected, dict):
        return isinstance(actual, dict) and set(expected) == set(actual) and all(
            derived_equal(value, actual[key]) for key, value in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(expected) == len(actual) and all(
            derived_equal(a, b) for a, b in zip(expected, actual))
    if isinstance(expected, float):
        return number(actual) and math.isclose(expected, actual, rel_tol=1e-12, abs_tol=1e-12)
    return type(expected) is type(actual) and expected == actual


def validate_independent_summary(recomputed, summary):
    expected = {'metrics', 'safety', 'confusion_matrices', 'strata', 'technical', 'errors_count', 'provenance'}
    require(isinstance(recomputed, dict) and set(recomputed) == expected, 'Incomplete independent recomputation')
    require(set(recomputed['metrics']) == {*FIELDS, 'all_fields_exact', 'all_field_decisions'}, 'Incomplete independent metrics')
    require(set(recomputed['safety']) == {'critical_cases', 'critical_priority_misses', 'critical_handoff_misses',
        'critical_safety_case_errors', 'urgent_cases', 'urgent_undertriage', 'unnecessary_critical_priority',
        'unnecessary_security_handoffs', 'non_escalation_reference_cases', 'unnecessary_escalations', 'missed_clarifications'},
        'Incomplete independent safety groups')
    for value in recomputed['safety'].values():
        require(set(value) == {'count', 'ids'} and type(value['count']) is int and isinstance(value['ids'], list)
                and value['count'] == len(value['ids']) == len(set(value['ids']))
                and all(isinstance(cid, str) for cid in value['ids']), 'Invalid independent safety group')
    require(set(recomputed['confusion_matrices']) == set(FIELDS), 'Incomplete independent confusion matrices')
    require(set(recomputed['strata']) == {'topic', 'style', 'answerability', 'priority', 'next_step'}, 'Incomplete independent strata')
    require(all(isinstance(groups, dict) and groups for groups in recomputed['strata'].values()), 'Empty independent strata')
    require(set(recomputed['technical']) == {'schema_valid_cases', 'truncated_cases', 'input_tokens_min',
        'input_tokens_max', 'forward_seconds_median', 'forward_seconds_p95', 'peak_observed_rss_bytes'}, 'Incomplete independent technical metrics')
    require(type(recomputed['errors_count']) is int and 0 <= recomputed['errors_count'] <= COUNT, 'Invalid independent error count')
    require(set(recomputed['provenance']) == {'requests_sha256', 'gold_sha256', 'predictions_sha256'}, 'Incomplete independent provenance')
    require(all(key in summary and derived_equal(value, summary[key]) for key, value in recomputed.items()), 'Independent final report/summary differs')


def verify_source(source):
    """Admit only the released complete export, with fresh hashes of every artifact."""
    source = Path(source)
    manifest = load(source/'FILE_SHA256.json')
    require(isinstance(manifest, dict) and manifest, 'Missing final file manifest')
    actual_files = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}
    require(actual_files == set(manifest) | {'FILE_SHA256.json'}, 'Unexpected/missing export files')
    for name, expected in manifest.items():
        require(isinstance(expected, str) and len(expected) == 64
                and sha(relative_file(source, name)) == expected, f'Final export hash differs: {name}')
    require(sha(source/'freeze_manifest.json') == FROZEN_MANIFEST_SHA256, 'Unknown pre-inference freeze')
    freeze = load(source/'freeze_manifest.json')
    require(freeze['case_count'] == COUNT and freeze['fields'] == list(FIELDS)
            and freeze['model_inference_before_freeze'] is False and freeze['requests_label_free'] is True,
            'Invalid freeze scope')
    for name, expected in freeze['files'].items():
        require(sha(relative_file(source, name)) == expected, f'Frozen input/source changed: {name}')
    require(sha(source/'data/requests.jsonl') == FROZEN_REQUESTS_SHA256, 'Wrong frozen requests')
    require(sha(source/'reference_runtime/joint_schema_model.py') == OFFICIAL_SOURCE_SHA256, 'Official source changed')
    require(sha(source/'reference_runtime/run_clef.py') == RUNNER_SHA256, 'Original runner changed')
    check = load(source/'audit/independent_score_check.json')
    require(check.get('passed') is True and check.get('prediction_count') == COUNT
            and check.get('mismatches') == [] and check.get('freeze_manifest_sha256') == FROZEN_MANIFEST_SHA256
            and check.get('checker_sha256') == CHECKER_SHA256
            and check.get('verified_frozen_file_count') == len(freeze['files']),
            'Independent final QA has not passed')
    for key, name in (
        ('checker_sha256', 'scripts/independent_score_check.py'),
        ('run_metadata_sha256', 'results/predictions.metadata.json'),
        ('summary_sha256', 'results/summary.json'), ('errors_sha256', 'results/errors.jsonl')):
        require(check.get(key) == sha(relative_file(source, name)), f'Stale independent QA hash: {key}')
    recomputed = check['independently_recomputed']
    for key, name in (('requests_sha256', 'data/requests.jsonl'), ('gold_sha256', 'data/gold.jsonl'),
                      ('predictions_sha256', 'results/predictions.jsonl')):
        require(recomputed['provenance'].get(key) == sha(relative_file(source, name)), f'Stale QA provenance: {key}')
    summary = load(source/'results/summary.json')
    validate_independent_summary(recomputed, summary)
    require(check['independently_recomputed_errors'] == load(source/'results/errors.jsonl', True), 'Independent error cases differ')
    metadata = load(source/'results/predictions.metadata.json')
    require(metadata.get('status') == 'completed' and metadata.get('completed_at') and metadata.get('started_at')
            and metadata.get('request_count') == COUNT and metadata.get('benchmark_requests_only_no_gold') is True,
            'Main run is not complete/label-free')
    from datetime import datetime
    require(datetime.fromisoformat(freeze['frozen_at_host_utc']) <= datetime.fromisoformat(metadata['started_at'])
            <= datetime.fromisoformat(metadata['completed_at']), 'Invalid freeze/run chronology')
    require(metadata['requests_sha256'] == FROZEN_REQUESTS_SHA256 and metadata['revision'] == REVISION
            and metadata['source_code_sha256'] == OFFICIAL_SOURCE_SHA256 and metadata['runner_sha256'] == RUNNER_SHA256,
            'Run lineage differs')
    historical = load(ROOT/'results/run_metadata.json')
    for key in ('model', 'mode', 'quantization', 'dtype', 'device', 'threads', 'batch_size', 'max_length',
                'packages', 'joint_head_parameter_count', 'joint_head_dtypes'):
        require(metadata[key] == historical[key], f'Pinned CPU runtime differs: {key}')
    return check, metadata, summary


def build(source=None):
    source = Path(source or ROOT/'experiments/bank-support')
    check, metadata, summary = verify_source(source)
    data = source/'data'
    cases = load(data/'cases.jsonl', True); requests = load(data/'requests.jsonl', True)
    gold = load(data/'gold.jsonl', True); policy = load(data/'policy.json'); design = load(data/'design_summary.json')
    validate_inputs(cases, requests, gold, policy, design)
    raw = load(source/'results/predictions.jsonl', True)
    require(metadata['request_order_ids'] == [r['id'] for r in requests], 'Run request order differs')
    preflight = load(source/'audit/encoding_preflight.json')
    require(preflight['requests_sha256'] == FROZEN_REQUESTS_SHA256 and preflight['count'] == COUNT, 'Wrong token preflight')
    token_counts = {c['id']: c['input_tokens'] for c in preflight['cases']}
    require(all(token_counts.get(p['id']) == p['input_tokens'] for p in raw), 'Token count drift from pre-inference encoding')
    for key, name in (('requests_sha256', data/'requests.jsonl'), ('gold_sha256', data/'gold.jsonl'),
                      ('predictions_sha256', source/'results/predictions.jsonl')):
        require(summary['provenance'][key] == sha(name), f'Summary provenance drift: {key}')
    return make_dataset(cases, requests, raw, policy, summary, check)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'experiments/bank-support')
    parser.add_argument('--out', type=Path, default=ROOT/'web/data/bank-support.json')
    args = parser.parse_args()
    result = build(args.source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Bank support: {len(result["cases"])} verified cases; 3 native fields; no inference executed')


if __name__ == '__main__':
    main()
