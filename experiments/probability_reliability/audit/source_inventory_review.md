# Probability source inventory review

Read-only review of retained public scientific sources. No inference or new reliability metrics were computed. Inclusion is based on completeness and provenance, not performance.

## Overall finding

All six final suites pass ID, schema, gold, native-vector, rounding-consistency, request-hash, and completion checks. They support separate descriptive probability rescoring with the limitations below. Unrounded fields retain native float32-softmax outputs before display rounding; they are not claims of calibrated correctness.

Use probabilities_unrounded[field][option_id]. Match request, prediction and gold by exact id. Use each request’s criteria keys; never infer class order from a JSON object or reuse a vocabulary across unrelated tasks. The JSON companion contains exact retained-file hashes, option vocabularies and every structural check.

## original_text180

180 requests; 180 field observations; structural checks PASS.

Source locations:
- requests: sources/original_text180/requests.jsonl
- predictions: sources/original_text180/predictions.jsonl
- gold: sources/original_text180/gold.jsonl
- cases: sources/original_text180/cases.jsonl, sources/original_text180/diagnostic_cases.jsonl
- metadata: sources/original_text180/runtime_metadata.json

Fields: decision (180).

Freeze: 11 retained entries match; 0 documented portable code changes; 0 raw image files intentionally absent.

- Case records are split across cases.jsonl (150) and diagnostic_cases.jsonl (30); requests and gold contain all 180. Join on id, never row position.
- 120 German primary cases, 30 English controls, and 30 German-input/English-schema diagnostic requests. The 180 outputs are not 180 independent scenarios; preserve paired controls and the 120 source-scenario structure.
- Synthetic, AI-reviewed labels; no human-expert adjudication. Six category-specific option vocabularies; decision does not denote one common classification target.
- Original scoring has frozen and robust versions. Rescore retained native vectors against frozen gold; do not source probabilities from score or UI derivatives.

## finance100

100 requests; 100 field observations; structural checks PASS.

Source locations:
- requests: sources/finance100/requests.jsonl
- predictions: sources/finance100/predictions.jsonl
- gold: sources/finance100/gold.jsonl
- cases: sources/finance100/cases.jsonl
- metadata: sources/finance100/runtime_metadata.json

Fields: decision (100).

Freeze: 13 retained entries match; 0 documented portable code changes; 0 raw image files intentionally absent.

- 80 German primary cases and 20 deliberately selected English controls; preserve the paired 80-scenario structure and category-specific 5-option vocabularies.
- Frozen before this extension inference; review was aware of prior general benchmark results but did not consult finance outputs. Synthetic rules and AI review, not legal/financial validation.
- Keep separate from the original benchmark and later suites; no cross-suite pooled quality claim.

## insurance60

60 requests; 120 field observations; structural checks PASS.

Source locations:
- requests: sources/insurance60/requests.jsonl
- predictions: sources/insurance60/predictions.jsonl
- gold: sources/insurance60/benchmark.json
- cases: sources/insurance60/benchmark.json
- metadata: sources/insurance60/runtime_metadata.json

Fields: decision (60), evidence (60).

Freeze: 20 retained entries match; 0 documented portable code changes; 0 raw image files intentionally absent.

- Gold is cases[*].expected in benchmark/benchmark.json. Only decision and evidence are model fields; evidence_clauses is supporting annotation, not a third predicted field.
- All cases share decision options ja, nein, offen, konflikt, in varying request order. Evidence b1–b5 means a different offered clause set for each case; use each request and its case.evidence_options.
- 60 cases are clustered into 12 synthetic document packages with 5 cases each; 120 field observations are neither independent cases nor free evidence generation.
- The earlier public export also contains byte-identical aliases of benchmark inputs and predictions. The analysis retains one canonical copy only.

## clean72

72 requests; 72 field observations; structural checks PASS.

Source locations:
- requests: sources/clean72/requests.jsonl
- predictions: sources/clean72/predictions.jsonl
- gold: sources/clean72/gold.jsonl
- cases: sources/clean72/cases.jsonl
- metadata: sources/clean72/runtime_metadata.json

Fields: decision (72).

Freeze: 16 retained entries match; 0 documented portable code changes; 0 raw image files intentionally absent.

