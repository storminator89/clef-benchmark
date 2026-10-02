# Independent review of every error

All 9 erroneous cases have technically valid native outputs. All frozen gold labels remain supported by the explicit closed rules. No prediction, gold, protocol, or primary scorer was edited.

## Main distinctions
- Case exactness: 39/48; action: 40/48; determination: 42/48
- Both endpoints correct: 17/24 pairs
- Observed flip changes: 12/12; fully correct directional changes: 8/12
- Invariant stability: 11/12, including 2 stable-but-wrong pairs; invariant both-correct: 9/12
- Unjustified invariant changes: 1/12; valid-conditional denominator is also 12 because no native case is invalid

## Every erroneous case

### pair_tow_distance_records_b
Gold: {'action': 'answer', 'determination': 'no'}. Native: {'action': 'ask_target', 'determination': 'unresolved'}.
Both equal-status records give the same distance, 25 km. With a maximum of 20 km, the conjunction is definitively false. No target ambiguity or unresolved distance conflict remains.

### pair_report_delivery_target_b
Gold: {'action': 'ask_target', 'determination': 'unresolved'}. Native: {'action': 'answer', 'determination': 'yes'}.
The title-only edit does not choose between eligible report A and ineligible report B. The same unsupported answer/yes is repeated.

### pair_rental_days_conflict_b
Gold: {'action': 'resolve_conflict', 'determination': 'unresolved'}. Native: {'action': 'ask_target', 'determination': 'unresolved'}.
Changing the car color leaves the same 3-versus-8-day conflict. The unresolved determination is correct, but ask_target is the wrong clarification action.

### pair_statement_notification_a
Gold: {'action': 'ask_fact', 'determination': 'unresolved'}. Native: {'action': 'answer', 'determination': 'no'}.
Consent is not stated. The confirmed email condition holds, while either consent value remains possible. The closed rule therefore requires ask_fact/unresolved; no is not established.

### pair_report_delivery_target_a
Gold: {'action': 'ask_target', 'determination': 'unresolved'}. Native: {'action': 'answer', 'determination': 'yes'}.
Report A satisfies the rule and report B does not; the request explicitly leaves its target unspecified. Selecting yes resolves the target without evidence.

### pair_rental_days_conflict_a
Gold: {'action': 'resolve_conflict', 'determination': 'unresolved'}. Native: {'action': 'ask_target', 'determination': 'unresolved'}.
The records describe the same rental but give 3 versus 8 days, across an inclusive 5-day boundary. The missing resolution concerns conflicting facts about one target, so resolve_conflict is required rather than ask_target.

### pair_limit_order_price_step_a
Gold: {'action': 'answer', 'determination': 'no'}. Native: {'action': 'ask_fact', 'determination': 'unresolved'}.
EUR 12.34 is not a multiple of EUR 0.10. This false necessary conjunct already establishes no, even while the trading-window status is unknown. Asking for that status cannot change the result.

### pair_gadget_theft_notice_a
Gold: {'action': 'answer', 'determination': 'yes'}. Native: {'action': 'answer', 'determination': 'unresolved'}.
The receipt is present and the fully calculated elapsed time is exactly 48 hours. The stated latest-48-hours condition is inclusive, so yes is established. The action answer is correct but the determination unresolved is not.

### pair_redemption_window_conflict_a
Gold: {'action': 'answer', 'determination': 'no'}. Native: {'action': 'resolve_conflict', 'determination': 'no'}.
Both reports say the same window is closed. This is agreement on a false necessary condition. Determination no is correct, while resolve_conflict invents an unresolved conflict.

## Every erroneous pair
- pair_statement_notification: one missing-consent endpoint is answered no instead of clarified
- pair_gadget_theft_notice: the inclusive 48-hour endpoint is incorrectly unresolved
- pair_tow_distance_records: the resolved 25/25-km endpoint is still clarified
- pair_rental_days_conflict: both color variants stably use the wrong clarification action
- pair_redemption_window_conflict: the initial agreement endpoint incorrectly uses resolve_conflict
- pair_report_delivery_target: both title variants stably answer yes despite an unspecified target
- pair_limit_order_price_step: the unknown-window endpoint is unnecessarily clarified; confirming the window changes the output even though the failed price-step condition remains decisive

## Evidence and limits
Complete native probability maps and source context remain in results/predictions.jsonl, results/errors.jsonl and data/cases.jsonl; paired endpoints and outcomes remain in data/pairs.jsonl and results/pair_scores.jsonl. The independent checker recomputes all field and pair comparisons. Its corrected method and initial implementation assumptions are documented in audit/INDEPENDENT_METHOD.md. No pattern above is a population estimate or calibrated-confidence claim.
