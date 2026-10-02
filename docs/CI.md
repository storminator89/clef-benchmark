# Lightweight CI

`.github/workflows/check.yml` runs on pushes, pull requests and manual dispatch.
It grants only `contents: read`, does not persist checkout credentials, and has a
10-minute timeout. It uses Python 3.12 and Node 24, with no pip/npm project
dependencies, GPU, model download, inference, paid API or publishing step.

Checks cover both frozen manifests, artifact provenance, deterministic data
reconstruction, scorer synthetic tests, independent metric recomputation on the
saved complete predictions, HTTP server protections, adapter/importer safety,
byte-identical rebuilding of the static workbench datasets, and Node's built-in
UI logic tests. Optional browser tests are not invoked by unittest discovery;
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
