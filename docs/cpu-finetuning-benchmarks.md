# CPU Fine-Tuning Benchmarks — Proposal

A proposal to add LoRA/QLoRA fine-tuning throughput and cost benchmarks on CPU to the project's [benchmark suite](benchmark-suite-proposal.md). Fine-tuning is the least-mature category in the [CPU AI Gap Map](cpu-ai-gap-map.md#10-fine-tuning-lora--qlora) (CPU Stage 3, "viable but slow"; NPU Stage 0). Measured data would replace the current "it works but nobody publishes numbers" state with reproducible figures.

This is the [H1 2027 roadmap deliverable](../ROADMAP.md#later--h1-2027-jan-jun) ("CPU fine-tuning benchmarks").

---

## Contents

- [Motivation](#motivation)
- [Proposed Scope](#proposed-scope)
- [Reference Workloads](#reference-workloads)
- [Metrics](#metrics)
- [Output Format](#output-format)
- [Tooling](#tooling)
- [Caveats and Honest Framing](#caveats-and-honest-framing)
- [Relationship to Existing Assets](#relationship-to-existing-assets)
- [See also](#see-also)

---

## Motivation

Inference on CPU is well-benchmarked; fine-tuning is not. Yet the two questions practitioners actually ask are: *"Can I adapt a small model on the hardware I already have?"* and *"How long, and at what cost?"* The gap map scores fine-tuning at CPU Stage 3 precisely because the tooling exists ([llama.cpp finetune](https://github.com/ggml-org/llama.cpp), PEFT/LoRA on CPU) but the performance envelope is undocumented.

Publishing standardized CPU fine-tuning numbers would:

- Let teams decide between an overnight CPU LoRA run and renting a GPU by the hour.
- Quantify the parameter-efficient-tuning sweet spot on CPU (adapter rank vs time vs quality).
- Extend the CPU-first argument from serving into the adaptation phase, where "the output deploys on CPU anyway" is already true (see the gap-map fine-tuning caveat).

---

## Proposed Scope

The suite targets **parameter-efficient** fine-tuning only — full fine-tuning of 7B+ models on CPU is out of scope as impractical.

| Method | Base Models | Precision | Rationale |
|---|---|---|---|
| LoRA | Llama-3.2-1B, Llama-3.2-3B | BF16 / FP16 base | Fastest path; adapter-only gradients |
| QLoRA | Llama-3.1-8B | 4-bit (NF4) base | Fits 8B adaptation in commodity RAM |
| LoRA | Phi-3.5-mini-3.8B | BF16 base | Popular small-model target |

Second phase (optional): embedding-model fine-tuning (sentence-transformers) and small ASR adapter tuning.

---

## Reference Workloads

Each run is a fixed, small adaptation task so results are comparable:

| Parameter | Value |
|---|---|
| Dataset | 10,000-example instruction set (fixed, published with the suite) |
| Sequence length | 512 tokens |
| Adapter rank (r) | 8 and 16 (reported separately) |
| Epochs | 1 (report tokens/s; extrapolate longer runs linearly) |
| Batch size | 1 and 4 (gradient accumulation to a fixed effective batch) |
| Optimizer | AdamW (8-bit where supported) |

Runs execute on the [reference hardware tiers](hardware-reference.md#hardware-tiers) — laptop (S), server x86 (M), and server ARM (A). Edge (E) is measured best-effort; sub-3B LoRA on a Raspberry Pi 5 is a documented data point even if slow.

---

## Metrics

| Metric | Definition | Why it matters |
|---|---|---|
| **train_tok/s** | Training tokens processed per second (fwd+bwd) | Core throughput number |
| **time_to_adapter** | Wall-clock for the full reference task | The "overnight or not?" answer |
| **peak_ram_mb** | Peak resident memory | Determines the minimum instance class |
| **$/adapter** | `time_to_adapter × instance $/hr` on the tier's reference cloud instance | Direct comparison vs a GPU hourly rental |
| **W/adapter** | Energy for the full run via RAPL/IPMI | Ties into the [Green Inference Guide](green-inference.md) |

Quality (eval loss / task metric) is recorded for sanity but is *not* a suite pass/fail axis — the suite measures cost of adaptation, not model quality.

---

## Output Format

Results reuse the [benchmark reporting YAML](benchmark-methodology.md#reporting-template), extended with a `finetune` block:

```yaml
suite_version: 1.0
workload:
  task: finetune
  method: qlora
  base_model: meta-llama/Llama-3.1-8B
  base_precision: nf4
  adapter_rank: 16
  seq_len: 512
  dataset: cpu-suite-instruct-10k
  effective_batch: 16

hardware:
  tier: M
  cpu: "AMD EPYC 9354 @ 3.25 GHz"
  cores: 32
  ram: 128 GB DDR5-4800
  governor: performance

software:
  runtime: "llama.cpp finetune (b4043)"
  threads: 32

results:
  train_tok_s: { mean: 210.5, stddev: 6.2, unit: "tok/s" }
  time_to_adapter: { value: 2.7, unit: "hours" }
  peak_ram_mb: 11800
  cost_per_adapter_usd: 1.89
  energy_wh: 640
```

Results land in the same benchmark results repository under a `results/finetune/` subtree.

---

## Tooling

- [llama.cpp finetune](https://github.com/ggml-org/llama.cpp) — GGUF-native LoRA on CPU; the primary target.
- [Hugging Face PEFT](https://github.com/huggingface/peft) — LoRA/QLoRA on the PyTorch CPU backend for cross-checking.
- [ONNX Runtime training](https://onnxruntime.ai/docs/) — optional third data point for embedding-model adapters.

The suite runner pins thread count, governor, and NUMA binding exactly as the [inference suite](benchmark-suite-proposal.md#relationship-to-existing-tools) does, so fine-tuning and inference results are directly comparable.

---

## Caveats and Honest Framing

Consistent with the gap map's fine-tuning caveats:

- CPU fine-tuning is **slow** — expect hours where a GPU takes minutes. The report frames this as an availability/cost trade, not a speed win.
- Numbers are for **adapter** training; the base model is frozen. Full fine-tuning is explicitly excluded.
- QLoRA base-model quantization affects final quality; the suite records eval loss so readers can judge the quality/cost trade themselves.

---

## Relationship to Existing Assets

| Existing Asset | How This Builds On It |
|---|---|
| [Benchmark Suite Proposal](benchmark-suite-proposal.md) | Adds a `finetune` workload class using the same methodology and repo structure. |
| [CPU AI Gap Map](cpu-ai-gap-map.md#10-fine-tuning-lora--qlora) | Supplies measured data to re-score the Stage 3 fine-tuning category. |
| [Cost Calculator](cost-calculator.md) | The `$/adapter` metric reuses the calculator's pricing reference. |
| [Model Conversion Guide](model-conversion-guide.md) | Adapter merge/export steps for deploying the tuned model on CPU. |

---

## See also

- [Benchmark Suite Proposal](benchmark-suite-proposal.md) — The suite this extends
- [Benchmark Methodology](benchmark-methodology.md) — Shared metrics and reporting schema
- [CPU AI Gap Map](cpu-ai-gap-map.md#10-fine-tuning-lora--qlora) — The fine-tuning gap this measures
- [Model Conversion Guide](model-conversion-guide.md) — Deploying the resulting adapters on CPU
- [Roadmap](../ROADMAP.md) — Where this deliverable is scheduled
