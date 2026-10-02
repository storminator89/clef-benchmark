# Pre-inference protocol: clarification versus guessing

72 German synthetic closed-rule cases, purposefully 24 each in banking, insurance and finance. Every domain has four related scenario families with six cases each: missing material fact, ambiguous target, conflicting evidence, complete yes, complete no, and sufficient despite an omission. Thus 36 cases require clarification; 36 are answerable (18 yes / 18 no). Related examples share fictional rules. This is a diagnostic stress test, not a random sample, real customer dataset, human-expert holdout or legal/financial advice test. All text, gold and rationales were AI-authored; a separate AI reviewer checks every case before inference, with visibility of gold.

## Inputs and freeze

Only data/requests.jsonl enters the model. Each request includes a German fictional rule, German scenario and question, the same German two-field schema, and native English option IDs. The official English encoding wrapper is unchanged. No gold, rationale, stratum, family or domain metadata enters the model; scenario IDs are logging IDs and not prompt text. The rule may itself make a short-circuit answer possible: unknown facts are not automatically grounds for abstention. Decisive absent conditions are not unknown conditions.

The author may correct issues identified before inference, retaining review history. Gold, input, options, order, scoring code, runtime sources and this protocol are hashed before model load. Tokenizer-only preflight compares uncapped encoding with the exact 2048 cap for every request; no truncation is allowed. No benchmark inference before freeze. After inference begins, no prompt tuning, gold revision, option reordering, rerun selection or test filtering under this result identity.

## Outputs and primary counts

Two native fields: action (answer / ask_fact / ask_target / resolve_conflict) and determination (yes / no / unresolved). Primary exactness is both fields correct per case, denominator 72. Each field accuracy has denominator 72; combined 144 field decisions are descriptive and not independent observations. Required clarification means any gold action other than answer.

- Missed required clarification: predicted answer among 36 clarification-required cases
- Required clarification not successfully requested: missed above plus technical invalid/missing action, among the same 36
- Excess clarification: predicted ask_fact, ask_target or resolve_conflict among 36 answerable cases
- Wrong clarification kind: clarification requested but wrong category, denominator 36 required cases
- Risky wrong answer: model action answer and determination yes/no, but gold required clarification or opposite determination. Report count/72 and count/substantive model answers
- Confidently wrong answer: risky wrong answer where BOTH selected marginal option probabilities are at least 0.90. Also report fixed 0.80 and 0.95 sensitivity thresholds. These are uncalibrated model scores, not validated certainty or joint probability
- Inconsistency: answer with unresolved, or a clarification action with yes/no

All IDs, both fields, all unrounded option scores, input tokens, encoding/forward/total seconds and RSS are retained. Errors retain full scenario, rule, gold, predicted fields and rationale. Missing or malformed cases score incorrect in primary fixed-denominator metrics, and are separately enumerated as technical failures. Duplicated or unexpected prediction IDs prevent scoring rather than silently choosing a record. No averaging across retries.

## Execution

Cloudflare/clef-flash official revision 17f0b0ad64efb65d273590632833508766b2aae6. Original native joint head and output embeddings BF16; backbone CPU NF4 with double quantization and BF16 compute, six threads, batch 1, cap 2048. Torch 2.11.0+cpu / Transformers 5.10.2 / bitsandbytes 0.50.2. Exact dependencies and model hashes retained. One unrelated technical warmup and a first-case repeatability probe are excluded from quality/latency aggregates. Exclusive model load; no GPU or stock-precision comparison claimed. A memory guard may stop execution to protect the environment; a partial run remains partial and does not support the full result.

## Interpretation and follow-on work

This tests selecting a need/category of clarification and a bounded conclusion, not the quality, empathy or specificity of a generated German question. It does not test fraud handling or actual transactions. Fictional simple conjunctions and overt ambiguity phrases favor clear annotatability; they limit ecological realism. Family members are dependent; domain/stratum cells have only 12 or 24 cases. Scores are exact finite-set counts without population confidence claims; no naive binomial significance tests or pooled comparison with prior suites. A later minimal-change test must be separately frozen; calibration/reliability analysis will use locked results without retuning this suite.
