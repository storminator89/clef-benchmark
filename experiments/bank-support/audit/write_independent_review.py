#!/usr/bin/env python3
"""Independent pre-inference adjudication. Manual labels below are not copied from gold."""
import json,hashlib,collections,datetime
from pathlib import Path
A=Path(__file__).resolve().parent
P=A/'initial_snapshot'
# The reviewer read the construction data and policy, not model outputs. This is not a blinded review.
# Compact manually assigned labels: g guidance, s specialist_review, q clarify, h security_handoff.
STEPS={'g':'guidance','s':'specialist_review','q':'clarify','h':'security_handoff'}
manual={
'access_tan':[
 ('g','Planned TAN-device migration while the old device is retained; general instructions, no danger.'),
 ('s','Self-caused login lock with explicit displayed symptom and a restoration review request.'),
 ('s','TAN service connection error is described; technical review is sufficiently specified.'),
 ('s','TAN failure prevents authorizing tomorrow\'s rent; access route, urgent, technical review.'),
 ('q','“Online” alone could mean login, app, transfer or online card use; route is not established.'),
 ('g','Password-change navigation without disclosure or suspicious activity is routine access guidance.'),
 ('g','TAN fault is resolved; only general registered-device management instructions remain.'),
 ('s','App closes on launch after update while web login works; concrete technical support case.')],
'account_documents':[
 ('g','Monthly account-statement download is a general document-navigation question.'),
 ('g','Asks how to update an address safely without supplying the address; general guidance.'),
 ('s','A specified September statement is missing while earlier statements exist; concrete review.'),
 ('g','Asks generally about account switching; no execution or approval is requested.'),
 ('q','Requested historical copy cannot be selected because month and year are explicitly unknown.'),
 ('g','Address change is complete; only navigation to stored contact details remains.'),
 ('s','Status request for an already submitted closure instruction, identifying the sole account.'),
 ('g','Only download location for a tax document; no tax advice or account action.')],
'ambiguous_multi':[
 ('q','Payment type is explicitly unknown and authorization is undecided, not expressly denied; ask factual clarification.'),
 ('q','Two equally ranked live routes, card instructions and statements, with no ordering.'),
 ('g','The customer explicitly places statement-download guidance first and defers card activation.'),
 ('h','Unblocked lost card makes priority critical and handoff mandatory, but current intent rule leaves two unordered routes: unclear.'),
 ('h','Expressly unauthorized transfer and unsecured access override the fee-first preference; critical security handoff.'),
 ('g','Card found and no alien activity; sole remaining issue is username-navigation help.'),
 ('q','Two explicitly equal routes remain unclear, but tomorrow\'s blocked rent makes global priority urgent.'),
 ('q','No identifiable subject or concrete symptom; routine factual clarification, no invented threat.')],
'cards':[
 ('g','General first-use instructions for a newly delivered debit card.'),
 ('s','Cracked unreadable chip and specific replacement request; card retained, no security incident.'),
 ('h','Payment card currently lost and not blocked; cards route with critical security handoff.'),
 ('s','Stolen card expressly blocked and no unauthorized activity; existing replacement-status request.'),
 ('g','Working card; asks only where contactless setting can be changed.'),
 ('g','Forgotten card PIN, explicitly distinct from banking password; safe-path information only.'),
 ('q','Retained card vaguely does not work; error context or symptom must first be established.'),
 ('q','A replacement is requested but the affected card among two retained cards is not identified.')],
'cash':[
 ('g','General location/list of withdrawal machines; cash route, no specific incident.'),
 ('s','Own completed withdrawal charged without cash dispensed; retained card and concrete cash discrepancy.'),
 ('s','Completed cash deposit credited too little; specific cash-discrepancy review.'),
 ('g','General explanation of depositing cash before taking any action.'),
 ('s','Own cash withdrawal dispensed less than the charged requested amount; concrete review.'),
 ('q','ATM context known, card retained, but kind and symptom of the incident are unspecified.'),
 ('g','Cash and booking discrepancy is expressly resolved; only receipt-navigation guidance remains.'),
 ('s','Described failed cash withdrawal blocks the only means for payment due today; urgent by payment-dependency reading.')],
'direct_debits':[
 ('g','General navigation to direct-debit and mandate details.'),
 ('s','Known authorized electricity mandate, but duplicated debit; billing review without express authorization denial.'),
 ('h','Unknown creditor and expressly no mandate; security takes precedence and requires critical handoff.'),
 ('g','Preventive question about objecting to a direct debit, no current disputed transaction.'),
 ('s','Specific request concerning future collections from a known sole gym mandate; specialist routing only.'),
 ('s','Known own mobile-provider direct debit with disputed amount; not a bank fee or denied authorization.'),
 ('q','One of two known-club collections is disputed but the relevant item is explicitly not selected.'),
 ('g','Subscription is recognized as own and suspicion resolved; general creditor-name navigation.')],
'fees':[
 ('g','General request for account price-list location, no individual charge review.'),
 ('s','Two bank account-maintenance charges in the same month; concrete duplicate-fee review.'),
 ('s','Account-specific card fee and applied contractual condition require individual review.'),
 ('g','Shouting urgency does not establish policy urgency; only a price-list query, no payment.'),
 ('q','Specific charge-review request lacks an identified fee item or statement; clarify the item.'),
 ('g','Previously suspected fraud resolved as bank account price; asks only where price is published.'),
 ('s','Duplicate bank charge is the open issue; the paper statement itself was received.'),
 ('g','General own-bank withdrawal-fee information, no specific cash transaction or error.')],
'security':[
 ('h','Banking credentials entered on a suspect SMS-linked page and no containment; critical security.'),
 ('h','Card transaction explicitly not made by user or authorized person; possession of card does not remove critical risk.'),
 ('g','Suspicious SMS only received; no link, data entry or authorization; general reporting guidance.'),
 ('h','Stolen device with banking and TAN app, access explicitly not blocked; critical security.'),
 ('s','All affected access expressly secured, no new suspicious activity; status of existing security complaint.'),
 ('h','Unsolicited live TAN approval request is expressly a critical trigger; handoff before questions.'),
 ('h','Fraud-pattern “safe account” call still ongoing; critical even though no transfer has been made.'),
 ('h','Possible credential disclosure is unresolved and access unsecured; critical handoff overrides clarification.')],
'standing_orders':[
 ('g','General setup instructions for recurring monthly rent.'),
 ('s','Specific sole rent order with new execution day and starting month; known requested amendment.'),
 ('s','Active standing order did not execute; explicit review, no today/tomorrow deadline.'),
 ('g','Asks how to pause for one month, not to carry out a pause; general guidance.'),
 ('q','One of two standing orders should change, but customer has not selected which.'),
 ('q','Sole order is selected, but requested pause duration is explicitly undecided.'),
 ('s','Rent standing order due today was rejected; urgent concrete failed-order review.'),
 ('g','Old standing order already deleted; only overview-navigation question remains.')],
 'transfers':[
 ('g','General standard-versus-instant transfer process question before any order.'),
 ('s','Own just-approved wrong-recipient transfer with recall request; urgent if approval means it has been sent.'),
 ('s','Specified own transfer marked executed but not received; concrete review with no qualifying due date.'),
 ('g','Pre-authorization beneficiary mismatch warning; asks what the warning means/how to proceed, not a technical-failure review.'),
 ('s','Authorized transfer fails and blocks rent due today; transfer route and urgent technical review.'),
 ('q','Customer cannot establish whether zero, one or two transfers were sent; no confirmed sent error yet.'),
 ('g','General scheduled single-transfer function next week; no existing failed order or urgency.'),
 ('g','Wrong-transfer concern resolved; receipt-download instructions relate to the transfer.')]
}
# Explicit manually assigned route deviations from subject headings.
intent_override={
 'bank_access_tan_05':'unclear',
 'bank_direct_debits_03':'security',
 'bank_ambiguous_multi_01':'unclear','bank_ambiguous_multi_02':'unclear',
 'bank_ambiguous_multi_03':'account_documents','bank_ambiguous_multi_04':'unclear',
 'bank_ambiguous_multi_05':'security','bank_ambiguous_multi_06':'access_tan',
 'bank_ambiguous_multi_07':'unclear','bank_ambiguous_multi_08':'unclear'}
