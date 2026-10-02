"""Synthetic fixtures only. Never opens model prediction files."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

P = Path(__file__).resolve().parent.parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

old=load('frozen_score',P/'benchmark/score.py')
new=load('robust_score',P/'qa/score_v1_1.py')
CASE={'id':'synthetic','category':'fixture','split':'german_primary','expected':{'decision':'a'},'questions':{'decision':{'type':'choice','criteria':{'a':'A','b':'B'}}}}

def output(choice='a',p=None):
    p=p if p is not None else {'a':float(choice=='a'),'b':float(choice=='b')}
    return {'id':'synthetic','answers':{'decision':{'type':'choice','choice':choice,'confidence':p.get(choice,0),'probabilities':p}},'latency_ms':5}

class ScorerTests(unittest.TestCase):
    def test_frozen_bug_is_reproduced(self):
        for value in (None,[],1,'bad'):
            with self.subTest(value=value),self.assertRaises(AttributeError):
                old.inspect(CASE,{'answers':value})

    def test_malformed_answers_are_invalid(self):
        for value in (None,[],1,'bad'):
            for envelope in ({'answers':value},{'response':{'answers':value}},{'response':{'result':{'answers':value}}}):
                r=new.inspect(CASE,envelope)
                self.assertEqual(r['error'],'non_object_answers')
                self.assertFalse(r['correct']);self.assertFalse(r['schema_valid'])
                self.assertNotIn('latency_ms',r);self.assertNotIn('max_probability',r)

    def test_malformed_objects_and_missing(self):
        for value in (None,[],1,'bad'):
            self.assertFalse(new.inspect(CASE,{'response':value})['correct'])
            self.assertFalse(new.inspect(CASE,{'answers':{'decision':value}})['correct'])
        for value in ([],1,'bad'):
            self.assertEqual(new.inspect(CASE,value)['error'],'non_object_output_record')
        self.assertEqual(new.inspect(CASE,None)['error'],'missing_output')
        self.assertFalse(new.inspect(CASE,{'error':'timeout'})['correct'])

    def test_unchanged_valid_envelopes(self):
        raw=output();answer=raw['answers']
        for value in (raw,{'response':{'answers':answer}},{'result':{'answers':answer}},{'response':{'result':{'answers':answer}}}):
            self.assertEqual(old.inspect(CASE,value),new.inspect(CASE,value))
            self.assertTrue(new.inspect(CASE,value)['schema_valid'])

    def test_accuracy_macro_f1_and_missing(self):
        r=new.inspect(CASE,output())
        w=new.inspect(CASE,output('b'))
        cb=copy.deepcopy(CASE);cb['expected']['decision']='b'
        missing=new.inspect(cb,None)
        m=new.metrics([r,w,missing],['a','b'])
        self.assertAlmostEqual(m['choice_accuracy_all_planned'],1/3)
        self.assertEqual(m['n_present'],2)
        self.assertAlmostEqual(m['per_class']['a']['f1'],2/3)
        self.assertEqual(m['per_class']['b']['f1'],0)
        self.assertAlmostEqual(m['macro_f1'],1/3)
        self.assertEqual(m['confusion']['b'],{'__invalid_or_missing__':1})

    def test_brier_nll_ece_and_deferral(self):
        r=new.inspect(CASE,output('a',{'a':.8,'b':.2}))
        w=new.inspect(CASE,output('b',{'a':.4,'b':.6}))
        m=new.metrics([r,w],['a','b'])
        self.assertAlmostEqual(r['brier'],.08)
        self.assertAlmostEqual(w['brier'],.72)
        self.assertAlmostEqual(m['calibration']['multiclass_brier_sum'],.4)
        self.assertAlmostEqual(m['calibration']['ece_5_equal_width_bins'],.4)
        self.assertAlmostEqual(r['nll'],-math.log(.8))
        self.assertEqual(m['confidence_deferral']['0.8']['accepted'],1)
        self.assertEqual(m['confidence_deferral']['0.8']['coverage_all_planned'],.5)
        self.assertEqual(m['confidence_deferral']['0.8']['accepted_accuracy'],1)
        worst=new.inspect(CASE,output('b'))
        self.assertEqual(worst['brier'],2)
        self.assertAlmostEqual(worst['nll'],-math.log(1e-12))

    def test_bad_vectors_and_choice_schema(self):
        for p in ({'a':1},{'a':.8,'b':.8},{'a':-1,'b':2},{'a':float('nan'),'b':0},{'a':True,'b':0}):
            r=new.inspect(CASE,output('a',p));self.assertFalse(r['schema_valid'])
        r=new.inspect(CASE,{'answers':{'decision':{'type':'choice','choice':'not_a_class','confidence':.5,'probabilities':{'a':.5,'b':.5}}}})
        self.assertFalse(r['choice_valid'])
        raw=output();raw['probabilities_unrounded']={'decision':{'a':.4,'b':.6}}
        r=new.inspect(CASE,raw);self.assertTrue(r['correct']);self.assertFalse(r['strict_correct'])
        self.assertEqual(r['error'],'choice_disagrees_with_unrounded_argmax')

    def test_all_planned_paired_denominator(self):
        correct=new.inspect(CASE,output());wrong=new.inspect(CASE,output('b'));missing=new.inspect(CASE,None)
        pairs=[{'german_id':'a','english_id':'b'},{'german_id':'c','english_id':'d'},{'german_id':'e','english_id':'f'}]
        by_id={'a':correct,'b':correct,'c':correct,'d':missing,'e':wrong,'f':correct}
        complete=new.paired(pairs,by_id,'german_id','english_id')
        planned=new.paired_all_planned(pairs,by_id,'german_id','english_id')
        self.assertEqual(complete['n_pairs_valid_both'],2)
        self.assertEqual(complete['left_accuracy'],.5);self.assertEqual(complete['right_accuracy'],1)
        self.assertEqual(planned['n_pairs_used'],3)
        self.assertEqual(planned['n_pairs_with_invalid_or_missing'],1)
        self.assertAlmostEqual(planned['left_accuracy_all_planned'],2/3)
        self.assertAlmostEqual(planned['right_accuracy_all_planned'],2/3)
        self.assertEqual(planned['counts'],{'both_correct':1,'left_only_correct':1,'right_only_correct':1,'both_wrong':0})

    def test_exact_mcnemar(self):
        correct=new.inspect(CASE,output());wrong=new.inspect(CASE,output('b'))
        pairs=[{'german_id':f'a{i}','english_id':f'b{i}'} for i in range(4)]
        by_id={k:(correct if k.startswith('a') else wrong) for p in pairs for k in p.values()}
        self.assertEqual(new.paired_all_planned(pairs,by_id,'german_id','english_id')['exact_mcnemar_two_sided_p'],.125)

    def test_cli_full_synthetic_regression(self):
        cases=old.read(P/'benchmark/cases.jsonl')+old.read(P/'benchmark/diagnostic_cases.jsonl')
        raw=[]
        for case in cases:
            truth=case['expected']['decision'];probs={k:float(k==truth) for k in case['questions']['decision']['criteria']}
            raw.append({'id':case['id'],'answers':{'decision':{'type':'choice','choice':truth,'confidence':1.,'probabilities':probs}},'latency_ms':5})
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory);inputs=d/'synthetic.jsonl';inputs.write_text('\n'.join(json.dumps(r) for r in raw))
            reports=[]
            for path in (P/'benchmark/score.py',P/'qa/score_v1_1.py'):
                target=d/(path.stem+'.json')
                subprocess.run([sys.executable,str(path),str(inputs),'--out',str(target)],check=True,capture_output=True,text=True)
                reports.append(json.loads(target.read_text()))
            for key in reports[0]:
                if key not in {'scoring_version'}:self.assertEqual(reports[0][key],reports[1][key],key)
            self.assertEqual(reports[1]['splits']['german_primary']['choice_accuracy_all_planned'],1)
            self.assertEqual(reports[1]['splits']['german_primary']['category_macro_f1'],1)
            self.assertTrue(all(p['n_pairs_used']==30 for p in reports[1]['paired_all_planned'].values()))
            for malformed in ([None],[{'id':None}],[{'id':raw[0]['id']},{'id':raw[0]['id']}],[{'id':'unknown'}]):
                inputs.write_text('\n'.join(json.dumps(r) for r in malformed))
                process=subprocess.run([sys.executable,str(P/'qa/score_v1_1.py'),str(inputs),'--out',str(d/'bad.json')],capture_output=True,text=True)
                self.assertNotEqual(process.returncode,0)
                self.assertIn('ValueError',process.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
