# German minimal-change paired results

Independent final audit passed with 48 native predictions and no reported mismatches. All 50 frozen files remain unchanged.

## Primary finite-set results

- Complete two-field case accuracy: 39/48 (81.2%)
- Both members fully correct: 17/24 (70.8%)
- Correct full directional transition on outcome-changing pairs: 8/12 (66.7%)
- Observed output changes on flip pairs, irrespective of correctness: 12/12 (100.0%)
- Unjustified output changes on outcome-invariant pairs: 1/12 (8.3%)
- Stable invariant pairs: 11/12 (91.7%)
- Stable but not fully correct invariant pairs: 2/12 (16.7%)
- Technical invalid/missing cases: 0/48

A changed output alone is not a correct transition: both two-field endpoints must match their respective gold. Stable wrong outputs are separately counted. Pairwise observations are dependent; these are exact counts for this finite authored diagnostic, not population estimates.

## Domain and pair-kind counts

| Group | Both-correct pairs |
|---|---:|
| domain: banking | 7/8 (87.5%) |
| domain: insurance | 5/8 (62.5%) |
| domain: finance | 5/8 (62.5%) |
| kind: flip | 8/12 (66.7%) |
| kind: invariant | 9/12 (75.0%) |
| subtype: yes_to_no | 2/3 (66.7%) |
| subtype: no_to_yes | 3/3 (100.0%) |
| subtype: clarify_to_answer | 1/3 (33.3%) |
| subtype: answer_to_clarify | 2/3 (66.7%) |
| subtype: irrelevant_text | 4/6 (66.7%) |
| subtype: within_region_fact | 3/3 (100.0%) |
| subtype: short_circuit_control | 2/3 (66.7%) |

## Runtime and exclusions

Pinned official 9B Cloudflare/clef-flash revision 17f0b0ad64efb65d273590632833508766b2aae6. CPU NF4 backbone, original BF16 joint head and BF16 output embeddings. Six CPU threads, batch 1, maximum 2048 input tokens. Original native model code and runner unchanged. No GPU or unquantized baseline was run.

- Input tokens: 673–730; cap-versus-uncapped equality verified for every request
- Median forward time: 17.298s; p95: 20.289s
- Total benchmark forward time: 845.854s
- Model load time: 56.357s
- Peak RSS observed in benchmark rows: 5.759 GiB
- Single-case repeatability summary: maximum absolute probability difference 0.0; same native answer: True

The native execution log reported unavailable optional CPU GEMM/attention fast paths and fallback implementations; results/runtime_observations.json preserves these public-essential observations. The unrelated technical warmup and one first-case repeat probe are excluded from quality and benchmark forward-time aggregates. The original runner retains a warmup result and repeatability summary but does not expose the repeat’s separate full probability vector/timing. A single-case probe does not establish general determinism. Marginal native softmax values are not calibrated or joint probabilities.

## Observed failure patterns

- At the explicitly inclusive 48-hour boundary, one endpoint returned answer/unresolved rather than answer/yes.
- Unknown consent was treated as a definite no in one endpoint.
- Identical 25/25 distance records and identical closed/closed window records still triggered clarification actions in two answerable endpoints.
- An irrelevant report-title edit preserved a wrong answer/yes in both variants despite the unresolved target.
- An irrelevant vehicle-color edit preserved the wrong clarification category in both variants of a conflicting-record case.
- An invalid price increment already forced no, but an unknown trading window triggered ask_fact/unresolved; this pair produced the unjustified invariant change.

These describe retained error cases, not general failure-rate estimates. Every endpoint and its unrounded scores are preserved.

## Error pairs

### pair_statement_notification
- Kind: flip / clarify_to_answer
- Changed fact: Zustimmung unbekannt → bestätigt
- A: expected ask_fact / unresolved; predicted answer / no
- B: expected answer / yes; predicted answer / yes

### pair_gadget_theft_notice
- Kind: flip / yes_to_no
- Changed fact: Meldeabstand 48 → 49 Stunden
- A: expected answer / yes; predicted answer / unresolved
- B: expected answer / no; predicted answer / no

### pair_tow_distance_records
- Kind: flip / clarify_to_answer
- Changed fact: Zweite Streckenangabe 12 → 25 Kilometer; erste bleibt 25
- A: expected resolve_conflict / unresolved; predicted resolve_conflict / unresolved
- B: expected answer / no; predicted ask_target / unresolved

### pair_rental_days_conflict
- Kind: invariant / irrelevant_text
- Changed fact: Irrelevante Lackfarbe blau → grün
- A: expected resolve_conflict / unresolved; predicted ask_target / unresolved
- B: expected resolve_conflict / unresolved; predicted ask_target / unresolved

### pair_redemption_window_conflict
- Kind: flip / answer_to_clarify
- Changed fact: Zweite Fensterangabe geschlossen → offen
- A: expected answer / no; predicted resolve_conflict / no
- B: expected resolve_conflict / unresolved; predicted resolve_conflict / unresolved

### pair_report_delivery_target
- Kind: invariant / irrelevant_text
- Changed fact: Irrelevanter Titel von A verändert, Ziel bleibt offen
- A: expected ask_target / unresolved; predicted answer / yes
- B: expected ask_target / unresolved; predicted answer / yes

### pair_limit_order_price_step
- Kind: invariant / short_circuit_control
- Changed fact: Fenster unbekannt → offen, ungültige Preisstufe unverändert
- A: expected answer / no; predicted ask_fact / unresolved
- B: expected answer / no; predicted answer / no


## Scope and caveats

AI-authored and separately AI-reviewed with gold visibility, not human-expert validated. Exact schema and generic rule templates are reused from clarification72; all 24 scenario situations/rule texts are new. All edits, original review snapshots and pre-inference corrections are retained. One tariff-scope wording issue was corrected. Four other pre-run pair refinements reduce direction/outcome confounds; some gold endpoints changed before any model output existed. No outcome-driven correction or rerun selection occurred.

Eight pairs per domain; most subtype×domain cells have only one pair, irrelevant-text cells two. The three short-circuit controls are all no/no by construction. Synthetic explicit rules do not represent actual customer cases, banking rules, insurance coverage or financial advice. This tests bounded native decisions, not generated German answer/question quality. No naive independent-case significance tests or pooling with earlier suite scores.

See PROTOCOL.md, SOURCES.md, results/summary.json, complete native results and independent audit artifacts for reproducible details.

## Audit implementation history

The independent checker first flagged its own option-map ordering and manifest-schema assumptions. It was corrected against the unmodified native source, regression-tested, and rerun; the corrected checks and a concise methodological correction record remain included; redundant development diagnostics are outside the public package. No frozen input, gold, primary scorer or raw prediction was changed. Final audit passed 6,972 comparisons and 60 independent checker self-tests.
