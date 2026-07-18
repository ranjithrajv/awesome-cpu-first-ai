# The CPU-First Case, in Hub Data

This list argues that **most AI people actually deploy is small enough to run on a CPU**. That is a testable claim — so this doc tests it against the real distribution of what the Hugging Face Hub serves, rather than asserting it.

The data comes from [HF Landscape](https://huggingface.co/spaces/ranjithraj/hf-landscape) and its open [study dataset](https://huggingface.co/datasets/ranjithraj/hf-landscape-study-data) — a weekly crawl of the entire Hub (**2.9M models, 66.4B all-time downloads, 579K entities**). Every figure below ships with the exact DuckDB query that produced it, so you can re-run and challenge it.

*Snapshot: week of 2026-07-13. Last verified: 2026-07-18. Downloads are the trailing-30-day figure (`dl30`) unless noted.*

---

## Contents

- [Data Source and Method](#data-source-and-method)
- [Finding 1 — What people pull is small](#finding-1--what-people-pull-is-small)
- [Finding 2 — The top of the leaderboard is CPU-native](#finding-2--the-top-of-the-leaderboard-is-cpu-native)
- [Finding 3 — The task mix is CPU-native work](#finding-3--the-task-mix-is-cpu-native-work)
- [Finding 4 — People fine-tune small models](#finding-4--people-fine-tune-small-models)
- [What This Does and Doesn't Prove](#what-this-does-and-doesnt-prove)
- [Reproduce It](#reproduce-it)
- [See also](#see-also)

---

## Data Source and Method

- **Source**: `models.parquet` from the [study dataset](https://huggingface.co/datasets/ranjithraj/hf-landscape-study-data) — one row per model repo (2,903,100 rows), with `dl30` (30-day downloads), `params`, `sizeBucket`, `task`, `modality`, `license`, and fine-tune lineage (`baseModel`, `baseRelation`).
- **Metric**: 30-day downloads (`dl30`) — a measure of current *reach*, i.e. what the ecosystem is actively pulling.
- **Size honesty**: only **25.5%** of model repos publish a parameter count (from safetensors metadata); the rest are `sizeBucket = 'unknown'`. Size-share figures below are stated **among models with a known size**, and are reported both ways (bucket-based and params-based) — they agree.

---

## Finding 1 — What people pull is small

Share of 30-day downloads by model size, among models with a known size (smallest → largest, cumulative):

| Size bucket | % of downloads | Cumulative |
|---|---:|---:|
| < 5M | 3.7% | 3.7% |
| 5M–100M | 28.2% | 31.9% |
| 100M–500M | 27.4% | 59.3% |
| 0.5B–1B | 7.5% | **66.8%** |
| 1B–5B | 10.2% | **77.0%** |
| 5B–15B | 10.4% | **87.4%** |
| 15B–70B | 9.1% | 96.5% |
| 70B+ | 3.3% | 99.8% |

Cross-checked directly against parameter counts (models with published `params`), by download volume:

| Threshold | Share of downloads |
|---|---:|
| ≤ 1B params | 66.8% |
| ≤ 3B params | 72.6% |
| ≤ 7B params | 78.2% |
| ≤ 13B params | 86.3% |

**Two-thirds of model downloads go to models ≤ 1B parameters; roughly four-fifths to ≤ 7B.** The median model that publishes a size is **~900M parameters**. Every one of those thresholds fits comfortably in commodity CPU RAM at 4-bit quantization — a ≤ 7B Q4 model is ~4 GB. See the [CPU-Native Model Catalog](cpu-native-models.md) and [Hardware Reference](hardware-reference.md) for what that means in practice.

---

## Finding 2 — The top of the leaderboard is CPU-native

The 15 most-downloaded models on the Hub over the last 30 days:

| # | Model | Task | Size | 30-day dl |
|---|---|---|---|---:|
| 1 | `sentence-transformers/all-MiniLM-L6-v2` | sentence-similarity | 23M | 253.5M |
| 2 | `cross-encoder/ms-marco-MiniLM-L6-v2` | text-ranking | 23M | 85.0M |
| 3 | `google-bert/bert-base-uncased` | fill-mask | 110M | 72.6M |
| 4 | `BAAI/bge-small-en-v1.5` | feature-extraction | 33M | 66.4M |
| 5 | `sentence-transformers/paraphrase-multilingual-*` | sentence-similarity | 118M | 50.2M |
| 6 | `google/electra-base-discriminator` | — | (small) | 49.8M |
| 7 | `BAAI/bge-m3` | sentence-similarity | (small) | 34.7M |
| 8 | `sentence-transformers/all-mpnet-base-v2` | sentence-similarity | 109M | 32.6M |
| 9 | `Qwen/Qwen3-0.6B` | text-generation | 752M | 27.8M |
| 10 | `timm/mobilenetv3_small_100.lamb_in1k` | image-classification | 3M | 27.8M |
| 11 | `google-t5/t5-small` | translation | 61M | 26.5M |
| 12 | `openai/clip-vit-base-patch32` | zero-shot-image-classification | (small) | 23.7M |
| 13 | `FacebookAI/xlm-roberta-base` | fill-mask | 279M | 22.8M |
| 14 | `Qwen/Qwen3-8B` | text-generation | 8.2B | 18.1M |
| 15 | `BAAI/bge-reranker-v2-m3` | text-classification | 568M | 17.4M |

**14 of the top 15 are ≤ 1B parameters.** The first model larger than 1B is Qwen3-8B, at rank 14. The list is dominated by embedding models, rerankers, BERT-family encoders, and small vision/ASR models — every one of them a workload the [CPU AI Gap Map](cpu-ai-gap-map.md) rates at CPU maturity Stage 5.

---

## Finding 3 — The task mix is CPU-native work

Share of 30-day downloads by task:

| Task | % of downloads | CPU maturity |
|---|---:|---|
| text-generation | 20.7% | Stage 5 (small models) |
| sentence-similarity | 19.0% | Stage 5 |
| image-text-to-text | 11.4% | mixed |
| fill-mask | 7.8% | Stage 5 |
| feature-extraction | 7.5% | Stage 5 |
| automatic-speech-recognition | 6.0% | Stage 5 |
| text-ranking | 4.5% | Stage 5 |
| image-classification | 3.1% | Stage 5 |
| text-classification | 3.0% | Stage 5 |
| zero-shot-image-classification | 2.8% | Stage 5 |
| translation | 1.6% | Stage 5 (small) |

Adding up the tasks the gap map rates CPU Stage 5 *and excluding text-generation entirely* — embeddings/retrieval (sentence-similarity, feature-extraction, text-ranking, fill-mask), ASR, and classification/detection/segmentation — gives **49.1% of all model downloads**. By modality, **58.6%** of downloads are NLP and **8.0%** audio; only a minority sits in the large-diffusion / large-LLM territory where a GPU is genuinely required (see [When You Actually Do Want a GPU](../README.md#when-you-actually-do-want-a-gpu)).

---

## Finding 4 — People fine-tune small models

Base models with the most derivatives on the Hub (fine-tunes + adapters + quantizations + merges):

| Base model | Derivatives | Size |
|---|---:|---|
| `black-forest-labs/FLUX.1-dev` | 43,293 | 12B (diffusion — GPU-leaning) |
| `Qwen/Qwen1.5-0.5B` | 32,533 | 0.5B |
| `Qwen/Qwen1.5-1.8B` | 30,627 | 1.8B |
| `google/gemma-2b` | 24,036 | 2B |
| `distilbert/distilbert-base-uncased` | 12,437 | 66M |
| `stabilityai/stable-diffusion-xl-base-1.0` | 10,899 | 3.5B (diffusion) |
| `google/gemma-7b` | 9,582 | 7B |
| `Qwen/Qwen3-4B-Instruct-2507` | 7,747 | 4B |
| `google-bert/bert-base-uncased` | 6,974 | 110M |
| `Qwen/Qwen1.5-7B` | 6,372 | 7B |
| `meta-llama/Llama-3.1-8B-Instruct` | 6,309 | 8B |

Set the two text-to-image diffusion bases aside and **every most-fine-tuned base model is ≤ 8B — most are ≤ 2B.** The adaptation ecosystem centers on exactly the size class that fits CPU LoRA/QLoRA, which is the premise of the [CPU Fine-Tuning Benchmarks proposal](cpu-finetuning-benchmarks.md).

---

## What This Does and Doesn't Prove

**It shows** that the Hub's actual pull — leaderboard, task mix, and fine-tune lineage — is dominated by models small enough for CPU inference. That is direct, current, reproducible evidence for the list's core premise, replacing anecdote with a query.

**It does not show** the CPU-vs-GPU split of production *serving*. Downloads are a reach proxy, not a deployment census:

- Download counts include CI, mirrors, and pipeline defaults, so heavily-integrated small models (embeddings, BERT, Whisper) are over-represented — though that over-representation *is* the point: the models baked into everyday pipelines are the CPU-native ones.
- 74.5% of repos don't publish a size; size-share figures cover the 25.5% that do. The unknown-size tail is itself download-light per repo and skews small (several top-15 entries above are unknown-size but tiny).
- "Most-derived" counts adapters and quantizations, not just full fine-tunes.

Framed honestly: **this is what the ecosystem reaches for**, and what it reaches for runs on a CPU.

---

## Reproduce It

The dataset is plain Parquet, queryable with [DuckDB](https://duckdb.org) or Polars — no account needed.

```bash
# Grab the models table (~92 MB) and open a DuckDB shell
curl -fsSL -o models.parquet \
  "https://huggingface.co/datasets/ranjithraj/hf-landscape-study-data/resolve/main/models.parquet"
duckdb
```

```sql
-- Finding 1: download share by size, among models with a known size
WITH k AS (SELECT * FROM 'models.parquet' WHERE sizeBucket <> 'unknown')
SELECT sizeBucket,
       round(100.0*sum(dl30)/sum(sum(dl30)) OVER (), 1) AS pct_of_known_dl30
FROM k GROUP BY sizeBucket
ORDER BY array_position(
  ['<5M','5M–100M','100M–500M','0.5B–1B','1B–5B','5B–15B','15B–70B','70B+'], sizeBucket);

-- Finding 1 (cross-check): params-based cutoffs, by download volume
WITH p AS (SELECT * FROM 'models.parquet' WHERE params > 0)
SELECT round(100.0*sum(dl30) FILTER (WHERE params <= 1e9) /sum(dl30),1) AS pct_le_1B,
       round(100.0*sum(dl30) FILTER (WHERE params <= 7e9) /sum(dl30),1) AS pct_le_7B,
       round(median(params)/1e6,0) AS median_params_M
FROM p;

-- Finding 2: top 15 models by 30-day downloads
SELECT id, task, sizeBucket, round(dl30/1e6,1) AS dl30_M
FROM 'models.parquet' ORDER BY dl30 DESC LIMIT 15;

-- Finding 3: download share by task
SELECT task, round(100.0*sum(dl30)/sum(sum(dl30)) OVER (),1) AS pct
FROM 'models.parquet' WHERE task <> '' GROUP BY task ORDER BY pct DESC LIMIT 12;

-- Finding 4: most-derived base models
SELECT baseModel, count(*) AS derivatives
FROM 'models.parquet'
WHERE baseRelation IN ('finetune','adapter','quantized','merge') AND baseModel <> ''
GROUP BY baseModel ORDER BY derivatives DESC LIMIT 12;
```

DuckDB can also read the file in place via `hf://datasets/ranjithraj/hf-landscape-study-data/models.parquet` where remote range requests are permitted.

---

## See also

- [HF Landscape](https://huggingface.co/spaces/ranjithraj/hf-landscape) — the live leaderboard and ecosystem dashboard this data drives
- [hf-landscape-study-data](https://huggingface.co/datasets/ranjithraj/hf-landscape-study-data) — the open dataset
- [CPU AI Gap Map](cpu-ai-gap-map.md) — per-task CPU maturity the task mix is scored against
- [CPU-Native Model Catalog](cpu-native-models.md) — the small models this data ranks at the top
- [CPU Fine-Tuning Benchmarks](cpu-finetuning-benchmarks.md) — proposal grounded in Finding 4
- [State of CPU Inference Report](state-of-cpu-inference-report.md) — proposal that consumes this dataset as an ecosystem-data source
