# Independent pre-inference review: German clarification diagnostic

## Verdict

**72/72 pass; 0 require revision.** All 72 IDs are recorded below and individually in `pre_inference_review.jsonl`. Approval concerns the clarity and label correctness of this closed-rule diagnostic only. It is not validation of real banking, insurance, financial advice, or production conversation quality.

Reviewer identity type: **independent AI reviewer task**, `review_clarification_gold`. The reviewer is a separate task from the author; this is not a human or subject-matter-expert review and is not model-diverse validation. Gold labels and author rationales were visible; the review is not blinded. No evaluated model was loaded or called, and no later predictions or evaluation results were read. Review time (UTC): 2026-10-02T13:57:48.056324+00:00.

## Scope and method

Read all 72 source cases, all 72 nested request payloads, the complete shared policy, and the builder. For every case, checked the stated fictional rule, target property, action, determination, linguistic clarity and whether each uncertain variable can change the outcome. For every clarification example, the JSONL records a concrete yes/no outcome witness. For determinate omissions, it identifies why the missing information cannot affect the answer. Programmatic checks verify 72 unique IDs, identical case/request order, exact state composition, equal shared question policy, and exclusion of gold/metadata from nested model payloads. The author is separately responsible for the scorer, runner and preflight freeze.

The two gold fields are logically dependent: all three clarification actions entail unresolved; answer entails yes or no. They must not be treated as 144 independent evaluation observations.

## Revision requests and verification

1. R01, `clarify_savings_fee_05`: replace “eine Rate über 49 Euro” with an explicitly exact EUR 49 amount. “über” can mean greater than 49, allowing both 49.50 (no) and 50 (yes). Status: **resolved**.
2. R02, `clarify_card_replacement_04` and its shared family rule: replace the implicit “innerhalb von 24 Monaten” boundary with “höchstens 24 Monate nach Ausgabe (24 Monate eingeschlossen)” or equivalent. Exact 24 months must unambiguously qualify. Status: **resolved**.

Changed source files since original read: data/cases.jsonl, data/requests.jsonl, scripts/build_dataset.py.
Changed cases and fields: `{"clarify_card_replacement_01": ["rule"], "clarify_card_replacement_02": ["rule"], "clarify_card_replacement_03": ["rule"], "clarify_card_replacement_04": ["rule"], "clarify_card_replacement_05": ["rule"], "clarify_card_replacement_06": ["rule"], "clarify_savings_fee_05": ["message"]}`.

## Action distinctions

- `ask_fact`: one target is understood and one necessary fact is unknown; both yes and no remain possible.
- `ask_target`: two distinct, described targets individually give different answers, and the intended target is not specified. Their distinct facts are not a contradiction about one object.
- `resolve_conflict`: one target is identified, but equal-status, uncorrected accounts give incompatible material facts leading to opposite outcomes. The explicit no-priority policy rules out choosing the later mention.
- `answer`: facts already establish yes or no. A confirmed absent requirement is false, not unknown; a missing irrelevant attribute or an unknown conjunct after another necessary conjunct fails does not justify a question.

These definitions are distinguishable for these cases. In general dialogue, conflict resolution can itself be phrased as a factual question, so this is a stipulated action taxonomy, not a universal separation of utterance forms. The task chooses a label rather than generating or assessing the quality of an actual clarification question.

## Balance and representativeness

- 72 deliberately authored cases: 12 related rule families × 6 strata; no probability sampling.
- Each domain has 24 cases: banking, insurance and finance.
- Each stratum has 12 cases: missing fact, ambiguous target, conflicting evidence, complete yes, complete no, sufficient despite omission.
- Exactly 36 clarify and 36 answer. Clarify subtypes each have 12 examples; this is not a uniform four-class action distribution (answer has 36).
- Determinations: 36 unresolved, 18 yes, 18 no. The omission stratum has six no cases caused by a failed necessary condition and six yes cases with irrelevant missing details.
- Every family repeats its rule and uses related lexical and logical templates. Case outcomes are correlated within family, so row-wise binomial intervals or row bootstrap cannot be interpreted as independent-sample generalization evidence. Describe family-stratified results; if uncertainty is estimated, consider family-cluster resampling and disclose that only 12 clusters exist. Random row splitting does not create a genuine family-held-out test.
- The domain wrappers do not establish domain expertise: all rules are short, supplied, fictional two-condition conjunctions. There are no natural conversation samples, multi-turn follow-ups, disjunctions, uncertain rule interpretation, contradictory-source reliability judgments, same-result target ambiguity, irrelevant conflicts, or safety/action-execution evaluation. Findings should be restricted to this narrow controlled diagnostic.

