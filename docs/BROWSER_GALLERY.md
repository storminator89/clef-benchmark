# Genuine browser regression and README gallery

## Current evidence boundary

This workflow is prepared for an ordinary, permitted development machine or
GitHub-hosted runner. It has **not been successfully browser-executed in the
creation environment**. Chromium's process socket was denied there, and the
cloud browser refused loopback browsing. Those restrictions are not bypassed.
No screenshot files or placeholder image links are included merely because this
script exists. Offline tests do not establish CSS layout or visual quality.

`tests/test_browser.py` creates PNGs only with actual Chromium `page.screenshot`
calls. It renders the real local application, the five checked-in public
synthetic datasets and the bundled synthetic support example. It never replaces
responses, changes rendered content for a picture, injects scores, or uses a
model-response fixture. Existing benchmark results retain their recorded
provenance. The private editor is captured **before any inference**.

## Run locally, only where permitted

Python 3.12 and the optional pinned Playwright **1.62.0** dependency are used.
The application still has no browser/ML/npm runtime dependency. Install the
optional tools only with the machine owner's authorization:

```sh
python3 -m venv .venvs/browser-gallery
.venvs/browser-gallery/bin/python -m pip install -r tests/requirements-browser.txt
.venvs/browser-gallery/bin/python -m playwright install chromium
.venvs/browser-gallery/bin/python tests/test_browser.py --start-server \
  --output test-results/browser-gallery
```

Windows: use `.venvs\browser-gallery\Scripts\python.exe` for the same Python commands.
The script binds the existing application server to `127.0.0.1:8765` with
inference explicitly disabled. It stops only its own server. If this port is
already occupied, stop the other server yourself or omit `--start-server` only
when the existing server is the same checkout in results-only mode. The script
checks every served web-source/data hash before capture and refuses a
live-enabled or model-loaded backend.

A new or empty output directory is required. To retain a previous run, choose
another path under `test-results/`; do not mix files across runs.

The browser is the Chromium build installed by the pinned Playwright package.
`chromium_sandbox=True` is mandatory. There is no `CHROMIUM_PATH` fallback,
custom security-disabling flag, alternate host, remote browser, tunnel, security
setting change, or automatic retry after a launch denial. If sandbox support or
an OS library is missing, report the exact failure and prepare a normally
supported environment separately. Do not relax a security setting to make the
capture green.

## Standard GitHub Actions route

The separate `browser-gallery.yml` workflow runs on manual `workflow_dispatch`
or a push to `main` that changes UI/capture sources, their example/requirements,
`server.py`, or the gallery workflow itself. README/PNG-only commits do not trigger
another capture. It has `contents: read`, a 20-minute bound, no secrets, no
persisted checkout credentials, no pull-request trigger and no commit/publication step. Its Ubuntu 24.04 runner
installs the browser package/build, runs the existing integrity and Python/DOM
gates, rebuilds all five datasets, then starts the results-only server and
captures the UI. It performs no model download or inference. Browser dependencies
must already be supported by the normal hosted runner; the workflow does not
change kernel, AppArmor, sandbox, network or privilege settings.

When the workflow is present on the repository's default branch and publication
has been authorized separately, a repository maintainer can open Actions,
choose **Capture genuine browser gallery**, select a commit/branch and run it.
An authorized UI-source push to `main` also starts the same bounded capture. This document and the delivered workflow do not imply that a remote run
has already occurred. Repository writes and manual dispatches must be authorized in the active task.
The source-scoped push trigger exists for the authorized repository CI workflow;
it never grants permission to publish its artifacts automatically.

The artifact named `clef-browser-gallery-COMMIT` is retained for one day. On
failure it may contain a failure manifest or partial PNGs. A partial
capture is never a passing gallery. If an earlier gate fails, there may be no
browser artifact at all; read that step's log. The artifact is an ordinary
Actions download, not a permanent README image URL.

