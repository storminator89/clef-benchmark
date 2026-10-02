"""Fixed-model HTTP service configuration only; no model, GPU or download."""
import unittest
from pathlib import Path
from server import Workbench, validate_request
from runtime.model_registry import get_model

REQUEST={'state':'Synthetic input only.','questions':{'intent':{'type':'choice','instructions':'Choose a label.','criteria':{'a':'A','b':'B'}}}}

class ModelSelectionTests(unittest.TestCase):
    def test_default_health_is_flash_and_unloaded(self):
        app=Workbench(); health=app.health()
        self.assertEqual(health['model_key'],'flash-9b')
        self.assertEqual(health['model_id'],'Cloudflare/clef-flash')
        self.assertEqual(health['revision'],get_model('flash-9b')['revision'])
        self.assertFalse(health['model_loaded'])
        self.assertIsNone(health['runtime'])
        self.assertIsNone(health['requested_profile'])

    def test_27b_health_is_selected_not_hardware_verified(self):
        calls=[]
        app=Workbench(True,Path('.'),lambda *a,**kw:calls.append((a,kw)),model_key='clef-27b')
        health=app.health()
        self.assertEqual(calls,[])
        self.assertEqual(health['model_key'],'clef-27b')
        self.assertEqual(health['model_id'],get_model('clef-27b')['repo_id'])
        self.assertEqual(health['revision'],get_model('clef-27b')['revision'])
        self.assertIsNone(health['runtime'])
        self.assertFalse(health['model_loaded'])
        self.assertEqual(health['requested_profile'],'cpu-nf4')

    def test_27b_factory_receives_explicit_key_profile_and_device(self):
        calls=[]
        class Stub:
            def infer(self,request):
                return {'answers':{'intent':{'type':'choice','choice':'a'}},'probabilities_unrounded':{'intent':{'a':0.75,'b':0.25}}}
        def factory(*args,**kwargs):calls.append((args,kwargs));return Stub()
        app=Workbench(True,Path('.'),factory,profile='cpu-bf16',model_key='clef-27b')
        status,result=app.infer(validate_request(REQUEST))
        self.assertEqual(status,200)
        self.assertEqual(calls[0][1],{'profile':'cpu-bf16','device_index':0,'model_key':'clef-27b'})
        self.assertEqual(result['model_key'],'clef-27b')
        self.assertEqual(result['requested_profile'],'cpu-bf16')

    def test_request_cannot_switch_model_or_supply_gold(self):
        for key in ('model','model_key','model_id','gold','expected'):
            with self.subTest(key=key),self.assertRaises(ValueError):validate_request({**REQUEST,key:'clef-27b'})
        self.assertEqual(validate_request(REQUEST)['model'],'clef-flash')

    def test_invalid_model_fails_before_factory_or_download(self):
        with self.assertRaises(ValueError):Workbench(model_key='remote-api')

if __name__=='__main__':unittest.main()
