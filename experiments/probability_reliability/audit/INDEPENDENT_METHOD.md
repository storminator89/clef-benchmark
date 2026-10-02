# Independent probability reliability audit

The reference formulas and synthetic tests were implemented before opening real prediction files or the primary metric implementation. This audit does not call a model, alter predictions, fit parameters, calibrate scores, or select thresholds from observed outcomes.

## Formula contract

For each frozen suite and each field separately, retain the saved native choice. Its exact unrounded probability is the confidence. The saved choice must attain the numerical maximum; exact ties preserve the saved choice rather than applying a new tie-breaker.

- Brier: arithmetic mean over items of the **sum** over all classes of `(p - indicator)^2`, with theoretical range 0–2 for a normalized vector. No division by the class count.
- NLL: arithmetic mean of `-log(p_gold)` using natural logarithms. Any zero gold probability makes the full mean infinite. No clipping or substitute finite mean.
- Accuracy: saved choice equals the separate gold, divided by valid count. Invalid and missing cases remain explicit against the full expected denominator; complete-case figures never imply complete evaluation.
- Bins: ten fixed intervals `[0,.1), ... [.9,1]`, implemented by explicit decimal boundary comparisons, with empty-bin statistics undefined.
- ECE: `sum(bin_count * abs(bin_accuracy - bin_mean_confidence)) / valid_count`.
- Selective risk: error proportion among choices at or above each fixed threshold `.50, .70, .80, .90, .95, .99`. Coverage is retained count divided by valid count, with expected-count coverage separately retained when relevant. Zero retained cases give zero coverage and undefined risk.
- Error-detection AUROC: error is the positive class and `1-confidence` its score; all error/correct pairs are counted, with exact score ties receiving 0.5. Undefined without both classes.
- Every wrong choice and its original source representation are preserved; high-score errors are available at the protocol thresholds.

## Validation contract

Options must be nonempty unique strings. Probabilities must be finite nonboolean numbers in `[0,1]`, with absolute deviation of their accurate sum from 1 at most `1e-5`. Values are not renormalized. IDs must be unique and belong to the expected set, with missing IDs explicitly listed. Unknown choices/gold and nonmaximum native choices are invalid. Schema-specific source integrity is audited separately after the lock.

The native-output tolerance was supplied before source inspection. A secondary, rounded display is never a metric source.

## Synthetic coverage

The tests cover every decimal bin boundary plus adjacent representable values, exact-choice ties, multiclass scoring, perfect and maximally wrong Brier values, zero-gold infinite NLL, weighted ECE, all fixed threshold boundaries, missing/invalid/duplicate/unexpected IDs, empty metrics, no-selection undefined risk, no-class undefined AUROC, tied AUROC, tolerance without normalization, and original-output preservation.

Descriptive probability agreement on deliberately constructed tests is not evidence of deployment calibration or calibrated financial advice. No uncertainty band treats correlated fields or families as independent observations.
