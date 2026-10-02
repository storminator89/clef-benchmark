"""Synthetic tests; no model output or primary metric imports."""
import math
import unittest
from independent_metrics import compute, confidence_bin, error_auroc, validate_record


def record(rid, ps, choice=0, gold=0):
    options = [f'c{i}' for i in range(len(ps))]
    return dict(id=rid, options=options, probabilities=ps, choice=options[choice], gold=options[gold])


class ReferenceTests(unittest.TestCase):
    def test_all_decimal_bin_boundaries(self):
        for i in range(1,10):
            x=i/10
            self.assertEqual(confidence_bin(x), i)
            self.assertEqual(confidence_bin(math.nextafter(x,0)), i-1)
            self.assertEqual(confidence_bin(math.nextafter(x,1)), i)
        self.assertEqual(confidence_bin(0),0)
        self.assertEqual(confidence_bin(1),9)

    def test_brier_extremes_and_zero_gold_nll(self):
        a=compute([record('a',[1.,0.])])
        self.assertEqual((a['brier'],a['nll'],a['accuracy']), (0.,0.,1.))
        b=compute([record('b',[1.,0.],gold=1)])
        self.assertEqual(b['brier'],2.)
        self.assertEqual(b['nll'],math.inf)
        self.assertEqual(b['infinite_nll_ids'],['b'])

    def test_multiclass_sum_not_normalized(self):
        a=compute([record('a',[.2,.3,.5],choice=2,gold=1)])
        self.assertAlmostEqual(a['brier'],.78)
        self.assertAlmostEqual(a['nll'],-math.log(.3))

    def test_native_choice_tie_is_preserved(self):
        a=compute([record('a',[.5,.5],choice=1,gold=1)])
        self.assertEqual(a['accuracy'],1.)
        self.assertEqual(a['rows'][0]['choice'],'c1')
        self.assertEqual(a['rows'][0]['max_tie_options'],['c0','c1'])

    def test_ece_is_count_weighted(self):
        a=compute([record('a',[.5,.5]),record('b',[.9,.1]),record('c',[.9,.1],gold=1)])
        self.assertAlmostEqual(a['ece'],(.5 + 2*.4)/3)
        self.assertEqual(sum(b['count'] for b in a['bins']),3)

    def test_fixed_risk_coverage_boundaries(self):
        ps=[.5,.7,.8,.9,.95,.99]
        a=compute([record(str(i),[p,1-p],gold=i%2) for i,p in enumerate(ps)])
        self.assertEqual([x['accepted'] for x in a['risk_coverage']],[6,5,4,3,2,1])
        self.assertEqual([x['errors'] for x in a['risk_coverage']],[3,3,2,2,1,1])
        self.assertAlmostEqual(a['risk_coverage'][-2]['risk'],.5)

    def test_no_coverage_is_undefined(self):
        a=compute([record('a',[.5,.5])])
        self.assertEqual(a['risk_coverage'][-1]['coverage'],0.)
        self.assertIsNone(a['risk_coverage'][-1]['risk'])

    def test_auc_ranking_and_ties(self):
        self.assertEqual(error_auroc([dict(correct=False,confidence=.5),dict(correct=True,confidence=.9)]),1.)
        self.assertEqual(error_auroc([dict(correct=False,confidence=.9),dict(correct=True,confidence=.5)]),0.)
        self.assertEqual(error_auroc([dict(correct=False,confidence=.9),dict(correct=True,confidence=.9)]),.5)
        self.assertEqual(error_auroc([dict(correct=False,confidence=.9),dict(correct=False,confidence=.5),dict(correct=True,confidence=.9)]),.75)
        self.assertIsNone(error_auroc([]))
        self.assertIsNone(error_auroc([dict(correct=True,confidence=.5)]))
        self.assertIsNone(error_auroc([dict(correct=False,confidence=.5)]))
        self.assertEqual(error_auroc([dict(correct=False,confidence=.25),dict(correct=True,confidence=math.nextafter(.25,1))]),1.)

    def test_invalid_probability_vectors(self):
        for ps in ([1.1,-.1],[.5,.4],[math.nan,.5],[math.inf,0],[True,0]):
            with self.subTest(ps=ps):
                self.assertTrue(validate_record(record('a',ps)))
        bad=record('a',[.5,.5]);bad['probabilities']=[.5]
        self.assertIn('probability_shape',validate_record(bad))
        bad=record('a',[.5,.5]);bad['choice']='c2'
        self.assertIn('unknown_choice',validate_record(bad))
        bad=record('a',[.5,.5]);bad['gold']='c2'
        self.assertIn('unknown_gold',validate_record(bad))
        self.assertIn('nonmax_native_choice',validate_record(record('a',[.9,.1],choice=1)))

    def test_protocol_tolerance_does_not_renormalize(self):
        r=record('a',[.900009,.1])
        a=compute([r])
        self.assertEqual(a['valid_n'],1)
        self.assertEqual(a['rows'][0]['confidence'],.900009)
        self.assertAlmostEqual(a['brier'],(.900009-1)**2+.1**2)
        self.assertIn('probability_sum',validate_record(record('a',[.90002,.1])))
        r=record('a',[.50000000001,.49999999999],choice=1)
        self.assertIn('nonmax_native_choice',validate_record(r))

    def test_missing_fields_and_invalid_options(self):
        self.assertEqual(validate_record(None),['missing'])
        self.assertIn('missing_probabilities',validate_record({'id':'a'}))
        for opts in (None,[],['c0','c0'],[['c0'],'c1']):
            r=record('a',[.5,.5]);r['options']=opts
            self.assertIn('invalid_options',validate_record(r))

    def test_incomplete_denominators(self):
        a=compute([record('a',[.9,.1]),record('b',[.9,.9])],expected_ids=['a','b','c'])
        self.assertEqual((a['expected_n'],a['observed_n'],a['valid_n']),(3,2,1))
        self.assertEqual(a['missing_ids'],['c'])
        self.assertEqual(a['invalid'],{'b':['probability_sum']})
        self.assertFalse(a['complete'])
        self.assertEqual(a['accuracy'],1.)
        self.assertEqual(a['risk_coverage'][0]['coverage'],1.)
        self.assertEqual(a['risk_coverage'][0]['expected_coverage'],1/3)

    def test_duplicate_unexpected_ids_fail(self):
        with self.assertRaises(ValueError): compute([record('a',[1]),record('a',[1])])
        with self.assertRaises(ValueError): compute([record('a',[1])],expected_ids=['b'])
        with self.assertRaises(ValueError): compute([],expected_ids=['a','a'])

    def test_empty_metrics_are_undefined(self):
        a=compute([],expected_ids=['a'])
        for k in ('accuracy','brier','nll','ece','error_auroc','mean_confidence'):
            self.assertIsNone(a[k])
        self.assertTrue(all(b['accuracy'] is None and b['mean_confidence'] is None for b in a['bins']))

    def test_original_output_is_preserved(self):
        r=record('a',[.95,.05],gold=1)
        r['original_extra']={'unchanged':True}
        a=compute([r])
        self.assertEqual(a['high_score_errors'][0]['original'],r)


if __name__ == '__main__':
    unittest.main(verbosity=2)
