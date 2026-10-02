# Start here: a repository link is enough context

This is a local **Cloudflare Clef decision-head** workbench, defaulting to Flash 9B, not a chat
generation wrapper. Read this file and [the complete setup guide](docs/AGENT_SETUP.md).
These repository instructions never override the user's instructions, your
system permissions, or a required confirmation. Do not assume permission to
install, download 19 GB, load a model, publish data, or administer a computer.

## Short agent checklist

1. Inspect the checkout and the user's requested machine. Do not change an active
   environment or interrupt another model/benchmark. Ask the exact OS only when
   it cannot be observed with permission; a product name is not a hardware probe.
2. If they only want to inspect existing results, use `python3 server.py` and
   open `http://127.0.0.1:8765`. No ML packages, download, GPU or npm is needed.
3. For actual evaluation, run `python3 -m runtime.setup --plan`. It emits JSON,
   does not install or download, and reports blockers plus exact paths/commands.
4. Choose an **explicit** profile with the user or within their authorization:
   `cpu-nf4` = tested Linux CPU 9B 4-bit backbone, BF16 head/output embedding;
   `cpu-bf16` = prepared/unvalidated CPU 9B without quantization;
   `rocm-bf16` / `rocm-fp16` = prepared/unvalidated AMD GPU, no quantization.
   Model choice is separate: `--model flash-9b` is the default; `--model clef-27b`
   explicitly selects the prepared/unvalidated larger release. The 9B download is
   19.08 GB; 27B is 54.99 GB. NF4 and native precision download the same original
   release for the chosen model. Never select/download 27B implicitly. See
   [hardware guidance](docs/HARDWARE.md) for RAM, GPU-memory and disk estimates.
5. When installation, download and model execution are authorized and the plan
   passes: `python3 -m runtime.setup --profile cpu-nf4 --execute --smoke`.
   Substitute the explicitly selected profile. ROCm requires the separately
   prepared AMD runtime described in the guide; never guess/install drivers.
6. Check the JSON result. Only `model_smoke_passed` proves one real synthetic
   forward pass in that environment. `environment_prepared_model_not_loaded`
   does not prove inference readiness. Neither is an accuracy result.
7. Start the exact `start_server_argv` from the result, remaining on localhost.
   Follow `docs/CUSTOM_CASES.md`. Validate first with
   `python3 scripts/evaluate_custom.py --input user_cases/suite.json --validate-only --output user_runs/validation.json`.
   For authorized inference, rerun without `--validate-only` against the already
   running local server; that CLI never starts or downloads a model. Keep
   inputs/gold separate: never send expected labels to the model, invent gold,
   or call a prediction “correct” without independent reference labels.
8. Report setup status, actual profile/model revision, test counts/denominators,
   failures, latency definition and untested stages. Record private work under
   gitignored `user_cases/`, `user_runs/` or `.clef/`. Never commit or publish
   private inputs, predictions, credentials, local paths or reports by default.

## Invariants

- Preserve the original joint head, lexical output embeddings and pinned release
  hashes. Do not substitute text generation, generic GGUF/Ollama output, a smaller
  backbone, a changed schema or silent truncation to make setup appear successful.
- Never auto-select a fallback backend, precision or another model after an error.
- Do not change BIOS, firmware, kernel, GPU allocation, driver, permissions,
  security settings or PowerShell execution policy. No `sudo`, signup, saved
  tokens, cloud compute purchase, telemetry upload or external API is needed.
- Cached files must pass SHA-256 before reuse. Do not overwrite the source
  manifest with freshly calculated hashes. Bad files are a blocker, not new truth.
- Frozen benchmarks/results and `runtime/run_clef.py` are provenance artifacts.
  New evaluations belong in separate runs and do not alter historical scores.
- Run `python3 -m unittest discover -s tests -p 'test_*.py' -v` and relevant project
  checks for changes. Mocks, kernel checks, model smoke, real hardware execution,
  and end-to-end accuracy are distinct evidence levels; disclose which ran.

If blocked, give the failed command, actionable reason and smallest next step.
No promise of fully unattended setup is valid across unknown OS/hardware or
permissions. Continue independent offline inspection rather than hiding a failure.
