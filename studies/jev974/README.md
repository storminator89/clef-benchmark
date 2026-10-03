# Jev 974: completed benchmark evidence

974 cases attempted, 937 strict-valid responses, 37 technical exclusions, zero missing cases and zero retries. Technical exclusions remain in all-expected denominators; they are not repaired or renormalized. Results are descriptive and separated into 14 partitions. The frozen MASSIVE300 Clef baseline is pending; this bundle makes no paired claim for that suite.

- `run/`: six original collector files, byte-preserved.
- `scoring/`: five original frozen scorer outputs, independently reproduced byte-for-byte.
- `audit.json`: independent audit, reproduced byte-for-byte.
- `verification.json`: public provenance and partition summary (private Library identifier omitted).
- `strict-failures.json`: exact technical-exclusion case inventory.
- `cost-accounting.json`: corrected derived accounting; raw summaries remain unchanged.
- `PUBLIC_MANIFEST.json`: explicit publication allowlist, hashes and provenance.

Known reported input usage costs USD 0.043850352 (about 4.385 US cents): USD 0.04199832 for 937 strict-valid cases plus USD 0.001852032 for 35 quarantined cases. Two historical cases remain unpriced. These are usage-derived estimates, not a provider invoice. The original USD 2.680946688 capacity reservation is a conservative local guard, not a charge.

Hosted HTTP latency and Clef CPU forward-only latency are not directly comparable. Jev service version is jev-1.13.0; no immutable public weight checksum is available. Raw HTTP-body hashes provide linkage only; discarded response bodies cannot be independently rehashed.

## Offline replay from repository root

Use a fresh output directory:

```sh
python scripts/audit_jev_final_continuation.py --run studies/jev974/run
python experiments/jev_comparison/scripts/compare.py --run studies/jev974/run --output /tmp/jev974-replay
 diff -r studies/jev974/scoring /tmp/jev974-replay
```

These commands use the repository's frozen comparison snapshot and do not call the provider. Do not write replay outputs into the immutable collector input directory.

Source run: https://github.com/storminator89/clef-benchmark/actions/runs/37103896962
