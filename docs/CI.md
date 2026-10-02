# Lightweight CI

`.github/workflows/check.yml` runs on pushes, pull requests and manual dispatch.
It grants only `contents: read`, does not persist checkout credentials, and has a
10-minute timeout. It uses Python 3.12 and Node 24. There are no Python or npm runtime dependencies, GPU, model download, inference, paid API or publishing steps. The pure DOM regression suite installs the lockfile-pinned development dependency LinkeDOM 0.18.13 with `npm ci --ignore-scripts`; it does not launch a browser.

Checks cover both frozen manifests, artifact provenance, deterministic data
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

The same offline job additionally verifies the clean72, image90, and seven-pair ablation artifacts with `scripts/check_followups.py`; it rebuilds `web/data/clean72.json` byte-for-byte and checks its importer failure modes. Dataset source images and model weights are not fetched. Browser/visual QA remains a separately disclosed unrun check.

## Dokumentverständnis und UI-Redesign

Die Versicherungssuite unter `experiments/insurance` bleibt eigenständig. Der
Versicherungsimporter prüft vor der Rekonstruktion von `web/data/insurance.json`
die vollständige unabhängige Verifikation, alle Quellhashes, 60 Fälle und 120
Antwortfelder sowie die aus Rohoutputs nachgerechneten Resultate. CI rekonstruiert
alle vier Text-UI-Datensätze byte-identisch.

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