## Leakage and shortcuts

No case ID, stratum, expected label, author rationale, clarification target, or review claim appears in the nested model `request` object. Shared choice names/descriptions are legitimate task definitions and are not per-case gold. The outer JSONL ID reveals stratum through its suffix, and gold exists in separate source artifacts; the inference runner must pass only the nested request, never the entire case or wrapper. Source inspection also confirms `reference_runtime/run_clef.py` lines 20–27 build a fresh dictionary containing only model/state/questions, with the ID held separately; `infer` sends that dictionary to encode_record. No runtime inference was executed by this reviewer.

Strong lexical cues remain: missing-fact cases explicitly say the needed fact was not provided; target cases explicitly say a target has not been chosen; conflicts explicitly announce equal-ranking sources and absent correction. The six positive omission cases mention conspicuously irrelevant facts, with some declared irrelevant in the rule. All ambiguous-target A outcomes are yes and B outcomes no. These are controlled construction cues and potential shortcuts, not hidden direct gold fields; they materially limit claims about naturalistic robustness. Deterministic order shuffling does not remove them.

The builder assigns the final stratum's label by alternating family position rather than explicitly recording the intended label with each example. Current labels were checked independently and are consistent, but later family reordering could silently break them. Frozen hashes and a repeated semantic review are required after any future edit.

## Input hashes

SHA-256 of exact file bytes at the original review read:

- `data/cases.jsonl`: `e93c83467272bb348091dd95c3d6fc1e245a879517cb45bd064e818b9dc59787`
- `data/requests.jsonl`: `ca89c430226a6499a4fbb433c67a2643958efd5b4d9b08a261112210d7734776`
- `data/policy.json`: `f920a180fae80b29bf49ea882abad1bd3764cc4ececf73c8d82c639e42d16b15`
- `data/gold.jsonl`: `10b4223eae817647d37b34669cf88225d170400cdc8f7742b5d61c4b76e59c39`
- `data/metadata.jsonl`: `cb4f2c6455236d8e8c24dba189997622dc6529095c5bae92360da424e404095c`
- `data/design_summary.json`: `3f8d064506f9d87e43fe73120466768ee886a31423875281e4d3504e8b683393`
- `scripts/build_dataset.py`: `2368121218a1037bb24fb8ff28da59d544d8c2a3a2c33ad2eca2d3015aab8bcf`

SHA-256 of exact file bytes at this review revision:

- `data/cases.jsonl`: `0d134c26a9b06733103b207586cdd77c4e35899c1711f923cfbae17bf6968ac0`
- `data/requests.jsonl`: `6dbe7ca4621e7e8350ca0c929383f782d3f56782ca8f79f48d1be6fdef75fb14`
- `data/policy.json`: `f920a180fae80b29bf49ea882abad1bd3764cc4ececf73c8d82c639e42d16b15`
- `data/gold.jsonl`: `10b4223eae817647d37b34669cf88225d170400cdc8f7742b5d61c4b76e59c39`
- `data/metadata.jsonl`: `cb4f2c6455236d8e8c24dba189997622dc6529095c5bae92360da424e404095c`
- `data/design_summary.json`: `3f8d064506f9d87e43fe73120466768ee886a31423875281e4d3504e8b683393`
- `scripts/build_dataset.py`: `d2be27233d7f9f20894edd152c2f3be4a67963c2fffc7223bd2470c747839467`

## All reviewed IDs

