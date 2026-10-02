"""Publication gates for the separately verified clean72 dashboard."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('clean_import',ROOT/'scripts/build_clean_web_data.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class CleanImporterTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  shutil.copytree(ROOT/'experiments/clean72',self.root/'experiments/clean72')
  (self.root/'runtime').mkdir()
  for name in ('run_clef.py','joint_schema_model.py'):shutil.copy2(ROOT/'runtime'/name,self.root/'runtime'/name)
 def tearDown(self):self.tmp.cleanup()
 def edit(self,name,fn):
  p=self.root/'experiments/clean72'/name;v=json.loads(p.read_text());fn(v);p.write_text(json.dumps(v))
 def rejected(self):
  with self.assertRaises(ValueError):module.build(self.root)
 def test_final_and_exact_frozen_labels(self):
  data=module.build(self.root);self.assertEqual(data['suite']['id'],'clean72');self.assertEqual(len(data['cases']),72)
  self.assertEqual(sum(c['result']['correct'] for c in data['cases']),61);self.assertEqual(data['scores']['paired_all_planned'],{})
  self.assertEqual({c['split'] for c in data['cases']},{'german_clean_primary'})
 def test_incomplete(self):self.edit('results/predictions.metadata.json',lambda v:v.update(status='running'));self.rejected()
 def test_wrong_model(self):self.edit('results/predictions.metadata.json',lambda v:v.update(revision='other'));self.rejected()
 def test_missing_qa(self):self.edit('results/verification.json',lambda v:v.update(status='pending'));self.rejected()
 def test_wrong_qa_hash(self):self.edit('results/verification.json',lambda v:v.update(artifacts_sha256={}));self.rejected()
 def test_tampered_score(self):self.edit('results/scores.json',lambda v:v['overall'].update(correct=72));self.rejected()
 def test_tampered_case_score(self):self.edit('results/scores.json',lambda v:v['case_results'][0].update(prediction='fake'));self.rejected()
 def test_tampered_gold(self):
  p=self.root/'experiments/clean72/benchmark/gold.jsonl';p.write_text(p.read_text()+'\n');self.rejected()
 def test_missing_prediction(self):
  p=self.root/'experiments/clean72/results/predictions.jsonl';p.write_text('\n'.join(p.read_text().splitlines()[:-1])+'\n');self.rejected()
if __name__=='__main__':unittest.main()
