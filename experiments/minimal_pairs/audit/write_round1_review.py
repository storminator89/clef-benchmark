#!/usr/bin/env python3
"""Independent manual semantic review with mechanical consistency checks; no inference."""
from pathlib import Path
import hashlib,json,collections,datetime
ROOT=Path(__file__).resolve().parents[1]
snap=json.loads((ROOT/'audit/round1_review_snapshot.json').read_text())
D=snap['dataset']; hashes=snap['sha256']
read=lambda name:[json.loads(x) for x in D[name].splitlines() if x.strip()]
pairs=read('pairs.jsonl'); cases=read('cases.jsonl'); gold=read('gold.jsonl'); requests=read('requests.jsonl'); metadata=read('metadata.jsonl')
C={x['id']:x for x in cases};G={x['id']:x for x in gold};R={x['id']:x for x in requests};M={x['id']:x for x in metadata};policy=json.loads(D['policy.json'])
def ans(x):
 return {'action': 'answer' if x in ('yes','no') else x,'determination':x if x in ('yes','no') else 'unresolved'}
# Manually derived from the stated rules and scenario facts, not generated from supplied gold.
manual={
'paper_transfer_quota':('yes','no','With Basis Plus active, transfer 3 meets the inclusive cap of 3.','Transfer 4 exceeds that same cap.','A single transfer-number fact crosses an inclusive upper boundary.'),
'savings_stamp':('no','yes','74 Euro is below the 75 Euro minimum despite the active savings plan.','75 Euro meets the inclusive minimum, and the plan remains active.','A single monthly-total fact crosses an inclusive lower boundary.'),
'statement_notification':('ask_fact','yes','The verified address is given but consent is explicitly unspecified; consent changes eligibility.','Consent is explicitly present and the verified address remains given, so both conditions hold.','Only consent status changes from unknown to present; lack of reporting is not treated as absent consent.'),
'envelope_pickup':('no','ask_target','Target A is explicit; A is ready but its pickup slip is explicitly absent, so no.','The target is explicitly unspecified among A and B; A yields no and B yields yes.','Only the referent specification changes. The new sentence is slightly formal but clearly means that neither target has been uniquely selected, not that pickup is impossible.'),
'standing_order_express':('yes','yes','The order is active and 11:00 is before noon.','The same active order and 11:00 receipt remain; its personal label has no rule effect.','Only an explicitly irrelevant, self-assigned name changes. Neither name changes timing or active status.'),
'coin_bag_limit':('no','no','Readable identifier does not overcome 51 coins exceeding the maximum 50.','52 coins also exceed 50 while the identifier remains readable.','The sole count fact changes within the same failing region.'),
'fx_pickup_stock':('ask_fact','ask_fact','The appointment is confirmed, but stock availability is explicitly unknown and decisive.','Stock remains unknown; brown rather than white paper has no rule effect.','Only an explicitly irrelevant paper-envelope color changes; no availability inference is licensed.'),
'locker_waitlist':('no','no','Explicitly unpaid deposit falsifies a necessary condition regardless of unknown locker availability.','Even confirmed free capacity does not cure the unchanged unpaid deposit.','Only the free-locker status changes from unknown to yes; a known false conjunct short-circuits it.'),
'gadget_theft_notice':('yes','no','Receipt is present and exactly 48 elapsed hours satisfies no later than 48 hours.','49 elapsed hours violates the deadline despite the receipt.','Only an already fully calculated elapsed-hour count changes; no calendar, timezone, or start-time ambiguity remains.'),
'glass_cost_limit':('no','yes','Accidental breakage is established but 501 Euro exceeds the inclusive 500 Euro cap.','500 Euro is within the cap and the accident fact is unchanged.','Only the invoice amount crosses an inclusive upper boundary.'),
'tow_distance_records':('resolve_conflict','yes','The same covered breakdown has equal-rank unresolved 12 km and 25 km records; they straddle 20 km.','Both equal-rank records now say 12 km, so the covered breakdown meets the cap without a conflict.','Only the second reported-distance value changes. The first report and no-correction/no-precedence constraints remain unchanged.'),
'equipment_inspection':('no','ask_fact','Accidental damage is given; an explicitly absent valid certificate fails a necessary condition.','Certificate availability is now explicitly unknown, and either status would change the outcome.','Only certificate knowledge/status changes from confirmed absence to unknown; unknown is not synonymous with absence.'),
'camera_rental_cover':('yes','yes','10 days is within the inclusive 14-day limit and the rental receipt is signed.','The same 10 days and signed receipt remain; silver rather than black is irrelevant.','Only an explicitly irrelevant camera color changes; no ownership/receipt facts change.'),
'baggage_weight_cap':('no','no','Loss is confirmed but 21 kg exceeds 20 kg.','22 kg also exceeds 20 kg and loss remains confirmed.','The sole weight fact changes within the same failing region.'),
'rental_days_conflict':('resolve_conflict','resolve_conflict','The invoice is present but equal-rank 3-day and 8-day reports for one rental straddle 5 days.','The same decisive duration conflict remains after a paint-color change.','Only an explicitly irrelevant color changes, not the source hierarchy, rental identity, or durations.'),
'festival_cancellation':('no','no','The festival took place in full and was not cancelled, so the cancellation requirement is false regardless of refund uncertainty.','Confirmed lack of reimbursement cannot cure the unchanged non-cancellation.','Only reimbursement knowledge changes from unknown to no; the other conjunct remains decisively false.'),
'rebalance_interval':('yes','no','Under the intended Basistarif scope, 30 days meets the inclusive minimum and no special execution is requested.','Under that same intended tariff scope, 29 days fails the minimum.','Only elapsed days change, but tariff applicability is not explicit in either message or the generic question. This allows a reasonable alternate scope reading and should be clarified before freeze.'),
'savings_plan_components':('no','yes','All components are eligible but 11 exceeds the maximum 10 positions.','10 positions meet the cap and all remain eligible.','Only position count crosses an inclusive upper boundary; the requested package is explicit in the question.'),
'fund_switch_target':('ask_target','yes','The requested switch is unspecified; A satisfies same-depot and standard-universe conditions while B fails same-depot.','Target A is now explicit and satisfies both conditions.','Only target selection changes; facts and outcomes about both candidate switches are identical.'),
'redemption_window_conflict':('no','resolve_conflict','Holding time is satisfied but both equal-rank reports state closed, so the open-window condition is false.','Equal-rank closed and open reports about the same current window now conflict on a decisive fact.','Only the second window-status report changes. Neither source is a correction and the first report stays closed.'),
'fractional_sale_batch':('yes','yes','0.4 units is less than one whole unit and the batch is open.','Both decisive conditions remain true after the personal filing label changes.','Only an explicitly irrelevant personal filing name changes; the names themselves cannot override the explicit holdings amount.'),
'research_credit_age':('no','no','The unused voucher is 91 days old, exceeding the 90-day maximum.','92 days also exceeds the maximum; unused status is unchanged.','The sole age fact changes within the same failing region.'),
'report_delivery_target':('ask_target','ask_target','Target is explicitly unspecified between A, ready and enabled, and B, ready but disabled; their eligibility differs.','Changing A\'s explicitly irrelevant internal title does not select A or B; the target remains unspecified.','Only A\'s title changes. The question does not refer to either title, and an explicit sentence preserves target ambiguity.'),
'limit_order_price_step':('no','no','12.34 Euro is not a multiple of 0.10 Euro, so the necessary price-step condition fails regardless of unknown window status.','An open window cannot cure the unchanged invalid 12.34 Euro price increment.','Only window knowledge changes from unknown to open; exact decimal arithmetic makes the other conjunct false.')}
assert len(manual)==24
all_ids=[x['id'] for x in cases]
global_checks={
 '24_unique_pairs':len(pairs)==len({p['id'] for p in pairs})==24,
 '48_unique_cases':len(cases)==len(C)==48,
 'all_file_case_ids_identical':set(C)==set(G)==set(R)==set(M),
 '48_unique_rows_in_all_case_files':all(len(x)==48 for x in (gold,requests,metadata)) and all(len({v['id'] for v in x})==48 for x in (gold,requests,metadata)),
 'each_case_in_one_pair':collections.Counter(cid for p in pairs for cid in p['case_ids'])==collections.Counter(all_ids),
 '12_flip_12_invariant':dict(collections.Counter(p['kind'] for p in pairs))=={'flip':12,'invariant':12},
 '8_pairs_per_domain':dict(collections.Counter(p['domain'] for p in pairs))=={'banking':8,'insurance':8,'finance':8},
 'same_request_order_across_case_files':all([x['id'] for x in a]==all_ids for a in (gold,requests,metadata)),
 'action_schema_exact_order':list(policy)==['action','determination'] and list(policy['action']['criteria'])==['answer','ask_fact','ask_target','resolve_conflict'] and list(policy['determination']['criteria'])==['yes','no','unresolved'],
}
rows=[]
for p in pairs:
 a,b=[C[id] for id in p['case_ids']];g1,g2,why1,why2,change=manual[p['family']];derived=[ans(g1),ans(g2)]
 checks={
  'same_rule':a['rule']==b['rule']==p['rule'],
  'same_question':a['question']==b['question']==p['question'],
  'same_domain_family_kind_subtype':all(a[k]==b[k]==p[k] for k in ('domain','family','kind','subtype')),
  'distinct_changed_spans':p['span_a']!=p['span_b'],
  'one_bounded_replacement':all(c['message']==p['unchanged_prefix']+p['span_'+s]+p['unchanged_suffix'] for c,s in ((a,'a'),(b,'b'))),
  'correct_zero_based_character_offsets':all(p['changed_character_offsets_'+s]==[len(p['unchanged_prefix']),len(p['unchanged_prefix'])+len(p['span_'+s])] for s in ('a','b')),
  'correct_unchanged_sha256':all(p['unchanged_'+part+'_sha256']==hashlib.sha256(p['unchanged_'+part].encode()).hexdigest() for part in ('prefix','suffix')),
  'explicit_unchanged_components':p['unchanged_components']==['rule','question','schema_and_option_order','message_prefix','message_suffix'],
  'case_pair_side_identity':all(c['pair_id']==p['id'] and c['side']==s for c,s in ((a,'a'),(b,'b'))),
  'label_free_exact_request_construction':True,
  'supplied_gold_matches_manual_intended_scope':all(c['expected']==d==G[c['id']]['expected']==p['expected_'+s] for c,s,d in ((a,'a',derived[0]),(b,'b',derived[1]))),
  'metadata_matches_case':all(all(M[c['id']][k]==c[k] for k in M[c['id']]) for c in (a,b)),
  'kind_matches_gold_relation':(derived[0]!=derived[1])==(p['kind']=='flip')
 }
 for c in (a,b):
  r=R[c['id']]
  state=f"Fiktive Testregel:\n{c['rule']}\n\nSynthetische Anfrage und Unterlagen:\n{c['message']}\n\nZu beurteilende Eigenschaft:\n{c['question']}"
  checks['label_free_exact_request_construction'] &= (set(r)=={'id','request'} and set(r['request'])=={'model','state','questions'} and r['request']['model']=='clef-flash' and r['request']['state']==state and r['request']['questions']==policy and list(r['request']['questions'])==list(policy) and all(list(r['request']['questions'][k]['criteria'])==list(policy[k]['criteria']) for k in policy))
 issue=p['family']=='rebalance_interval'
 rows.append({'pair_id':p['id'],'case_ids':p['case_ids'],'review_round':1,'reviewer_type':'separate AI reviewer; not human expert; not blind to author gold','pre_inference':True,'independently_derived_gold':{a['id']:derived[0],b['id']:derived[1]},'gold_scope':'Intended base-tariff scope; applicability ambiguity requires correction' if issue else 'Literal closed fictional rule and supplied facts','case_rationales':{a['id']:why1,b['id']:why2},'changed_fact_or_span_review':change,'unchanged_components_review':{'rule':'identical','question':'identical','schema_and_option_order':'identical','message_prefix':'identical and hash checked','message_suffix':'identical and hash checked'},'alternate_interpretations': ['If the tariff is an unstated applicability prerequisite rather than the presupposed evaluation scope, applicability is unknown. Depending on unprovided other-tariff rules, either endpoint could require ask_fact/unresolved. Explicitly state Basistarif applicability in both messages or scope the question to Basistarif.'] if issue else [],'ambiguity_review':'FAIL: fix tariff scope before freeze' if issue else 'PASS: no material alternate reading found under the explicit fictional policy','leakage_review':'No case gold, rationale, pair kind/subtype, side, or expected transition enters request.state/questions. Outer request ID is not passed to the encoder by the inspected runner. Shared policy label definitions are intentional task instructions.','mechanical_checks':checks,'pass':not issue and all(checks.values()) and all(global_checks.values()),'rationale':'One scope ambiguity needs a wording correction; intended labels are otherwise consistent.' if issue else 'Both gold endpoints independently supported; the single bounded change and all declared invariants verified.','dataset_file_sha256':hashes})
(ROOT/'audit/pre_inference_review_round1.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in rows))
summary={'review_round':1,'scope':'All 24 pairs / 48 cases; data review only, protocol/scorer pending','pre_inference':True,'reviewer_type':'Separate AI reviewer; no blind gold review or human/expert holdout claim','global_checks':global_checks,'mechanical_pair_checks_all_pass':all(all(r['mechanical_checks'].values()) for r in rows),'semantic_pass_count':sum(r['pass'] for r in rows),'semantic_fail_count':sum(not r['pass'] for r in rows),'dataset_file_sha256':hashes}
(ROOT/'audit/pre_inference_review_round1_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
