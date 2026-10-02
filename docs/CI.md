# Lightweight CI

`.github/workflows/check.yml` runs on pushes, pull requests and manual dispatch.
It grants only `contents: read`, does not persist checkout credentials, and has a
10-minute timeout. It uses Python 3.12 and Node 24. There are no Python or npm runtime dependencies, GPU, model download, inference, paid API or publishing steps. The pure DOM regression suite installs the lockfile-pinned development dependency LinkeDOM 0.18.13 with `npm ci --ignore-scripts`; it does not launch a browser.

Checks cover the suite-specific frozen manifests, artifact provenance, deterministic data
reconstruction, scorer synthetic tests, independent metric recomputation on the
saved complete predictions, HTTP server protections, adapter/importer safety,
byte-identical rebuilding of the static workbench datasets, and Node's built-in
UI logic tests plus LinkeDOM interaction tests. Optional browser tests are not invoked by unittest discovery;
see [VALIDATION.md](VALIDATION.md) for the separately disclosed visual-QA status.
Passing CI verifies code/data consistency, not fresh model inference or deployment
fitness. The CI Python/Node versions are testing infrastructure; the exact
recorded model environment remains in `runtime/requirements_frozen.txt` and run
metadata.

## Verified action pins

The following official release and commit links were inspected when assembling
this package on 2026-10-02. Full commit SHAs are pinned in the workflow; no moving
action tags are executed.

- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1):
  [3d3c42e5aac5ba805825da76410c181273ba90b1](https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1)