- `clarify_bicycle_theft_01`: **pass**, gold ask_fact/unresolved; Report after 3 days is timely. Locked/attached bicycle -> yes; not attached -> no.
- `clarify_bicycle_theft_02`: **pass**, gold ask_target/unresolved; Case A attached and reported after 3 days -> yes; case B not attached and reported after 3 days -> no.
- `clarify_bicycle_theft_03`: **pass**, gold resolve_conflict/unresolved; Report after 3 days. Attached -> yes; not attached -> no. Equal statements without resolved priority prevent a determination.
- `clarify_bicycle_theft_04`: **pass**, gold answer/yes; Attached bicycle and report exactly 7 calendar days later satisfy both conditions; inclusive deadline -> yes.
- `clarify_bicycle_theft_05`: **pass**, gold answer/no; Report after 8 calendar days misses the 7-day deadline despite attached bicycle -> no.
- `clarify_bicycle_theft_06`: **pass**, gold answer/no; Bicycle confirmed not attached. Any reporting interval still fails a necessary condition -> no.
- `clarify_card_replacement_01`: **pass**, gold ask_fact/unresolved; No intentional damage is confirmed. Age 18 months -> yes; age 30 months -> no. Ask for relative age, or issue and defect dates sufficient to establish it.
- `clarify_card_replacement_02`: **pass**, gold ask_target/unresolved; Card A at 18 months with no intentional damage -> yes; card B at 30 months with no intentional damage -> no.
- `clarify_card_replacement_03`: **pass**, gold resolve_conflict/unresolved; Age 18 months -> yes; age 30 months -> no. The same target and equal uncorrected sources make this a conflict, not a target choice.
- `clarify_card_replacement_04`: **pass**, gold answer/yes; Technical defect at exactly 24 months, no intentional damage and no loss -> yes only with the intended inclusive limit explicitly stated.
- `clarify_card_replacement_05`: **pass**, gold answer/no; Technical defect at 25 months exceeds the 24-month limit -> no.
- `clarify_card_replacement_06`: **pass**, gold answer/yes; Technical defect at 12 months with no intentional damage and no loss -> yes. Color and old-letter number do not enter the rule.
- `clarify_depot_statement_fee_01`: **pass**, gold ask_fact/unresolved; Digital delivery selected. Account age 18 months at report date -> yes; age 8 months -> no.
- `clarify_depot_statement_fee_02`: **pass**, gold ask_target/unresolved; Report A for 18-month account with digital delivery -> yes; report B for 8-month account with digital delivery -> no.
- `clarify_depot_statement_fee_03`: **pass**, gold resolve_conflict/unresolved; Account age 18 months. Equal current digital versus paper delivery entries yield yes versus no.
- `clarify_depot_statement_fee_04`: **pass**, gold answer/yes; Exactly 12 months at report date reaches inclusive minimum and digital delivery is selected -> yes.
- `clarify_depot_statement_fee_05`: **pass**, gold answer/no; Paper delivery explicitly fails the delivery condition despite 18-month account age -> no.
- `clarify_depot_statement_fee_06`: **pass**, gold answer/no; Paper delivery is confirmed, so every possible account age still yields no.
- `clarify_device_damage_01`: **pass**, gold ask_fact/unresolved; Accidental breakage is confirmed. Damage during contract -> yes; after contract -> no.
- `clarify_device_damage_02`: **pass**, gold ask_target/unresolved; Case A accidental break during contract -> yes; case B accidental break after contract -> no.
- `clarify_device_damage_03`: **pass**, gold resolve_conflict/unresolved; Accidental damage is confirmed. Equal records put the same break within versus outside contract: yes versus no.
- `clarify_device_damage_04`: **pass**, gold answer/yes; Accidental break within contract satisfies both stated conditions -> yes.
- `clarify_device_damage_05`: **pass**, gold answer/no; Break was intentionally caused and is explicitly excluded, despite occurring within contract -> no.
- `clarify_device_damage_06`: **pass**, gold answer/no; Damage confirmed after contract ended. Either accidental or intentional cause still gives no.
- `clarify_giro_fee_01`: **pass**, gold ask_fact/unresolved; Active mailbox with EUR 1,350 salary -> yes; inactive mailbox with the same salary -> no.
- `clarify_giro_fee_02`: **pass**, gold ask_target/unresolved; August: EUR 1,300 salary and active mailbox -> yes; September: EUR 900 salary and active mailbox -> no.
- `clarify_giro_fee_03`: **pass**, gold resolve_conflict/unresolved; EUR 1,300 with active mailbox -> yes; EUR 900 with active mailbox -> no. Equal sources and no correction prevent choosing either.
- `clarify_giro_fee_04`: **pass**, gold answer/yes; Salary equals the inclusive EUR 1,200 minimum and mailbox was active -> yes.
- `clarify_giro_fee_05`: **pass**, gold answer/no; Mailbox was inactive for the entire month; EUR 1,500 salary cannot overcome this failed necessary condition -> no.
- `clarify_giro_fee_06`: **pass**, gold answer/no; Salary is confirmed absent; private repayment does not count. Every mailbox state still gives no.
- `clarify_luggage_delay_01`: **pass**, gold ask_fact/unresolved; 30-hour luggage delay meets threshold. Receipts for necessary replacement purchases present -> yes; absent -> no.
- `clarify_luggage_delay_02`: **pass**, gold ask_target/unresolved; Case A 30 hours with receipts -> yes; case B 10 hours with receipts -> no. Rule and property ask only the stated conditions.
- `clarify_luggage_delay_03`: **pass**, gold resolve_conflict/unresolved; Receipts exist. Equal duration reports 30 versus 10 hours yield yes versus no.
- `clarify_luggage_delay_04`: **pass**, gold answer/yes; Exactly 24 hours delay reaches the inclusive minimum and necessary-purchase receipts exist -> yes.
- `clarify_luggage_delay_05`: **pass**, gold answer/no; Purchase receipts explicitly absent despite 40-hour delay -> no.
- `clarify_luggage_delay_06`: **pass**, gold answer/yes; 27-hour delay and necessary-purchase receipts establish yes; luggage color explicitly irrelevant.
- `clarify_order_cancellation_01`: **pass**, gold ask_fact/unresolved; Open status fixed. No confirmed execution -> yes; confirmed partial or full execution -> no.
- `clarify_order_cancellation_02`: **pass**, gold ask_target/unresolved; Order A open without confirmed execution -> yes; order B open with confirmed partial execution -> no.
- `clarify_order_cancellation_03`: **pass**, gold resolve_conflict/unresolved; Open order has equal current reports of no execution versus partial execution: yes versus no. No correction is stated.
- `clarify_order_cancellation_04`: **pass**, gold answer/yes; Order open and explicitly neither full nor partial execution confirmed -> yes.
- `clarify_order_cancellation_05`: **pass**, gold answer/no; Confirmed partial execution counts as execution and violates a necessary condition despite open status -> no.
- `clarify_order_cancellation_06`: **pass**, gold answer/yes; Open order with explicitly no confirmed full or partial execution establishes yes; icon color irrelevant.
- `clarify_savings_fee_01`: **pass**, gold ask_fact/unresolved; EUR 70 rate meets amount condition. Fund Mohn or Linde -> yes; Kiesel -> no.
- `clarify_savings_fee_02`: **pass**, gold ask_target/unresolved; Plan A EUR 70 in Mohn -> yes; plan B EUR 70 in Kiesel -> no.
- `clarify_savings_fee_03`: **pass**, gold resolve_conflict/unresolved; EUR 70 rate is fixed. Equal current records of Mohn versus Kiesel yield yes versus no; neither corrects the other.
- `clarify_savings_fee_04`: **pass**, gold answer/yes; Exactly EUR 50 reaches the inclusive minimum and Linde is explicitly listed -> yes.
- `clarify_savings_fee_05`: **pass**, gold answer/no; An explicitly exact EUR 49 rate is below the EUR 50 minimum despite listed fund Mohn -> no. Original wording “über 49 Euro” was ambiguous.
- `clarify_savings_fee_06`: **pass**, gold answer/no; Kiesel is explicitly outside the exhaustive promotional list. Any amount still yields no.
- `clarify_statement_download_01`: **pass**, gold ask_fact/unresolved; Account is open. Statement age 8 months -> yes; age 25 months -> no. Ask age or enough dates to establish age.
- `clarify_statement_download_02`: **pass**, gold ask_target/unresolved; Statement A is 8 months old on an open account -> yes; statement B is 8 months old on a closed account -> no.
- `clarify_statement_download_03`: **pass**, gold resolve_conflict/unresolved; Statement is 10 months old. Open account -> yes; closed account -> no. Equal current records conflict.
- `clarify_statement_download_04`: **pass**, gold answer/yes; Statement age exactly 24 months is within the explicit inclusive limit; account open -> yes.
- `clarify_statement_download_05`: **pass**, gold answer/no; Statement age 25 months exceeds the limit even though account is open -> no.
- `clarify_statement_download_06`: **pass**, gold answer/yes; Open account and 4-month-old statement establish yes; self-assigned filing label is irrelevant.
- `clarify_transfer_recall_01`: **pass**, gold ask_fact/unresolved; Status planned and execution run not started -> yes; status planned and run started -> no.
- `clarify_transfer_recall_02`: **pass**, gold ask_target/unresolved; Transfer A is planned and its run has not started -> yes; transfer B already executed -> no.
- `clarify_transfer_recall_03`: **pass**, gold resolve_conflict/unresolved; With run not started, planned -> yes; executed -> no under the explicit executed-transfer exclusion. Equal current status sources cannot be ordered.
- `clarify_transfer_recall_04`: **pass**, gold answer/yes; Planned status and execution run confirmed not started -> yes.
- `clarify_transfer_recall_05`: **pass**, gold answer/no; Execution run already started violates a necessary condition despite planned status -> no.
- `clarify_transfer_recall_06`: **pass**, gold answer/no; Executed status is confirmed and expressly excluded. Unknown historical run start cannot change no.
- `clarify_travel_delay_01`: **pass**, gold ask_fact/unresolved; Written carrier confirmation exists. Delay 7 hours -> yes; delay 2 hours -> no.
- `clarify_travel_delay_02`: **pass**, gold ask_target/unresolved; Trip A 7 hours late with confirmation -> yes; trip B 2 hours late with confirmation -> no.
- `clarify_travel_delay_03`: **pass**, gold resolve_conflict/unresolved; Confirmation exists. Equal records of 7 versus 2 hours lead to yes versus no; neither is a confirmed correction.
- `clarify_travel_delay_04`: **pass**, gold answer/yes; Exactly 6 hours delay reaches the inclusive minimum and written carrier confirmation exists -> yes.
- `clarify_travel_delay_05`: **pass**, gold answer/no; Written carrier confirmation is explicitly absent despite 8 hours delay -> no; absent is not unknown.
- `clarify_travel_delay_06`: **pass**, gold answer/yes; 9 hours delay and written carrier confirmation suffice for yes. Travel price is explicitly irrelevant.
- `clarify_welcome_bonus_01`: **pass**, gold ask_fact/unresolved; New account is confirmed. EUR 1,100 in-period deposits -> yes; EUR 900 in-period deposits -> no.
- `clarify_welcome_bonus_02`: **pass**, gold ask_target/unresolved; Account A newly opened with EUR 1,100 in-period -> yes; account B established for years with EUR 1,100 -> no.
- `clarify_welcome_bonus_03`: **pass**, gold resolve_conflict/unresolved; New account is confirmed. Equal uncorrected statements of EUR 1,100 versus EUR 900 yield yes versus no.
- `clarify_welcome_bonus_04`: **pass**, gold answer/yes; New account and exactly EUR 1,000 in-period deposits meet both conditions -> yes.
- `clarify_welcome_bonus_05`: **pass**, gold answer/no; Only EUR 800 of EUR 1,200 was paid within the promotional period; EUR 400 afterward is explicitly excluded -> no.
- `clarify_welcome_bonus_06`: **pass**, gold answer/yes; New account and EUR 1,500 in-period deposits establish yes. Singular target is clear without its personal label.

