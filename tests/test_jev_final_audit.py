"""Adversarial offline synthetic audit tests; fixtures are never observations."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_jev_final_continuation as collector
import audit_jev_final_continuation as auditor

def response(body,flagged=False):
 request=json.loads(body);answers={}
 for field,q in request['questions'].items():
  options=list(q['criteria']);p=dict.fromkeys(options,0.0);p[options[0]]=.6;p[options[1]]=.2 if flagged else .4
  answers[field]={'type':'choice','choice':options[0],'probabilities':p,'confidence':.6}
 return 200,json.dumps({'model':'jev-1.13.0','answers':answers,'usage':{'input_tokens':10,'output_tokens':1}}).encode(),None
class AuditTests(unittest.TestCase):
 def make(self,flagged=False,full=False,transport=None,**kwargs):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);out=Path(temp.name)/'run';calls=[]
  def send(body):
   calls.append(body)
   if transport:return transport(body,len(calls))
   if len(calls)>1 and not full:return 401,b'',None
   return response(body,flagged)
  collector.run(out,3,send,sleep=lambda _:None,**kwargs);return out
 def mutate_json(self,out,name,change):
  f=out/name;value=json.loads(f.read_text());change(value);f.write_text(json.dumps(value)+'\n')
 def mutate_rows(self,out,name,change):
  f=out/name;value=[json.loads(x) for x in f.read_text().splitlines()];change(value);f.write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in value))
 def test_full_strict_and_sum_only_counters(self):
  for flagged,strict,failed in [(False,972,2),(True,452,522)]:
   with self.subTest(flagged=flagged):
    result=auditor.audit(self.make(flagged,full=True));self.assertEqual((result['strict_valid'],result['technical_failed'],result['missing']),(strict,failed,0))
 def test_partial_fatal_first_and_after_gate(self):
  for send in [lambda b,n:(401,b'',None),lambda b,n: response(b) if n==1 else (500,b'',None),lambda b,n:(200,b'{}',None)]:
   out=self.make(transport=send);self.assertEqual(auditor.audit(out)['status'],'passed')
 def test_transport_failure_and_unattempted_deadline(self):
  def bad(b,n):raise OSError('mock')
  self.assertEqual(auditor.audit(self.make(transport=bad))['missing'],519)
  times=iter([0,99999]);out=self.make(now=lambda:next(times));self.assertEqual(auditor.audit(out)['missing'],520)
 def test_retry_exhaustion_continues_without_false_success(self):
  def send(b,n):return (429,b'',None) if n in (2,3) else response(b)
  result=auditor.audit(self.make(full=True,transport=send));self.assertEqual(result['retries'],1);self.assertEqual(result['technical_failed'],3)
 def test_missing_quarantine_rejected(self):
  out=self.make(True);(out/'flagged_native.jsonl').write_bytes(b'')
  with self.assertRaisesRegex(ValueError,'flagged native'):auditor.audit(out)
 def test_flagged_invalid_billing_and_choice_rejected(self):
  for change in [lambda r:r['usage'].update(input_tokens=65537),lambda r:r.update(strict_scoring_eligible=True),lambda r:r['diagnostic']['probability_sums'].clear()]:
   out=self.make(True);self.mutate_rows(out,'flagged_native.jsonl',lambda rs:change(rs[0]))
   with self.assertRaises(ValueError):auditor.audit(out)
 def test_summary_coverage_and_budget_tampering_rejected(self):
  for key,value in [('completed_cases',999),('remaining_cases',0),('retry_attempts',1),('capacity_reserved_usd','0'),('flagged_native_input_tokens',0)]:
   out=self.make(True);self.mutate_json(out,'run_summary.json',lambda r:r.update({key:value}))
   with self.assertRaises(ValueError):auditor.audit(out)
 def test_unsettled_reservation_and_missing_diagnostic_rejected(self):
  out=self.make(True);f=out/'attempts.jsonl';f.write_bytes(f.read_bytes()+b'{"event":"reserved"}\n')
  with self.assertRaises(ValueError):auditor.audit(out)
  out=self.make(True);prior=collector.FIRST_RUN/'validation_diagnostics.jsonl';(out/'validation_diagnostics.jsonl').write_bytes(prior.read_bytes())
  with self.assertRaises(ValueError):auditor.audit(out)
 def test_old_bytes_gate_and_fatal_reason_rejected(self):
  out=self.make();f=out/'predictions.jsonl';f.write_bytes(b' '+f.read_bytes())
  with self.assertRaisesRegex(ValueError,'Historical'):auditor.audit(out)
  out=self.make();self.mutate_json(out,'connection_check.json',lambda r:r.update(connection_valid=False))
  with self.assertRaisesRegex(ValueError,'gate'):auditor.audit(out)
  out=self.make();self.mutate_json(out,'run_summary.json',lambda r:r.update(halt_reason='http_403'))
  with self.assertRaisesRegex(ValueError,'Halt reason'):auditor.audit(out)
 def test_final_fatal_cannot_be_relabelled_completed(self):
  for invalid in (False,True):
   def send(body,index):
    if index==520:return (200,b'{}',None) if invalid else (401,b'',None)
    return response(body)
   out=self.make(full=True,transport=send)
   self.assertEqual(auditor.audit(out)['status'],'passed')
   self.mutate_json(out,'run_summary.json',lambda r:r.update(status='completed_with_failures',halt_reason=None))
   with self.assertRaisesRegex(ValueError,'False completion'):auditor.audit(out)
 def test_unexhausted_retry_stop_cannot_be_relabelled_completed(self):
  out=self.make(full=True,transport=lambda b,n:(429,b'',121) if n==520 else response(b))
  self.assertEqual(auditor.audit(out)['status'],'passed')
  self.mutate_json(out,'run_summary.json',lambda r:r.update(status='completed_with_failures',halt_reason=None))
  with self.assertRaisesRegex(ValueError,'False completion'):auditor.audit(out)
 def test_auditor_does_not_import_collector(self):
  text=(Path(auditor.__file__)).read_text();self.assertNotIn('import run_jev_final_continuation',text)
if __name__=='__main__':unittest.main()
