"""Read-only clarification72 admission and deterministic UI/provenance regressions."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import copy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_clarification_web_data as clarification
import check_clarification

class ClarificationImporterTests(unittest.TestCase):
    def test_actual_metrics_vectors_and_full_input_preserved(self):
        data = clarification.build()
        self.assertEqual([data['summary']['metrics'][f]['numerator'] for f in (*clarification.FIELDS, 'all_fields_exact')], [65, 66, 64])
        requests = clarification.load(clarification.SOURCE / 'data/requests.jsonl', True)
        raw = clarification.load(clarification.SOURCE / 'results/predictions.jsonl', True)
        for c, req, p in zip(data['cases'], requests, raw):
            self.assertEqual(c['input'], req['request']['state'])
            self.assertEqual(c['questions'], req['request']['questions'])
            self.assertTrue(all(x in c['input'] for x in (c['rule'], c['message'], c['question'])))
            for f in clarification.FIELDS:
                self.assertEqual(c['result']['fields'][f]['probabilities'], p['probabilities_unrounded'][f])
                self.assertEqual(c['result']['fields'][f]['prediction'], p['answers'][f]['choice'])

    def test_missed_excess_and_inconsistent_native_pairs_are_not_repaired(self):
        data = clarification.build()
        for key, count in [('missed_required_clarifications', 4), ('excess_clarifications', 2), ('inconsistent_fields', 3), ('wrong_clarification_kind', 1), ('risky_wrong_answers', 4)]:
            self.assertEqual(sum(key in c['diagnostic_events'] for c in data['cases']), count)
        c = next(c for c in data['cases'] if c['id'] == 'clarify_order_cancellation_02')
        self.assertEqual([c['result']['fields'][f]['prediction'] for f in clarification.FIELDS], ['ask_fact', 'no'])
        self.assertFalse(c['result']['correct'])

    def test_export_manifest_pins_even_whitespace_changes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'suite'; shutil.copytree(clarification.SOURCE, root)
            p = root / 'results/predictions.jsonl'; p.write_bytes(p.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'Export hash mismatch'): clarification.build(root)

    def test_frozen_inputs_cannot_be_replaced_with_rehashed_export(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'suite'; shutil.copytree(clarification.SOURCE, root)
            name = 'data/cases.jsonl'; p = root / name; p.write_bytes(p.read_bytes() + b'\n')
            manifest = clarification.load(root / 'FILE_SHA256.json'); manifest[name] = clarification.sha(p)
            (root / 'FILE_SHA256.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Frozen input changed|Public export manifest changed'): clarification.build(root)

    def test_rehashed_summary_or_partial_report_rejected(self):
        for name in ('results/summary.json', 'audit/independent_result_check.json'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                root = Path(td) / 'suite'; shutil.copytree(clarification.SOURCE, root)
                value = clarification.load(root / name)
                if name.startswith('results'): value['metrics']['action']['numerator'] += 1
                else: value['recomputed_metrics'] = {}
                (root / name).write_text(json.dumps(value))
                manifest = clarification.load(root / 'FILE_SHA256.json'); manifest[name] = clarification.sha(root / name)
                (root / 'FILE_SHA256.json').write_text(json.dumps(manifest))
                with self.assertRaises(ValueError): clarification.build(root)

    def test_extra_or_missing_export_file_rejected(self):
        for extra in (True, False):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td) / 'suite'; shutil.copytree(clarification.SOURCE, root)
                if extra: (root / 'unreviewed.json').write_text('{}')
                else: (root / 'REPORT.md').unlink()
                with self.assertRaisesRegex(ValueError, 'Missing or extra'): clarification.build(root)

    def test_previous_science_runtime_and_ui_data_unchanged(self):
        manifest = clarification.load(ROOT / 'provenance/clarification_baseline.json')
        self.assertEqual(len(manifest['protected_files_sha256']), 310)
        self.assertEqual(check_clarification.verify_protected_files(), (310, 2))

    def test_public_metadata_evolution_cannot_expand_to_scientific_files(self):
        baseline = clarification.load(ROOT / 'provenance/clarification_baseline.json')
        evolution = clarification.load(ROOT / 'provenance/public_curation_evolution.json')
        for change in ('expand', 'wrong_from', 'wrong_to'):
            mutated = copy.deepcopy(evolution)
            name = 'experiments/bank-support/provenance/portable_export.json'
            if change == 'expand': mutated['changes']['results/predictions.jsonl'] = mutated['changes'][name]
            else: mutated['changes'][name][('from_sha256' if change == 'wrong_from' else 'to_sha256')] = '0' * 64
            with patch.object(check_clarification, 'load', side_effect=[baseline, mutated]):
                with self.assertRaises(AssertionError): check_clarification.verify_protected_files()

    def test_public_curation_has_no_realized_private_omission_identifiers(self):
        allowed = {'schema_version', 'suite_id', 'frozen_content_changed', 'frozen_manifest_sha256',
                   'frozen_file_count', 'public_scope', 'excluded_scope'}
        for suite in ('bank-support', 'clarification72'):
            obj = clarification.load(ROOT / 'experiments' / suite / 'provenance/portable_export.json')
            self.assertEqual(set(obj), allowed | ({'frozen_file_mapping'} if suite == 'bank-support' else set()))
            if suite == 'bank-support':
                frozen = clarification.load(ROOT / 'experiments' / suite / 'freeze_manifest.json')['files']
                for row in obj['frozen_file_mapping']:
                    self.assertEqual(row['original_path'], row['published_path'])
                    self.assertEqual(row['original_sha256'], frozen[row['published_path']])
                    self.assertEqual(row['published_sha256'], frozen[row['published_path']])
            self.assertFalse(obj['frozen_content_changed'])
        for name in ('resource_monitor.jsonl', 'execution_events.jsonl'):
            self.assertFalse((clarification.SOURCE / 'results' / name).exists())

    def test_exact_deterministic_derived_file(self):
        self.assertEqual(clarification.build(), clarification.load(ROOT / 'web/data/clarification.json'))

if __name__ == '__main__': unittest.main()
