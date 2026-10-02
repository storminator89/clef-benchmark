#!/usr/bin/env python3
"""Record the independently reviewed final revisions and verify frozen bytes. No model inference."""
import json,pathlib,hashlib,collections,re,subprocess,tempfile,shutil,datetime
root=pathlib.Path(__file__).resolve().parents[1]; data=root/'data'; audit=root/'audit'
cases=[json.loads(x) for x in (data/'cases.jsonl').read_text().splitlines()]
req=[json.loads(x) for x in (data/'requests.jsonl').read_text().splitlines()]
gold=[json.loads(x) for x in (data/'gold.jsonl').read_text().splitlines()]
meta=[json.loads(x) for x in (data/'metadata.jsonl').read_text().splitlines()]
policy=json.loads((data/'policy.json').read_text())
initial={x['id']:x for x in map(json.loads,(audit/'initial_snapshot/cases.jsonl').read_text().splitlines())}
review={x['id']:x for x in map(json.loads,(audit/'pre_inference_review_initial.jsonl').read_text().splitlines())}
assert len(cases)==len(req)==len(gold)==len(meta)==len(review)==80
assert len({r['id'] for r in cases})==len({r['message'] for r in cases})==80
changed={r['id']: [k for k in r if r[k]!=initial[r['id']][k]] for r in cases if r!=initial[r['id']]}
assert changed=={'bank_cards_08':['clarification_target'],'bank_fees_05':['message'],'bank_transfers_02':['message'],'bank_access_tan_05':['message']}
# These two revised labels are the reviewer's manual judgments after inspecting the new text/policy.
review['bank_access_tan_05']['independently_assigned_expected']['intent']='access_tan'
review['bank_access_tan_05']['reasoning']='Online-banking access is now explicitly the subject, but no symptom is given; routine access clarification.'
review['bank_ambiguous_multi_04']['independently_assigned_expected']['intent']='cards'
review['bank_ambiguous_multi_04']['reasoning']='Explicit new lost-unblocked-card precedence selects cards over address change; acute loss gives critical priority and mandatory handoff.'
review['bank_cash_08']['reasoning']='Necessary blocked cash withdrawal is expressly covered by urgent policy; payment is due today and no alternative exists; described symptom supports review.'
review['bank_transfers_02']['reasoning']='Own wrong-recipient transfer is now expressly authorized and sent; urgent recall review, without unauthorized-payment security routing.'
review['bank_transfers_08']['reasoning']='Earlier transfer concern is resolved; policy explicitly keeps its receipt-download guidance in the transfer route.'
review['bank_cash_07']['reasoning']='Cash discrepancy is resolved; policy explicitly keeps this cash-transaction receipt-navigation question in cash.'
review['bank_ambiguous_multi_01']['reasoning']='Payment type and own initiation remain unknown, with no expressed fraud suspicion or express denial; new policy explicitly permits unclear/routine/clarify.'
review['bank_standing_orders_06']['reasoning']='Sole order is selected but requested pause period is explicitly undecided; policy now expressly requires clarification.'
review['bank_cards_08']['reasoning']='One of two retained cards needs replacement but is not selected; clarification now correctly asks which card, using a nonsecret app description.'
review['bank_fees_05']['reasoning']='The message now explicitly identifies a bank fee, but cannot identify the item or statement to review; fees/routine/clarify.'
resolved=set(review)-{'bank_ambiguous_multi_07'}
for sid in resolved:
 if review[sid]['review_flags']:
  review[sid]['resolved_initial_flags']=review[sid]['review_flags']
 review[sid]['review_flags']=[]
for r,q,g,m in zip(cases,req,gold,meta):
 sid=r['id']
 assert sid==q['id']==g['id']==m['id']
 assert set(q)=={'id','request'} and set(q['request'])=={'model','state','questions'}
 assert q['request']['model']=='clef-flash'
 assert q['request']['state']=='Synthetische Kundennachricht:\n'+r['message']
 assert q['request']['questions']==policy['questions']
 assert g['expected']==r['expected']==initial[sid]['expected']
 assert set(r['expected'])=={'intent','priority','next_step'}
 assert all(v in policy['questions'][k]['criteria'] for k,v in r['expected'].items())
 assert m=={k:v for k,v in r.items() if k not in ('message','expected')}
 assert (r['expected']['next_step']=='security_handoff')==(r['expected']['priority']=='critical')
 assert (r['expected']['next_step']=='clarify')==(r['answerability']=='clarification_needed')
 assert not re.search(r'\b[A-Z]{2}\d{2}[A-Z0-9 ]{10,}\b|https?://|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\d{8,}',r['message'])
 rr=review[sid]
 rr['per_label_agreement']={k:rr['independently_assigned_expected'][k]==r['expected'][k] for k in r['expected']}
 rr['agree']=all(rr['per_label_agreement'].values())
 assert rr['agree'],sid
