#!/usr/bin/env python3
"""Deterministic admission/export of the completed clarification72 experiment.

Read-only source verification; no model imports, inference, score repair or rounding.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

from build_bank_web_data import load, require, sha, relative_file, derived_equal

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'experiments/clarification72'
EXPORT_MANIFEST_SHA256 = 'ec8a1e29146d089144b0afc8bfb47425b4f1124195ba6f9da0a70dc1153fbde6'
FIELDS = ('action', 'determination')
SPLIT = 'german_clarification_primary'
FREEZE_SHA256 = '8eeb30bec0e06776298509328323e6fa2d7849e0d2ff75d03eb922edcf692f6a'
CATEGORIES = {'finance': 'Finanzen', 'insurance': 'Versicherung', 'banking': 'Banking'}
STRATA = {
    'ambiguous_target': 'Unklarer Zielvorgang', 'missing_fact': 'Entscheidende Angabe fehlt',
    'conflicting_evidence': 'Widersprüchliche Angaben', 'complete_yes': 'Vollständiges Ja',
    'complete_no': 'Vollständiges Nein', 'sufficient_despite_omission': 'Trotz Lücke entscheidbar',
}


def build(source=SOURCE):
    source = Path(source)
    require(sha(source / 'FILE_SHA256.json') == EXPORT_MANIFEST_SHA256, 'Public export manifest changed')
    manifest = load(source / 'FILE_SHA256.json')
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*')
              if p.is_file() and p.name != 'FILE_SHA256.json' and '__pycache__' not in p.parts}
    require(set(manifest) == actual, 'Missing or extra public export files')
    for name, digest in manifest.items():
        require(sha(relative_file(source, name)) == digest, f'Export hash mismatch: {name}')
    require(sha(source / 'freeze_manifest.json') == FREEZE_SHA256, 'Wrong pre-inference freeze')
    freeze = load(source / 'freeze_manifest.json')
    for name, digest in freeze['files'].items():
        require(sha(relative_file(source, name)) == digest, f'Frozen input changed: {name}')
    portable = load(source / 'provenance/portable_export.json')
    require(portable['frozen_content_changed'] is False and portable['frozen_manifest_sha256'] == FREEZE_SHA256,
            'Wrong export lineage')
    # Import the archived standard-library checker only after verifying its exact export hash.
    path = source / 'scripts/independent_result_check.py'
    spec = importlib.util.spec_from_file_location('clarification_independent_check', path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    repeated = checker.check(source, completed_authorized=True)
    require(repeated['passed'] is True and repeated['mismatches'] == [] and repeated['prediction_count'] == 72,
            f'Independent verification failed: {repeated["mismatches"]}')
    saved = load(source / 'audit/independent_result_check.json')
    for key in ('passed', 'prediction_count', 'predictions_sha256', 'summary_sha256', 'errors_sha256',
                'freeze_manifest_sha256', 'checker_sha256', 'recomputed_metrics', 'error_ids', 'case_scores'):
        require(derived_equal(repeated[key], saved[key]), f'Independent report differs: {key}')
    summary = load(source / 'results/summary.json')
    require(summary['case_count'] == 72 and summary['field_count'] == 2 and summary['suite_id'] == 'clarification', 'Wrong scope')
    cases = load(source / 'data/cases.jsonl', True)
    requests = {r['id']: r['request'] for r in load(source / 'data/requests.jsonl', True)}
    raw = {r['id']: r for r in load(source / 'results/predictions.jsonl', True)}
    scored = {r['id']: r for r in repeated['case_scores']}
    rows = []
    for c in cases:
        ident = c['id']; request = requests[ident]; p = raw[ident]; s = scored[ident]
        require(s['valid'] is True and not s['technical_issues'], f'Invalid prediction: {ident}')
        fields = {f: {'prediction': p['answers'][f]['choice'], 'correct': s['field_correct'][f],
                      'schema_valid': True, 'probabilities': p['probabilities_unrounded'][f]} for f in FIELDS}
        events = [name for name, item in summary['events'].items() if ident in item['ids']]
        rows.append({
            'id': ident, 'title': c['question'], 'split': SPLIT, 'category': c['domain'],
            'tags': [c['stratum'], c['family']], 'synthetic': True, 'manipulation': False,
            'rule': c['rule'], 'message': c['message'], 'question': c['question'],
            'family': c['family'], 'stratum': c['stratum'], 'input': request['state'],
            'questions': request['questions'], 'expected': c['expected'], 'gold_rationale': c['rationale'],
            'clarification_target': c['clarification_target'], 'diagnostic_events': events,
            'input_tokens': p['input_tokens'], 'latency_ms': 1000 * p['inference_seconds'],
            'result': {'fields': fields, 'correct': s['all_fields_exact'], 'schema_valid': True},
        })
    return {
        'status': 'completed',
        'suite': {'id': 'clarification', 'title': 'Rückfragen statt Raten', 'primary_split': SPLIT,
                  'splits': {SPLIT: 'Deutsch · Rückfragen'}, 'categories': CATEGORIES, 'strata': STRATA,
                  'scope': '72 gezielt balancierte synthetische Fälle in zwölf verwandten Regelfamilien; eigener Nenner'},
        'model': {'name': 'Cloudflare/clef-flash', 'revision': '17f0b0ad64efb65d273590632833508766b2aae6',
                  'configuration': 'Experimental CPU NF4 backbone with original BF16 joint head'},
        'verification': {'status': 'pass', 'n_present': 72,
                         'source': 'experiments/clarification72/audit/independent_result_check.json',
                         'freeze_manifest_sha256': FREEZE_SHA256,
                         'predictions_sha256': repeated['predictions_sha256'],
                         'independent_raw_metric_recomputation': True},
        'summary': summary, 'cases': rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, default=ROOT / 'web/data/clarification.json')
    args = parser.parse_args()
    dataset = build(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('PASS: clarification72 completed-run admission, exact outputs and independent recomputation; deterministic UI export')

if __name__ == '__main__': main()
