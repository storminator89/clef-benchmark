"""Immutable admission, independent recomputation and unpooled UI regression tests."""
from __future__ import annotations
import builtins
from collections import defaultdict
import copy
import json
import math
import os
import re
import subprocess
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_minimal_pairs_web_data as paired
import build_reliability_web_data as reliability
import check_paired_reliability as gate
from paired_reliability_common import load, sha, serialize, verify_manifest, public_file


class PairedReliabilityImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pairs = paired.build()
        cls.reliability = reliability.build()

    def copied_source(self, source):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / 'suite'
        shutil.copytree(source, root)
        return root

    def test_exact_deterministic_exports(self):
        self.assertEqual(serialize(self.pairs), (ROOT / 'web/data/minimal_pairs.json').read_bytes())
        self.assertEqual(serialize(self.reliability), (ROOT / 'web/data/reliability.json').read_bytes())

    def test_exact_paired_metrics_and_denominators(self):
        summary = self.pairs['summary']
        self.assertEqual([summary['case_metrics'][f]['numerator'] for f in ('action', 'determination', 'all_fields_exact')], [40, 42, 39])
        for key, n, d in [('both_correct',17,24), ('correct_directional_change',8,12),
                          ('observed_change_on_flip',12,12), ('stable_invariant',11,12),
                          ('stable_but_incorrect',2,12), ('unjustified_change',1,12)]:
            self.assertEqual(summary['pair_metrics'][key], {'numerator': n, 'denominator': d, 'rate': n/d})
        self.assertEqual(summary['pair_strata']['kind']['invariant']['both_correct']['numerator'], 9)

    def test_pair_sides_and_changed_spans_preserve_exact_source(self):
        raw_pairs = load(paired.SOURCE / 'data/pairs.jsonl', True)
        raw_cases = {r['id']: r for r in load(paired.SOURCE / 'data/cases.jsonl', True)}
        for pair, raw in zip(self.pairs['pairs'], raw_pairs):
            self.assertEqual(pair['id'], raw['id'])
            self.assertEqual(pair['changed_fact'], raw['changed_fact'])
            for side in ('a', 'b'):
                member = pair[side]; context = raw_cases[member['id']]
                self.assertEqual(member['message'], raw['unchanged_prefix'] + raw['span_' + side] + raw['unchanged_suffix'])
                lo, hi = pair['change']['offsets_' + side]
                self.assertEqual(member['message'][lo:hi], raw['span_' + side])
                for k in ('rule','message','question'):
                    self.assertEqual(member[k], context[k]); self.assertIn(member[k], member['input'])
                self.assertEqual(member['gold_rationale'], context['rationale'])
                self.assertEqual(member['expected'], context['expected'])

    def test_native_choices_vectors_and_confidence_are_not_repaired(self):
        native = {r['id']: r for r in load(paired.SOURCE / 'results/predictions.jsonl', True)}
        changed_but_wrong = stable_wrong = 0
        for pair in self.pairs['pairs']:
            outcome = pair['outcome']
            changed_but_wrong += pair['kind'] == 'flip' and outcome['observed_change'] and not outcome['both_correct']
            stable_wrong += outcome['stable_but_incorrect'] is True
            for side in ('a', 'b'):
                member = pair[side]; raw = native[member['id']]
                for field, value in member['result']['fields'].items():
                    self.assertEqual(value['prediction'], raw['answers'][field]['choice'])
                    self.assertEqual(value['probabilities'], raw['probabilities_unrounded'][field])
                    self.assertEqual(value['confidence'], value['probabilities'][value['prediction']])
                    self.assertEqual(value['correct'], value['prediction'] == member['expected'][field])
        self.assertEqual((changed_but_wrong, stable_wrong), (4, 2))

    def test_reliability_retains_each_group_and_explicit_scope(self):
        data = self.reliability
        self.assertEqual((len(data['suites']),len(data['field_groups']),len(data['case_groups']),
                          len(data['observations']),len(data['cases'])), (9,78,64,1186,716))
        self.assertEqual(data['thresholds'], [.5,.7,.8,.9,.95,.99])
        self.assertEqual(data['field_groups'], load(reliability.SOURCE / 'results/field_metrics.json'))
        self.assertEqual(data['case_groups'], load(reliability.SOURCE / 'results/case_metrics.json'))
        self.assertNotIn('accuracy', data)
        self.assertTrue(all('accuracy' not in s and 'mean_selected_score' not in s for s in data['suites']))
        self.assertFalse(data['verification']['model_inference_performed'])
        self.assertEqual(data['verification']['independent_comparisons'], 65127)

    def test_every_observation_matches_original_unrounded_field(self):
        normalized = load(reliability.SOURCE / 'results/normalized_fields.jsonl', True)
        self.assertEqual(len(normalized), len(self.reliability['observations']))
        for row, original in zip(self.reliability['observations'], normalized):
            for key in ('suite_id','id','field','group_id','partition','option_keys','status','issues','gold','choice','probabilities'):
                self.assertEqual(row[key], original[key])
            self.assertEqual(row['confidence'], original['probabilities'][original['choice']])
            self.assertEqual(row['correct'], original['choice'] == original['gold'])
        self.assertEqual(sum(not r['correct'] for r in self.reliability['observations']), 124)

    def test_bins_threshold_risks_and_counts_recompute_within_groups(self):
        groups = defaultdict(list)
        for row in self.reliability['observations']: groups[row['group_id']].append(row)
        for metric in self.reliability['field_groups']:
            rows = groups[metric['group_id']]
            self.assertEqual(len(rows), metric['expected_count'])
            self.assertEqual(len(rows), metric['valid_count'])
            self.assertEqual(sum(r['correct'] for r in rows), metric['correct'])
            self.assertEqual({r['suite_id'] for r in rows}, {metric['suite_id']})
            self.assertEqual({r['field'] for r in rows}, {metric['field']})
            for row in rows:
                self.assertEqual(row['partition'], metric['partition'])
                self.assertEqual(row['option_keys'], metric['option_keys'])
            self.assertAlmostEqual(math.fsum(r['brier'] for r in rows)/len(rows), metric['brier_mean'], places=12)
            for bin_ in metric['bins']:
                selected = [r for r in rows if bin_['lower'] <= r['confidence']
                            and (r['confidence'] <= bin_['upper'] if bin_['upper_inclusive'] else r['confidence'] < bin_['upper'])]
                self.assertEqual(len(selected), bin_['count'])
                self.assertEqual(sum(r['correct'] for r in selected), bin_['correct'])
                if selected:
                    self.assertAlmostEqual(math.fsum(r['confidence'] for r in selected)/len(selected), bin_['mean_score'], places=12)
                    self.assertEqual(sum(r['correct'] for r in selected)/len(selected), bin_['accuracy'])
                else:
                    self.assertIsNone(bin_['mean_score']); self.assertIsNone(bin_['accuracy'])
            for threshold in metric['risk_coverage']:
                selected = [r for r in rows if r['confidence'] >= threshold['threshold']]
                errors = [r['id'] for r in selected if not r['correct']]
                self.assertEqual(len(selected), threshold['selected_count'])
                self.assertEqual(len(errors), threshold['incorrect'])
                self.assertEqual(threshold['coverage'], len(selected)/metric['expected_count'])
                self.assertEqual(threshold['risk'], len(errors)/len(selected) if selected else None)
                self.assertEqual(set(metric['high_score_error_ids'][f"{threshold['threshold']:.2f}"]), set(errors))

    def test_case_gate_is_minimum_not_product_and_preserves_full_context(self):
        rows = defaultdict(list)
        for observation in self.reliability['observations']:
            rows[observation['suite_id'], observation['id']].append(observation)
        for case in self.reliability['cases']:
            fields = rows[case['suite_id'], case['id']]
            self.assertEqual(case['minimum_selected_field_score_heuristic'], min(r['confidence'] for r in fields))
            self.assertEqual(case['exact'], all(r['correct'] for r in fields))
            self.assertEqual(set(case['questions']), set(case['required_fields']))
            self.assertEqual(case['expected'], {r['field']:r['gold'] for r in fields})
        evidence = [c for c in self.reliability['cases'] if c['suite_id'] == 'insurance60']
        self.assertTrue(all(c['questions']['evidence']['criteria'] for c in evidence))
        images = [g for g in self.reliability['field_groups'] if g['suite_id'] == 'images90']
        self.assertIn('blank', {g['partition']['condition'] for g in images})
        self.assertTrue(all(g['partition'].get('kind') and g['partition'].get('language') for g in images))

    def test_native_manifest_rejects_whitespace_tampering(self):
        for module in (paired, reliability):
            with self.subTest(module=module.__name__):
                root = self.copied_source(module.SOURCE)
                path = root / ('results/predictions.jsonl' if module is paired else 'sources/minimal_pairs48/predictions.jsonl')
                path.write_bytes(path.read_bytes() + b'\n')
                with self.assertRaisesRegex(ValueError, 'Export hash mismatch'): module.build(root)

    def test_rehashed_manifest_cannot_admit_tampering(self):
        for module in (paired, reliability):
            with self.subTest(module=module.__name__):
                root = self.copied_source(module.SOURCE)
                path = root / 'FILE_SHA256.json'
                path.write_bytes(path.read_bytes() + b' ')
                with self.assertRaisesRegex(ValueError, 'Public export manifest changed'): module.build(root)

    def test_missing_or_extra_public_files_fail(self):
        for module in (paired, reliability):
            for extra in (True, False):
                with self.subTest(module=module.__name__, extra=extra):
                    root = self.copied_source(module.SOURCE)
                    if extra: (root / 'unreviewed.json').write_text('{}')
                    else: (root / 'README.md').unlink()
                    with self.assertRaisesRegex(ValueError, 'Missing or extra'): module.build(root)

    def test_frozen_byte_checks_are_independent_of_export_admission(self):
        for module, name in ((paired,'data/gold.jsonl'), (reliability,'sources/minimal_pairs48/gold.jsonl')):
            root = self.copied_source(module.SOURCE)
            path = root / name; path.write_bytes(path.read_bytes() + b'\n')
            with patch.object(module, 'verify_manifest', return_value=(lambda m: m.get('files', m))(load(root / 'FILE_SHA256.json'))):
                with self.assertRaisesRegex(ValueError, 'Frozen input changed'): module.build(root)

    def test_paired_metrics_tampering_fails_independent_recompute(self):
        root = self.copied_source(paired.SOURCE)
        path = root / 'results/summary.json'; summary = load(path)
        summary['pair_metrics']['both_correct']['numerator'] += 1
        path.write_text(json.dumps(summary))
        with patch.object(paired, 'verify_manifest', return_value=(lambda m: m.get('files', m))(load(root / 'FILE_SHA256.json'))):
            with self.assertRaisesRegex(ValueError, 'Independent paired comparison failed'): paired.build(root)

    def test_paired_duplicate_native_ids_stop_scoring(self):
        root = self.copied_source(paired.SOURCE)
        path = root / 'results/predictions.jsonl'
        path.write_bytes(path.read_bytes() + path.read_bytes().splitlines(keepends=True)[0])
        with patch.object(paired, 'verify_manifest', return_value=(lambda m: m.get('files', m))(load(root / 'FILE_SHA256.json'))):
            with self.assertRaisesRegex(ValueError, 'Independent paired scoring stopped'): paired.build(root)

    def test_reliability_metrics_tampering_fails_raw_recompute(self):
        root = self.copied_source(reliability.SOURCE)
        path = root / 'results/field_metrics.json'; groups = load(path)
        groups[0]['risk_coverage'][0]['selected_count'] += 1
        path.write_text(json.dumps(groups))
        with patch.object(reliability, 'verify_manifest', return_value=(lambda m: m.get('files', m))(load(root / 'FILE_SHA256.json'))):
            with self.assertRaisesRegex(ValueError, 'raw-source recomputation differs'): reliability.build(root)

    def test_public_path_escape_and_symlinks_fail_closed(self):
        root = self.copied_source(paired.SOURCE)
        for name in ('../README.md', '/README.md', 'data/../README.md', './README.md', 'data\\gold.jsonl'):
            with self.subTest(name=name), self.assertRaises(ValueError): public_file(root, name)
        original = root / 'README.md'; original.unlink(); original.symlink_to(root / 'REPORT.md')
        with self.assertRaisesRegex(ValueError, 'Symlink'): paired.build(root)

    def test_scope_only_public_provenance_and_aggregate_baseline(self):
        allowed = {'schema_version','suite_id','frozen_content_changed','frozen_manifest_sha256',
                   'frozen_file_count','public_scope','excluded_scope'}
        for module in (paired,reliability):
            self.assertEqual(set(load(module.SOURCE / 'provenance/portable_export.json')), allowed)
        baseline = load(ROOT / 'provenance/paired_reliability_baseline.json')
        self.assertEqual((baseline['schema_version'],baseline['file_count']),(2,388))
        self.assertNotIn('protected_files_sha256', baseline)
        self.assertNotIn('files', baseline)
        self.assertEqual(gate.verify_protected_files(),388)
        self.assertEqual(gate.verify_retained_source_lineage(),69)

    def test_baseline_rejects_prior_science_tamper(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for row in gate.protected_rows():
            out = root / row['path']; out.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT / row['path'], out)
        for name in ('paired_reliability_baseline.json','clarification_baseline.json'):
            (root/'provenance').mkdir(exist_ok=True)
            shutil.copyfile(ROOT/'provenance'/name, root/'provenance'/name)
        self.assertEqual(gate.verify_protected_files(root),388)
        path=root/'web/data/clarification.json';path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'Previous scientific artifact set or bytes changed'):gate.verify_protected_files(root)

    def test_curated_public_allowlist_rejects_extra_rehashed_scope(self):
        for module, lockname in ((paired, 'freeze_manifest.json'), (reliability, 'SOURCE_LOCK.json')):
            root = self.copied_source(module.SOURCE)
            manifest = load(root / 'FILE_SHA256.json'); manifest = manifest.get('files', manifest)
            manifest['audit/development_debug.json'] = '0' * 64
            with patch.object(module, 'verify_manifest', return_value=manifest):
                with self.assertRaisesRegex(ValueError, 'reviewed curated allowlist'): module.build(root)

    def test_compact_final_evidence_has_no_diagnostic_inventory(self):
        report = load(paired.SOURCE / 'audit/independent_result_check.json')
        self.assertEqual(set(report), {'schema_version','passed','mismatches','prediction_count',
            'predictions_sha256','summary_sha256','synthetic_fixture_only','check_count','independence',
            'scoring_stopped','coverage','timing_percentile_definition','audit_script_sha256',
            'public_scope','reproduction_scope'})
        self.assertEqual((report['schema_version'],report['check_count'],report['mismatches']), (2,6972,[]))
        prose = load(paired.SOURCE / 'audit/independent_prose_review.json')
        self.assertEqual(prose['reviewed_error_case_count'],9)
        self.assertEqual(prose['reviewed_error_pair_count'],7)
        self.assertNotIn('supersedes',prose)
        method=(paired.SOURCE/'audit/INDEPENDENT_METHOD.md').read_text()
        for fact in ('815','6,972','60 independent','insertion order','byte lengths'):
            self.assertIn(fact,method)
        self.assertFalse(re.search(r'[a-f0-9]{64}',method))
        review=load(reliability.SOURCE/'audit/independent_review.json')
        self.assertNotIn('supplement_sha256',review)
        self.assertEqual(review['independent_comparisons'],65127)

    def test_scope_evolution_is_scoped_and_hash_free(self):
        for module,count in ((paired,50),(reliability,73)):
            note=load(module.SOURCE/'provenance/public_scope_evolution.json')
            self.assertFalse(note['scientific_inputs_outputs_changed'])
            self.assertEqual(note['locked_scientific_file_count'],count)
            self.assertFalse(re.search(r'[a-f0-9]{64}',json.dumps(note)))
            self.assertTrue(all(not isinstance(v,(dict,list)) for v in note.values()))

    def test_export_copies_only_manifest_and_rejects_an_alternate(self):
        root=self.copied_source(paired.SOURCE)
        (root/'audit/development_debug.json').write_text('{}')
        exported=root.parent/'exported'
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        process=subprocess.run([sys.executable,str(root/'scripts/export_public.py'),
                                '--destination',str(exported)],env=env,capture_output=True,text=True)
        self.assertEqual(process.returncode,0,process.stderr)
        verify_manifest(exported,paired.EXPORT_MANIFEST_SHA256,paired.PUBLIC_FILE_COUNT-1)
        self.assertFalse((exported/'audit/development_debug.json').exists())
        alternate=root.parent/'alternate.json'
        alternate.write_bytes((root/'FILE_SHA256.json').read_bytes()+b' ')
        process=subprocess.run([sys.executable,str(root/'scripts/export_public.py'),
            '--destination',str(root.parent/'rejected'),'--manifest',str(alternate)],
            env=env,capture_output=True,text=True)
        self.assertNotEqual(process.returncode,0)
        self.assertIn('current reviewed public allowlist',process.stderr)
        self.assertFalse((root.parent/'rejected').exists())

    def test_adapters_do_not_import_model_or_network_packages(self):
        original = builtins.__import__
        def no_model(name, *args, **kwargs):
            if name.split('.')[0] in {'torch','transformers','requests','huggingface_hub'}:
                raise AssertionError('Model/network package imported: '+name)
            return original(name, *args, **kwargs)
        with patch('builtins.__import__', side_effect=no_model):
            paired.build(); reliability.build()
        verify_manifest(paired.SOURCE, paired.EXPORT_MANIFEST_SHA256,paired.PUBLIC_FILE_COUNT - 1)
        verify_manifest(reliability.SOURCE,reliability.EXPORT_MANIFEST_SHA256,reliability.PUBLIC_FILE_COUNT - 1)

if __name__ == '__main__': unittest.main()
