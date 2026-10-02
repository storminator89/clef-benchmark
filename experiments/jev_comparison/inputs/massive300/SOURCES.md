# Sources and attribution

- Dataset: AmazonScience/massive on [Hugging Face](https://huggingface.co/datasets/AmazonScience/massive), pinned revision `ff6bd8e4b27c3543e4f8fe2108f32bb95a6f8740`.
- [Pinned loader source, inspected as text only](https://huggingface.co/datasets/AmazonScience/massive/blob/ff6bd8e4b27c3543e4f8fe2108f32bb95a6f8740/massive.py). Its individual-locale configurations use MASSIVE 1.1. Its `_INTENTS` array supplies the class-index mapping. The official JSONL carries intent strings directly; numeric HF ClassLabel IDs were never mistaken for model choices.
- [Official upstream MASSIVE repository](https://github.com/alexa/massive). MASSIVE 1.1 adds Catalan; its German data is unchanged from 1.0, according to upstream release documentation.
- [Official MASSIVE 1.1 JSONL archive](https://amazon-massive-nlu-dataset.s3.amazonaws.com/amazon-massive-dataset-1.1.tar.gz). The exact fetched archive and the German JSONL bytes are pinned by SHA-256 in the source manifest. Hugging Face hosts the metadata/loader; this loader-referenced official archive supplies the data. No remote dataset loader code was executed.
- Jack FitzGerald et al., 2022. [MASSIVE: A 1M-Example Multilingual Natural Language Understanding Dataset with 51 Typologically-Diverse Languages](https://arxiv.org/abs/2204.08582). The paper describes MASSIVE 1.0; the dataset used here is the 1.1 distribution.
- Emanuele Bastianelli, Andrea Vanzo, Pawel Swietojanski and Verena Rieser, 2020. [SLURP: A Spoken Language Understanding Resource Package](https://aclanthology.org/2020.emnlp-main.588/). English SLURP was the source for human translation/localization. These examples are not originally collected German banking support cases.
- Copyright Amazon.com Inc. or its affiliates. Dataset license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Exact distributed license, upstream NOTICE and citations are retained under `licenses/`. The 300 utterances and their gold labels remain unchanged; this derivative selects, deduplicates and reorganizes records, removes worker identifiers, and adds evaluation schema/analysis. No endorsement by Amazon, the dataset authors, Hugging Face or Cloudflare is implied.
- [Cloudflare/clef-flash](https://huggingface.co/Cloudflare/clef-flash), pinned revision `17f0b0ad64efb65d273590632833508766b2aae6`. Native release model/encoder/head, Apache-2.0. Model license and reproducible runtime references are retained. This run applies NF4 backbone quantization on CPU; it is not an unquantized GPU evaluation.

## Verified dataset documentation discrepancy

The current HF card summary lists 19,521 examples per language, whereas its German split table lists 11,514 train + 2,033 dev + 2,974 test = 16,521. The actual pinned German JSONL has 16,521 records. Raw-source counts govern this evaluation. The 2,974 test records represent 59 gold intents; the complete ontology has 60. The absent test intent is `cooking_query`.

## Interpretation

This is a zero-shot, native-schema, closed-set intent experiment on a deterministic 300-case slice with all 60 choices. It is not the official full-test leaderboard protocol. Public benchmark pretraining overlap is unknown. Annotation/localization quality is measured from provided judgments without outcome-based filtering, and all observed cross-split normalized text overlaps are disclosed.
