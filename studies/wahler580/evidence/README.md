# Reproduce the German three-model comparison

This evidence bundle contains the exact frozen 580-case input plan, original gold labels, native selections and complete unrounded probability tables for Clef, Jev and Wähler, plus original Wähler HTTP request/response bodies. Missing Jev responses remain explicit. No vector is normalized or repaired.

Run `python3 recompute.py --evidence .` from this directory. Python standard library only; no model, network, account or ML installation. It checks file digests and independently recomputes all-fields-correct counts, missing counts and sum-only diagnostics for each planned group. It does not pool groups. The two missing Jev cases remain in their planned denominators.

`original-benchmark.py` is the unchanged original scorer/collector source for provenance, not this portable entry point. The new `recompute.py` is a separately reviewed offline replay adapter. `provenance.json` binds both sources, frozen inputs, final scores, model/runtime/calibration/configuration and the complete audited source archive. Detailed operational records are not copied into this public projection.

All probability option tables are included. JSON numeric reserialization preserves the original numeric values without decimal rounding; the Wähler raw response bytes are also retained as base64 with their SHA-256. Clef uses its stored `probabilities_unrounded`. Jev uses its native option table and checks any separately stored unrounded table agrees. Gold and inputs are never sent to a model by the replay script.

These are score-reproduction materials, not a promise of bit-identical fresh inference. Clef's CPU-NF4/BF16-head profile, Wähler's Q8/native-calibration profile and Jev's hosted service differ. Jev does not expose immutable weight or serving-hardware identity. The small synthetic and related cases do not establish a general model ranking.
