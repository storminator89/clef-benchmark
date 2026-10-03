import copy, importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('derive',ROOT/'scripts/derive_jev_answer_correctness_v1.py'); d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class AnswerCorrectnessTests(unittest.TestCase):
    def test_frozen_counts_and_null_baseline(self):
        summary,cases,restored=d.derive();self.assertEqual(len(restored),35)
        expected=[(48,39,47),(72,64,71),(80,68,75),(120,116,119),(30,29,30),(30,29,30),(80,76,78),(20,18,20),(60,50,56),(72,61,67),(7,4,6),(7,5,7),(48,24,44),(300,None,233)]
        self.assertEqual([(p['planned'],p['clef_correct'],p['jev_correct']) for p in summary['partitions']],expected)
        self.assertEqual(sum(not c['evaluable']['jev'] for c in cases),2)
        self.assertTrue(all(c['exact']['jev'] is None for c in cases if not c['evaluable']['jev']))
        self.assertIsNone(summary['partitions'][-1]['clef_accuracy_all_expected'])
    def test_sum_only_is_not_repair(self):
        record=d.rows(ROOT/'studies/jev974/run/flagged_native.jsonl')[0]
        requests=d.rows(ROOT/'experiments/jev_comparison/inputs'/record['suite']/'requests.jsonl');request=next(x['request'] for x in requests if x['id']==record['id'])
        before=copy.deepcopy(record);answers,sums=d.answer_fields(request,record)
        self.assertEqual(record,before);self.assertTrue(any(abs(s-1)>1e-5 for s in sums.values()))
        for mutation in ['argmax','field','option','nan','hash','confidence','model']:
            bad=copy.deepcopy(record);field=next(iter(bad['answers']));a=bad['answers'][field]
            if mutation=='argmax':a['choice']=min(a['probabilities'],key=a['probabilities'].get)
            elif mutation=='field':bad['answers']['extra']=a
            elif mutation=='option':a['probabilities']['extra']=0
            elif mutation=='nan':a['probabilities'][a['choice']]=float('nan')
            elif mutation=='hash':bad['request_body_sha256']='bad'
            elif mutation=='confidence':a['confidence']=2
            else:bad['provider_model']='other'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):d.answer_fields(request,bad)
if __name__=='__main__':unittest.main()
