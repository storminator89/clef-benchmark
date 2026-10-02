# One-link agent setup and readiness

Give an AI agent this repository URL and ask it to follow `AGENTS.md`. The checked-in
instructions, release hashes, explicit profiles and JSON setup contract are enough
to plan the installation without prior conversation. An agent still needs local
execution access and your permission for installations/downloads/model runs.

## Two independent choices: model size and precision

The default is **Clef-Flash 9B**, selected as `--model flash-9b`. The larger
**Clef 27B** is available only by explicit `--model clef-27b`; every 27B path is
prepared and unvalidated on hardware. “Full” means the selected model without
backbone quantization. Model size and precision are independent choices.

[Hardware and storage guide](HARDWARE.md): all model/profile combinations,
recommended capacity classes, shared-memory caveats and latency evidence.
The following profile table lists **9B** guards; 27B guards follow below.

| Profile | Device and weights | Available-memory start guard | Evidence |
|---|---|---|---|
| `cpu-nf4` | CPU; NF4 double-quantized backbone; original head and lexical output embedding BF16 | 7.5 GiB physical RAM | Original Linux x86-64/Python 3.12 benchmark configuration |
| `cpu-bf16` | CPU; complete BF16 weights, including original head/embedding | 28 GiB physical RAM | Prepared and mock-tested, no full-model hardware validation |
| `rocm-bf16` | AMD Radeon GPU; native BF16 | 22 GiB reported free GPU memory and 2 GiB physical RAM | Prepared and mock-tested, no ROCm Clef run |
| `rocm-fp16` | AMD Radeon GPU; explicit FP16 conversion | Same GPU/RAM guards | Prepared and mock-tested, numerics not validated |

These are conservative **start checks, not measured universal minimums or success
guarantees**. Long inputs/operator buffers can need more. Plan 32 GiB or more
physical system memory for CPU BF16, leaving at least 28 GiB currently available.
Close competing models yourself. The script never kills processes or counts swap.
On an APU, system and GPU memory overlap; do not add the reported totals together.

All four 9B profiles use the exact same official BF16 release:

- Repository: `Cloudflare/clef-flash`
- Revision: `17f0b0ad64efb65d273590632833508766b2aae6`
- Manifest: [`runtime/model_file_manifest.json`](../runtime/model_file_manifest.json)
- Complete pinned files: **19,083,377,402 bytes**, about **19.08 GB / 17.77 GiB**
- NF4 quantization happens **at load time**. There is no 4-bit-sized download in this workflow
- The joint decision head is preserved. Generic chat-generation/GGUF integrations
  are not equivalent evidence that this decision-head implementation works