- [actions/setup-python v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0):
  [5fda3b95a4ea91299a34e894583c3862153e4b97](https://github.com/actions/setup-python/commit/5fda3b95a4ea91299a34e894583c3862153e4b97)
- [actions/setup-node v7.0.0](https://github.com/actions/setup-node/releases/tag/v7.0.0):
  [820762786026740c76f36085b0efc47a31fe5020](https://github.com/actions/setup-node/commit/820762786026740c76f36085b0efc47a31fe5020)

The action manifests at these commits use the Node 24 action runtime. The job
uses a GitHub-hosted Ubuntu 24.04 runner. No repository secrets need to be added.

## Follow-up coverage

The same offline job additionally verifies the clean72, image90, and seven-pair ablation artifacts with `scripts/check_followups.py`; it rebuilds `web/data/clean72.json` byte-for-byte and checks its importer failure modes. Dataset source images and model weights are not fetched. Browser/visual QA is separately source-versioned; see [BROWSER_GALLERY.md](BROWSER_GALLERY.md) for actual captures.

## Dokumentverständnis und UI-Redesign

Die Versicherungssuite unter `experiments/insurance` bleibt eigenständig. Der
Versicherungsimporter prüft vor der Rekonstruktion von `web/data/insurance.json`
die vollständige unabhängige Verifikation, alle Quellhashes, 60 Fälle und 120
Antwortfelder sowie die aus Rohoutputs nachgerechneten Resultate. CI rekonstruiert
alle sechs Text-UI-Datensätze byte-identisch.

`provenance/followup_baseline.json` bleibt unverändert. Die absichtlich erweiterten
Dateien `server.py`, `runtime/live_adapter.py` und `tests/test_device_profiles.py`
werden ausschließlich mit ihren genauen Vorher-/Nachher-Hashes aus
`provenance/workbench_evolution.json` zugelassen. Die Liste erlaubter Änderungen
ist im Prüfer eng begrenzt; Originalrunner, Vendor-Code und Messdaten dürfen nicht
über diesen Mechanismus ausgenommen werden. Fünf Tests prüfen diese Grenze.

Die DOM-Tests prüfen die App mit tatsächlich erzeugten DOM-Knoten, Eventhandlern
und ausdrücklich testinternen Request-/Fehlerfixtures. Es wird dabei weder eine
Modellantwort erzeugt noch ein Browser gestartet. Die optionale Browserabnahme
ist davon klar getrennt. `audit_public.py` wird nur auf einen bereinigten
Veröffentlichungsbaum ohne installierte Entwicklungsabhängigkeiten angewendet.

## Bank-Kundensupport

`check_bank_support.py` prüft die abgeschlossene eigenständige Bank-Suite,
Export-/Freeze-/QA-Hashes, beide erneut ausgeführten Scorer, exakte Fall-/Feld- und
Safety-Metriken und alle 80 nativen Requests gegen die vorhandenen Live-Grenzen.
209 vorbestehende Daten-/Runtime-Artefakte bleiben byte-identisch geschützt; drei explizite Runtime-Erweiterungen sind separat hashgebunden.
Der damalige CI-Stand baute sechs UI-Datensätze deterministisch neu. Es wird kein Modell
geladen und keine Aussage über Browserdarstellung oder AMD-Ausführung abgeleitet.

## Clarification72 integration

The clarification integration workflow executed four integrity gates and rebuilds all six completed-result datasets byte-identically. The recorded local regression count is 266 Python and 111 JavaScript/DOM tests. `check_clarification.py` additionally checks both scorers, balanced denominators, all native vectors and exact public-curation evolution. The genuine sandboxed Chrome run is linked in the README and records its own source hash; it does not run a model. Public inventory format 2 exposes aggregate integrity only and excludes its two self-reports deterministically.


## Paired and reliability release

This release adds `scripts/check_paired_reliability.py`, covering exact curated
minimal-pair and probability-analysis exports, preservation of preceding scientific
artifacts, independent result recomputation, synthetic scorer checks, and deterministic
`web/data/minimal_pairs.json` / `web/data/reliability.json` rebuilds. These are separate
diagnostic views, not additional pooled suite metrics. Browser capture retains the
installed Chrome channel, active sandbox, results-only server, ten-MiB artifact budget
and one-day retention. Historical galleries remain bound to their source hashes.

The historical pair/reliability release passed **289 Python tests, 142 JavaScript/DOM tests, five
integrity gates and eight byte-identical UI dataset rebuilds**. The public exports
are exact allowlists: 81 paired files and 119 reliability files, preserving all
50 paired frozen files, 73 reliability locks and 388 prior scientific artifacts.
Redundant development diagnostics are outside the public package; compact checker
correction history, native results, all errors and independent recomputation remain.

The [genuine Chrome capture](https://github.com/storminator89/clef-benchmark/actions/runs/37041382266)
passed 12 browser check groups and produced 30 source/hash-verified PNGs at
`a21344f8c1d3ebc848a753c88f90ae257c36608d`. Its tests include every reliability
field group, empty selection, dependent error context and narrow-table keyboard
access. Browser evidence is source-versioned separately from final documentation CI.

## Multi-document and inactive comparison integration

The additional `check_multidoc.py` gate independently rescores all 48 archived native predictions and verifies its scientific freeze. A ninth deterministic UI rebuild adds the source/determination suite. The existing reliability analysis stays unchanged and does not silently absorb this new dataset.

`check_jev.py` verifies the exact curated preparation allowlist, links retained request and native Clef baseline bytes to the source suites, checks the pending MASSIVE baseline and proves the workflow template remains inactive. CI runs its 23 offline mock tests separately. No secret, API execution or activation step is installed.

The UI copy cleanup uses compact labels, consistent icons and progressive disclosure. Important error, privacy, pending-run and finite-set caveats remain at their relevant controls. Genuine browser checks and visual evidence remain bound to their exact captured source commit.

The exact UI-source commit `4289d761f1ab866ec29ffee6de5f6021a342558e` passed [CI 37048924340](https://github.com/storminator89/clef-benchmark/actions/runs/37048924340): **310 root Python tests, 156 JS/DOM tests, 23 separate Jev mock tests, seven integrity gates and nine identical UI rebuilds**. [Chrome capture 37048924234](https://github.com/storminator89/clef-benchmark/actions/runs/37048924234) passed all 14 browser groups with 34 hash-verified PNGs. The README retains a bounded five-image selection; no model, key or paid API was used. Later gallery-only documentation changes do not alter that captured source.