critical={'bank_cards_03','bank_ambiguous_multi_04','bank_ambiguous_multi_05','bank_direct_debits_03',
          'bank_security_01','bank_security_02','bank_security_04','bank_security_06','bank_security_07','bank_security_08'}
urgent={'bank_access_tan_04','bank_ambiguous_multi_07','bank_cash_08','bank_standing_orders_07','bank_transfers_02','bank_transfers_05'}
flags={
 'bank_access_tan_05':['Route gold is over-specific for the literal message; add explicit banking-access context.'],
 'bank_ambiguous_multi_04':['Gold intent conflicts with current multi-route precedence; add a lost-unblocked-card override.'],
 'bank_cash_08':['Make urgent payment dependency through necessary cash withdrawal explicit in policy.'],
 'bank_transfers_02':['Make sent status explicit rather than inferring it from authorization.'],
 'bank_transfers_08':['Make transaction-specific receipt routing explicit, versus general document route.'],
 'bank_cash_07':['Make transaction-specific receipt routing explicit, versus general document route.'],
 'bank_ambiguous_multi_01':['Uncertain authorization is not express denial; clarify distinction from an affirmative security suspicion.'],
 'bank_standing_orders_06':['Specify that an explicitly undecided pause duration is an essential clarification parameter.'],
 'bank_cards_08':['Suggested clarification should ask which card, not merely card type, since two cards may share a type.'],
 'bank_fees_05':['Use “Bankgebühr” in the message to exclude a merchant fee.'],
 'bank_ambiguous_multi_07':['Coherent fictional edge case; equal importance despite rent deadline is somewhat constructed.']}
