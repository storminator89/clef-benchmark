# Clef hardware and storage guide

Checked 2026-10-02. These are **capacity-planning recommendations**, not certified
minimums or purchase/performance guarantees. Run the setup plan on the actual
machine before downloading; passing a resource check does not prove a model works.

## Choose model size and precision separately

- `flash-9b`: Cloudflare/Clef-Flash, the default 9B model.
- `clef-27b`: Cloudflare/Clef, the explicitly selected larger 27B model.
- `cpu-nf4`: quantize eligible backbone layers to 4-bit NF4 while loading; retain
  the original BF16 joint head and lexical output embeddings. This is not a
  pre-quantized download, and not every tensor is 4-bit.
- `cpu-bf16`: unquantized CPU inference at the release's native BF16 precision.
- `rocm-bf16` / `rocm-fp16`: unquantized AMD GPU inference at the selected 16-bit
  precision. FP16 and BF16 both use two bytes per stored scalar; FP16 does not halve
  BF16 memory, and numerical results can differ.

“Full/native” in this project means **unquantized 16-bit**, not FP32. Changing
precision does not turn the 9B model into the separate 27B model. These profiles
are single-device; adding two GPU capacities does not produce one usable pool.
No ROCm NF4, NPU, NVIDIA/CUDA, GGUF, or multi-GPU profile is supplied by this setup.
That is a project scope statement, not a claim those technologies cannot support
these models. Keep the original Clef decision head; a generic chat-model loader
or GGUF replacement is not equivalent.

## Evidence levels

| Evidence | What it establishes |
| --- | --- |
| **Observed here: 9B CPU NF4** | Real local forward passes were completed. A development host had roughly 9.7 GiB total RAM; observed process memory was roughly 6–7 GiB on the tested short-record workloads. The existing available-RAM guard is 7.5 GiB. Neither number establishes a universal memory minimum or peak. |
| **Vendor tested** | Cloudflare's release cards report Torch 2.11 and Transformers 5.10.2 on a single NVIDIA H200. That is a tested environment, not a mandatory GPU. |
| **Prepared, unvalidated here** | 9B unquantized CPU/GPU profiles and every 27B profile. The 27B metadata, configuration and source were inspected; its weights were not downloaded or loaded for this work. |
| **Engineering estimate** | All recommended installed capacities and all new native/27B resource guards below. They need real workload validation on the target machine. |

