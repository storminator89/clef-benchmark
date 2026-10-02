import unittest,json,copy
from pathlib import Path
from score_results import score
B=json.loads((Path(__file__).resolve().parents[1]/'benchmark/benchmark.json').read_text())
def fixture(wrong=False):
 rows=[]
 for c in B['cases']:
  answers={};probs={}
  for f in ('decision','evidence'):
   key=c['expected'][f]
   if wrong:key=next(k for k in c[f'{f}_options'] if k!=key)
   probs[f]={k:float(k==key) for k in c[f'{f}_options']};answers[f]={'choice':key,'confidence':1.,'probabilities':probs[f]}
  rows.append({'id':c['id'],'answers':answers,'probabilities_unrounded':probs,'input_tokens':900,'truncated':False,'inference_seconds':1.,'encode_seconds':.01})
 return rows
class ScorerTests(unittest.TestCase):
 def test_perfect(self):
  self.assertEqual(score(B,fixture())['summary']['exact_case']['correct'],60)
 def test_wrong(self):
  self.assertEqual(score(B,fixture(True))['summary']['field_accuracy']['correct'],0)
 def test_missing(self):
  with self.assertRaises(AssertionError):score(B,fixture()[:-1])
 def test_duplicate(self):
  rows=fixture()
  with self.assertRaises(AssertionError):score(B,rows+[rows[0]])
 def test_invalid_probs(self):
  rows=fixture();rows[0]['probabilities_unrounded']['decision']['ja']=float('nan')
  with self.assertRaises(AssertionError):score(B,rows)
 def test_truncation(self):
  rows=fixture();rows[0]['truncated']=True
  with self.assertRaises(AssertionError):score(B,rows)
 def test_one_field_only(self):
  rows=fixture();c=B['cases'][0];wrong=next(k for k in c['evidence_options'] if k!=c['expected']['evidence']);rows[0]['answers']['evidence']['choice']=wrong;rows[0]['probabilities_unrounded']['evidence']={k:float(k==wrong) for k in c['evidence_options']}
  s=score(B,rows)['summary'];self.assertEqual(s['decision']['correct'],60);self.assertEqual(s['evidence']['correct'],59);self.assertEqual(s['exact_case']['correct'],59);self.assertEqual(s['field_accuracy']['correct'],119)
if __name__=='__main__':unittest.main()
