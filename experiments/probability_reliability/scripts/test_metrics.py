import math,unittest
from metrics import field_metrics
from analyze import probability_issues

def row(i,p,gold,choice):return dict(id=i,probabilities=p,gold=gold,choice=choice)
def native(p,c):return {'type':'choice','choice':c,'confidence':round(p[c],4),'probabilities':{k:round(v,4) for k,v in p.items()}}
class MetricsTests(unittest.TestCase):
 def test_perfect(self):
  m=field_metrics([row('a',{'x':1.,'y':0.},'x','x')],1)
  self.assertEqual((m['brier_mean'],m['nll_mean'],m['ece_10_equal_width'],m['accuracy']),(0,0,0,1))
 def test_impossible_gold(self):
  m=field_metrics([row('a',{'x':1.,'y':0.},'y','x')],1)
  self.assertEqual(m['brier_mean'],2);self.assertTrue(m['nll_is_infinite']);self.assertIsNone(m['nll_mean']);self.assertEqual(m['zero_gold_probability_ids'],['a'])
 def test_multiclass_sum(self):
  m=field_metrics([row('a',{'x':.5,'y':.3,'z':.2},'y','x')],1)
  self.assertAlmostEqual(m['brier_mean'],.78);self.assertAlmostEqual(m['nll_mean'],-math.log(.3))
 def test_saved_tie_choice(self):
  m=field_metrics([row('a',{'x':.5,'y':.5},'y','y')],1)
  self.assertEqual(m['correct'],1);self.assertEqual(m['tie_count'],1)
 def test_auroc_tie(self):
  m=field_metrics([row('a',{'x':.8,'y':.2},'x','x'),row('b',{'x':.8,'y':.2},'y','x')],2)
  self.assertEqual(m['error_detection_auroc'],.5)
 def test_auroc_good(self):
  m=field_metrics([row('a',{'x':.9,'y':.1},'x','x'),row('b',{'x':.6,'y':.4},'y','x')],2)
  self.assertEqual(m['error_detection_auroc'],1)
 def test_auroc_bad(self):
  m=field_metrics([row('a',{'x':.6,'y':.4},'x','x'),row('b',{'x':.9,'y':.1},'y','x')],2)
  self.assertEqual(m['error_detection_auroc'],0)
 def test_empty(self):
  m=field_metrics([],2);self.assertEqual(m['valid_count'],0);self.assertIsNone(m['accuracy']);self.assertIsNone(m['nll_mean']);self.assertIsNone(m['error_detection_auroc'])
  self.assertTrue(all(x['risk'] is None and x['coverage']==0 for x in m['risk_coverage']))
 def test_expected_denominator(self):
  m=field_metrics([row('a',{'x':.8,'y':.2},'x','x')],2)
  self.assertEqual(m['accuracy'],1);self.assertEqual(m['correct_over_expected'],.5);self.assertEqual(m['risk_coverage'][0]['coverage'],.5);self.assertEqual(m['risk_coverage'][0]['valid_coverage'],1)
 def test_ece_weighting(self):
  m=field_metrics([row('a',{'x':.8,'y':.2},'x','x'),row('b',{'x':.8,'y':.2},'x','x'),row('c',{'x':.6,'y':.4},'y','x')],3)
  self.assertAlmostEqual(m['ece_10_equal_width'],(2*.2+.6)/3)
 def test_exact_boundary(self):
  for v,bin_index in [(.5,5),(.7,7),(.8,8),(.9,9),(1.,9),(math.nextafter(.9,0),8)]:
   m=field_metrics([row('a',{'x':v,'y':1-v},'x','x')],1)
   self.assertEqual([i for i,b in enumerate(m['bins']) if b['count']],[bin_index])
 def test_threshold_boundary(self):
  m=field_metrics([row('a',{'x':.9,'y':.1},'x','x')],1)
  self.assertEqual(m['risk_coverage'][3]['selected_count'],1);self.assertEqual(m['risk_coverage'][4]['selected_count'],0)
 def test_nll_finite_only_explicit(self):
  m=field_metrics([row('a',{'x':.5,'y':.5},'x','x'),row('b',{'x':1.,'y':0.},'y','x')],2)
  self.assertIsNone(m['nll_mean']);self.assertEqual(m['finite_nll_count'],1);self.assertAlmostEqual(m['finite_nll_mean'],math.log(2))
 def test_validation_success(self):
  p={'x':.5,'y':.5};self.assertEqual(probability_issues({'type':'choice','criteria':{'x':'X','y':'Y'}},native(p,'y'),p,'x'),[])
 def test_validation_bad_probability(self):
  for p in [{'x':float('nan'),'y':.5},{'x':True,'y':0.},{'x':1.2,'y':-.2}]:
   self.assertIn('invalid_probability_value',probability_issues({'type':'choice','criteria':{'x':'X','y':'Y'}},{'type':'choice','choice':'x'},p,'x'))
 def test_validation_sum(self):
  p={'x':.8,'y':.3};self.assertIn('probability_sum_outside_tolerance',probability_issues({'type':'choice','criteria':{'x':'X','y':'Y'}},native(p,'x'),p,'x'))
 def test_validation_argmax(self):
  p={'x':.8,'y':.2};self.assertIn('native_choice_not_exact_maximum',probability_issues({'type':'choice','criteria':{'x':'X','y':'Y'}},native(p,'y'),p,'x'))
 def test_validation_display(self):
  p={'x':.8,'y':.2};a=native(p,'x');a['confidence']=.9;self.assertIn('displayed_confidence_rounding_mismatch',probability_issues({'type':'choice','criteria':{'x':'X','y':'Y'}},a,p,'x'))
 def test_validation_no_renormalization(self):
  p={'x':.500001,'y':.5};self.assertEqual(probability_issues({'type':'choice','criteria':{'x':'X','y':'Y'}},native(p,'x'),p,'x'),[]);self.assertEqual(p['x'],.500001)
 def test_validation_missing_options(self):
  self.assertIn('invalid_or_missing_unrounded_options',probability_issues({'type':'choice','criteria':{'x':'X','y':'Y'}},{'type':'choice','choice':'x'},{'x':1.},'x'))
if __name__=='__main__':unittest.main()
