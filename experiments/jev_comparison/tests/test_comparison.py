import copy, hashlib, importlib.util, json, math, os, pathlib, sys, tempfile, unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import jev_runner as j
from compare import probability_metrics, confusion, compare

def sample():return {'model':'clef-flash','state':'Synthetischer Test.','questions':{'x':{'type':'choice','instructions':'Wähle.','criteria':{'a':'Erste Option','b':'Zweite Option'}}}}
def response():return {'model':j.MODEL,'answers':{'x':{'type':'choice','choice':'a','probabilities':{'a':.75,'b':.25},'confidence':.5}},'usage':{'input_tokens':100,'output_tokens':20}}
def fixture(root,n=1):
    (root/'inputs'/'sample').mkdir(parents=True)
    rs=[{'id':str(i),'request':sample()} for i in range(n)];p=root/'inputs/sample/requests.jsonl';p.write_text(''.join(json.dumps(r)+'\n' for r in rs))
    j.write(root/'manifest.json',{'suites':[{'id':'sample','count':n,'baseline':'pending'}],'files':{'inputs/sample/requests.jsonl':j.sha(p)},'excluded':[]})
class ContractTests(unittest.TestCase):
    def test_payload_only_model_changes(self):
        r=sample();before=copy.deepcopy(r);p=j.payload(r)
        self.assertEqual(r,before);self.assertEqual(list(r['questions']['x']['criteria']),list(p['questions']['x']['criteria']));p['model']='clef-flash';self.assertEqual(r,p)
    def test_native_not_generated(self):
        r=sample();r['questions']['x']['type']='noul'
        with self.assertRaises(j.ContractError):j.payload(r)
    def test_gold_envelope_rejected(self):
        r=sample();r['expected']={'x':'a'}
        with self.assertRaises(j.ContractError):j.payload(r)
    def test_images_rejected(self):
        r=sample();r['state']={'image_url':'https://example.invalid/x'}
        with self.assertRaises(j.ContractError):j.payload(r)
    def test_invalid_question_content(self):
        for which,value in [('instructions',None),('instructions',42),('instructions',{'image_url':'not-text'}),('criteria',{'a':42,'b':'okay'}),('criteria',{'a':{'image':'not-text'},'b':'okay'})]:
            r=sample();r['questions']['x'][which]=value
            with self.assertRaises(j.ContractError):j.payload(r)
    def test_response_preserves_native(self):
        r=response();self.assertEqual(j.validate_response(j.payload(sample()),r),r);self.assertNotEqual(r['answers']['x']['confidence'],r['answers']['x']['probabilities']['a'])
    def test_invalid_vectors_and_usage(self):
        changes=[lambda x:x['answers']['x']['probabilities'].update(a=float('nan')),lambda x:x['answers']['x']['probabilities'].update(a=True),lambda x:x['answers']['x']['probabilities'].update(c=.1),lambda x:x['answers']['x'].update(choice='b'),lambda x:x['answers']['x'].update(type='score'),lambda x:x.update(model='jev-latest'),lambda x:x['usage'].update(input_tokens=65537),lambda x:x['usage'].update(input_tokens=True),lambda x:x['usage'].pop('output_tokens'),lambda x:x['answers']['x'].pop('confidence')]
        for edit in changes:
            with self.subTest(edit=edit):
                r=response();edit(r)
                with self.assertRaises(j.ContractError):j.validate_response(j.payload(sample()),r)
    def test_budget_counts_retries(self):
        l=j.Ledger('3')
        for _ in range(974):l.reserve()
        for _ in range(50):l.reserve(True)
        self.assertEqual(l.attempts,1024);self.assertEqual(l.status()['capacity_reserved_usd'],'2.818572288')
        with self.assertRaises(j.BudgetError):l.reserve()
    def test_bad_caps_fail_closed(self):
        for n in ['0','-1','3.01','Infinity','NaN']:
            with self.assertRaises(j.BudgetError):j.Ledger(n)
        l=j.Ledger('.001')
        with self.assertRaises(j.BudgetError):l.reserve()
    def test_dry_plan_does_not_read_secret(self):
        with patch.dict(os.environ,{},clear=True),patch.object(j,'HttpTransport',side_effect=AssertionError('network disabled')):p=j.make_plan(ROOT)
        self.assertEqual(p['one_pass_requests'],974);self.assertEqual(len(p['exact_payload_repeats']),7);self.assertEqual(p['question_count'],1362)
    def test_complete_fixture_records_native(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);fixture(root)
            called=[]
            def transport(body):called.append(json.loads(body));return 200,json.dumps(response()).encode(),None
            result=j.run(root,root/'out',3,transport,sleep=lambda _:None)
            self.assertEqual(result['status'],'complete');p=j.rows(root/'out/predictions.jsonl')[0];self.assertEqual(p['answers'],response()['answers']);self.assertEqual(p['probabilities_unrounded']['x'],{'a':.75,'b':.25});self.assertEqual(set(called[0]),{'model','state','questions'})
    def test_retry_only_documented_statuses(self):
        for status in [401,422,500,302,429,529]:
            with self.subTest(status=status),tempfile.TemporaryDirectory() as d:
                root=pathlib.Path(d);fixture(root);calls=[]
                def transport(body):calls.append(body);return (status,b'',0) if len(calls)==1 else (200,json.dumps(response()).encode(),None)
                result=j.run(root,root/'out',3,transport,sleep=lambda _:None)
                self.assertEqual(len(calls),2 if status in [429,529] else 1)
                self.assertEqual(result['status'],'complete' if status in [429,529] else 'halted')
    def test_transport_error_never_logged_or_retried(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);fixture(root)
            def transport(_):raise RuntimeError('PRIVATE_EXCEPTION_SENTINEL')
            result=j.run(root,root/'out',3,transport,sleep=lambda _:None)
            self.assertEqual(result['wire_attempts_reserved'],1)
            for p in (root/'out').iterdir():self.assertNotIn('PRIVATE_EXCEPTION_SENTINEL',p.read_text())
    def test_invalid_success_halts(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);fixture(root,2)
            result=j.run(root,root/'out',3,lambda _:(200,b'{"echo":"PRIVATE_RESPONSE_SENTINEL"}',None),sleep=lambda _:None)
            self.assertEqual(result['wire_attempts_reserved'],1);self.assertEqual(result['remaining_cases'],1)
            for p in (root/'out').iterdir():self.assertNotIn('PRIVATE_RESPONSE_SENTINEL',p.read_text())
    def test_retry_after_numeric_and_date(self):
        self.assertEqual(j.retry_delay('12'),12)
        self.assertEqual(j.retry_delay('Wed, 01 Jan 2020 00:00:00 GMT'),0)
        self.assertGreater(j.retry_delay('Thu, 01 Jan 2099 00:00:00 GMT'),120)
        for v in ['garbage','-1','NaN','Infinity',None]:self.assertIsNone(j.retry_delay(v))
    def test_redirect_refused(self):
        with self.assertRaises(j.ContractError):j.NoRedirect().redirect_request(None,None,302,'',{},'https://example.invalid')
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);fixture(root);(root/'out').mkdir()
            with self.assertRaises(j.ContractError):j.run(root,root/'out',3,lambda _:None)
    def test_missing_massive_baseline_not_invented(self):
        self.assertFalse((ROOT/'inputs/massive300/predictions.jsonl').exists())
    def test_zero_prob_nll_and_empty_risk(self):
        m=probability_metrics([{'correct':False,'p_selected':.6,'p_gold':0,'brier':2}],2)
        self.assertTrue(m['nll_is_infinite']);self.assertIsNone(m['nll']);self.assertEqual(m['accuracy_all_expected'],0);self.assertIsNone(m['risk_coverage'][-1]['risk']);self.assertEqual(m['invalid_or_missing'],1)
    def test_macro_label_denominators(self):
        m=confusion([{'gold':'a','choice':'a'},{'gold':'a','choice':None}],['a','b'])
        self.assertEqual(m['gold_supported_label_count'],1);self.assertAlmostEqual(m['macro_f1_gold_supported'],2/3);self.assertAlmostEqual(m['macro_f1_fixed_options_zero_division_0'],1/3)
    def test_full_incomplete_offline_scoring(self):
        # Empty Jev results test denominator/failure coverage without fabricated model outputs.
        with tempfile.TemporaryDirectory() as d:
            d=pathlib.Path(d);(d/'run').mkdir();(d/'run/predictions.jsonl').write_text('')
            result=compare(ROOT,d/'run',d/'comparison');self.assertEqual(result['scored_expected_cases'],974)
            report=json.loads((d/'comparison/comparison_summary.json').read_text());self.assertEqual(report['baseline_pending'],['massive300']);self.assertTrue(all(x['jev_valid']==0 for x in report['partitions']))
            diagnostics=json.loads((d/'comparison/special_diagnostics.json').read_text());self.assertEqual(len(diagnostics['attack_ablation14']),7);self.assertEqual(len(diagnostics['original_text180']['language_control_pairs']),30);self.assertEqual(len(diagnostics['finance100']['language_control_pairs']),20);special=diagnostics['massive300']['jev'];self.assertEqual([special[k]['n'] for k in special],[300,285,284]);self.assertEqual(special['primary300']['gold_supported_label_count'],59)
    def test_empty_complete_baseline_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            d=pathlib.Path(d);fixture(d);src=d/'inputs/sample';(src/'gold.jsonl').write_text(json.dumps({'id':'0','expected':{'x':'a'}})+'\n');(src/'predictions.jsonl').write_text('')
            m=json.loads((d/'manifest.json').read_text());m['suites'][0]['baseline']='complete';j.write(d/'manifest.json',m)
            (d/'run').mkdir();(d/'run/predictions.jsonl').write_text('')
            with self.assertRaises(j.ContractError):compare(d,d/'run',d/'comparison')
    def test_all_source_hashes_and_gold(self):
        m=json.loads((ROOT/'manifest.json').read_text())
        for p,h in m['files'].items():self.assertEqual(j.sha(ROOT/p),h,p)
        for s in m['suites']:
            rq=j.rows(ROOT/'inputs'/s['id']/'requests.jsonl');g={r['id']:r for r in j.rows(ROOT/'inputs'/s['id']/'gold.jsonl')}
            for r in rq:self.assertEqual(set(r['request']['questions']),set(g[r['id']]['expected']))
if __name__=='__main__':unittest.main()
