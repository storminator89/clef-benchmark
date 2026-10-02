#!/usr/bin/env python3
"""Admit and independently recompute the frozen 48-case, 24-pair public experiment.

No model imports, inference, gold repair, output repair or probability rounding.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from paired_reliability_common import (ROOT, load, require, sha, verify_manifest,
    verify_lock, verify_curated_scope, module_from_file, write_data)

SOURCE = ROOT / 'experiments/minimal_pairs'
EXPORT_MANIFEST_SHA256 = '3f5794bbf5a2e823653a095b117e59dc1d9366e439a481d608ddeb7f0624d5bc'
FREEZE_SHA256 = 'b060188d3690dbfa94019a51e9d74928f110e091c98a50e74cc151474c63afbb'
FIELDS = ('action', 'determination')
PUBLIC_FILE_COUNT = 81
PUBLIC_ADDITIONS = frozenset({
    'ERRORS.md',
    'README.md',
    'REPORT.md',
    'audit/INDEPENDENT_METHOD.md',
    'audit/independent_checker_self_tests.json',
    'audit/independent_error_review.md',
    'audit/independent_error_semantic_review.json',
    'audit/independent_prose_review.json',
    'audit/independent_result_check.json',
    'audit/independent_result_review.md',
    'audit/independent_summary.json',
    'freeze_manifest.json',
    'provenance/portable_export.json',
    'provenance/public_scope_evolution.json',
    'results/case_scores.jsonl',
    'results/errors.jsonl',
    'results/execution_events.jsonl',
    'results/pair_errors.jsonl',
    'results/pair_scores.jsonl',
    'results/predictions.jsonl',
    'results/predictions.metadata.json',
    'results/resource_monitor.jsonl',
    'results/run_outcome.json',
    'results/runtime_observations.json',
    'results/summary.json',
    'scripts/build_reports.py',
    'scripts/export_public.py',
    'scripts/independent_result_check.py',
    'scripts/test_independent_result_check.py',
    'scripts/verify_export.py',
})


def recompute(source):
    checker = module_from_file('paired_independent_check', source / 'scripts/independent_result_check.py')
    data = checker.load_data(source)
    ledger = checker.Ledger()
    checker.dataset_checks(source, data, ledger)
    native, _, errors = checker.read_rows(source / 'results/predictions.jsonl')
    derived = checker.compute(data['cases'], data['pairs'],
        {r['id']: r for r in data['gold']}, {r['id']: r for r in data['requests']},
        data['preflight'], native, errors)
    require(not derived['scoring_stopped'] and not derived['fatal_errors'], 'Independent paired scoring stopped')
    checker.compare_primary(source, source / 'results', derived, ledger)
    for row in derived['case_results']:
        require(row['valid'] and not row['invalid_reasons'], f'Invalid paired prediction: {row["id"]}')
        for check in row['native_checks']:
            require(check['passed'], f'Native paired output mismatch: {row["id"]}/{check["path"]}')
    require(not ledger.failures, f'Independent paired comparison failed: {ledger.failures[:3]}')
    require(derived['summary'] == load(source / 'audit/independent_summary.json'),
            'Saved independent paired summary differs')
    saved = load(source / 'audit/independent_result_check.json')
    require(saved['passed'] is True and saved['mismatches'] == [] and saved['prediction_count'] == 48,
            'Paired final scientific review failed')
    require(saved['predictions_sha256'] == sha(source / 'results/predictions.jsonl')
            and saved['summary_sha256'] == sha(source / 'results/summary.json'), 'Paired scientific review hashes differ')
    prose = load(source / 'audit/independent_prose_review.json')
    require(prose['passed'] and prose['report_sha256'] == sha(source / 'REPORT.md')
            and prose['errors_md_sha256'] == sha(source / 'ERRORS.md'), 'Paired report review differs')
    return data, derived, len(ledger.rows)


def build(source=SOURCE):
    source = Path(source)
    manifest = verify_manifest(source, EXPORT_MANIFEST_SHA256, PUBLIC_FILE_COUNT - 1)
    lock = verify_lock(source, 'freeze_manifest.json', FREEZE_SHA256, 50)
    verify_curated_scope(source, lock, manifest, PUBLIC_ADDITIONS)
    data, derived, checks = recompute(source)
    native = {r['id']: r for r in load(source / 'results/predictions.jsonl', True)}
    scored = {r['id']: r for r in load(source / 'results/case_scores.jsonl', True)}
    pair_scores = {r['id']: r for r in load(source / 'results/pair_scores.jsonl', True)}
    requests = {r['id']: r['request'] for r in data['requests']}
    cases = {}
    for c in data['cases']:
        ident = c['id']; p = native[ident]; s = scored[ident]; req = requests[ident]
        fields = {f: {'prediction': p['answers'][f]['choice'],
                      'confidence': p['probabilities_unrounded'][f][p['answers'][f]['choice']],
                      'probabilities': p['probabilities_unrounded'][f],
                      'correct': s['field_correct'][f]} for f in FIELDS}
        cases[ident] = {k: c[k] for k in ('id', 'side', 'rule', 'message', 'question')}
        cases[ident].update(input=req['state'], questions=req['questions'], expected=c['expected'],
                           gold_rationale=c['rationale'], authorship=c['authorship'],
                           result={'correct': s['all_fields_exact'], 'schema_valid': s['valid'], 'fields': fields})
    pairs = []
    for p in data['pairs']:
        row = {k: p[k] for k in ('id', 'domain', 'family', 'kind', 'subtype', 'rule', 'question', 'changed_fact')}
        row.update(change={'prefix': p['unchanged_prefix'], 'span_a': p['span_a'], 'span_b': p['span_b'],
                           'suffix': p['unchanged_suffix'], 'offsets_a': p['changed_character_offsets_a'],
                           'offsets_b': p['changed_character_offsets_b'], 'unchanged_components': p['unchanged_components']},
                   outcome=pair_scores[p['id']], a=cases[p['case_ids'][0]], b=cases[p['case_ids'][1]])
        pairs.append(row)
    summary = load(source / 'results/summary.json')
    return {
        'schema_version': 1, 'status': 'completed',
        'suite': {'id': 'minimal_pairs', 'title': 'Minimalpaare: Was ändert die Entscheidung?',
                  'fields': list(FIELDS), 'categories': {'banking': 'Banking', 'insurance': 'Versicherung', 'finance': 'Finanzen'},
                  'scope': '48 synthetische Fälle in 24 abhängigen Paaren: 12 Wechsel- und 12 Invarianzpaare; eigener Nenner'},
        'model': {'name': 'Cloudflare/clef-flash', 'revision': '17f0b0ad64efb65d273590632833508766b2aae6',
                  'configuration': 'Experimental CPU NF4 backbone with original BF16 joint head'},
        'definitions': {
            'confidence': 'Unrounded marginal option score of the saved native choice; not calibrated correctness or joint probability.',
            'both_correct': 'Both action and determination match frozen gold on both A and B.',
            'correct_directional_change': 'Flip pair with both complete native endpoints correct; a changed output alone is insufficient.',
            'stable': 'Invariant pair has equal valid native endpoint outputs; stable outputs can both be wrong.',
            'offsets': 'Zero-based Unicode code-point positions [start, end), measured in the complete message.'},
        'verification': {'status': 'pass', 'public_file_count': PUBLIC_FILE_COUNT, 'frozen_file_count': 50,
                         'case_count': 48, 'pair_count': 24, 'model_inference_performed': False,
                         'independent_raw_metric_recomputation': True, 'recomputed_comparisons': checks,
                         'export_manifest_sha256': EXPORT_MANIFEST_SHA256, 'freeze_manifest_sha256': FREEZE_SHA256},
        'provenance': {'source': 'experiments/minimal_pairs',
                       'manifest': 'experiments/minimal_pairs/FILE_SHA256.json',
                       'report': 'experiments/minimal_pairs/REPORT.md',
                       'errors': 'experiments/minimal_pairs/ERRORS.md',
                       'scientific_files': summary['provenance']},
        'summary': summary, 'caveats': summary['limitations'], 'pairs': pairs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, default=ROOT / 'web/data/minimal_pairs.json')
    args = parser.parse_args()
    write_data(args.output, build(args.source))
    print('PASS: paired frozen admission, independent native recomputation and deterministic side-by-side export; no inference')

if __name__ == '__main__': main()
