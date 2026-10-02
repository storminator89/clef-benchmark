# Independent minimal-pair result audit

Status: PASS
Checked 48 source predictions, 48 case results, 24 pair results, and 6972 comparisons.
Prediction SHA256: c3cf3aa50f66340c9b43a0b8cfc168e280f130b2282d92f47ec80dd6e8fe200e

Primary scorer was not read, imported, or invoked by this checker. Source predictions were not modified.

## Independently calculated main results
- case_exact: 39/48 (0.8125)
- pair_both_correct: 17/24 (0.7083333333333334)
- flip_correct_directional_change: 8/12 (0.6666666666666666)
- invariant_unjustified_change: 1/12 (0.08333333333333333)
- invariant_unjustified_change_valid_conditional: 1/12 (0.08333333333333333)
- invariant_stable: 11/12 (0.9166666666666666)
- invariant_stable_wrong: 2/12 (0.16666666666666666)
- invariant_invalid: 0/12 (0.0)

## Every erroneous case
- pair_tow_distance_records_b: expected {'action': 'answer', 'determination': 'no'}; native {'action': 'ask_target', 'determination': 'unresolved'}; valid=True
- pair_report_delivery_target_b: expected {'action': 'ask_target', 'determination': 'unresolved'}; native {'action': 'answer', 'determination': 'yes'}; valid=True
- pair_rental_days_conflict_b: expected {'action': 'resolve_conflict', 'determination': 'unresolved'}; native {'action': 'ask_target', 'determination': 'unresolved'}; valid=True
- pair_statement_notification_a: expected {'action': 'ask_fact', 'determination': 'unresolved'}; native {'action': 'answer', 'determination': 'no'}; valid=True
- pair_report_delivery_target_a: expected {'action': 'ask_target', 'determination': 'unresolved'}; native {'action': 'answer', 'determination': 'yes'}; valid=True
- pair_rental_days_conflict_a: expected {'action': 'resolve_conflict', 'determination': 'unresolved'}; native {'action': 'ask_target', 'determination': 'unresolved'}; valid=True
- pair_limit_order_price_step_a: expected {'action': 'answer', 'determination': 'no'}; native {'action': 'ask_fact', 'determination': 'unresolved'}; valid=True
- pair_gadget_theft_notice_a: expected {'action': 'answer', 'determination': 'yes'}; native {'action': 'answer', 'determination': 'unresolved'}; valid=True
- pair_redemption_window_conflict_a: expected {'action': 'answer', 'determination': 'no'}; native {'action': 'resolve_conflict', 'determination': 'no'}; valid=True

## Every erroneous pair
- pair_statement_notification (flip/clarify_to_answer): {'action': 'answer', 'determination': 'no'} → {'action': 'answer', 'determination': 'yes'}; expected {'action': 'ask_fact', 'determination': 'unresolved'} → {'action': 'answer', 'determination': 'yes'}; valid=True
- pair_gadget_theft_notice (flip/yes_to_no): {'action': 'answer', 'determination': 'unresolved'} → {'action': 'answer', 'determination': 'no'}; expected {'action': 'answer', 'determination': 'yes'} → {'action': 'answer', 'determination': 'no'}; valid=True
- pair_tow_distance_records (flip/clarify_to_answer): {'action': 'resolve_conflict', 'determination': 'unresolved'} → {'action': 'ask_target', 'determination': 'unresolved'}; expected {'action': 'resolve_conflict', 'determination': 'unresolved'} → {'action': 'answer', 'determination': 'no'}; valid=True
- pair_rental_days_conflict (invariant/irrelevant_text): {'action': 'ask_target', 'determination': 'unresolved'} → {'action': 'ask_target', 'determination': 'unresolved'}; expected {'action': 'resolve_conflict', 'determination': 'unresolved'} → {'action': 'resolve_conflict', 'determination': 'unresolved'}; valid=True
- pair_redemption_window_conflict (flip/answer_to_clarify): {'action': 'resolve_conflict', 'determination': 'no'} → {'action': 'resolve_conflict', 'determination': 'unresolved'}; expected {'action': 'answer', 'determination': 'no'} → {'action': 'resolve_conflict', 'determination': 'unresolved'}; valid=True
- pair_report_delivery_target (invariant/irrelevant_text): {'action': 'answer', 'determination': 'yes'} → {'action': 'answer', 'determination': 'yes'}; expected {'action': 'ask_target', 'determination': 'unresolved'} → {'action': 'ask_target', 'determination': 'unresolved'}; valid=True
- pair_limit_order_price_step (invariant/short_circuit_control): {'action': 'ask_fact', 'determination': 'unresolved'} → {'action': 'answer', 'determination': 'no'}; expected {'action': 'answer', 'determination': 'no'} → {'action': 'answer', 'determination': 'no'}; valid=True

## Mismatches
None

## Timing definition
P95 uses linear interpolation at sorted index (n−1)×0.95 across valid benchmark forward timings. Warmup and repeated-first-case timing are excluded.

## Evidence limits
Freeze chronology is supported by recorded UTC timestamps, approved hashes and retained run evidence, not an external trusted timestamp service. The single repeatability probe exposes only its native summary, not a second full vector or separate timing. Marginal probabilities are not calibration claims. Missing/invalid predictions cannot receive stability credit.