- 72 new German synthetic cases, six categories of 12, one decision field each; no English or image controls.
- 50 information-sufficient and 22 missing-or-unresolved cases are source design labels, not outcome-selected cohorts.
- Public freeze verifies public copies. Earlier-to-public code/document portability changes are documented; scientific cases, requests, order, and gold remain unchanged. No private predecessor hash lineage is reproduced here.
- Independent AI review before this suite inference; not human adjudication or representative production validation.

## attack_ablation14

14 requests; 14 field observations; structural checks PASS.

Source locations:
- requests: sources/attack_ablation14/requests.jsonl
- predictions: sources/attack_ablation14/predictions.jsonl
- gold: sources/attack_ablation14/gold.jsonl
- cases: sources/attack_ablation14/cases.jsonl
- metadata: sources/attack_ablation14/runtime_metadata.json

Fields: decision (14).

Freeze: 13 retained entries match; 0 documented portable code changes; 0 raw image files intentionally absent.

- Post-hoc diagnostic designed after original finance outputs, frozen before its own inference. Includes all seven German finance cases tagged prompt_injection, not an accuracy-selected subset within that stratum.
- 14 requests are seven attack/clean pairs tied by source_id and pairs.jsonl; these source scenarios overlap finance100 and are not a new independent 14-case benchmark.
- Clean condition removes the exact appended injection and wrapper only. It also changes length and lexical content; avoid population-level causal or safety claims.
- Public freeze verifies public copies; earlier-to-public portability changes do not alter cases, requests, gold, numeric annotations or scoring formulas. No private predecessor hash lineage is reproduced here.

## images90

90 requests; 220 field observations; structural checks PASS.

Source locations:
- requests: sources/images90/requests.jsonl
- predictions: sources/images90/predictions.jsonl
- gold: sources/images90/gold.jsonl
- cases: sources/images90/cases.jsonl
- metadata: sources/images90/runtime_metadata.json

Fields: chart_type (50), legend_count (50), document_type (40), tax_note (40), gross_band (40).

Freeze: 17 retained entries match; 4 documented portable code changes; 50 raw image files intentionally absent.

- 50 German image requests are primary (30 charts, 20 invoices; 120 fields); 20 English-image and 20 German-blank controls add 100 fields. Total: 90 requests and 220 field observations.
- All 90 are genuine recorded vision-path executions, including blank controls: pixel tensors, image grid, and exactly one BF16 vision hook per request are retained. This is archival evidence, not a rerun.
- Source case_id links 50 source images to language/blank controls. Blank gold deliberately remains the original source-image label; blank scores describe forced-choice image dependence, not an answerable image task or calibrated abstention.
- Chart labels are English in-image; German questions do not make the chart source German. Invoices are synthetic German examples and have no official test split.
- Frozen chart_type options bar_line and vbar2 have overlapping descriptions (bars plus line versus vertical bars with two y-axes). Interpret strict source-label probability scores with this documented ambiguity; do not relabel or remove cases post hoc.
- Tax-note gold follows the explicit footnote even where synthetic line-item tax rates conflict. Gross-band gold uses the signed printed total. Neither is a legal validity determination.
- 50 raw images and full source labels are intentionally omitted from the public result package. They are unnecessary for probability rescoring; no acquisition or fresh pixel re-audit was performed.
- The four frozen image code mismatches are documented portable adaptations and match published export hashes. Retained cases, requests, gold and predictions match their scientific hashes. Full original pixel-hash verification cannot be repeated from this package.

## Image engineering pilots

Exclude all three pilot attempts from reliability metrics. The initial attempt has metadata only. The completed low-resolution pilot retains one request/one field, and the completed high-resolution pilot retains two requests/four fields; both preserve native probabilities and vision evidence, but neither has dedicated benchmark gold. They are engineering records, not extra benchmark observations. Also exclude metadata warmups and repeatability probes.

## Provenance and interpretation boundaries

Scientific input/output hashes match SOURCE_INVENTORY.json and the byte-identical public-source copies in this analysis package. Original and finance freezes match every listed file. Insurance, clean72 and attack14 public freezes also match every listed file. Image cases, requests and gold match the original scientific freeze; four portable code adaptations match their separately published export hashes. Original pixels are not bundled, so this review confirms retained records and historical vision evidence without claiming a fresh visual re-audit.

Only relative paths and hashes of retained public scientific files are listed. No private predecessor execution paths, hosts, process IDs or private hash lineage are included. Sources were not edited or published.