Action pins are full commit SHAs. Checkout/setup pins match the existing
[CI documentation](CI.md). The additional artifact action was verified against
[actions/upload-artifact v7.0.1](https://github.com/actions/upload-artifact/releases/tag/v7.0.1)
and its [release commit](https://github.com/actions/upload-artifact/commit/043fb46d1a93c77aae656e7c1c64a875d1fc6a0a).
The implementation follows Playwright's official
[CI workflow](https://playwright.dev/python/docs/ci) and
[browser launch API](https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch).

## Coverage and outputs

The runner uses isolated Chromium storage, German locale, UTC, reduced motion,
device scale 1, a 1440 × 1000 desktop viewport and 390 × 844 / 320 × 844 phone
viewports. Phone captures are Chromium viewport emulation, not physical iPhone
or Android-device validation. Screenshots use the genuine application theme;
no screenshot-only DOM/CSS replacement is applied.

Checks include:

- All five suite primary/total denominators and error counts, independent language
  controls, result views and the bank suite's three answer fields
- Insurance clause navigation and gold highlights, search with empty-result
  clearing, reset, field selection and recorded result provenance
- Actual two-/three-field replay; editing text, reordering questions or malformed
  JSON immediately invalidates the saved answer; clearing removes stale output
- Actual results-only model readiness, explicit server-health refresh and
  disabled inference controls, without pretending weights are loaded
- Genuine file-input parsing of JSON, JSONL and CSV; explicit preview acceptance,
  synthetic private case editing, invalid gold rejection, discard, exported JSON
  byte parsing, no invented result downloads, search/status filters, and reversible
  replacement/clear confirmations with cancel
- Back/Forward, control-case deep links, keyboard case navigation, search shortcut,
  keyboard theme activation and persisted dark mode
- Every public suite's three phone panes, overview/live/method routes and the
  private editor at 320 and 390 pixels, with horizontal document-overflow checks
- Browser exceptions, error-level console messages, failed/HTTP-error requests,
  and attempted inference or off-origin requests all fail the run

The request guard allows only same-origin GET/HEAD and explicitly rejects
`/api/infer`, so a regression cannot accidentally invoke a real model. The
server is independently started without inference. The test never clicks a
live run button. Live start/stop/error/pending flows remain covered by the
separate explicitly model-free unit/DOM tests; no claim of live browser inference
or hardware readiness is made by this gallery.

A passing run writes:

- `screenshots/*.png`: actual desktop, dark, import/editor and phone captures
- `manifest.json`: pass/fail, UTC timestamps, Chromium/Playwright versions,
  source/data SHA-256 hashes, git commit when available, CI run URL when present,
  real backend state, each image hash/dimensions/viewport/theme/route/case,
  diagnostics and exact completed checks
- `README-GALLERY.txt`: an insertable README section, **only after all checks pass**

The local output is under the existing gitignored `test-results/` directory.
The exports must never be regenerated from private customer data for a
public gallery. Only the bundled synthetic inputs are supported here.

## Publish only a verified, reviewed capture

1. Download the artifact from the successful run for the intended commit, or use
   the output of a successful permitted local run. Keep its files together
2. On that exact checkout, verify without launching another browser:

   ```sh
   python3 tests/test_browser.py --verify-artifact test-results/browser-gallery
   ```

   This refuses failed runs, missing/tampered PNGs, absent required screenshots,
   unsafe paths, diagnostics, and any change to the captured UI/data/test sources
3. Open the PNGs and review clipping, legibility, visual hierarchy and focus
   appearance. Automated overflow checks do not replace visual review or a
   screen-reader/accessibility audit
4. Only after approval to publish, copy the PNGs from `screenshots/` and their
   `manifest.json` into `docs/screenshots/`. Insert the text from
   `README-GALLERY.txt` into the root README. The fragment uses repository-relative
   image links that become valid only after these files have been copied
5. Run the link/unit/DOM checks again and inspect the diff. Publish the selected
   real PNGs and provenance together; do not publish a trace or failure artifact
   by default. No script performs this repository write or commit automatically

The source/PNG hashes establish which bytes a run recorded. They are not a
cryptographic attestation of browser execution; inspect the matching CI logs when reviewing provenance. A screenshot is evidence of that viewport and
state, not a new accuracy measurement or a general production-readiness claim.

## Bounded GitHub capture storage

The workflow uses only the standard `ubuntu-24.04` hosted runner, never a larger
or GPU runner. It records no videos or Playwright trace archive, uses no extra
browser/model cache, and uploads at most 10 MiB with one-day artifact retention.
The artifact-size guard prevents an oversized upload, including after a failed
capture. Artifact storage remains separate from the public repository's standard
runner allowance; this workflow makes no unlimited-storage or hardware-cost claim.
Only the reviewed PNGs and their provenance are later committed to the README.
