#!/usr/bin/env python3
"""Deterministic, unpooled UI adapter for locked descriptive score reliability.

Runs primary and independent standard-library recomputation from raw records.
No inference, recalibration, threshold tuning, renormalization or native repairs.
"""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
from paired_reliability_common import (ROOT, load, require, sha, verify_manifest,
    verify_lock, verify_curated_scope, module_from_file, module_dependency, serialize, write_data)

SOURCE = ROOT / 'experiments/probability_reliability'
EXPORT_MANIFEST_SHA256 = 'fc3285af17c5bc7b0279855bfd00df25088a7bcc920243b597ec0ca2d31a1552'
SOURCE_LOCK_SHA256 = 'c02c5378121b67c91706c3f2edcff45b50224f2b752bbb6188849ec9f329bff4'
THRESHOLDS = [0.5, 0.7, 0.8, 0.9, 0.95, 0.99]
PUBLIC_FILE_COUNT = 119
PUBLIC_ADDITIONS = frozenset({
    'CASE_HEURISTICS.md',
    'ERRORS.md',
    'FIELD_DETAILS.md',
    'LICENSE',
    'NOTICE',
    'README.md',
    'REPORT_DE.md',
    'SOURCE_LOCK.json',
    'SOURCE_LOCK.sha256',
    'audit/INDEPENDENT_METHOD.md',
    'audit/INDEPENDENT_REVIEW.md',
    'audit/audit_reports.py',
    'audit/deterministic_reproduction.json',
    'audit/independent_field_metrics.json',
    'audit/independent_metrics.py',
    'audit/independent_recomputation.json',
    'audit/independent_review.json',
    'audit/primary_synthetic_tests.json',
    'audit/recompute.py',
    'audit/report_review.json',
    'audit/test_independent_metrics.py',
    'licenses/BELEGE-LICENCE.txt',
    'licenses/CLEF-Apache-2.0.txt',
    'licenses/Cloudflare-clef-flash-Apache-2.0.txt',
    'provenance/portable_export.json',
    'provenance/public_scope_evolution.json',
    'reference_model/README.md',
    'reference_model/config.json',
    'reference_model/image_requirements_frozen.txt',
    'reference_model/joint_head_config.json',
    'reference_model/model_file_manifest.json',
    'reference_model/text_requirements_frozen.txt',
    'results/all_errors.jsonl',
    'results/case_items.jsonl',
    'results/case_metrics.json',
    'results/execution.json',
    'results/field_items.jsonl',
    'results/field_metrics.json',
    'results/integrity.json',
    'results/normalized_fields.jsonl',
    'scripts/analyze.py',
    'scripts/build_reports.py',
    'scripts/metrics.py',
    'scripts/test_metrics.py',
    'scripts/verify_artifact.py',
})
RESULT_FILES = ('field_metrics.json', 'case_metrics.json', 'integrity.json',
                'normalized_fields.jsonl', 'field_items.jsonl', 'case_items.jsonl', 'all_errors.jsonl')
TITLES = {'minimal_pairs48': 'Minimalpaare · 48', 'clarification72': 'Rückfragen · 72',
          'bank_support80': 'Banksupport · 80', 'original_text180': 'Ursprüngliche Textsuite · 180',
          'finance100': 'Finanzrouting · 100', 'insurance60': 'Versicherungsdokumente · 60',
          'clean72': 'Saubere Verwaltungstexte · 72', 'attack_ablation14': 'Angriffskontrollen · 14',
          'images90': 'Bildsuite · 90'}
