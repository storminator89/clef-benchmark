"""Lightweight offline admission checks; fixtures are inventory bytes, not model observations."""
from pathlib import Path
import hashlib,importlib.util,json,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('study_builder',ROOT/'scripts/build_study_web_data.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class StudyImporterTests(unittest.TestCase):
 def make(self):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name);(root/'input.txt').write_text('synthetic inventory fixture only\n');manifest={'files':{'input.txt':hashlib.sha256((root/'input.txt').read_bytes()).hexdigest()}};(root/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifest));return root,hashlib.sha256((root/'PUBLIC_MANIFEST.json').read_bytes()).hexdigest()
 def test_reviewed_inventory_verified(self):
  root,pin=self.make();self.assertEqual(len(builder.verify_bundle(root,'PUBLIC_MANIFEST.json',pin)['files']),1)
 def test_modified_bytes_rejected(self):
  root,pin=self.make();(root/'input.txt').write_text('changed')
  with self.assertRaisesRegex(ValueError,'bytes changed'):builder.verify_bundle(root,'PUBLIC_MANIFEST.json',pin)
 def test_extra_files_rejected(self):
  root,pin=self.make();(root/'unreviewed.txt').write_text('extra')
  with self.assertRaisesRegex(ValueError,'file set'):builder.verify_bundle(root,'PUBLIC_MANIFEST.json',pin)
 def test_repinned_manifest_rejected(self):
  root,pin=self.make();(root/'PUBLIC_MANIFEST.json').write_text('{}')
  with self.assertRaisesRegex(ValueError,'manifest pin'):builder.verify_bundle(root,'PUBLIC_MANIFEST.json',pin)
 def test_completed_language_native_metrics(self):
  if 'language72' not in builder.ADMISSIONS:self.skipTest('No completed language source admitted')
  data=builder.build_all()['language72'];self.assertEqual(len(data['cases']),72);self.assertEqual(sum(r['correct'] for r in data['cases']),64)
  self.assertEqual([(m['numerator'],m['denominator']) for m in data['metrics']],[(64,72),(72,72),(40,48)])
  self.assertEqual({r['expected']['action'] for r in data['cases'] if not r['correct']},{'ask_target'})
  self.assertTrue(all('native_answers' in r for r in data['cases']))
 def test_jev_matched_denominators_and_pending_baseline(self):
  data=builder.build_all()['jev974'];self.assertEqual(len(data['cases']),974);self.assertEqual(sum(r['valid'] for r in data['cases']),937)
  self.assertEqual(sum('native_quarantine' in r for r in data['cases']),35)
  by={(r['suite'],r['split']):r for r in data['comparisons']}
  bank=by['bank_support80','german_primary'];self.assertEqual((bank['clef_correct'],bank['jev_correct'],bank['matched'],bank['expected']),(67,75,79,80))
  finance=by['finance100','german_primary'];self.assertEqual((finance['clef_correct'],finance['jev_correct'],finance['matched']),(75,78,79))
  massive=by['massive300','german_test_primary'];self.assertFalse(massive['baseline_ready']);self.assertIsNone(massive['clef_correct']);self.assertEqual((massive['jev_correct_valid_only'],massive['jev_valid'],massive['expected']),(219,266,300))
 def test_index_and_admitted_data_match(self):
  data=builder.build_all();index=json.loads((ROOT/'web/studies-data/index.json').read_text());self.assertEqual({x['id'] for x in index['studies'] if x['status']=='completed'},set(data))
  for ident,value in data.items():self.assertEqual(value,json.loads((ROOT/f'web/studies-data/{ident}.json').read_text()))
if __name__=='__main__':unittest.main()