rows=[json.loads(l) for l in (P/'cases.jsonl').read_text().splitlines()]
reviews=[]
for row in rows:
 topic=row['topic']; n=int(row['id'].rsplit('_',1)[1]); sid=row['id']; st,reason=manual[topic][n-1]
 e={'intent':intent_override.get(sid,topic),'priority':'critical' if sid in critical else 'urgent' if sid in urgent else 'routine','next_step':STEPS[st]}
 eq={k:e[k]==row['expected'][k] for k in e}
 reviews.append({'id':sid,'independently_assigned_expected':e,'agree':all(eq.values()),'per_label_agreement':eq,'reasoning':reason,'review_flags':flags.get(sid,[])})
assert len(reviews)==80 and len({x['id'] for x in reviews})==80
(A/'pre_inference_review.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in reviews))
(A/'pre_inference_review_initial.jsonl').write_text((A/'pre_inference_review.jsonl').read_text())
# Integrity and separation checks are independent of the manual adjudications.
pol=json.loads((P/'policy.json').read_text()); req=[json.loads(l) for l in (P/'requests.jsonl').read_text().splitlines()]
gold=[json.loads(l) for l in (P/'gold.jsonl').read_text().splitlines()]; meta=[json.loads(l) for l in (P/'metadata.jsonl').read_text().splitlines()]
assert len(rows)==len(req)==len(gold)==len(meta)==80
assert [r['id'] for r in rows]==[r['id'] for r in req]==[r['id'] for r in gold]==[r['id'] for r in meta]
for r,q,g,m in zip(rows,req,gold,meta):
 assert q['request']['state']=='Synthetische Kundennachricht:\n'+r['message']
 assert q['request']['questions']==pol['questions']
 assert g['expected']==r['expected']
 assert set(q['request'])=={'model','state','questions'}
 assert all(v in pol['questions'][k]['criteria'] for k,v in r['expected'].items())
 assert len(r['expected'])==3
 assert (r['expected']['next_step']=='security_handoff')==(r['expected']['priority']=='critical')
 assert (r['expected']['next_step']=='clarify')==(r['answerability']=='clarification_needed')
 assert m=={k:v for k,v in r.items() if k not in ('message','expected')}
assert len({r['message'] for r in rows})==80
hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.iterdir()) if f.is_file()}
summary={'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'pre_inference':True,'model_outputs_inspected':False,'blind_to_gold':False,
 'independent_annotator':True,'human_annotator':False,'case_count':80,
 'full_case_agreement':sum(r['agree'] for r in reviews),
 'label_agreement':sum(sum(r['per_label_agreement'].values()) for r in reviews),
 'label_count':240,'status':'revision_required','initial_source_sha256':hashes,
 'validation_checks':'80 unique IDs and messages; all 3 labels valid; requests carry only message/policy; gold and metadata synchronize; critical/handoff invariant holds',
 'gold_distributions':{k:dict(collections.Counter(r['expected'][k] for r in rows)) for k in ('intent','priority','next_step')}}
(A/'pre_inference_initial_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