The measured 9B CPU latency varies substantially with the input, with examples
roughly in the 10–40 second range. This is not a GPU estimate, a 27B estimate, or a
service-level promise. Keep model loading, encoding and forward-only latency
separate when reporting measurements. [Cloudflare's Flash card](https://huggingface.co/Cloudflare/clef-flash)
and [Clef card](https://huggingface.co/Cloudflare/clef) describe the vendor's own
hardware and results, which should not be projected onto another machine.

### GPU speed versus Jev: published results and local expectations

Cloudflare publishes these latency results from its evaluation:

| Model | Median | p95 |
| --- | ---: | ---: |
| Clef-Flash 9B | 38.8 ms | 122.4 ms |
| Clef 27B | 209.3 ms | 238.6 ms |
| Jev | 524.1 ms | 536.0 ms |

These are **vendor-environment results**, not measurements from this repository on
Ryzen, CPU NF4, or the browser UI. They show Clef's potential on the vendor's
workload; they do not establish a matching local latency boundary or a guarantee
that every record finishes under one second. The H200 mentioned in the release
cards is a vendor-tested platform, not evidence that all comparison models used
identical hardware or an instruction to buy an H200.
[Cloudflare's published latency comparison](https://blog.cloudflare.com/clef-decision-models/).

Sub-second warm inference on short Flash inputs is a plausible goal for a working
Ryzen GPU configuration, **but remains unmeasured here**. Long documents, images,
large schemas and first-load requests have no such promise. Validate this on the
actual machine: report cold load separately, then warm repeated representative
requests with token counts, model/precision, device, median and p95. Measure both
the synchronized model forward and user-visible end-to-end time, including
encoding and server/UI overhead. Never compare local end-to-end time against an
unspecified vendor timing boundary as if they were equivalent.

## Disk: NF4 still downloads the full source release

`GB = 1,000,000,000 bytes`; `GiB = 1,073,741,824 bytes`. Download figures below
include the release's backbone shards, head, tokenizer, configuration and source.
They are summed from pinned Hugging Face file metadata, without fetching weights.

| Model | Pinned source download / retained release | Fresh CPU setup arithmetic reserve* | Practical free-space planning target |
| --- | ---: | ---: | ---: |
| Flash 9B, any profile | 19,083,377,402 bytes = 19.08 GB = 17.77 GiB | 28.77 GiB | **40 GiB free** before a fresh CPU setup; **30 GiB** if the ML environment already exists |
| Clef 27B, any profile | 54,989,894,057 bytes = 54.99 GB = 51.21 GiB | 62.21 GiB | **80 GiB free** before a fresh CPU setup; **70 GiB** if the ML environment already exists |
| Both releases, one CPU environment | 74,073,271,459 bytes = 74.07 GB = 68.99 GiB | About 80 GiB before existing artifacts | **100 GiB free** for one copy of each, the environment and working room |

\* The fresh CPU setup reserve is a missing release plus 3 GiB download/workspace
reserve and 8 GiB environment reserve. These are checks, not measured installed
sizes. The practical targets intentionally leave more space. A new ROCm runtime,
container image, pip cache, logs, user data and exported runs require additional
space; provision the GPU runtime separately, then check remaining space again.

- NF4 conversion happens in memory. The BF16 source remains on disk, so choosing
  4-bit does **not** reduce the download or retained release to one quarter.
- Another physical copy, separate model directory, cache or retained revision can
  add another 17.77 GiB or 51.21 GiB. Do not assume tools deduplicate across paths.
  A symlink is not a second physical copy, but a manual copy generally is.
- A verified already-present release can be reused without downloading again.
  Wrong-size or bad-hash files must be treated as a blocker, not silently trusted.
- Use an SSD, preferably NVMe. Capacity on the intended model filesystem matters;
  spare space on a different volume does not help that download.
- Swap/pagefile is disk use, not replacement RAM for the resource checks.

Pinned source metadata:
[Flash 17f0b0a](https://huggingface.co/api/models/Cloudflare/clef-flash/revision/17f0b0ad64efb65d273590632833508766b2aae6?blobs=true),
[Clef 2f3de3d](https://huggingface.co/api/models/Cloudflare/clef/revision/2f3de3dd85f379784083b0814d997ab627200f0c?blobs=true).

## RAM and GPU memory

The budgets assume **one loaded model, one short text record at a time and modest
question/option counts**. Available memory means immediately usable physical
memory after other applications and container limits, not the box's advertised
installed RAM. Close other model processes before measuring. Preflight guards are
conservative policy thresholds; passing them does not guarantee freedom from OOM.

| Model / profile | Available-memory guard / proposed planning floor | Recommended installed capacity class | Validation |
| --- | --- | --- | --- |
| 9B `cpu-nf4` | 7.5 GiB system RAM | 16 GB RAM for modest use; 32 GB for more headroom | Real short-record CPU runs; broader limits unvalidated |
| 9B `cpu-bf16` | 28 GiB system RAM | 48–64 GB RAM preferred; 32 GB can be tight after OS/apps | Estimate; not run here |
| 9B `rocm-bf16` or `rocm-fp16` | 22 GiB **free GPU-accessible memory**, plus host room | 32 GB dedicated GPU memory with 32 GB+ host RAM; or a 64 GB shared-memory APU, subject to actual visibility | Estimate; not run here |
| 27B `cpu-nf4` | 24 GiB system RAM | 32 GB entry class only if the guard passes; 64 GB preferred | Estimate; not run here |
| 27B `cpu-bf16` | 68 GiB system RAM | 96–128 GB RAM | Estimate; not run here |
| 27B `rocm-bf16` or `rocm-fp16` | 60 GiB **free GPU-accessible memory**, plus host room | At least a 64 GB GPU capacity class, with little spare room; larger is preferable. For shared-memory APUs, plan on 128 GB total | Estimate; not run here |

On discrete GPUs, retain at least 2 GiB available host memory for the 9B GPU
profile or 4 GiB for 27B as a basic preflight reserve; substantially more installed
host RAM is recommended for the OS, file mappings, loading and other programs.
On a shared-memory APU these pools overlap: require both the GPU-visible budget
**and** sufficient physical system memory to back it plus host room. A conservative
combined check is at least 24 GiB available system RAM for 9B or 64 GiB for 27B,
not merely 2/4 GiB left on the host. Even those checks cannot see every driver or
transient-allocation constraint.

A supported 24 GB GPU may be a constrained 9B native test candidate only if it
actually reports at least 22 GiB free. It is not the comfortable recommendation.
A 48 GB GPU cannot hold this guide's 27B unquantized budget. A 32 GB Radeon AI PRO
R9700 is one official-spec example of the 9B capacity class; that does **not** mean
this project has tested it, that an external enclosure works, or that the rest of
a particular PC supports the card. [AMD R9700 specifications](https://www.amd.com/en/products/graphics/workstations/radeon-ai-pro/ai-9000-series/amd-radeon-ai-pro-r9700.html).

### Why “weights divided by four” is wrong

The input and output embeddings are separate (`tie_word_embeddings=false`). From
the official configuration, their BF16 storage alone is about **3.79 GiB for 9B**
or **4.74 GiB for 27B**, before the head, quantized layers, quantization metadata,
activations, operator workspaces and allocator overhead. The release head files
are another approximately 0.23/0.24 GiB. RSS on a short CPU workload can differ
from all tensor payload bytes because file-backed pages need not all be resident.
Do not turn a low observed RSS into a guaranteed peak or fit calculation.
[Flash configuration](https://huggingface.co/Cloudflare/clef-flash/blob/17f0b0ad64efb65d273590632833508766b2aae6/config.json),
[27B configuration](https://huggingface.co/Cloudflare/clef/blob/2f3de3dd85f379784083b0814d997ab627200f0c/config.json).

### Context, batches and workload shape

Longer state text, verbose criteria, more options, batch size and concurrent model
processes increase memory and time. Images/video add encoder work and visual
tokens. Do not extrapolate short text smoke results to large multimodal batches.
The official Clef forward disables the persistent generation KV cache; generic
chat-model KV-cache calculators are therefore not an exact model for this path.
Attention/activation/workspace memory still matters, and some attention paths can
scale quadratically with sequence length. Start with batch 1 and short records,
then measure a representative upper-bound case before raising limits. Never
silently truncate to make a test fit. The backbone's advertised context length is
not evidence that the available machine or repository workload limit supports it.
[Official forward and loader](https://huggingface.co/Cloudflare/clef-flash/blob/17f0b0ad64efb65d273590632833508766b2aae6/joint_schema_model.py).

## MINISFORUM S1 / Ryzen AI Max

Verify the exact model first. The MS-S1 MAX product page specifies a Ryzen AI Max+
395, Radeon 8060S and configurations up to 128 GB LPDDR5x-8000. “S1” alone does not
establish CPU generation, installed RAM, OS, firmware or GPU memory availability.
Do not infer this machine's specification from a similar past setup or product
advertisement. [MINISFORUM MS-S1 MAX specifications](https://store.minisforum.com/products/minisforum-ms-s1-max-mini-pc).

As checked on 2026-10-02, AMD's **unified ROCm 10.0** documentation lists Ryzen AI
Max 300 and Radeon 8060S/gfx1151. Its APU matrix names Ubuntu 26.04 (GA 7.0), Ubuntu
24.04.4 (OEM 6.17) and Windows 11 25H2. Linux Mint is not explicitly listed there;
being Ubuntu-derived does not itself establish a supported stack. Consult the
exact current hardware/OS row rather than an old Ryzen ROCm 7.2.1 page or a generic
all-GPU OS list. [ROCm compatibility matrix](https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html).

Shared RAM is not automatically all available as GPU memory. AMD documents GPUVM/
GTT mappings on these APUs and an approximately 50% default GTT limit; limits and
firmware reservations affect what frameworks can allocate. Thus 64 GB installed
RAM does not imply 64 GiB free for a model. A 128 GB APU is a more sensible capacity
class for 27B native, but its effective GPU memory limit and remaining host memory
must still pass. Kernel support matters too: AMD documents required Ryzen AI Max
fixes, with specific Ubuntu backports or kernel 6.18.4+ for other distributions.
A suitable kernel does not alone certify an unlisted distribution.
[AMD RDNA3.5 memory and kernel guidance](https://rocm.docs.amd.com/en/latest/reference/system-optimization/rdna3-5.html).

These profiles use the **Radeon GPU through ROCm/PyTorch**, not the NPU. NPU TOPS
and combined marketing TOPS do not predict this workload. In a ROCm PyTorch build,
`torch.cuda` is intentionally the API used for AMD GPUs; check `torch.version.hip`
as well as device availability. A `cuda:0` device name alone does not mean NVIDIA.
[PyTorch HIP semantics](https://docs.pytorch.org/docs/stable/notes/hip.html).

Prepare a matching ROCm Torch/Torchvision environment using AMD's current selector
for the observed OS and architecture. Do not install the project's CPU Torch lock
on top of it. The setup's application dependency pins do not establish that every
newer Torch/ROCm combination is compatible with Clef. A small kernel check and an
actual Clef smoke test are separate required checks.
[Official AMD PyTorch installation](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html).

Modern bitsandbytes documentation lists AMD gfx1151 support, but this repository's
prepared ROCm profiles deliberately use native BF16/FP16. Do not silently switch
to a different GPU quantization stack. The CPU wheel documentation names AVX2 for
x86-64; the repository's complete dependency lock may impose stricter OS/library
requirements than bitsandbytes alone.
[bitsandbytes installation requirements](https://huggingface.co/docs/bitsandbytes/main/en/installation).

## Safe first check

Use the repository's read-only hardware probe and setup plan before installation
or weights download. Record the exact CPU/SKU, total and available physical RAM,
OS/version/kernel, Python, available disk on both model and environment volumes,
and, in the existing AMD environment, HIP version, GPU name and free/total GPU
memory. Do not post private paths or machine identifiers in a public issue.

The setup must not automatically change BIOS, GPU allocation, drivers, kernels,
permissions or system security settings. If the current stack fails, report the
specific blocker and obtain approval for any separately proposed system changes.
A successful probe is not inference validation; only an actual model smoke proves
that one forward pass worked in that environment, and accuracy requires separate
reference-label evaluation.
