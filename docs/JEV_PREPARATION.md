# Jev comparison: frozen preparation

**This is the archived preparation state.** A later [first manual run](../execution/jev/first-run-audit/PUBLIC_AUDIT.md) produced 180 valid cases and one technical failure, leaving 793 unattempted. Its [continuation](JEV_CONTINUATION.md) is separately reviewed. The package contains public/synthetic frozen text requests, archived Clef baselines and offline-tested collection/scoring code. The original 974-case mock exercise validates software only; real observations are separately identified in the linked audit.

## Current scope

- 974 requests across ten separate source suites, with 1,362 native questions; inventory counts only
- Nine archived Clef baselines complete; the MASSIVE300 baseline is pending its owner's final independent audit
- All 90 image requests excluded because Jev has no native image input; no OCR substitution
- Exact task text, options, order and question structure retained; only the model identifier changes for the prepared API payload
- Field/suite/control partitions stay separate. Vendor confidence and selected-option probability use different definitions. CPU forward time and hosted HTTP latency are not directly comparable

## Why it cannot run on publication

The file `workflow/jev-comparison.yml.in` stays inside the experiment directory with a template extension. That original template remains inactive and its placeholder unresolved. The later activation has a separate pinned workflow in `.github/workflows`; ordinary CI still runs only offline tests and integrity checks. See [current execution state](JEV_EXECUTION.md).

Activation requires a separately reviewed workflow commit pinned to this package's immutable code commit, the user entering `JEV_API_KEY` directly in GitHub, and explicit approval of the destination, frozen data scope and bounded API budget. The template's approval flags default to false. Pricing, terms and availability must be rechecked then. The proposed USD 3 local reservation guard is not a provider-enforced account spending limit.

Public preparation retains exact requests, gold and native Clef outputs, with compact scientific provenance. Operational metadata and redundant development inventories are excluded. Final MASSIVE head-to-head scoring needs a separately reviewed baseline update.

[Full protocol, dated cost illustration and activation contract](../experiments/jev_comparison/README.md) · [Native adapter](../experiments/jev_comparison/scripts/jev_runner.py) · [Offline scorer](../experiments/jev_comparison/scripts/compare.py) · [Inactive template](../experiments/jev_comparison/workflow/jev-comparison.yml.in)

## Source-document boundary

`inputs/massive300/SOURCES.md` is preserved documentation from the original MASSIVE study. Its references to the full upstream-source archive, supplementary notices/citations and runtime provenance describe that original study, not files included in this narrow comparison package. This package pins the exact selected requests, gold, label schema and sampling metadata and includes the CC-BY-4.0 license and attribution. It does not bundle the full source or runtime archive.
