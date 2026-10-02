"""Results publication gates; mutate temporary fixtures, never original results."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_web_data',ROOT/'scripts/build_web_data.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class ImporterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'benchmark',self.root/'benchmark');shutil.copytree(ROOT/'results',self.root/'results')
    def tearDown(self):self.temp.cleanup()
    def edit_json(self,name,fn):
        p=self.root/name;v=json.loads(p.read_text());fn(v);p.write_text(json.dumps(v))
    def test_final(self):
        result=module.build(self.root);self.assertEqual(result['status'],'completed');self.assertEqual(len(result['cases']),180)
    def test_cases_only_no_results(self):
        result=module.build(self.root,True);self.assertEqual(result['status'],'test_data_only');self.assertNotIn('scores',result);self.assertTrue(all('result' not in c for c in result['cases']))
    def test_incomplete(self):
        self.edit_json('results/run_metadata.json',lambda v:v.update(status='running'))
        with self.assertRaises(ValueError):module.build(self.root)
    def test_wrong_model_revision(self):
        self.edit_json('results/run_metadata.json',lambda v:v.update(revision='different-model-version'))
        with self.assertRaises(ValueError):module.build(self.root)
    def test_hash_mismatch(self):
        self.edit_json('results/verification.json',lambda v:v.update(source_predictions_sha256='0'*64))
        with self.assertRaises(ValueError):module.build(self.root)
    def test_tampered_gold(self):
        with (self.root/'benchmark/gold.jsonl').open('a') as f:f.write('\n')
        with self.assertRaises(ValueError):module.build(self.root)
    def test_tampered_score(self):
        self.edit_json('results/scores_robust_v1_1.json',lambda v:v['case_results'][0].update(prediction='fabricated'))
        with self.assertRaises(ValueError):module.build(self.root)
    def test_duplicate(self):
        self.edit_json('results/scores_robust_v1_1.json',lambda v:v['case_results'].__setitem__(1,v['case_results'][0]))
        with self.assertRaises(ValueError):module.build(self.root)
    def test_aggregate_tamper(self):
        self.edit_json('results/scores_robust_v1_1.json',lambda v:v['splits']['german_primary'].update(choice_accuracy_all_planned=1))
        with self.assertRaises(ValueError):module.build(self.root)
if __name__=='__main__':unittest.main()