CAVEATS = [
    'Post-hoc descriptive reanalysis of existing outcomes; not a preregistered, blinded or held-out calibration study.',
    'Never pool suites, fields, task/language/condition partitions or unequal option-key sets. Matching labels do not make scores comparable.',
    'Pairs, translations, document families and image/blank variants are dependent. Counts are observations, not independent sample sizes.',
    'Purposeful synthetic challenge sets do not estimate population performance. Most labels are AI-authored and AI-reviewed, not human-expert validated.',
    'Native marginal option scores are not calibrated correctness probabilities. The minimum-selected-field-score case gate is only a heuristic, not a joint probability.',
    'Thresholds and bins are fixed descriptive cutoffs, not tuned deployment recommendations. Tiny bins and zero observed errors do not establish safety or calibration.',
    'Insurance evidence options are case-local candidate clause slots; b1 is not a stable semantic class. Original candidate descriptions remain in each request.',
    'Image results reanalyze saved native outputs only; they do not reacquire image pixels, rerun vision, or independently revalidate source labels. Image and blank conditions remain separate.',
    'Brier/NLL/ECE depend on option counts, labels and task mix; cross-group comparisons are not causal model rankings.',
    'Text uses experimental CPU NF4 with original BF16 heads/embeddings. Images retain their original BF16 vision encoder and cap; no stock-precision/GPU/OCR equivalence is inferred.',
]
DEFINITIONS = {
    'group': 'One suite, field, task/language/condition partition and exact option-key set. Metrics may only be shown within this group.',
    'confidence': 'Unrounded probability assigned to the saved native choice; the original vector is neither rounded nor renormalized.',
    'accuracy': 'Correct native field choices / valid field observations; correct_over_expected uses all expected observations.',
    'brier_mean': 'Mean sum over all offered classes of squared probability error; no division by number of classes.',
    'nll_mean': 'Mean -ln(p_gold), in nats; a zero gold probability yields null plus nll_is_infinite=true. No clipping.',
    'bins': 'Ten fixed bins [0,.1), [.1,.2), ..., [.9,1]. Count is the denominator for bin mean/accuracy; empty statistics are null.',
    'ece_10_equal_width': 'Valid-count-weighted absolute bin score/accuracy gaps; finite-set, bin/sample-size-dependent summary.',
    'risk_coverage': 'Keep native selected score >= threshold. Coverage = selected/expected; valid_coverage = selected/valid; risk = incorrect/selected, null if none selected.',
    'error_detection_auroc': 'Error ranking by 1-selected score; pairwise ties contribute .5. Null if either outcome class is absent.',
    'case_gate': 'Minimum selected field score across all required fields; heuristic only. Exactness requires all fields correct. Never multiply marginal probabilities.',
    'denominators': 'Every field group and case group retains its own expected/valid/missing/invalid counts. Suite counts are inventory accounting, never pooled accuracy or probability.',
}


def recompute(source):
    """All writes go to a temporary result directory or are captured in memory."""
    with tempfile.TemporaryDirectory(prefix='clef-reliability-derived-') as td:
        out = Path(td)
        with module_dependency('metrics', source / 'scripts/metrics.py'):
            primary = module_from_file('reliability_primary', source / 'scripts/analyze.py')
            with redirect_stdout(io.StringIO()):
                primary.compute(source, out)
        for name in RESULT_FILES:
            require((out / name).read_bytes() == (source / 'results' / name).read_bytes(),
                    f'Reliability raw-source recomputation differs: {name}')
        saved_execution = load(source / 'results/execution.json')
        repeated_execution = load(out / 'execution.json')
        for key in set(saved_execution) - {'python_version'}:
            require(saved_execution[key] == repeated_execution[key], f'Reliability execution lineage differs: {key}')
    reports = {}
    with module_dependency('independent_metrics', source / 'audit/independent_metrics.py'):
        independent = module_from_file('reliability_independent', source / 'audit/recompute.py')
        independent.ROOT = source
        independent.output = lambda path, value: reports.__setitem__(Path(path).name, value)
        # The source script prints its saved report after writing. Captured writes above
        # are checked against that immutable report, rather than modifying it.
        with redirect_stdout(io.StringIO()):
            independent.main()
    for name, report in reports.items():
        require(serialize(report) == (source / 'audit' / name).read_bytes(), f'Independent reliability report differs: {name}')
    require(set(reports) == {'independent_field_metrics.json', 'independent_recomputation.json'},
            'Independent reliability report set changed')
    audit = reports['independent_recomputation.json']
    require(audit['status'] == 'PASS metrics and source integrity' and audit['primary_imports_used'] is False
            and audit['real_model_inference_performed'] is False, 'Independent reliability verification failed')
    require((audit['suite_count'], audit['request_count'], audit['field_count'], audit['field_groups'], audit['case_groups'])
            == (9, 716, 1186, 78, 64), 'Wrong reliability scope')
    return audit


