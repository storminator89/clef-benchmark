import hashlib,json
from pathlib import Path
import shutil,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_jev_final_activation as gate
class ActivationTests(unittest.TestCase):
 def copy(self):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)/'project';root.mkdir()
  for name in [*gate.SOURCE_PINS,'provenance/jev_final_activation.json']:
   dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(gate.ROOT/name,dest)
  shutil.copytree(gate.ROOT/'.github',root/'.github');return root
 def test_current_state_is_explicitly_gated(self):
  result=gate.check();self.assertIn(result['activation_state'],('prepared_inert_not_activated','activated_awaiting_one_manual_dispatch'))
 def test_unknown_state_is_rejected(self):
  root=self.copy();f=root/'provenance/jev_final_activation.json';state=json.loads(f.read_text());state['status']='anything_else';f.write_text(json.dumps(state))
  with self.assertRaises(ValueError):gate.check(root)
 def test_source_and_workflow_tamper_rejected(self):
  for name in ['scripts/run_jev_final_continuation.py','scripts/audit_jev_final_continuation.py','.github/workflows/jev-comparison.yml']:
   root=self.copy();f=root/name;f.write_bytes(f.read_bytes()+b'\n')
   with self.assertRaises(ValueError):gate.check(root)
 def test_scope_metadata_rejected(self):
  root=self.copy();f=root/'provenance/jev_final_activation.json';s=json.loads(f.read_text());s['remaining_initial_requests']=974;f.write_text(json.dumps(s))
  with self.assertRaises(ValueError):gate.check(root)
 def test_pinned_activation_only_in_temporary_copy(self):
  root=self.copy();f=root/'provenance/jev_final_activation.json';state=json.loads(f.read_text());sha='a'*40
  text=(root/'scripts/workflows/jev-final-continuation.yml.in').read_text().replace('REVIEWED_FINAL_CONTINUATION_COMMIT',sha)
  (root/'.github/workflows/jev-comparison.yml').write_text(text);state.update(status='activated_awaiting_one_manual_dispatch',reviewed_code_commit=sha,workflow_sha256=hashlib.sha256(text.encode()).hexdigest());f.write_text(json.dumps(state));self.assertEqual(gate.check(root)['activation_state'],'activated_awaiting_one_manual_dispatch')
  state['reviewed_code_commit']='main';f.write_text(json.dumps(state))
  with self.assertRaises(ValueError):gate.check(root)
 def test_no_provider_trigger_except_false_default_manual(self):
  text=(gate.ROOT/'scripts/workflows/jev-final-continuation.yml.in').read_text();self.assertEqual(text.count('default: false'),2);self.assertNotIn('\n  push:',text);self.assertIn('github.run_attempt == 1',text);self.assertIn('flagged_native.jsonl',text);self.assertLess(text.index('scripts/audit_jev_final_continuation.py --run'),text.index('scripts/compare.py --root'))
