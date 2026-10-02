from pathlib import Path
import sys,copy,json,unittest
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'))
from score_images import score,lines
class Tests(unittest.TestCase):
 def setUp(self):
  self.req=lines(P/'benchmark/requests.jsonl');self.gold=lines(P/'benchmark/gold.jsonl');self.cases=lines(P/'benchmark/cases.jsonl');self.pairs=lines(P/'benchmark/pairs.jsonl');self.pred=[]
  for r,g in zip(self.req,self.gold):
   ans={};probs={}
   for q,ex in g['expected'].items():
    opts=r['request']['questions'][q]['criteria'];pr={o:1. if o==ex else 0. for o in opts};ans[q]={'type':'choice','choice':ex};probs[q]=pr
   self.pred.append({'id':r['id'],'answers':ans,'probabilities_unrounded':probs,'inference_seconds':1.,'vision_forward_events':[{}],'input_tokens':1,'truncated':False})
 def do(self):return score(self.req,self.gold,self.pred,self.cases,self.pairs)
 def test_perfect(self):
  s=self.do();self.assertEqual(s['schema_valid'],90);self.assertEqual(s['groups']['chart_de_image']['field_micro']['correct'],60);self.assertEqual(s['groups']['invoice_de_image']['field_micro']['correct'],60)
 def test_single_wrong(self):
  r=self.pred[0];q='chart_type';opts=r['probabilities_unrounded'][q];wrong=next(o for o in opts if o!=r['answers'][q]['choice']);r['answers'][q]['choice']=wrong;r['probabilities_unrounded'][q]={o:float(o==wrong) for o in opts};s=self.do();self.assertEqual(s['groups']['chart_de_image']['field_micro']['correct'],59);self.assertEqual(s['groups']['chart_de_image']['all_fields_per_image']['correct'],29)
 def test_bad_option(self):
  self.pred[0]['answers']['chart_type']['choice']='not-an-option';self.assertEqual(self.do()['schema_valid'],89)
 def test_nonfinite(self):
  self.pred[0]['probabilities_unrounded']['chart_type']['pie']=float('nan');self.assertEqual(self.do()['schema_valid'],89)
 def test_missing(self):
  self.pred.pop();self.assertRaises(AssertionError,self.do)
 def test_duplicate(self):
  self.pred.append(self.pred[0]);self.assertRaises(AssertionError,self.do)
if __name__=='__main__':unittest.main()
