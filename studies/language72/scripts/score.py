#!/usr/bin/env python3
"""New model-free Stage 7 recovery scorer; not restoration of the lost scorer.
No inference imports or external calls. See RECOVERY_PROTOCOL.md.
"""
import argparse
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('action', 'determination')
OPTIONS = {'action': ('answer', 'ask_fact', 'ask_target', 'resolve_conflict'), 'determination': ('yes', 'no', 'unresolved')}
DOMAINS = ('banking', 'insurance', 'finance')
STYLES = ('typo', 'compact_colloquial', 'abbreviation', 'de_en_mix')
GROUPS = ('invariant', 'ambiguity_change')
SUBTYPES = ('answer_to_missing_fact', 'answer_to_missing_target')
FILES = {'cases': 'cases.reconstructed.jsonl', 'gold': 'gold.reconstructed.jsonl', 'pairs': 'pairs.reconstructed.jsonl', 'requests': 'requests.jsonl'}
REQUEST_SHA256 = '0a5d7e070afdb17c10ee8fd4c74c321aafd3ee8197dcd0ef7d2d253d816c2e12'
CONTRACT = {
    'identity': 'new recovery scorer; no original-source-hash restoration claim',
    'sum_absolute_error_strictly_less_than': 1e-5,
    'latency_ms_absolute_error_strictly_less_than': 1e-5,
    'native_rounding': 'exact Python round(raw,4) for every map value and selected confidence',
    'ties': 'first maximum in original request criteria order; not lexical encoder option order',
    'tokens': 'integer 1..2048, exactly matching per-ID preflight; truncated is false',
    'shape': 'exact action/determination field maps, exact option membership, exact native answer keys',
    'invalid_rows': 'all fields incorrect; invalid rows are excluded from high-score selection',
    'high_score': 'valid output and min(selected unrounded marginals)>=0.90; not a joint probability',
    'field_gates': 'fields: own marginal>=0.90; fields_on_case_gate: same min-score gate as case',
    'zero_denominator': 'rate=null means NA',
    'complete_pair': 'both endpoint outputs valid',
    'telemetry': 'one observation per recorded main request with finite nonnegative value; no pair weighting, load, warmup or repeat observations',
    'evidence': 'original raw text retained unchanged; nonfinite parsed numbers tagged only in derived JSON',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(items):
    obj = {}
    for key, value in items:
        require(key not in obj, 'Duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def reject_constant(value):
    raise ValueError('Nonstandard JSON constant: ' + value)


def loads(text):
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)


def read(path):
    return [loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def index(rows):
    out = {}
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get('id'), str) and bool(row['id']), 'Unassignable row ID')
        require(row['id'] not in out, 'Duplicate row ID: ' + row['id'])
        out[row['id']] = row
    return out


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def numeric(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def metric(n, d):
    return {'numerator': n, 'denominator': d, 'rate': n / d if d else None}


def validate(data):
    data = Path(data)
    require(digest(data / FILES['requests']) == REQUEST_SHA256, 'Recovered request hash mismatch')
    x = {key: index(read(data / name)) for key, name in FILES.items()}
    C, G, P, Q = [x[key] for key in ('cases', 'gold', 'pairs', 'requests')]
    policy = loads((data / 'policy.json').read_text())
    require(len(C) == len(G) == len(Q) == 72 and len(P) == 54, 'Wrong cardinality')
    require(set(C) == set(G) == set(Q), 'Case/gold/request ID mismatch')
    require(list(policy) == list(FIELDS), 'Policy field order')
    for field in FIELDS:
        require(list(policy[field]['criteria']) == list(OPTIONS[field]), 'Policy option order')
    require(Counter(c['group'] for c in C.values()) == {'invariant': 60, 'ambiguity_change': 12}, 'Case group count')
    require(Counter(c['domain'] for c in C.values()) == dict.fromkeys(DOMAINS, 24), 'Case domain count')
    for id_, c in C.items():
        g, q = G[id_]['expected'], Q[id_]
        require(set(g) == set(FIELDS) and all(g[f] in OPTIONS[f] for f in FIELDS), 'Gold labels')
        require((g['action'] == 'answer') == (g['determination'] != 'unresolved'), 'Inconsistent gold')
        require(c['expected'] == g, 'Case/gold mismatch')
        state = f"Fiktive Testregel:\n{c['rule']}\n\nSynthetische Anfrage und Unterlagen:\n{c['message']}\n\nZu beurteilende Eigenschaft:\n{c['question']}"
        require(set(q) == {'id', 'request'} and q['request'] == {'model': 'clef-flash', 'state': state, 'questions': policy}, 'Request contract mismatch')
        require(list(q['request']['questions']) == list(FIELDS), 'Question order')
        for f in FIELDS:
            require(list(q['request']['questions'][f]['criteria']) == list(OPTIONS[f]), 'Criteria order')
    inv = [p for p in P.values() if p['kind'] == 'invariant']
    amb = [p for p in P.values() if p['kind'] == 'ambiguity_change']
    require(len(inv) == 48 and len(amb) == 6, 'Pair groups')
    require(Counter(p['subtype'] for p in inv) == dict.fromkeys(STYLES, 12), 'Transformation counts')
    require(Counter(p['domain'] for p in inv) == dict.fromkeys(DOMAINS, 16), 'Pair domain counts')
    require(Counter((p['domain'], p['subtype']) for p in amb) == {(d, s): 1 for d in DOMAINS for s in SUBTYPES}, 'Control cells')
    used = {group: set() for group in GROUPS}
    for p in P.values():
        a, b = C[p['a_id']], C[p['b_id']]
        require(a['id'] != b['id'], 'Same endpoint')
        require(a['cluster_id'] == b['cluster_id'] == p['cluster_id'], 'Cluster mismatch')
        require(a['domain'] == b['domain'] == p['domain'] and a['group'] == b['group'] == p['kind'], 'Pair metadata mismatch')
        require(a['rule'] == b['rule'] and a['question'] == b['question'] and a['style'] == 'canonical', 'Endpoint context')
        if p['kind'] == 'invariant':
            require(a['expected'] == b['expected'] and b['style'] == p['subtype'], 'Invariant endpoint mismatch')
        else:
            factual = p['subtype'] == 'answer_to_missing_fact'
            require(a['expected'] == {'action': 'answer', 'determination': 'yes' if factual else 'no'}, 'Control source gold')
            require(b['expected'] == {'action': 'ask_fact' if factual else 'ask_target', 'determination': 'unresolved'}, 'Control target gold')
            require(b['style'] == ('fact_status_removed' if factual else 'target_removed'), 'Control target style')
        used[p['kind']].update((a['id'], b['id']))
    require(len(used['invariant']) == 60 and len(used['ambiguity_change']) == 12 and not used['invariant'] & used['ambiguity_change'] and set.union(*used.values()) == set(C), 'Endpoint partition')
    require(len({p['a_id'] for p in inv}) == 12 and set(Counter(p['a_id'] for p in inv).values()) == {4} and len({p['b_id'] for p in inv}) == 48, 'Shared canonical topology')
    clusters = {p['cluster_id'] for p in inv}
    controls = {p['cluster_id'] for p in amb}
    require(len(clusters) == 12 and len(controls) == 6 and not clusters & controls, 'Conceptual clusters')
    for cluster in clusters:
        members = [c for c in C.values() if c['cluster_id'] == cluster]
        ps = [p for p in inv if p['cluster_id'] == cluster]
        require(Counter(c['style'] for c in members) == dict.fromkeys(('canonical',) + STYLES, 1), 'Five views')
        require(Counter(p['subtype'] for p in ps) == dict.fromkeys(STYLES, 1), 'Four transformations')
    bases = [c for c in C.values() if c['group'] == 'invariant' and c['style'] == 'canonical']
    require(Counter(c['domain'] for c in bases) == dict.fromkeys(DOMAINS, 4), 'Cluster domain counts')
    require(Counter(tuple(c['expected'][f] for f in FIELDS) for c in bases) == {('answer', 'yes'): 3, ('answer', 'no'): 3, ('ask_fact', 'unresolved'): 3, ('ask_target', 'unresolved'): 2, ('resolve_conflict', 'unresolved'): 1}, 'Base gold composition')
    x['pairs'] = list(P.values())
    return x


def validate_preflight(path, data, requests):
    report = loads(Path(path).read_text())
    require(report['requests_sha256'] == digest(Path(data) / FILES['requests']), 'Preflight hash mismatch')
    records = index(report['cases'])
    require(set(records) == set(requests), 'Preflight ID coverage')
    if 'count' in report:
        require(type(report['count']) is int and report['count'] == 72, 'Preflight count')
    require(report['all_full_cap_equal'] is True, 'Preflight full/cap mismatch')
    for id_, record in records.items():
        n = record['input_tokens']
        require(type(n) is int and 0 < n <= 2048, 'Preflight tokens')
        require(record['truncated'] is False, 'Preflight truncated')
        require(record['full_cap_equal'] is True, 'Preflight token inequality')
        questions = record['encoded_questions']
        require(isinstance(questions, list) and [q['question_id'] for q in questions] == list(FIELDS), 'Encoded field shape')
        for q in questions:
            # Encoder IDs are lexical, unlike the original native argmax tie rule.
            opts = sorted(requests[id_]['request']['questions'][q['question_id']]['criteria'])
            require(q['option_ids'] == opts and type(q['question_type']) is int and q['question_type'] == 1 and isinstance(q['option_spans'], list) and len(q['option_spans']) == len(opts), 'Encoded option shape')
            for span in [q['question_span']] + q['option_spans']:
                require(isinstance(span, list) and len(span) == 2 and all(type(v) is int for v in span) and 0 <= span[0] < span[1] <= n, 'Encoded span')
    return records


def native(row, request, expected_tokens):
    actual, selected = {}, {}
    try:
        require(isinstance(row, dict) and 'error' not in row, 'explicit_error_or_not_object')
        require(row.get('truncated') is False and type(row['input_tokens']) is int and 0 < row['input_tokens'] <= 2048, 'tokens_or_truncation')
        require(row['input_tokens'] == expected_tokens, 'preflight_token_mismatch')
        require(isinstance(row['answers'], dict) and isinstance(row['probabilities_unrounded'], dict), 'field_maps')
        require(set(row['answers']) == set(row['probabilities_unrounded']) == set(FIELDS), 'field_set')
        for f in FIELDS:
            a, p, opts = row['answers'][f], row['probabilities_unrounded'][f], request['questions'][f]['criteria']
            require(isinstance(a, dict) and set(a) == {'type', 'choice', 'confidence', 'probabilities'}, f + ':answer_schema')
            require(a['type'] == 'choice' and isinstance(a['choice'], str) and a['choice'] in opts, f + ':choice')
            require(isinstance(p, dict) and set(p) == set(opts), f + ':probability_options')
            require(all(numeric(v) and 0 <= v <= 1 for v in p.values()) and abs(sum(p.values()) - 1) < 1e-5, f + ':probability_values')
            require(a['choice'] == max(opts, key=p.__getitem__), f + ':argmax')
            r = a['probabilities']
            require(isinstance(r, dict) and set(r) == set(opts) and all(numeric(v) and 0 <= v <= 1 for v in r.values()), f + ':rounded_map')
            require(r == {k: round(p[k], 4) for k in opts}, f + ':rounded_values')
            require(numeric(a['confidence']) and a['confidence'] == round(p[a['choice']], 4), f + ':confidence')
            actual[f], selected[f] = a['choice'], p[a['choice']]
        require(all(numeric(row[k]) and row[k] >= 0 for k in ('encode_seconds', 'inference_seconds', 'total_seconds', 'latency_ms', 'rss_bytes')), 'telemetry')
        require(abs(row['latency_ms'] - 1000 * row['inference_seconds']) < 1e-5, 'latency')
        return actual, selected, []
    except (ValueError, KeyError, TypeError, OverflowError) as error:
        return dict.fromkeys(FIELDS), {}, [str(error)]


def high_score(rows):
    selected = [s for s in rows if s['high_score_selected']]
    def counts(chosen, field=None):
        wrong = sum(not (s['exact'] if field is None else s['field_correct'][field]) for s in chosen)
        return {'selected': metric(len(chosen), len(rows)), 'wrong_and_selected': metric(wrong, len(rows)), 'wrong_among_selected': metric(wrong, len(chosen))}
    return {**counts(selected), 'threshold': .90,
            'fields': {f: counts([s for s in rows if s['field_high_score_selected'][f]], f) for f in FIELDS},
            'fields_on_case_gate': {f: counts(selected, f) for f in FIELDS}}


def case_aggregate(rows):
    return {'count': len(rows), 'valid_outputs': metric(sum(s['valid'] for s in rows), len(rows)),
            'all_fields_exact': metric(sum(s['exact'] for s in rows), len(rows)),
            **{f + '_exact': metric(sum(s['field_correct'][f] for s in rows), len(rows)) for f in FIELDS},
            'field_inconsistency': metric(sum(s['field_inconsistent'] for s in rows), len(rows)), 'high_score': high_score(rows)}


def pair_aggregate(rows, invariant):
    keys = ('both_correct', 'observed_change', 'invalid_or_missing', 'missing_endpoint', 'invalid_existing_endpoint')
    keys += ('stability', 'stable_correct', 'stable_wrong', 'failed_invariance', 'degradation', 'improvement', 'both_incorrect') if invariant else ('correct_directional_change', 'changed_but_direction_wrong')
    result = {'count': len(rows), **{k: metric(sum(p[k] for p in rows), len(rows)) for k in keys},
              'observed_change_among_valid': metric(sum(p['observed_change'] for p in rows), sum(p['valid_pair'] for p in rows))}
    if invariant:
        result['conditional_loss_given_correct_canonical'] = metric(sum(p['degradation'] for p in rows), sum(p['a_exact'] for p in rows))
    return result


def cluster_aggregate(rows):
    return {'count': len(rows), **{k: metric(sum(c[k] for c in rows), len(rows)) for k in ('all_five_correct', 'all_five_valid')}}


def descriptive(values):
    return {'count': len(values), 'sum': sum(values), 'min': min(values) if values else None,
            'max': max(values) if values else None, 'median': statistics.median(values) if values else None,
            'mean': statistics.mean(values) if values else None}


def score(data, predictions, preflight=None):
    data, predictions = Path(data), Path(predictions)
    x = validate(data)
    preflight = Path(preflight) if preflight is not None else data.parent / 'evidence' / 'encoding_preflight.json'
    tokens = validate_preflight(preflight, data, x['requests'])
    raw = predictions.read_bytes().decode('utf-8')
    lines = [line for line in raw.splitlines() if line.strip()]
    P = index([loads(line) for line in lines])
    C, G, Q = [x[k] for k in ('cases', 'gold', 'requests')]
    require(set(P) <= set(C), 'Unexpected prediction ID')
    raw_lines = dict(zip(P, lines))
    cases = []
    for id_, c in C.items():
        row, gold = P.get(id_), G[id_]['expected']
        actual, selected, issues = native(row, Q[id_]['request'], tokens[id_]['input_tokens']) if row is not None else (dict.fromkeys(FIELDS), {}, ['missing_prediction'])
        valid = not issues
        correct = {f: valid and actual[f] == gold[f] for f in FIELDS}
        cases.append({'id': id_, **{k: c[k] for k in ('cluster_id', 'domain', 'group', 'style')}, 'expected': gold,
                      'predicted': actual, 'recorded': id_ in P, 'valid': valid, 'exact': all(correct.values()), 'field_correct': correct,
                      'selected_probabilities': selected, 'minimum_selected_probability': min(selected.values()) if valid else None,
                      'high_score_selected': valid and min(selected.values()) >= .90,
                      'field_high_score_selected': {f: valid and selected[f] >= .90 for f in FIELDS},
                      'field_inconsistent': valid and ((actual['action'] == 'answer') != (actual['determination'] != 'unresolved')),
                      'issues': issues, 'probabilities_unrounded': row.get('probabilities_unrounded') if row else None,
                      'native_answers': row.get('answers') if row else None, 'raw_native_row': row, 'raw_prediction_line': raw_lines.get(id_)})
    S, pairs = index(cases), []
    for p in x['pairs']:
        a, b = S[p['a_id']], S[p['b_id']]
        valid = a['valid'] and b['valid']
        equal, both = valid and a['predicted'] == b['predicted'], a['exact'] and b['exact']
        out = {**p, 'expected_a': a['expected'], 'expected_b': b['expected'], 'predicted_a': a['predicted'], 'predicted_b': b['predicted'],
               'a_exact': a['exact'], 'b_exact': b['exact'], 'valid_pair': valid, 'recorded_pair': a['recorded'] and b['recorded'],
               'both_correct': both, 'observed_change': valid and not equal, 'invalid_or_missing': not valid,
               'missing_endpoint': not a['recorded'] or not b['recorded'],
               'invalid_existing_endpoint': (a['recorded'] and not a['valid']) or (b['recorded'] and not b['valid'])}
        if p['kind'] == 'invariant':
            out.update(stability=equal, stable_correct=equal and both, stable_wrong=equal and not both, failed_invariance=not equal,
                       degradation=a['exact'] and not b['exact'], improvement=not a['exact'] and b['exact'], both_incorrect=not a['exact'] and not b['exact'])
        else:
            out.update(correct_directional_change=both and valid and not equal, changed_but_direction_wrong=valid and not equal and not both)
        pairs.append(out)
    inv, amb = [[p for p in pairs if p['kind'] == group] for group in GROUPS]
    clusters = []
    for id_ in sorted({p['cluster_id'] for p in inv}):
        members = [s for s in cases if s['group'] == 'invariant' and s['cluster_id'] == id_]
        clusters.append({'id': id_, 'domain': members[0]['domain'], 'case_ids': [s['id'] for s in members],
                         'correct_count': sum(s['exact'] for s in members), 'valid_count': sum(s['valid'] for s in members),
                         'all_five_correct': all(s['exact'] for s in members), 'all_five_valid': all(s['valid'] for s in members)})
    def strata(rows, ip, ap, cs):
        return {'all_cases': case_aggregate(rows), 'by_group': {g: case_aggregate([s for s in rows if s['group'] == g]) for g in GROUPS},
                'invariant_views': {st: case_aggregate([s for s in rows if s['group'] == 'invariant' and s['style'] == st]) for st in ('canonical',) + STYLES},
                'invariant_pairs': pair_aggregate(ip, True), 'ambiguity_controls': pair_aggregate(ap, False), 'cluster_robustness': cluster_aggregate(cs),
                'invariant_by_transformation': {st: pair_aggregate([p for p in ip if p['subtype'] == st], True) for st in STYLES},
                'ambiguity_by_subtype': {st: pair_aggregate([p for p in ap if p['subtype'] == st], False) for st in SUBTYPES}}
    summary = {'suite_id': 'german_variant_robustness_recovery_v1', 'scoring_contract': CONTRACT,
               'design': {'unique_requests': 72, 'invariant_unique_requests': 60, 'ambiguity_unique_requests': 12, 'pairs': 54,
                          'invariant_pairs': 48, 'ambiguity_pairs': 6, 'invariant_clusters': 12, 'conceptual_clusters': 18,
                          'canonical_executions': 12, 'canonical_pair_uses': 48}, **strata(cases, inv, amb, clusters),
               'all_field_decisions': metric(sum(sum(s['field_correct'].values()) for s in cases), 144),
               'by_domain': {d: strata([s for s in cases if s['domain'] == d], [p for p in inv if p['domain'] == d],
                                      [p for p in amb if p['domain'] == d], [c for c in clusters if c['domain'] == d]) for d in DOMAINS},
               'technical': {'recorded': len(P), 'valid': sum(s['valid'] for s in cases), 'missing': 72-len(P),
                             'invalid_existing': sum(s['recorded'] and not s['valid'] for s in cases),
                             'valid_outputs': metric(sum(s['valid'] for s in cases), 72), 'failures': metric(sum(not s['valid'] for s in cases), 72),
                             'complete_pairs': metric(sum(p['valid_pair'] for p in pairs), 54), 'recorded_pairs': metric(sum(p['recorded_pair'] for p in pairs), 54),
                             'complete_pairs_by_group': {g: metric(sum(p['valid_pair'] for p in pairs if p['kind'] == g), sum(p['kind'] == g for p in pairs)) for g in GROUPS},
                             'invalid_or_missing_ids': [s['id'] for s in cases if not s['valid']],
                             'descriptive_unique_recorded_requests': {k: descriptive([r[k] for r in P.values() if k in r and numeric(r[k]) and r[k] >= 0]) for k in ('input_tokens', 'encode_seconds', 'inference_seconds', 'total_seconds', 'latency_ms', 'rss_bytes')}},
               'provenance': {**{k+'_sha256': digest(data/v) for k,v in FILES.items()}, 'policy_sha256': digest(data/'policy.json'),
                              'encoding_preflight_sha256': digest(preflight), 'predictions_sha256': digest(predictions), 'scorer_sha256': digest(__file__)}}
    errors = [dict(s, **{k: C[s['id']][k] for k in ('rule', 'message', 'question')}) for s in cases if not s['exact']]
    return {'summary': summary, 'case_scores': cases, 'pair_scores': pairs, 'cluster_scores': clusters, 'errors': errors, 'raw_predictions': raw}


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return {'nonfinite_parsed_number': repr(value)}
    if isinstance(value, dict):
        return {k: json_safe(v) for k,v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value


def write(result, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    names = {k: k+('.json' if k == 'summary' else '.jsonl') for k in result}
    require(not any((output/name).exists() for name in names.values()), 'Refusing to overwrite scoring artifacts')
    # Preserve exact original UTF-8 bytes before writing any derived artifacts.
    (output/names['raw_predictions']).write_bytes(result['raw_predictions'].encode('utf-8'))
    for k,v in result.items():
        if k == 'raw_predictions':
            continue
        if k == 'summary':
            content = json.dumps(json_safe(v), ensure_ascii=False, allow_nan=False, indent=2)+'\n'
        else:
            content = ''.join(json.dumps(json_safe(row), ensure_ascii=False, allow_nan=False)+'\n' for row in v)
        (output/names[k]).write_text(content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'data')
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--preflight', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = score(args.data, args.predictions, args.preflight)
    write(result, args.output)
    print(json.dumps({k: result['summary'][k] for k in ('all_cases', 'invariant_pairs', 'ambiguity_controls', 'cluster_robustness')}, indent=2))
