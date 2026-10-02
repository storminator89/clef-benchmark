"""Immutable multidoc admission, complete source display, native outputs and curation."""
from __future__ import annotations
import builtins
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_multidoc_web_data as multidoc
import check_multidoc
from paired_reliability_common import serialize, module_from_file


class MultidocImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = multidoc.build()

    def copied_source(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        target = Path(temporary.name) / 'suite'; shutil.copytree(multidoc.SOURCE, target)
        return target

    def test_deterministic_exact_export(self):
        self.assertEqual(serialize(self.data), (ROOT / 'web/data/multidoc.json').read_bytes())
        self.assertEqual(self.data['suite']['fields'], ['source', 'determination'])
        self.assertEqual(self.data['suite']['id'], 'multidoc')

    def test_every_prior_scientific_suite_and_ui_dataset_preserved(self):
        self.assertEqual(check_multidoc.verify_protected_files(), 590)
        names = {r['path'] for r in check_multidoc.protected_rows()}
        self.assertTrue({'web/data/minimal_pairs.json', 'web/data/reliability.json'} <= names)
        self.assertTrue(any(n.startswith('experiments/minimal_pairs/') for n in names))
        self.assertTrue(any(n.startswith('experiments/probability_reliability/') for n in names))
        rows = check_multidoc.protected_rows()
        rows[0]['sha256'] = '0' * 64
        with patch.object(check_multidoc, 'protected_rows', return_value=rows):
            with self.assertRaisesRegex(ValueError, 'Previous scientific artifact set or bytes changed'):
                check_multidoc.verify_protected_files()

    def test_native_metrics_and_all_errors(self):
        summary = self.data['summary']
        self.assertEqual(summary, multidoc.load(multidoc.SOURCE / 'results/summary.json'))
        for field, expected in [('source', 42), ('determination', 24), ('all_fields_exact', 24)]:
            self.assertEqual(summary['case_metrics'][field], {'numerator': expected, 'denominator': 48, 'rate': expected/48})
        self.assertEqual([r['id'] for r in self.data['cases'] if not r['result']['correct']], summary['error_case_ids'])
        self.assertEqual(len(summary['error_case_ids']), 24)
        self.assertEqual(sum(r['result']['schema_valid'] for r in self.data['cases']), 48)

    def test_full_native_context_order_and_exact_document_blocks(self):
        original = multidoc.load(multidoc.SOURCE / 'data/cases.jsonl', True)
        requests = multidoc.load(multidoc.SOURCE / 'data/requests.jsonl', True)
        for case, raw, request in zip(self.data['cases'], original, requests):
            self.assertEqual(case['input'], raw['state'])
            self.assertEqual(case['input'], request['request']['state'])
            self.assertEqual(case['questions'], request['request']['questions'])
            for key in ('documents', 'precedence', 'facts', 'question', 'expected', 'plausible_source_ids', 'source_position', 'template_id'):
                self.assertEqual(case[key], raw[key])
            self.assertEqual(list(case['document_texts']), [d['id'] for d in raw['documents']])
            for document in raw['documents']:
                block = case['document_texts'][document['id']]
                self.assertIn(block, case['input'])
                self.assertTrue(block.startswith(f'Dokument {document["id"]} — {document["title"]}\n'))
                self.assertIn('Vollständige Regel:', block)
                self.assertFalse(block.endswith('\n'))
            self.assertIn('\n\n'.join(case['document_texts'].values()), case['input'])

    def test_native_choices_and_probabilities_are_not_repaired_or_rounded(self):
        predictions = multidoc.load(multidoc.SOURCE / 'results/predictions.jsonl', True)
        for case, native in zip(self.data['cases'], predictions):
            self.assertEqual(case['native_answers'], native['answers'])
            self.assertEqual(case['probabilities_unrounded'], native['probabilities_unrounded'])
            for field in multidoc.FIELDS:
                value = case['result']['fields'][field]
                self.assertEqual(value['prediction'], native['answers'][field]['choice'])
                self.assertEqual(value['probabilities'], native['probabilities_unrounded'][field])
                self.assertEqual(value['confidence'], value['probabilities'][value['prediction']])
                self.assertEqual(value['correct'], value['prediction'] == case['expected'][field])

    def test_source_ambiguity_can_have_a_correct_definite_answer(self):
        controls = [r for r in self.data['cases'] if r['source_uncertain_answer_definite']]
        self.assertEqual(len(controls), 9)
        self.assertEqual(sum(r['result']['correct'] for r in controls), 6)
        for row in controls:
            self.assertEqual(row['expected']['source'], 'not_unique')
            self.assertIn(row['expected']['determination'], ('yes', 'no'))
            if row['result']['correct']:
                self.assertNotIn('field_pair_inconsistent_with_visible_rules', row['diagnostic_events'])
        self.assertEqual(sum(r['material_clarification'] for r in self.data['cases']), 12)
        # The stratum includes definite controls and cannot define required clarification.
        self.assertNotEqual({r['id'] for r in self.data['cases'] if r['material_clarification']},
                            {r['id'] for r in self.data['cases'] if r['stratum'] == 'unresolved'})
        self.assertEqual(sum('missed_clarification' in r['diagnostic_events'] for r in self.data['cases']), 8)
        self.assertEqual(sum('excess_clarification' in r['diagnostic_events'] for r in self.data['cases']), 8)

    def test_frozen_all_61_files_unchanged_and_scope_only_provenance(self):
        frozen = multidoc.load(multidoc.SOURCE / 'freeze_manifest.json')
        self.assertEqual(len(frozen['files']), 61)
        self.assertEqual(multidoc.sha(multidoc.SOURCE / 'freeze_manifest.json'), multidoc.FREEZE_SHA256)
        for name, digest in frozen['files'].items(): self.assertEqual(multidoc.sha(multidoc.SOURCE / name), digest)
        portable = multidoc.load(multidoc.SOURCE / 'provenance/portable_export.json')
        self.assertEqual(set(portable), {'schema_version','suite_id','frozen_content_changed',
            'frozen_manifest_sha256','frozen_file_count','public_scope','excluded_scope'})
        manifest = multidoc.load(multidoc.SOURCE / 'FILE_SHA256.json')
        self.assertEqual(set(manifest), set(frozen['files']) | multidoc.PUBLIC_ADDITIONS)
        self.assertEqual(len(manifest) + 1, multidoc.PUBLIC_FILE_COUNT)
        audit = multidoc.load(multidoc.SOURCE / 'audit/independent_actual_result_audit.json')
        self.assertNotIn('case_rows', audit)
        self.assertNotIn('summary', audit)
        self.assertFalse(audit['model_loaded'])
        review = multidoc.load(multidoc.SOURCE / 'audit/independent_final_review.json')
        self.assertNotIn('reviewed_public_files', review)
        self.assertNotIn('runtime_public_evidence_checks', review)

    def test_changed_native_bytes_or_rehashed_input_rejected(self):
        for name in ('results/predictions.jsonl', 'data/cases.jsonl', 'results/summary.json', 'audit/independent_actual_result_audit.json'):
            with self.subTest(name=name):
                root = self.copied_source(); path = root / name
                path.write_bytes(path.read_bytes() + b'\n')
                with self.assertRaisesRegex(ValueError, 'Export hash mismatch'): multidoc.build(root)
                manifest = multidoc.load(root / 'FILE_SHA256.json'); manifest[name] = multidoc.sha(path)
                (root / 'FILE_SHA256.json').write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, 'Public export manifest changed'): multidoc.build(root)

    def test_missing_extra_symlink_and_empty_directory_rejected(self):
        for mutation in ('missing', 'extra', 'symlink', 'directory'):
            with self.subTest(mutation=mutation):
                root = self.copied_source()
                if mutation == 'missing': (root / 'REPORT.md').unlink()
                elif mutation == 'extra': (root / 'unreviewed.txt').write_text('unreviewed')
                elif mutation == 'symlink':
                    path = root / 'REPORT.md'; path.unlink(); path.symlink_to(root / 'README.md')
                else: (root / 'unreviewed').mkdir()
                with self.assertRaises((ValueError, AssertionError)): multidoc.build(root)

    def test_document_boundary_corruption_rejected(self):
        case = multidoc.load(multidoc.SOURCE / 'data/cases.jsonl', True)[0]
        with self.assertRaises(ValueError):
            multidoc.document_texts(case, case['state'].replace('Vollständige Regel:', 'Rule:'))
        changed = copy.deepcopy(case); changed['documents'].reverse()
        with self.assertRaises(ValueError): multidoc.document_texts(changed, case['state'])

    def test_model_libraries_cannot_be_imported(self):
        original = builtins.__import__
        def guarded(name, *args, **kwargs):
            self.assertNotIn(name.split('.')[0], {'torch','transformers','bitsandbytes','accelerate','huggingface_hub','safetensors'})
            return original(name, *args, **kwargs)
        with patch('builtins.__import__', side_effect=guarded):
            self.assertEqual(multidoc.build(), self.data)

    def test_independent_rescore_rejects_native_semantic_drift(self):
        root = self.copied_source()
        rows = multidoc.load(root / 'results/predictions.jsonl', True)
        rows[0]['answers']['source']['confidence'] += .0001
        (root / 'results/predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        with self.assertRaisesRegex(ValueError, 'Independent multidoc recomputation differs'):
            multidoc.recompute(root)

if __name__ == '__main__': unittest.main()
