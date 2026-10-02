"""Server contract/security tests. Stub inference is used only in tests, never UI data."""
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Workbench, make_server, validate_request

REQUEST={'state':'Das Passwort ist gesperrt.','questions':{'decision':{'type':'choice','instructions':'Ordne das Anliegen zu.','criteria':{'identity':'Passwort und Anmeldung','other':'Andere Anliegen'}}}}
class ValidationTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate_request(REQUEST)['model'],'clef-flash')
    def test_no_gold(self):
        with self.assertRaises(ValueError): validate_request({**REQUEST,'expected':'identity'})
    def test_empty(self):
        with self.assertRaises(ValueError): validate_request({**REQUEST,'state':' '})
    def test_limit(self):
        with self.assertRaises(ValueError): validate_request({**REQUEST,'state':'a'*6001})
    def test_wrong_type(self):
        with self.assertRaises(ValueError): validate_request({**REQUEST,'questions':{'decision':{'type':'number','instructions':'x','criteria':{'a':'a','b':'b'}}}})
    def test_no_urls_or_media(self):
        with self.assertRaises(ValueError): validate_request({**REQUEST,'image_url':'https://example.org/a.png'})
    def test_serialized(self):
        app=Workbench(True,Path('.'),lambda _:None);app.lock.acquire()
        try:self.assertEqual(app.infer(REQUEST)[0],409)
        finally:app.lock.release()
    def test_disabled(self): self.assertEqual(Workbench().infer(REQUEST)[0],503)
    def test_lazy(self):
        calls=[]
        class Stub:
            def infer(self,request): return {'answers':{'decision':{'type':'choice','choice':'identity'}},
                'probabilities_unrounded':{'decision':{'identity':0.75,'other':0.25}},'test_fixture_only':True}
        app=Workbench(True,Path('.'),lambda p:calls.append(p) or Stub())
        self.assertEqual(calls,[])
        self.assertEqual(app.infer(REQUEST)[0],200);self.assertEqual(app.infer(REQUEST)[0],200)
        self.assertEqual(len(calls),1)

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=make_server(0);cls.port=cls.server.server_address[1]
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls): cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def call(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        conn.request(method,path,body,headers or {});r=conn.getresponse();result=(r.status,dict(r.getheaders()),r.read());conn.close();return result
    def test_index(self):
        status,headers,body=self.call('GET','/');self.assertEqual(status,200);self.assertIn(b'Clef Lab',body);self.assertIn('Content-Security-Policy',headers)
    def test_no_parent_files(self): self.assertEqual(self.call('GET','/%2e%2e/server.py')[0],404)
    def test_no_repo_files(self): self.assertEqual(self.call('GET','/runtime/live_adapter.py')[0],404)
    def test_health(self):
        status,_,body=self.call('GET','/api/health');self.assertEqual(status,200);self.assertFalse(json.loads(body)['inference_enabled'])
    def test_host_rebinding(self): self.assertEqual(self.call('GET','/',headers={'Host':f'evil.example:{self.port}'})[0],403)
    def test_foreign_origin(self): self.assertEqual(self.call('POST','/api/infer',json.dumps(REQUEST),{'Content-Type':'application/json','X-Clef-Request':'1','Origin':'https://evil.example'})[0],403)
    def test_no_custom_header(self): self.assertEqual(self.call('POST','/api/infer',json.dumps(REQUEST),{'Content-Type':'application/json'})[0],415)
    def test_bad_json(self): self.assertEqual(self.call('POST','/api/infer','{',{'Content-Type':'application/json','X-Clef-Request':'1'})[0],400)
    def test_large_body(self): self.assertEqual(self.call('POST','/api/infer','x'*33000,{'Content-Type':'application/json','X-Clef-Request':'1'})[0],413)
    def test_no_cors(self): self.assertEqual(self.call('OPTIONS','/api/infer')[0],403)
    def test_disabled_api(self): self.assertEqual(self.call('POST','/api/infer',json.dumps(REQUEST),{'Content-Type':'application/json','X-Clef-Request':'1'})[0],503)
if __name__=='__main__': unittest.main()
