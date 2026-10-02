# Independent pre-inference review of synthetic bank-support classification

Status: APPROVED FOR FREEZE after full revised-set re-audit: 80/80 cases and 240/240 labels agree. All nine requested amendments are implemented; no blocking issue remains. No model predictions, scores, logits, calibration outputs or inference results were inspected. This review concerns only fictional workflow classification and next-step routing. It authorizes no banking action.

## Method and provenance

An independent AI reviewer manually read all 80 messages, the complete fictional policy, the three gold labels for every message, the request packaging, and the construction script. It assigned intent, priority and next-step labels from the policy and checked them against the supplied gold. This is a separate-reviewer, pre-inference audit, not a blinded annotation experiment and not a human bank-domain validation: gold and construction rationales were visible. The reviewer is not independent of the general language-model technology used in constructing the test.

The compact manual judgments and case-specific explanations are in `write_independent_review.py`. Those manual assignments do not derive their labels from the gold. A separate comparison checks agreement. `pre_inference_review_initial.jsonl` preserves every original judgment. `initial_snapshot/` preserves the exact first-reviewed inputs, including policy and construction code; `pre_inference_initial_summary.json` records their hashes. The canonical `pre_inference_review.jsonl` contains the final revised judgments, with resolved initial flags retained separately.

The initial audit agreed on 78/80 complete cases and 238/240 labels. Both disagreements concerned intent, not priority or safety handoff:

- `bank_ambiguous_multi_04`: the original policy gave security-topic precedence but no precedence to a lost unblocked card over another open route. Literal application implied `unclear`, while gold selected `cards`. Priority `critical` and `security_handoff` were already unambiguous.
- `bank_access_tan_05`: “Online geht bei mir nichts” did not uniquely identify access/TAN, as opposed to online payment or another internet-facing service. The most defensible strict reading was `unclear/routine/clarify`.

## Exact requested amendments and dispositions

1. Add explicit intent precedence for an acute unblocked lost card while retaining the `cards` label. This resolves the first disagreement without changing any gold.
2. Replace the access case with “Mit meinem Online-Banking-Zugang geht nichts. Mehr kann ich gerade nicht sagen.” This resolves the second disagreement while retaining missing-symptom clarification.
3. State that payment-specific/cash-specific receipts remain with their transaction route; general account statements remain `account_documents`. This makes `bank_transfers_08` and `bank_cash_07` unique despite the broad word “Dokumente”.
4. State that a necessary blocked cash withdrawal with no alternative, needed for payment due today/tomorrow, satisfies `urgent`. This removes an interpretive gap in `bank_cash_08`.
5. State that explicitly undecided target transactions or required dates/periods, and technical complaints with no described symptom, need `clarify`; other execution details and identification may be gathered by the specialist once the case and request are sufficiently specified. This avoids an unstated standard for how much case-identifying detail is enough for review.
6. In `bank_transfers_02`, add explicit sent status (“und abgesendet”). Approval alone can precede a failed send; urgency requires an already sent own erroneous transfer.
7. In `bank_fees_05`, use “Bankgebühr” rather than unspecified “Gebühr”. A merchant charge belongs to a different route.
8. In `bank_cards_08`, ask which of the two cards, for example using its app description, not only its card type. Two cards may be of the same type. This change improves the clarification target rather than changing the three labels.
9. Distinguish mere uncertainty about a booking's type or own initiation from an expressed fraud suspicion in the intent policy. This makes `bank_ambiguous_multi_01`'s `unclear` classification explicit. The priority policy separately requires express denial of authorization for that critical trigger. This is a test convention, not a general recommendation to delay security help in live banking.

The original supplied gold was not changed in response to model behavior. All requested amendments arise from the pre-inference policy audit.

## Policy consistency and label exclusivity

The route names are not naturally disjoint: a card can appear in a cash-withdrawal or fraud message; a transaction can also have a receipt; an app can be mentioned while discussing a transfer. Exclusivity therefore comes from the ordered selection policy, not keyword uniqueness. The revised policy explicitly settles these overlaps for this set. Security overrides routine ordering; an acute unblocked lost card keeps its card route and overrides ordinary service; otherwise explicit customer ordering wins, and equally ranked distinct routes are `unclear`.

Priority is global to the entire message and independent of the chosen intent. `critical` wins; otherwise defined `urgent` triggers apply; otherwise `routine`. A contained historical event without new suspicious activity is not critical. Receiving a suspicious SMS alone without interaction is not critical; possible disclosure or unexpected live approval is critical. Emotional emphasis by itself does not change priority.

Next-step selection is ordered: `security_handoff` for every critical case, then necessary clarification, then concrete review, then general guidance. This supports exactly one answer per question while preserving the important distinction between a missing ordinary detail and a reason to postpone a security handoff.

`bank_ambiguous_multi_07` is a deliberately constructed policy edge case: the customer gives two routes equal importance despite a blocked rent payment due tomorrow. `unclear/urgent/clarify` follows the fictional policy, which separates global urgency from route selection. It should be reported as designed edge coverage, not evidence that live banks ought to ask a route-preference question before helping with a rent deadline.

