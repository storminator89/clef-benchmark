"""Synthetic fixtures for full-data chart admission; never benchmark measurements."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ.get('CHART_BASE_ROOT',str(ROOT)))
spec=importlib.util.spec_from_file_location('charts',ROOT/'scripts/generate_evaluation_charts.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class WahlerChartTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        for name in c.SOURCES:
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((SOURCE/name).read_bytes())
        self.legacy=c.render(self.root)
        self.study=self.root/c.WAHLER_STUDY;self.evidence=self.study/'evidence';self.evidence.mkdir(parents=True)
        plan=[];cases=[];groups=[]
        for (suite,_,label),n,fields in zip(c.GROUPS,[120,80,72,80,60,72,48,48],[1,1,1,3,2,2,2,2]):
            questions={f'f{f}':{'type':'choice','instructions':'SYNTHETIC TEST ONLY','criteria':{'yes':'yes','no':'no'}} for f in range(fields)}
            missing=int(suite in ('finance100','bank_support80'))
            for i in range(n):
                plan.append({'suite':suite,'id':str(i),'request':{'model':'fixture','state':'SYNTHETIC TEST ONLY','questions':questions}})
                answers={f:{'type':'choice','choice':'yes','confidence':.8,'probabilities':{'yes':.8,'no':.2}} for f in questions}
                models={m:{'status':'native_answer','answers':answers} for m in ('clef','jev','wahler')}
                if missing and i==0:models['jev']={'status':'missing_or_structurally_invalid','answers':None}
                cases.append({'suite':suite,'id':str(i),'expected':{f:'yes' for f in questions},'models':models})
            groups.append({'suite':suite,'label':label,'planned':n,'models':{m:{'correct':n-(missing if m=='jev' else 0),'planned':n,'classifiable':n-(missing if m=='jev' else 0),'missing_or_structurally_invalid':missing if m=='jev' else 0,'sum_only_diagnostics':0} for m in ('clef','jev','wahler')}})
        for name,data in [('planned.jsonl',plan),('cases.jsonl',cases)]:
            (self.evidence/name).write_text(''.join(json.dumps(r)+'\n' for r in data))
        for name in ('wahler-native-responses.jsonl','wahler-requests.jsonl','original-benchmark.py','README.md'):(self.evidence/name).write_text('SYNTHETIC TEST ONLY\n')
        replay=(ROOT/'scripts/recompute_wahler_evidence.py').read_bytes();(self.evidence/'recompute.py').write_bytes(replay)
        self.provenance={'provenance':{'unique_completed_cases':580,'choice_fields':968},'recompute_sha256':hashlib.sha256(replay).hexdigest(),'final_score_sha256':{'summary.json':'fixture','cases.jsonl':'fixture'}}
        (self.evidence/'provenance.json').write_text(json.dumps(self.provenance))
        self.comparison={'schema_version':1,'metric':'all_fields_native_exact_over_same_planned_cases','groups':groups,'planned_sha256':hashlib.sha256((self.evidence/'planned.jsonl').read_bytes()).hexdigest(),'score_sha256':self.provenance['final_score_sha256']}
        (self.study/'comparison.json').write_text(json.dumps(self.comparison));self.seal()
    def seal(self):
        hashes={n:hashlib.sha256((self.evidence/n).read_bytes()).hexdigest() for n in c.WAHLER_FILES}
        (self.evidence/'SHA256SUMS').write_text(json.dumps(hashes))
    def test_full_fixture_routes_only_direct_chart(self):
        result=c.render(self.root)
        self.assertEqual(result['language_diagnostic.svg'],self.legacy['language_diagnostic.svg'])
        self.assertNotEqual(result['matched_accuracy.svg'],self.legacy['matched_accuracy.svg'])
        self.assertIn('Wähler 4B',result['matched_accuracy.svg']);ET.fromstring(result['matched_accuracy.svg'])
        self.assertEqual(len(json.loads(result['data.json'])['wahler580']['groups']),8)
        self.assertEqual(result,c.render(self.root))
    def test_partial_bundle_fails_closed(self):
        (self.evidence/'cases.jsonl').unlink()
        with self.assertRaisesRegex(ValueError,'Incomplete'):c.render(self.root)
    def test_tampered_count_rejected(self):
        self.comparison['groups'][0]['models']['wahler']['correct']=119
        (self.study/'comparison.json').write_text(json.dumps(self.comparison))
        with self.assertRaisesRegex(ValueError,'counts differ'):c.render(self.root)
    def test_partial_case_inventory_rejected(self):
        path=self.evidence/'cases.jsonl';path.write_text('\n'.join(path.read_text().splitlines()[:-1])+'\n');self.seal()
        with self.assertRaisesRegex(ValueError,'580-case'):c.render(self.root)
    def test_changed_vector_digest_rejected(self):
        with (self.evidence/'cases.jsonl').open('a') as f:f.write(' ')
        with self.assertRaisesRegex(ValueError,'digest mismatch'):c.render(self.root)
    def test_replay_source_change_rejected(self):
        (self.evidence/'recompute.py').write_text('SYNTHETIC TEST ONLY\n');self.seal()
        with self.assertRaisesRegex(ValueError,'scorer differs'):c.render(self.root)
if __name__=='__main__':unittest.main()
