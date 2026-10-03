# Native-answer correctness v1

This **new, post-hoc analysis** evaluates whether every native choice field exactly matches the frozen gold answer. The denominator is every planned case in its partition, identically for Clef and Jev. Probability normalization is not an answer-correctness criterion. Original strict scoring, raw records, gold and requests remain unchanged in their original locations.

The 35 retained sum-only native responses independently pass model, exact request/source linkage, answer-field/option structure, finite in-range probabilities, native choice argmax, confidence and usage checks. Their original vectors are untouched; this analysis does not normalize them and makes no calibration claim. 937 strict-valid plus 35 sum-only answers give 972 evaluable Jev answers across 974 planned cases.

Two historical responses have no recoverable evaluable native answer (bank_access_tan_01 and de_finance_advice_escalation_005). They count as not correct in the planned-case metric. Their exact correctness remains null, never a claimed semantic error. Original discarded HTTP bodies cannot be independently rehashed; archived body hashes establish linkage only.

All 14 partitions are separate descriptive results. The eight main groups total 580 planned cases; no pooled performance score is claimed. MASSIVE has no complete Clef baseline: its Clef numerator/rate are null, not zero. A cancelled partial run is not scored or used here.

## Reproduce offline

From repository root, run `python scripts/derive_jev_answer_correctness_v1.py --output /tmp/jev-native-answer-replay` with a new directory. Compare its three JSON/JSONL output files byte-for-byte with this directory. Run `python -m unittest discover -s tests -p 'test_jev_answer_correctness_v1.py' -v`.

`comparison_summary.json` pins every source byte hash and exposes partition counts. `case_comparison.jsonl` exposes native choices, nullable exact correctness and explicit evaluability per case. `restored_native_answers.json` identifies the 35 included sum-only records with untouched vector sums. `SHA256.json` pins this package and the derivation/tests. No inference, provider API or network call is performed.