## Dataset and request checks

The validation checks all 80 cases, not a sample:

- 80 distinct IDs and 80 distinct message strings; all IDs and ordering match across cases, gold, metadata and requests
- Exactly three valid gold labels per case
- Canonical request state contains only the synthetic customer message; questions reproduce the public fictional policy
- Gold labels, construction rationales, style labels, topic metadata and clarification targets are absent from the request's `state` and `questions`
- Every critical case is a security handoff; no other case is a security handoff
- Clarification answerability metadata matches clarification gold labels
- Gold and metadata mirrors agree with the case records

The outer JSONL row ID contains its construction topic. It must remain a transport identifier only and must not be added to model-visible message text. The request's inner body is the inference input; do not send the gold/cases files to the model.

## Coverage, realism and limitations

There are ten construction groups of eight messages: cards, single transfers, standing orders, direct debits, access/TAN, bank fees, security, cash/ATMs, account/documents, and ambiguity/multiple concerns. Construction group is not always the expected route. The intended gold-route distribution is cards 9, transfers 8, standing orders 8, direct debits 7, access/TAN 9, fees 8, security 10, cash 8, account/documents 9, unclear 4.

Priorities are 64 routine, 6 urgent and 10 critical. Next steps are 31 guidance, 25 specialist review, 14 clarification and 10 security handoff. There are 40 plain, 8 colloquial/typo, 15 negation/context, 12 uncertainty and 5 multi-intent examples. This purposeful small sample is unsuitable for prevalence estimates. A routine-only predictor is already 80% accurate on priority; report baselines, per-class recall and a confusion matrix alongside accuracy.

The content depicts plausible everyday support needs and contains no prompt injection, system-role attack, jailbreak, actual login request, intentional instruction-hierarchy trap or malicious benchmark directive. However, many messages explicitly negate irrelevant dangers or say “only general information”, “my only account” and “no due date today or tomorrow”. These phrasings improve label determinacy and help test negation, but are cleaner and more policy-aligned than typical raw customer tickets. The finite test therefore measures controlled instruction-following and triage distinctions, not end-to-end production readiness.

No actual names, addresses, IBANs, card numbers, telephone numbers, passwords, PINs, TAN values, account identifiers, balances or other private customer records occur. Generic references to a rent payment, mobile provider, fitness studio or banking device are fabricated scenario context. No specific bank product capability, legal period, refund entitlement, fee amount, credit decision or legal promise is asserted. Requested changes and complaints are only classified; the task explicitly forbids executing them. No external bank source was used to override the fictional policy.

Safety-sensitive coverage includes lost unblocked card/device, disclosed or possibly disclosed credentials, expressly unauthorized card/direct-debit/transfer activity, unexpected TAN approval and an ongoing fraudulent call. Counterexamples include confirmed containment, resolved suspicion, retained devices/cards and untouched suspicious messages. Missing coverage includes a merely requested/unconfirmed block, new suspicious activity after prior containment, a confirmed sent duplicate transfer, and a contained incident competing with another live route. Add these in a separately versioned future set, not after observing performance on this one.

The small number of urgent/critical examples means even perfect recall is weak evidence about rare-event safety. Report exact denominators and uncertainty. Do not make deployment, regulatory, customer-protection or financial-advice claims from these synthetic classifications. No banking professional or real-ticket annotator participated in this audit.

## Freeze requirements

Freeze applies to exact content hashes only. Before inference, resolve the amendments, revalidate all 80 request/policy/gold records, update each adjudication, and record SHA-256 hashes for cases, requests, gold, metadata, policy and the construction script. Any later edit requires a new version and renewed audit. Never change gold after looking at model outcomes and describe that as a pre-inference correction.


## Final approval and frozen hashes

The full revised set was rechecked after all nine amendments and before model inference. No gold label changed; only policy/message clarity and one suggested clarification question changed. All five generated data files reproduce byte-for-byte from the construction script in an isolated temporary directory. `freeze_approval.json` is the machine-readable approval and hash record.

- `data/cases.jsonl`: `f65f179d11c5ead7a770f271d694aa8065ab5859893db400a4dfbea8ee3ed29b`
- `data/gold.jsonl`: `cf93ec9032c3e8bbf5f14f88122cb7531f1c0a07268c5035e66f8532e06ea83f`
- `data/requests.jsonl`: `a4ee04381c9d98e7d0365d487fadbe54a6f8c0e3dd751c1a08ebab14c0919562`
- `data/policy.json`: `2c13a461c9a5393174c2c37638c7a7fc12551de4923b0069f556be33cb9641b3`
- `data/metadata.jsonl`: `ad5771986f85c1764fa8eeab70aed121f48c347d48ad9422415df59ec46cf478`
- `scripts/build_dataset.py`: `fb6d4d3aca03c24dd47a0f5bb1fbfd14e1a982171a3fe3189dc3206b95b8c111`
- `audit/pre_inference_review.jsonl`: `a7f306e184b91588cf99b7cabc92fa17799cad4e0adc84706068f74f2a3424d4`
