# Independent validation method and corrections

The independent standard-library checker reads the original native predictions,
frozen gold, requests and pair definitions. It does not call or import the primary
scorer. All 48 cases, 24 pairs and complete error inventories are checked.

## Initial checker corrections

The initial implementation produced 815 false comparison mismatches from two
checker assumptions. They were corrected before the final successful review:

- Full native probability-map insertion order was incorrectly required to match
  request criterion order. Validation now requires the exact option set, preserves
  the original native map and applies the defined criterion order separately for
  tie handling. No probabilities or choices were changed
- Complete model-manifest objects were incorrectly compared with a narrower
  pre-run checksum record. The corrected check compares filenames, byte lengths
  and SHA-256 values, and separately verifies the pinned upstream revision

All 50 frozen files, native predictions, gold, primary scores and scientific
conclusions remain unchanged. The final scientific audit passed 6,972 comparisons
and 60 independent synthetic checker tests. The reproducible checker, primary
native results, independent summary and complete semantic review of all nine
erroneous cases and seven erroneous pairs remain public.

## Final report review

The prose review added the distinction between 12/12 observed output changes and
8/12 fully correct flip transitions, the inclusive-boundary error pattern and the
recorded optional-kernel/fast-path fallback limitations. Those disclosures remain
in the final report. Public curation changes only packaging and methodological
wording; it does not repair model outputs or remove a scored error.

## Public scope and verification limits

Canonical frozen model, protocol and source pins remain available. Compact final
review evidence replaces redundant development comparisons, duplicate runtime
inventories and operational bookkeeping. No private predecessor identity or
omission hash is part of public provenance.

The release adapter recomputes every native case and pair score from the original
records without model inference. This offline check does not reload model weights
or independently establish hardware execution or a trusted freeze timestamp.
The original recorded-runtime limitations remain in the scientific report.