# Ensure policy fragments required by the adjudication are present in exact model-visible questions.
assert 'Akuter ungesperrter Kartenverlust' in policy['questions']['intent']['instructions']
assert 'Bloße Unkenntnis der Buchungsart' in policy['questions']['intent']['instructions']
assert 'Belege einzelner Zahlungen' in policy['questions']['intent']['instructions']
assert 'notwendige blockierte Bargeldabhebung' in policy['questions']['priority']['instructions']
assert 'Explizit unentschiedene Zielvorgänge' in policy['questions']['next_step']['instructions']
assert 'Sonstige nicht genannte Ausführungsdetails' in policy['questions']['next_step']['instructions']
# Reproduce dataset solely in an isolated directory, leaving canonical data untouched.
with tempfile.TemporaryDirectory(prefix='bank-pre-inference-audit-') as t:
 p=pathlib.Path(t); (p/'scripts').mkdir()
 shutil.copy2(root/'scripts/build_dataset.py',p/'scripts/build_dataset.py')
 subprocess.run(['python',str(p/'scripts/build_dataset.py')],check=True,capture_output=True,text=True)
 for name in ('cases.jsonl','gold.jsonl','requests.jsonl','metadata.jsonl','policy.json'):
  assert (p/'data'/name).read_bytes()==(data/name).read_bytes(),name
ordered=[review[x['id']] for x in cases]
(audit/'pre_inference_review.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in ordered))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={str(p.relative_to(root)):sha(p) for p in [data/'cases.jsonl',data/'gold.jsonl',data/'requests.jsonl',data/'policy.json']}
extra={str(p.relative_to(root)):sha(p) for p in [data/'metadata.jsonl',root/'scripts/build_dataset.py',audit/'pre_inference_review.jsonl']}
assert files['data/requests.jsonl']=='a4ee04381c9d98e7d0365d487fadbe54a6f8c0e3dd751c1a08ebab14c0919562'
assert files['data/cases.jsonl']=='f65f179d11c5ead7a770f271d694aa8065ab5859893db400a4dfbea8ee3ed29b'
summary={'approved_for_freeze':True,'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'files':files,'additional_sha256':extra,'case_count':80,'label_count':240,'full_case_agreement':80,'label_agreement':240,
 'reviewer_type':'independent AI reviewer; not a human bank-domain expert','blind_to_gold':False,
 'model_outputs_inspected':False,'pre_inference':True,'gold_changed_during_review':False,
 'reproduction_check':'All five data files reproduced byte-for-byte from the construction script in isolated temporary directory',
 'blocking_issues':[],
 'nonblocking_caveats':['Synthetic controlled set; not representative live-bank data','Gold-visible review, not blinded human annotation','bank_ambiguous_multi_07 is a deliberately designed global-urgency/route-ambiguity edge case','Inference must consume inner request only, without topic-bearing row ID or metadata','Approval covers the exact listed bytes only; later changes require renewed review'],
 'gold_distributions':{k:dict(collections.Counter(r['expected'][k] for r in cases)) for k in ('intent','priority','next_step')}}
(audit/'freeze_approval.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
md=audit/'pre_inference_review.md'
s=md.read_text().replace('Status: initial review complete; final freeze awaits re-audit of the revised bytes.','Status: APPROVED FOR FREEZE after full revised-set re-audit: 80/80 cases and 240/240 labels agree. All nine requested amendments are implemented; no blocking issue remains.')
s=s.replace('The canonical `pre_inference_review.jsonl` is reserved for the most recently adjudicated version.','The canonical `pre_inference_review.jsonl` contains the final revised judgments, with resolved initial flags retained separately.')
s=s.replace('The revised policy must explicitly settle these overlaps.','The revised policy explicitly settles these overlaps for this set.')
s += '\n\n## Final approval and frozen hashes\n\nThe full revised set was rechecked after all nine amendments and before model inference. No gold label changed; only policy/message clarity and one suggested clarification question changed. All five generated data files reproduce byte-for-byte from the construction script in an isolated temporary directory. `freeze_approval.json` is the machine-readable approval and hash record.\n\n'
for name,h in {**files,**extra}.items():s+=f'- `{name}`: `{h}`\n'
md.write_text(s)
print(json.dumps(summary,ensure_ascii=False,indent=2))
