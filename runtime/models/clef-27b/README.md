# Clef 27B pinned metadata, not downloaded weights

Explicit opt-in model: `--model clef-27b`. Default remains `flash-9b`.

- Official repository: [Cloudflare/clef](https://huggingface.co/Cloudflare/clef)
- Pinned revision: `2f3de3dd85f379784083b0814d997ab627200f0c`
- [Official pinned metadata](https://huggingface.co/api/models/Cloudflare/clef/revision/2f3de3dd85f379784083b0814d997ab627200f0c?blobs=true), inspected 2026-10-02
- 25 files, 54,989,894,057 bytes, including twelve backbone shards and joint head

The source, configuration and index retained here were downloaded as small files
and checked against the official Git blob IDs and locally computed SHA-256.
Other small-file SHA-256 values were also calculated from downloaded bytes.
The tokenizer/head/weight LFS hashes are official metadata pins: the weights were
**not downloaded or locally verified** in this preparation. `manifest.json`
records `hash_source` separately. A future authorized setup checks every downloaded
file against these pins before loading any vendor source/model.

The pinned source is byte-identical to the existing Flash loader (SHA-256
`0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3`).
The actual config says `Qwen3_5ForConditionalGeneration`, text hidden size 5120,
vocabulary 248320 and untied embeddings. The official card's base-model naming
is distinct from this loader class. The adapter validates the 27B lexical output
embedding as `(248320, 5120)` rather than reusing Flash's 4096-dimensional shape.
Head hidden size is 5120; loading its pinned state dictionary remains strict.

No 27B accuracy, latency, hardware compatibility or full installation is claimed.
All 27B profiles remain prepared/unvalidated. See [setup](../../../docs/AGENT_SETUP.md)
and [hardware guidance](../../../docs/HARDWARE.md). The original Apache-2.0
licensed upstream source/configuration is preserved; see the repository LICENSE.