## Supplemental protocol and scoring checks

Read PROTOCOL.md, scripts/score.py and scripts/validate.py after the author requested an additional definition check. The fixed case denominators, clarification-kind distinction, risky-answer definition, field inconsistency test, and use of both selected marginal scores for thresholds 0.80/0.90/0.95 match the protocol. No calibrated or joint-probability interpretation is justified.

Ran scripts/validate.py successfully before freeze. Independently created temporary synthetic scoring fixtures, never reading actual model predictions: perfect gold fixture yielded 72/72 exact; eight deliberately perturbed records yielded 64/72 exact. Expected counts matched: two invalid/missing, two missed required clarifications, three required clarifications not successfully requested, two excess clarifications, one wrong clarification kind, two inconsistent field pairs, and two risky wrong answers. The risky fixture with marginals 0.93/0.89 passed the 0.80 confidence threshold but not 0.90; a 0.95/0.95 fixture passed all three thresholds. Duplicate prediction IDs correctly raised an error. These tests cover selected scoring paths and do not replace the author's complete scorer/runner/preflight freeze.

Final revision verification: exactly seven case records changed from the preserved initial snapshot: the six card-replacement rules and the EUR 49 sentence. Gold, metadata, shared policy and design summary remained byte-identical. The builder changed only those two wording substitutions. The complete requests were rechecked against every current case and shared policy. The author's preserved initial_snapshot matches the reviewer's original file bytes. All 72 final cases now pass the stated review checks.
