# Protocol: descriptive reliability of recorded Clef option scores

This protocol is locked before new reliability metric computation, after the source benchmark outcomes already existed and were available to the authors. This is **post-hoc descriptive analysis**, not a preregistered, blinded or held-out calibration study. No model inference, calibration fitting, temperature estimation, threshold tuning, label correction or selective retry is performed.

## Source selection and units

Include every completed final suite in the approved scientific collection that retains original requests, gold, native choices and unrounded probabilities and passes scientific hash/provenance verification: minimal pairs, clarification, bank support, original text, finance routing, insurance documents, clean administrative tasks, attack ablation, and images. The inventory records provenance limitations and completeness before score computation. Pilots, warmups, repeatability probes, duplicate exports and unfinished/non-final runs are excluded by role, not score quality. All final records/IDs, raw outputs and source gold remain intact; original validity caveats stay in force. Image rescoring reproduces recorded-output analysis only; it does not re-execute vision, reacquire image pixels or revalidate image labels.

Fields are never pooled. Partition the older multi-task suites by category and input/schema language; partition attack ablation additionally by attack/clean condition. Partition images by task kind, language and image/blank condition. Split any remaining unequal option-key sets. Insurance evidence option slots are case-local candidate clause sets: retain the original candidate descriptions and score the offered slot task, never interpret b1 as a stable semantic class. Insurance decision remains its own field. Do not pool suites, even where option keys match. Related cases, pairs, translated items, document families and image/blank variants are dependent. Counts are observations, not independent sample sizes.

## Validation and denominators

Validate ID uniqueness, complete request/gold correspondence, requested choice schema, gold membership, exact answer/probability field and option keys, completion and nontruncation. Use saved native choice, even for exact ties. It must attain the exact maximum of its unrounded probability vector; no epsilon argmax reordering. Every probability must be a finite number (not a Boolean) in [0,1]; absolute probability-sum deviation must be <= 1e-5. Preserve actual values without renormalization. Cross-check displayed four-decimal probability/confidence values within 5.0001e-5 of their unrounded counterparts; they are never the metric source. Validate all originals, preserving invalid and missing rows with reasons. Report expected, raw, valid, invalid, missing, extra and duplicate denominators explicitly. Uncomputable field metrics are null, not invented zero. Source-record invalidity is distinct from incorrect prediction.

## Locked measures

For each separate field group:
- Native-choice accuracy: correct / valid; report correct / expected as completeness-aware accounting too
- Multiclass Brier: mean of the **sum over all offered classes** of (p_k - 1[k=gold])²; no division by number of classes; theoretical simplex range 0–2. Retained floating-point sum deviations may cause negligible numerical deviations
- NLL: mean -ln(p_gold), in nats. Zero gold probability yields infinite NLL, represented as a null numeric mean plus an explicit infinity flag, zero count and IDs. Never clip. Finite-only mean is supplemental and clearly excludes zeros
- Mean selected score, observed accuracy and signed score-minus-accuracy gap
- Ten fixed equal-width bins [0,.1), [.1,.2), …, [.9,1]. Every bin reports count, correct, mean score, accuracy, signed gap and absolute gap; empty-bin statistics are null
- ECE: sum over bins of (bin count / valid count) × |bin accuracy − bin mean score|. This fixed-bin finite-set summary is sample-size/bin-dependent; it is not a calibration certificate
- Risk/coverage at selected-score thresholds ≥ .50/.70/.80/.90/.95/.99: count, correct, incorrect, selected / expected coverage, selected / valid coverage, risk=incorrect/selected; risk is null if none selected
- Error-ranking AUROC using 1−selected score as the error score. Pairwise ties contribute .5. Null if either correct or incorrect class is absent
- Every incorrect field, not just examples, with ID, complete native probabilities, gold, original request context and case metadata. Fixed-threshold high-score-error ID lists make all cutoffs explicit

Whole-case exactness is reported separately. An optional minimum-selected-field-score gate is explicitly a **score heuristic**, not a joint correctness probability. It uses the same fixed thresholds and all required fields, and is reported only within the same schema/task partitions. No multiplication of marginal probabilities. No confidence intervals, bootstrap intervals or naive IID significance claims.

## Interpretation and runtime

Purposeful samples and chosen challenge items do not estimate population performance. Most labels are AI-authored/AI-reviewed, not human-expert validated; image labels have their separately retained source limitations. Label classes, option counts and language/task mix differ, so raw Brier/NLL/ECE comparisons are not causal model rankings. High-score bins can be tiny; zero observed errors, even at a high threshold, do not establish safety or calibration. CPU NF4 text backbones with original BF16 heads/embeddings differ from unquantized native precision and GPU execution. The image run preserves its original BF16 vision encoder and its own encoding cap. No native/GPU/OCR equivalence is inferred.

## Reproducibility and public scope

The source lock lists only retained public scientific files and their exact SHA-256 digests. Native scientific inputs/outputs are copied byte-for-byte; any normalized analytical rows are additional derived records with original IDs. Source selection and this protocol are hashed before metric computation; implementations, synthetic tests, independent reimplementation and results are audited after computation. Private environment diagnostics omitted. No private omission lineage is recorded. Public release is handled by the designated publisher, not this analysis task.