def build(source=SOURCE):
    source = Path(source)
    manifest = verify_manifest(source, EXPORT_MANIFEST_SHA256, PUBLIC_FILE_COUNT - 1)
    lock = verify_lock(source, 'SOURCE_LOCK.json', SOURCE_LOCK_SHA256, 73)
    verify_curated_scope(source, lock, manifest, PUBLIC_ADDITIONS)
    require((source / 'SOURCE_LOCK.sha256').read_text().split()[0] == SOURCE_LOCK_SHA256,
            'Source lock checksum differs')
    audit = recompute(source)
    field_groups = load(source / 'results/field_metrics.json')
    case_groups = load(source / 'results/case_metrics.json')
    for group in field_groups:
        require([r['threshold'] for r in group['risk_coverage']] == THRESHOLDS, 'Changed field thresholds')
        require(len(group['bins']) == 10, 'Changed reliability bin count')
        for i, bin_ in enumerate(group['bins']):
            require((bin_['lower'], bin_['upper'], bin_['upper_inclusive']) == (i / 10, (i + 1) / 10, i == 9),
                    'Changed reliability bin boundaries')
    for group in case_groups:
        require([r['threshold'] for r in group['risk_coverage_heuristic']] == THRESHOLDS, 'Changed case thresholds')
    normalized = load(source / 'results/normalized_fields.jsonl', True)
    items = {(r['suite_id'], r['id'], r['field']): r for r in load(source / 'results/field_items.jsonl', True)}
    observations = []
    contexts = {}
    for row in normalized:
        key = row['suite_id'], row['id'], row['field']
        metric = items[key]
        observation = {k: row[k] for k in ('suite_id', 'id', 'group_id', 'field', 'partition', 'option_keys',
                                         'status', 'issues', 'gold', 'choice', 'probabilities')}
        observation.update({k: metric[k] for k in ('confidence', 'correct', 'brier', 'nll', 'nll_is_infinite',
                                                   'gold_probability', 'tied_maximum_count')})
        observations.append(observation)
        context = {'input': row['request']['request']['state'], 'questions': row['request']['request']['questions'],
                   'expected': row['gold_source_record']['expected'], 'metadata': row['case_metadata']}
        casekey = row['suite_id'], row['id']
        require(casekey not in contexts or contexts[casekey] == context, 'Inconsistent case context across fields')
        contexts[casekey] = context
    cases = [r | contexts[(r['suite_id'], r['id'])] for r in load(source / 'results/case_items.jsonl', True)]
    integrity = load(source / 'results/integrity.json')
    accounting = {s['suite_id']: s for s in integrity['suites']}
    suites = []
    for info in load(source / 'SOURCE_INVENTORY.json')['suites']:
        sid = info['suite_id']; counts = accounting[sid]
        suites.append({'id': sid, 'title': TITLES[sid], 'expected_count': info['expected_request_count'],
                       'valid_field_count': counts['valid_field_rows'], 'invalid_field_count': counts['invalid_field_rows'],
                       'missing_field_count': counts['missing_field_rows'],
                       'field_group_ids': [g['group_id'] for g in field_groups if g['suite_id'] == sid],
                       'case_group_ids': [g['case_group_id'] for g in case_groups if g['suite_id'] == sid],
                       'source_files': info['files']})
    return {
        'schema_version': 1, 'status': 'completed', 'analysis_type': 'post-hoc descriptive',
        'thresholds': THRESHOLDS, 'bin_edges': [i / 10 for i in range(11)],
        'caveats': CAVEATS, 'definitions': DEFINITIONS,
        'verification': {'status': 'pass', 'public_file_count': PUBLIC_FILE_COUNT, 'locked_file_count': 73,
                         'suite_count': 9, 'case_count': 716, 'field_count': 1186,
                         'field_group_count': 78, 'case_group_count': 64,
                         'model_inference_performed': False, 'independent_raw_metric_recomputation': True,
                         'independent_comparisons': audit['independent_comparisons'],
                         'export_manifest_sha256': EXPORT_MANIFEST_SHA256, 'source_lock_sha256': SOURCE_LOCK_SHA256},
        'provenance': {'source': 'experiments/probability_reliability',
                       'manifest': 'experiments/probability_reliability/FILE_SHA256.json',
                       'source_lock': 'experiments/probability_reliability/SOURCE_LOCK.json',
                       'protocol': 'experiments/probability_reliability/PROTOCOL.md',
                       'report': 'experiments/probability_reliability/REPORT_DE.md',
                       'field_details': 'experiments/probability_reliability/FIELD_DETAILS.md',
                       'case_heuristics': 'experiments/probability_reliability/CASE_HEURISTICS.md',
                       'errors': 'experiments/probability_reliability/ERRORS.md'},
        'suites': suites, 'field_groups': field_groups, 'case_groups': case_groups,
        'observations': observations, 'cases': cases, 'integrity': integrity,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, default=ROOT / 'web/data/reliability.json')
    args = parser.parse_args()
    write_data(args.output, build(args.source))
    print('PASS: reliability frozen admission, two raw-source recomputations and deterministic unpooled export; no inference')

if __name__ == '__main__': main()
