# Clarification72: an independent sixth suite

The UI derives `web/data/clarification.json` from the complete reviewed public export in [`experiments/clarification72/`](../experiments/clarification72/README.md). All 72 cases, both native fields and every unrounded probability are preserved. This adds no model run and does not change earlier benchmark outputs.

## Admission and reproducibility

`python scripts/build_clarification_web_data.py` verifies the full public file inventory, the pinned pre-inference freeze, completed-run metadata and the independent report. It reruns the archived independent standard-library checker read-only and compares its exact case records and recomputed metrics. No model library is imported. `python scripts/check_clarification.py` additionally reruns the primary scorer and both sets of scorer self-tests in a temporary copy, validates current live request limits and protects 308 preceding scientific/runtime/UI-data files byte-for-byte plus two explicitly bounded public metadata/inventory redactions.

All frozen scientific sources and native outputs are immutable; presentation labels and derived data are outside them. The public packaging layer uses minimal scope-only provenance and reviewed-manifest copying. `provenance/clarification_baseline.json` records the preceding release, `b084dc17e8e285e0eef20e00af07fae76d371ec2`. Public packaging scope is documented without identifiers or fingerprints of excluded private files. The narrow existing-bank metadata redaction is recorded in `provenance/public_curation_evolution.json`; it does not alter frozen data, results or Git history.

## What the interface shows

- One suite, one denominator: 72 German cases, never pooled with earlier studies
- Original fictional rule, request and target question together; the exact original state and native field schemas remain inspectable
- `action` (next step) and `determination` (yes/no/unresolved), with 65/72 and 66/72 correct respectively; both correct only in 64/72
- All eight failed cases, plus separate filters for seven action errors, six determination errors, four missed required clarifications, two unnecessary clarifications, one wrong clarification type, three inconsistent field pairs and four risky wrong concrete answers; categories can overlap
- Both balanced denominators: 36 required clarifications and 36 answerable cases
- All original probabilities; no calibration, joint-probability or safety claim
- Saved replay only for an unchanged native input and schema; editing them invalidates replay, and no answer is simulated

The three inconsistent pairs are deliberately shown unchanged, including clarification with a concrete determination and answer with `unresolved`. A schema-valid response is not necessarily semantically consistent. `clarification_target` and gold rationales are author annotations, not model-generated German questions or explanations.

## Interpretation

[Report](../experiments/clarification72/REPORT.md) · [Eight errors](../experiments/clarification72/ERRORS.md) · [Protocol](../experiments/clarification72/PROTOCOL.md)

All cases use fictional simple rules, AI-authored references and independent AI review, without human-expert validation. Twelve related families and overt uncertainty cues limit generalization. Zero wrong answers among only five concrete outputs meeting both 0.90 thresholds does not establish reliability. The recorded CPU-NF4 profile is not a GPU or native-precision comparison.

The older six-image README gallery retains its original version and labels. It does not depict this later suite. Exact-commit CI and a new genuine browser capture are required to establish the new UI's integration status.

## Public package inventory

`provenance/package_inventory.json` uses aggregate-only format 2: file count, byte count and a deterministic digest. It replaces the redundant broad per-file public inventory. Both audit self-reports are excluded to avoid recursive hashes; `scripts/audit_public.py --write` reproduces the summary. Per-suite scientific freeze manifests and exact Git tree hashes remain available. This minimizes public metadata without changing scientific evidence.
