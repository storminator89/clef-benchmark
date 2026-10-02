# Clef probability reliability

Post-hoc descriptive reanalysis of nine frozen completed suites. No inference, tuning, fitted calibration or changed labels.

- [Deutscher Ergebnisbericht](REPORT_DE.md)
- [Locked protocol](PROTOCOL.md) and [source lock](SOURCE_LOCK.json)
- [Every field / bin / threshold](FIELD_DETAILS.md)
- [Separate whole-case score heuristics](CASE_HEURISTICS.md)
- [Every error](ERRORS.md)
- Exact native inputs/outputs in sources/; machine-readable derived results in results/
- Independent implementation, fixtures and full artifact review in audit/

Run python scripts/verify_artifact.py and follow REPORT_DE.md for no-model reproduction. Weights and original source images are not bundled. Source predictions are unchanged; labels, purposeful sampling, cluster dependence and CPU-NF4 limitations remain material.

## Compact public verification

All 73 locked source/protocol/inventory files, native records and derived metrics
are unchanged. Independent formula code, synthetic tests and structured review
results remain included. Redundant console transcripts and duplicate reference
inventories are outside the public package. Public provenance records scope only.
