"""Public inactive comparison contract; no live network or secret access."""
import importlib.util,json,hashlib,sys,tempfile,unittest,shutil
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import check_jev
class JevPreparationTests(unittest.TestCase):
    def test_curated_export_and_offline_preflight(self):
        result=check_jev.check()
        self.assertEqual(result['requests'],974)
        self.assertEqual(result['scientific_files_sha256_verified'],68)
        self.assertEqual(result['network_calls'],0)
        self.assertEqual(result['credential_reads'],0)
    def test_scientific_files_have_no_changed_native_values(self):
        m=json.loads((check_jev.SOURCE/'manifest.json').read_text())
        self.assertFalse(m['publication_scope']['scientific_inputs_and_native_predictions_changed'])
        self.assertEqual(m['base_public_commit'],'74b9c52cf7fb2f09f3dc19caf448b6a4a40be9ba')
        self.assertEqual(len(m['suites']),10)
        self.assertEqual(sum(s['count'] for s in m['suites']),974)
    def test_changed_request_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'suite';shutil.copytree(check_jev.SOURCE,p)
            f=p/'inputs/multidoc48/requests.jsonl';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'artifact changed'):check_jev.check(p)
    def test_extra_result_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'suite';shutil.copytree(check_jev.SOURCE,p)
            (p/'unreviewed_result.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'missing or extra'):check_jev.check(p)
    def test_rehashed_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'suite';shutil.copytree(check_jev.SOURCE,p)
            f=p/'FILE_SHA256.json';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'Unexpected curated'):check_jev.check(p)
    def test_historical_gate_evolution_preserves_exact_prior_digest(self):
        import check_paired_reliability as previous
        self.assertEqual(previous.verify_protected_files(),388)
        evolution=json.loads((ROOT/'provenance/multidoc_gate_evolution.json').read_text())
        self.assertEqual(evolution['new_stage_only'],['experiments/multidoc48/','experiments/jev_comparison/','web/data/multidoc.json'])
        self.assertEqual(evolution['to_sha256'],hashlib.sha256((ROOT/evolution['gate']).read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as td:
            copy=Path(td)/'project';shutil.copytree(ROOT,copy)
            (copy/'experiments/minimal_pairs/new-unreviewed.json').write_text('{}')
            # The newer paired exporter rejects extra additions even though this older gate predates it.
            import build_minimal_pairs_web_data
            with self.assertRaises(ValueError):build_minimal_pairs_web_data.build(copy/'experiments/minimal_pairs')
    def test_inactive_template_and_offline_ci(self):
        template=(check_jev.SOURCE/'workflow/jev-comparison.yml.in').read_text()
        self.assertIn('ref: REVIEWED_CODE_COMMIT_SHA',template)
        self.assertEqual(template.count('default: false'),2)
        for p in (ROOT/'.github/workflows').iterdir():
            if p.name == 'jev-comparison.yml':
                activation=json.loads((ROOT/'provenance/jev_final_activation.json').read_text())
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),activation['workflow_sha256'])
                if activation['status']=='prepared_inert_not_activated':
                    self.assertNotIn('JEV_API_KEY',p.read_text())
                    self.assertNotIn('--execute',p.read_text())
                else:
                    self.assertIn('ref: '+activation['reviewed_code_commit'],p.read_text())
                continue
            self.assertNotIn('JEV_API_KEY',p.read_text())
            self.assertNotIn('jev_runner.py --execute',p.read_text())
    def test_no_jev_results_or_completed_massive_baseline(self):
        m=json.loads((check_jev.SOURCE/'manifest.json').read_text())
        self.assertEqual(m['status'],'prepared_not_executed')
        self.assertEqual([x['id'] for x in m['suites'] if x['baseline']!='complete'],['massive300'])
        self.assertFalse((check_jev.SOURCE/'runs').exists())
        self.assertFalse((check_jev.SOURCE/'inputs/massive300/predictions.jsonl').exists())
    def test_compact_public_provenance(self):
        p=json.loads((check_jev.SOURCE/'baseline_provenance.json').read_text())
        self.assertEqual(len(p['baselines']),9)
        for obj in p['baselines'].values():
            self.assertTrue(set(obj)<= {'model','revision','mode','dtype','device','threads','batch_size','max_length','request_count','status','request_sha256','prediction_sha256','timing_definition'})
if __name__=='__main__':unittest.main()
