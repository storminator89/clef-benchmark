#!/usr/bin/env python3
"""Deterministic, model-free admission of the frozen multidoc48 experiment.

Preserves native source/determination choices, full input, and unrounded scores.
No inference, model imports, output repair, gold changes or probability rounding.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from paired_reliability_common import (ROOT, load, require, sha, verify_manifest,
    verify_lock, verify_curated_scope, module_from_file, write_data)

SOURCE = ROOT / 'experiments/multidoc48'
EXPORT_MANIFEST_SHA256 = 'bf7a1adba55bbf8b37956650846e5df51f3399d39448fb3c1ec95d5b237d06ca'
FREEZE_SHA256 = '69713f59dfcd175413e7d8b07d8cd7295c39af06aa45c01e6fcbe247ee2ce32a'
PUBLIC_FILE_COUNT = 79
FIELDS = ('source', 'determination')
SPLIT = 'german_multidoc_primary'
CATEGORIES = {'banking': 'Banking', 'insurance': 'Versicherung', 'finance': 'Finanzen'}
STRATA = {'authority': 'Rang und Vorrang', 'effective_date': 'Gültigkeitsdatum',
          'scope': 'Geltungsbereich', 'unresolved': 'Unklare Quelle und Kontrollen'}
PUBLIC_ADDITIONS = frozenset({
    'freeze_manifest.json', 'README.md', 'REPORT.md', 'ERRORS.md',
    'results/predictions.jsonl', 'results/predictions.metadata.json',
    'results/case_scores.jsonl', 'results/errors.jsonl', 'results/summary.json',
    'audit/independent_actual_result_audit.json', 'audit/independent_error_review.json',
    'audit/independent_final_review.json', 'audit/INTEGRATION_METHOD.md',
    'provenance/portable_export.json', 'provenance/public_scope_evolution.json',
    'scripts/export_public.py', 'scripts/verify_export.py',
})
EVENTS = ('missed_clarification', 'excess_clarification', 'wrong_definite_answer',
          'wrong_concrete_source', 'unnecessary_source_uncertainty', 'invented_unique_source',
          'field_pair_inconsistent_with_visible_rules')


def document_texts(case, state):
    """Exact displayed document blocks, preserving full rules and the original order."""
    headers = [f'Dokument {d["id"]} — {d["title"]}\n' for d in case['documents']]
    require(len(headers) == 3 and len({d['id'] for d in case['documents']}) == 3,
            f'Wrong document count or IDs: {case["id"]}')
    require(all(state.count(header) == 1 for header in headers), 'Ambiguous document boundaries')
    starts = [state.index(header) for header in headers]
    end = state.index('\n\nBekannte Fakten:')
    require(starts == sorted(starts) and starts[-1] < end, 'Document order differs from input')
    blocks = {}
    for index, document in enumerate(case['documents']):
        stop = starts[index + 1] - 2 if index + 1 < len(starts) else end
        block = state[starts[index]:stop]
        require('Vollständige Regel:' in block and block.startswith(headers[index]), 'Missing full document rule')
        blocks[document['id']] = block
    require('\n\n'.join(blocks.values()) == state[starts[0]:end], 'Incomplete document display')
    return blocks


def recompute(source):
    checker = module_from_file('multidoc_independent_checker', source / 'audit/independent_score_check.py')
    native = checker.read_rows(source / 'results/predictions.jsonl')
    summary, scores = checker.recompute(source / 'data', native)
    differences = checker.compare(source / 'results', summary, scores, source / 'data', native)
    require(not differences, f'Independent multidoc recomputation differs: {differences[:3]}')
    require(len(scores) == 48 and all(s['valid'] for s in scores), 'Incomplete or invalid multidoc results')
    context = checker.verify_actual_context(source / 'data', source / 'results/predictions.jsonl')
    require(context['status'] == 'passed' and context['native_completed'], 'Completed frozen-run verification failed')
    saved = load(source / 'audit/independent_actual_result_audit.json')
    require(saved['status'] == 'passed' and saved['primary_comparison_mismatches'] == []
            and saved['primary_scorer_imported'] is False and saved['model_loaded'] is False
            and saved['inference_performed'] is False, 'Wrong independent audit status')
    require(saved['frozen_run_verification'] == context and saved['case_count'] == 48
            and saved['valid_count'] == 48 and saved['error_count'] == 24, 'Saved independent audit differs')
    require(saved['case_metrics'] == summary['case_metrics']
            and saved['error_case_ids'] == summary['error_case_ids'], 'Saved independent metrics differ')
    require(saved['independent_checker_sha256'] == sha(source / 'audit/independent_score_check.py'), 'Wrong independent checker')
    for name, digest in saved['input_sha256'].items():
        require(sha(source / name) == digest, f'Independent audit scientific pin differs: {name}')
    review = load(source / 'audit/independent_final_review.json')
    require(review['passed'] and review['no_unresolved_gold_or_scoring_issue'] and review['all_errors_reviewed']
            and review['post_outcome_gold_changes'] is False, 'Final scientific review failed')
    require(review['report_sha256'] == sha(source / 'REPORT.md')
            and review['errors_md_sha256'] == sha(source / 'ERRORS.md'), 'Scientific report review differs')
    errors = load(source / 'audit/independent_error_review.json')
    require(errors['passed'] and errors['error_count'] == errors['reviewed_error_count'] == 24
            and set(errors['error_ids']) == set(summary['error_case_ids']), 'Incomplete independent error review')
    for name, digest in errors['files'].items():
        require(sha(source / name) == digest, f'Semantic error review scientific pin differs: {name}')
    return scores


def build(source=SOURCE):
    source = Path(source)
    manifest = verify_manifest(source, EXPORT_MANIFEST_SHA256, PUBLIC_FILE_COUNT - 1)
    lock = verify_lock(source, 'freeze_manifest.json', FREEZE_SHA256, 61)
    verify_curated_scope(source, lock, manifest, PUBLIC_ADDITIONS)
    # This also rejects nonregular entries and empty unreviewed directories.
    verifier = module_from_file('multidoc_export_verifier', source / 'scripts/verify_export.py')
    verifier.verify(source)
    independent = {r['id']: r for r in recompute(source)}
    cases = load(source / 'data/cases.jsonl', True)
    requests = load(source / 'data/requests.jsonl', True)
    native = load(source / 'results/predictions.jsonl', True)
    require([c['id'] for c in cases] == [r['id'] for r in requests] == [p['id'] for p in native],
            'Native multidoc ordering differs')
    summary = load(source / 'results/summary.json')
    require(summary['suite_id'] == 'multidocument_precedence_2026_10_02'
            and summary['case_count'] == 48 and summary['family_count'] == 12
            and summary['paired_order_intervention'] is False, 'Wrong multidoc scope')
    require([summary['case_metrics'][f]['numerator'] for f in (*FIELDS, 'all_fields_exact')] == [42, 24, 24],
            'Wrong multidoc result')
    rows = []
    for case, request_row, prediction in zip(cases, requests, native):
        ident = case['id']; request = request_row['request']; score = independent[ident]
        require(request['state'] == case['state'], f'Input differs from native case: {ident}')
        require(list(request['questions']) == list(FIELDS), 'Wrong native schema field order')
        require(all(case[k] in request['state'] for k in ('precedence', 'facts', 'question')), 'Incomplete case context')
        fields = {f: {'prediction': prediction['answers'][f]['choice'],
                      'confidence': prediction['probabilities_unrounded'][f][prediction['answers'][f]['choice']],
                      'probabilities': prediction['probabilities_unrounded'][f],
                      'correct': score['field_correct'][f], 'schema_valid': score['valid']} for f in FIELDS}
        row = {k: case[k] for k in ('id', 'precedence', 'documents', 'facts', 'question', 'family', 'stratum',
               'subtype', 'template_id', 'plausible_source_ids', 'material_clarification',
               'source_uncertain_answer_definite', 'source_position')}
        row.update(title=case['question'], split=SPLIT, category=case['domain'],
                   tags=[case['stratum'], case['family'], case['template_id'], case['subtype']],
                   synthetic=True, manipulation=False, input=request['state'], questions=request['questions'],
                   document_texts=document_texts(case, request['state']), expected=case['expected'],
                   gold_rationale=case['rationale'], native_answers=prediction['answers'],
                   probabilities_unrounded=prediction['probabilities_unrounded'],
                   diagnostic_events=[event for event in EVENTS if score[event]],
                   input_tokens=prediction['input_tokens'], latency_ms=prediction['latency_ms'],
                   result={'fields': fields, 'correct': score['all_fields_exact'], 'schema_valid': score['valid']})
        rows.append(row)
    return {
        'schema_version': 1, 'status': 'completed',
        'suite': {'id': 'multidoc', 'title': 'Mehrere Dokumente: Was gilt?', 'fields': list(FIELDS),
                  'primary_split': SPLIT, 'splits': {SPLIT: 'Deutsch · Dokumentenvorrang'},
                  'categories': CATEGORIES, 'strata': STRATA,
                  'scope': '48 gezielt konstruierte synthetische Fälle, je drei Dokumente; 16 geteilte Vorlagen und 12 abhängige Regelfamilien; eigener Nenner'},
        'model': {'name': 'Cloudflare/clef-flash', 'revision': '17f0b0ad64efb65d273590632833508766b2aae6',
                  'configuration': 'Experimental CPU NF4 backbone with original BF16 joint head'},
        'definitions': {
            'source': 'Das eindeutig maßgebliche vollständige Dokument; not_unique, wenn mehrere Quellen möglich bleiben.',
            'determination': 'yes/no bei sicherem Ergebnis aller plausiblen vollständigen Quellen; unresolved nur bei ergebnisrelevanter Unklarheit.',
            'same_answer_controls': 'not_unique plus yes oder no kann korrekt sein: neun Fälle mit unklarer Quelle, aber sicherer Antwort.',
            'clarification_denominator': '12 erforderliche Klärungen und 36 sichere Antworten nach Gold-Determination; der Stratumname unresolved ist kein Nenner.',
            'confidence': 'Unveränderter marginaler Optionswert der nativen Wahl, keine kalibrierte Korrektheit und keine gemeinsame Wahrscheinlichkeit.',
            'native_answers': 'Unveränderte gespeicherte native Auswahl mit vierstellig gerundeter Anzeige; vollständige ungerundete Vektoren separat.',
            'consistency': summary['consistency']['scope'],
            'latency_ms': 'Recorded model-forward time only, excluding encoding, model loading and warmup; run-specific CPU NF4 observation.',
        },
        'verification': {'status': 'pass', 'n_present': 48, 'frozen_file_count': 61,
                         'source': 'experiments/multidoc48/audit/independent_actual_result_audit.json',
                         'freeze_manifest_sha256': FREEZE_SHA256,
                         'predictions_sha256': sha(source / 'results/predictions.jsonl'),
                         'independent_raw_metric_recomputation': True, 'model_inference_performed': False},
        'summary': summary, 'cases': rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, default=ROOT / 'web/data/multidoc.json')
    args = parser.parse_args()
    write_data(args.output, build(args.source))
    print('PASS: multidoc48 independent recomputation, native choices/vectors and complete context; deterministic UI export; no model loaded')

if __name__ == '__main__': main()