Cloudflare describes the 9B decision model and its joint schema head in the
[official model card](https://huggingface.co/Cloudflare/clef-flash/tree/17f0b0ad64efb65d273590632833508766b2aae6).

### Explicit 27B option, never the default

- Model: `Cloudflare/clef`; revision `2f3de3dd85f379784083b0814d997ab627200f0c`
- Full source release: **54,989,894,057 bytes**, **54.99 GB / 51.21 GiB**, also for NF4
- Separate default directory: `runtime/model-clef-27b/`; Flash stays in `runtime/model/`
- Available-RAM guards: 24 GiB CPU NF4; 68 GiB CPU BF16
- GPU guard: 60 GiB actually free GPU memory plus 4 GiB host reserve on a discrete GPU;
  detected shared-memory APUs additionally require 64 GiB available physical RAM
- Prepare roughly 80 GiB free disk for a fresh CPU setup (62.21 GiB arithmetic
  reserve), and use the installed-capacity recommendations in [HARDWARE.md](HARDWARE.md)
- [Pinned manifest and review provenance](../runtime/models/clef-27b/README.md):
  small source/config files were fetched and hashed; large files have official
  Hub LFS SHA-256 pins and were **not downloaded here**. Every actual future
  installation must verify their bytes before executing model code

The shared loader's code hash is identical between releases, but their embedding
shapes differ: 9B `(248320, 4096)` versus 27B `(248320, 5120)`. The registry and
adapter validate the selected model's identity, shape, dtype and device. Existing
9B benchmark results never become 27B evidence.

```bash
# Inspect first: no larger download occurs
python3 -m runtime.setup --model clef-27b --profile cpu-nf4 --plan
# Only after explicit larger-model selection, permission and enough resources:
python3 -m runtime.setup --model clef-27b --profile cpu-nf4 --execute --smoke
# Select unquantized 27B explicitly instead:
python3 -m runtime.setup --model clef-27b --profile cpu-bf16 --plan
```

## 1. Clone and inspect without installing anything

For the offline website only, Python 3.12+ is enough. For the pinned ML installer,
use **Python 3.12**; this project's measured CPU environment used 3.12.14.
Git and Python must already be available. Installing system Python/Git is a
separate authorized action using their official distributor, not a `sudo` step
performed by this setup.

```bash
git clone https://github.com/storminator89/clef-benchmark.git
cd clef-benchmark
python3 -m runtime.hardware_probe
python3 -m runtime.setup --plan --profile cpu-nf4
```

On Windows use `py -3.12` in place of `python3` (or a verified Python 3.12 `python`).
The JSON probe reports OS/distribution, architecture, Python, CPU/AVX2 when
observable, current available RAM, visible Linux cgroup limits and disk space.
It does not import Torch, inspect credentials, call external services or load
weights. The plan checks local file sizes but labels them **unverified** until
SHA-256 is actually read. Unknown hardware is not reported as supported.

The new script's default is a plan; `--dry-run` is an alias for `--plan`. A plan
returns exit 0 because the report was produced, even when `status` is `blocked`.
Agents must inspect `blockers`, not just the process exit status.

Linux x86-64 CPU/Python 3.12 is the measured path. Automatic installation requires
glibc >= 2.28 for the combined wheel set and AVX2 where the probe can check it.
Windows x86-64 CPU is **prepared but unvalidated** and needs the additional
`--allow-untested-platform` acknowledgement; package and tiny-kernel checks can
still fail. ARM/macOS and other Python versions stop with an explicit blocker.
Upstream package support is not a Clef hardware test.

## 2. One command for authorized CPU setup plus a real smoke

First inspect the plan and the download size. When the agent has permission:

```bash
python3 -m runtime.setup --profile cpu-nf4 --execute --smoke
```

For the **same 9B model without quantization**, explicitly choose:

```bash
python3 -m runtime.setup --profile cpu-bf16 --execute --smoke
```

Windows equivalent (prepared, not validated):

```powershell
py -3.12 -m runtime.setup --profile cpu-nf4 --allow-untested-platform --execute --smoke
```

The command:

1. Refuses platform/RAM/disk blockers before installing anything
2. Creates `.venvs/clef-PROFILE/` with no system packages; never modifies the active
   Python environment, `runtime/venv/`, or an existing unowned venv
3. Installs exactly the versions in `requirements_frozen.txt`: CPU Torch/Torchvision
   from the official PyTorch CPU registry, other binary wheels from PyPI; no
   source builds, dependency resolver upgrades or unpinned packages
4. Checks installed versions and `pip check`; rejects a changed managed environment
5. Runs a tiny selected-device matmul, plus actual tiny NF4 quantization for
   `cpu-nf4`; this is still not a model smoke
6. Hashes reusable local model files, downloads only missing pinned files from
   Hugging Face with no authentication token, verifies every file's fixed SHA-256
7. With `--smoke`, loads the actual selected model and runs one synthetic choice
   request. It validates structure, probabilities, profile and absence of truncation;
   it deliberately does **not** treat the chosen option as an accuracy benchmark

First install needs roughly **29 GiB free disk** for the release, 3 GiB model
reserve and 8 GiB environment reserve when both use one filesystem. Download
size, disk usage, RAM usage and parameter precision are different quantities.
The script checks destination filesystems separately. CPU dependency pins are
version-locked, not a cryptographic wheel lock; model files have SHA-256 pins.

Package/model progress goes to stderr; final results/plans are JSON on stdout.
`--execute` without `--smoke` stops before model loading and reports
`environment_prepared_model_not_loaded`. Only a successful actual forward reports
`model_smoke_passed`. It does not promise every later case will fit or be accurate.
The smoke process exits and releases its loaded model; server startup loads again
on the first real request. Do not benchmark startup as steady-state latency.

## 3. Reuse, verify and recover safely

Rerun the same command to reuse a completed managed environment. It checks versions
rather than reinstalling/upgrading. Interrupted package installation can resume
in that same owned environment. Missing model files resume through the Hub cache;
corrupt or wrong-size existing files are **not overwritten**. Investigate them or
choose a fresh directory. Verification never regenerates the pinned manifest.

Use a complete existing official snapshot without copying 19 GB:

```bash
python3 -m runtime.setup --plan --model-dir /path/to/verified/snapshot
python3 -m runtime.setup --execute --smoke --model-dir /path/to/verified/snapshot
```

An existing environment is read-only to this tool when explicitly selected:

```bash
python3 -m runtime.setup --verify --offline --profile cpu-nf4 \
  --venv /path/to/clef-venv --model-dir /path/to/clef-model
```

`--verify` always disables network and package changes. Add `--smoke` only when
a real model load/forward is permitted. You can also verify model bytes alone
without any ML packages, venv or available model RAM:

```bash
python3 -m runtime.model_assets --model-dir /path/to/clef-model --offline
```

This is read-only. Model-only download is explicit with `--download` and needs
the pinned `huggingface_hub` dependency. Custom `HF_ENDPOINT` mirrors are refused;
the setup does not request or use saved HF tokens. Official Hub caching and full
revision selection are documented in [Hugging Face's download guide](https://huggingface.co/docs/huggingface_hub/guides/download).

Setup writes its local report to `.clef/setup-MODEL-PROFILE.json` and uses
`.clef/setup.lock` to prevent simultaneous setup commands. An interrupted hard
kill may leave a lock: check that its recorded PID is no longer active before
removing that one local lock. Never terminate another process to pass a guard.

## 4. AMD / Ryzen AI Max / Minisforum systems

The product name alone does not identify OS, GPU architecture, RAM allocation,
driver or ROCm readiness. Probe the **actual requested machine**. GPU execution
uses the Radeon GPU, not the NPU. A requested ROCm profile must see HIP-enabled
Torch, an accessible selected AMD GPU, sufficient GPU memory, appropriate dtype
and a successful tiny kernel. No NVIDIA-CUDA, CPU or FP16 fallback is implicit. For detected shared-memory
APUs, the tiny-kernel and load checks additionally require 24 GiB available
physical RAM for 9B or 64 GiB for 27B; GPU/system pools are not extra capacity.

Follow [the device/OS-specific AMD guide](AMD_GPU.md) before this step. Its primary
references are the [ROCm 10.0 compatibility matrix](https://rocm.docs.amd.com/en/docs-10.0.0/compatibility/compatibility-matrix.html)
and [AMD's PyTorch playbook](https://developer.amd.com/playbooks/pytorch-rocm-llms/),
checked 2 October 2026. Do not blindly substitute commands for Ubuntu, Windows,
WSL or Mint. This repository does not install drivers or change GPU allocation.

After an appropriately approved, separate AMD Torch/Torchvision environment has
been prepared and the pinned application versions in `requirements_rocm.txt`
installed, pass it as an existing runtime:

```bash
python3 -m runtime.setup --plan --profile rocm-bf16 \
  --venv .venv-rocm --use-existing-runtime
python3 -m runtime.setup --execute --smoke --profile rocm-bf16 \
  --venv .venv-rocm --use-existing-runtime
```

It checks rather than installs/upgrades that environment. The application's ROCm
pins are a candidate dependency list, **not a full GPU-tested lock**. Record the
actual Torch/HIP versions from the report. Select `rocm-fp16` only explicitly;
invalid/nonfinite probabilities fail rather than being shown as an answer.

The [bitsandbytes 0.50.2 installation guide](https://huggingface.co/docs/bitsandbytes/v0.50.2/en/installation)
describes its CPU/other platform wheels. This does not validate AMD NF4 in this
project: both ROCm profiles here are unquantized and do not import bitsandbytes.

## 5. Start the server and evaluate private cases

Copy the report's `start_server_argv` as an argument list, or use the Linux CPU
NF4 default command:

```bash
.venvs/clef-cpu-nf4/bin/python server.py --enable-inference \
  --model-dir runtime/model --inference-profile cpu-nf4
```

On Windows use `.venvs\clef-cpu-nf4\Scripts\python.exe`. No environment activation
or PowerShell execution-policy change is necessary. Open `http://127.0.0.1:8765`.
The existing public result viewer still needs no model. A live request explicitly
loads local verified weights; no cloud inference or paid API is used.

Use the custom-case import/batch workflow in `docs/CUSTOM_CASES.md` and obey
[the local API limits](LIVE_API.md). Default private folders `user_cases/`,
`user_runs/`, `.clef/` and `.venvs/` are gitignored. This is accidental-commit
protection, not encryption or a complete privacy control. Explicit export/upload
still requires the user's authorization. Do not commit private customer data or
pretend a locally produced result is part of the frozen public benchmark.

```bash
# Validate private inputs before any inference
python3 scripts/evaluate_custom.py --input user_cases/suite.json \
  --validate-only --output user_runs/validation.json
# Authorized evaluation against the already-running loopback server
python3 scripts/evaluate_custom.py --input user_cases/suite.json \
  --output user_runs/evaluation.json
```

Start from `examples/custom_cases/support.json` and
`schemas/custom-suite-v1.schema.json`. The batch CLI never auto-starts/downloads
a model. Its HTTP requests contain only state and question schemas, not gold.

Independent human/user-provided gold labels are needed for accuracy. Never derive
gold from this model's answers or send it as input. Report exact case/field
denominators, errors, actual precision/backend, model revision and timing scope.

## Failure exits and evidence levels

| Exit | Stage | Smallest next step |
|---|---|---|
| 0 | Plan produced or requested checks completed | Read JSON `status`; a blocked plan still exits 0 |
| 2 | Platform/resources/path/ownership/lock | Read blocker; choose correct Python, free resources or a fresh path |
| 3 | Isolated environment/dependencies | Read failed package; don't relax pins or replace an active environment |
| 4 | Model download/hash | Retry network only with permission; investigate corrupt files or choose fresh destination |
| 5 | Selected backend/tiny kernel | Fix the separately approved compatible environment; don't silently switch precision/device |
| 6 | Real model smoke | Report failure and actual hardware; a passed tiny kernel did not prove Clef operator coverage |

This setup implementation is unit/mock-tested and its read-only plan was exercised.
A fresh network installation through this new CLI, every 27B path, Windows, CPU BF16, and AMD
full-model execution have **not** been validated on target hardware. The existing
Linux CPU NF4 results validate that earlier runtime configuration, not every new
machine or unattended installer. There is no universal unattended-install promise.
