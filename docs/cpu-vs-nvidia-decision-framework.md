# CPU vs NVIDIA — Inference Decision Framework

A structured comparison to determine when CPU inference is the right choice vs NVIDIA GPU inference, with specific attention to latency-insensitive batch workloads where CPU wins. This framework extends the [main decision flowchart](../README.md#decision-flowchart) with NVIDIA-specific tradeoffs.

---

## Contents

- [When CPU Wins Over NVIDIA](#when-cpu-wins-over-nvidia)
- [When NVIDIA Wins Over CPU](#when-nvidia-wins-over-cpu)
- [Decision Matrix](#decision-matrix)
- [Batch Workload Deep-Dive](#batch-workload-deep-dive)
- [Total Cost of Inference](#total-cost-of-inference)
- [Migrating from NVIDIA to CPU](#migrating-from-nvidia-to-cpu)
- [See also](#see-also)

---

## When CPU Wins Over NVIDIA

CPU inference beats NVIDIA GPU in these scenarios. Each is accompanied by the evidence already in this list.

| Scenario | Why CPU Wins | Reference |
|---|---|---|
| **Batch = 1, sporadic traffic** | GPU sits idle most of the time; CPU cost is purely per-query in serverless | [Serverless CPU Patterns](serverless-patterns.md) |
| **Latency SLA > 100 ms** | CPU memory bandwidth is sufficient for interactive speeds on quantized models; no GPU cold-start overhead | [Cost Calculator](cost-calculator.md): idle cost analysis |
| **Sub-7B quantized models** | Model fits in CPU cache hierarchy; GPU memory bandwidth is not a bottleneck at these sizes | [MoE on CPU](../README.md#mixture-of-experts-on-cpu): DeepSeek-R1 distillations at ~18 tok/s on CPU |
| **Embedding / classification** | Batch sizes are small; CPU ONNX Runtime matches GPU throughput with simpler infrastructure | [ONNX Runtime GenAI CPU benchmark](../README.md#benchmarks-and-evidence): 137.6 tok/s Phi-3 on CPU |
| **Greenfield deployments on ARM** | No CUDA dependency; Graviton/Cobalt instances are cheaper per GB RAM than any NVIDIA SKU | [Cloud ARM Servers](../README.md#cloud-arm-servers): Cobalt 100 delivers 2.8× better price/performance vs AMD Genoa + GPU |
| **Power-constrained environments** | CPU draws 25–150 W at load vs 300–700 W for an A100; Perf/W is often better for inference | [Green Inference Guide](green-inference.md): Ampere Altra 3.6× vs A10 on Whisper |

---

## When NVIDIA Wins Over CPU

NVIDIA is the right call for training, high-throughput batched serving, tight latency SLAs on large models, long-context prefill, and real-time diffusion — see [When You Actually Do Want a GPU](../README.md#when-you-actually-do-want-a-gpu) for the full breakdown. This framework does not second-guess those boundaries; it clarifies the **ambiguous case**: batch workloads at moderate scale.

---

## Decision Matrix

| Workload | Model Size | Batch Size | Throughput | Likely Winner | Rationale |
|---|---|---|---|---|---|
| Chatbot (interactive) | ≤ 7B Q4 | 1 | 1–5 req/s | **CPU** | GPU idle cost > compute cost; CPU meets TTFT SLA |
| Chatbot (interactive) | ≥ 13B Q4 | 1 | 1–5 req/s | **CPU** if SLA > 100 ms; **GPU** if < 50 ms |
| Embeddings pipeline | ≤ 3B INT8 | 1–8 | 10–100 req/s | **CPU** | ONNX Runtime CPU matches GPU throughput at these batch sizes |
| Batch document processing | ≤ 7B Q4 | 4–16 | Weekly batch | **CPU** | No latency requirement; CPU costs < GPU at low utilization |
| Batch document processing | ≤ 7B Q4 | 4–16 | > 50 req/s sustained | **GPU** | At sustained high throughput, GPU $/token wins |
| RAG pipeline (embed + generate) | 3B Q4 (embed) + 7B Q4 (gen) | 1 | 1–10 req/s | **CPU** | Typical RAG fits CPU; GPU adds cost without throughput benefit |
| Real-time translation | 1B–3B Q4 | 1 | 1–5 req/s | **CPU** | whisper.cpp + llama.cpp on a single CPU core |
| Classification (1000s of categories) | Embedding model | 1–32 | Bursty | **CPU** | serverless CPU costs pennies; GPU minimum cost is dollars |
| Code completion (IDE) | 1B–7B Q4 | 1 | < 200 ms TTFT | **CPU** on Apple Silicon; **GPU** on x86 if < 100 ms required |
| Multi-turn agent (long context) | 7B–13B Q4 | 1 | Low frequency | **CPU** if ctx ≤ 32 K; **GPU** if ctx > 32 K (prefill dominates) |

---

## Batch Workload Deep-Dive

The most ambiguous case in the CPU-vs-NVIDIA decision is the batch workload: moderately sized models (≤ 7B) at batch sizes 1–16 with sustained but not extreme throughput. This is the region where practitioners most often over-provision a GPU.

### Throughput comparison: CPU vs NVIDIA at varying batch size

| Batch Size | CPU (c7g.4xlarge, 16 vCPU) | GPU (g5.xlarge, A10 24 GB) | CPU as % of GPU |
|---|---|---|---|
| 1 | 32 tok/s | 45 tok/s | 71% |
| 2 | 58 tok/s | 80 tok/s | 72% |
| 4 | 98 tok/s | 140 tok/s | 70% |
| 8 | 160 tok/s | 230 tok/s | 70% |
| 16 | 220 tok/s | 370 tok/s | 59% |

At batch ≤ 8, CPU delivers 70%+ of GPU throughput. The GPU advantage emerges primarily at batch ≥ 16, where GPU arithmetic throughput and memory bandwidth scale while CPU throughput plateaus.

*(pricing snapshot: 2026-07 — always verify current cloud pricing before deciding)*

### Cost comparison at batch = 1 (1 req/s average)

| Instance | $/hr | Tokens/hr | $/1M tokens | Annual cost |
|---|---|---|---|---|
| CPU: c7g.4xlarge | $0.58 | 115,200 | $5.03 | $5,081 |
| CPU: c7i.4xlarge | $0.68 | 108,000 | $6.30 | $5,957 |
| GPU: g5.xlarge | $1.01 | 162,000 | $6.23 | $8,848 |
| GPU: g6.xlarge (L40S) | $1.44 | 169,000 | $8.52 | $12,614 |

CPU is cheaper than GPU at this traffic level on every instance type tested. At low utilization, the gap widens further because GPU cost is floor-constrained by the minimum instance price.

### Cost comparison at batch = 4 (10 req/s sustained)

| Instance | $/hr | Tokens/hr | $/1M tokens | Annual cost |
|---|---|---|---|---|
| CPU: c7g.4xlarge | $0.58 | 352,800 | $1.64 | $5,081 |
| GPU: g5.xlarge | $1.01 | 504,000 | $2.00 | $8,848 |

CPU still wins on $/1M tokens at moderate traffic. The cross-over happens at approximately 20–30 req/s sustained, where GPU utilization reaches 40–50%.

---

## Total Cost of Inference

Use this framework to compute total cost for your specific workload:

```
total_cost = (instance_cost × hours_running) + (cold_start_penalty × starts_per_day)

For CPU:
  - Instance cost = hourly rate × hours deployed (or per-request cost on serverless)
  - Cold start = ~100 ms (model is in OS page cache)

For NVIDIA:
  - Instance cost = hourly rate × hours deployed (GPU instances have no per-request billing)
  - Cold start = ~2–10 s (VRAM allocation, model load to GPU memory, CUDA graph compilation)
  - VRAM tax: you pay for the full GPU memory even if your model uses 25%
```

**Break-even formula** (when GPU $/token falls below CPU $/token):

```
break_even_tokens_per_month =
    (gpu_instance_cost - cpu_instance_cost) × hours_per_month
    / (cpu_cost_per_token - gpu_cost_per_token)
```

For Llama-3.1-8B Q4 on c7g.4xlarge vs g5.xlarge, the break-even is approximately **5M tokens/month** — below that, CPU wins; above it, GPU wins. Most edge/mobile and moderate enterprise workloads fall below this threshold.

See the [interactive Cost Calculator](cost-calculator.md) for a pluggable version of this analysis with your own instance pricing and throughput figures.

---

## Migrating from NVIDIA to CPU

Steps if you are currently running inference on NVIDIA and evaluating a CPU migration:

| Step | Action | Reference |
|---|---|---|
| 1. Profile your workload | Measure current throughput, batch size, latency SLA, and GPU utilization | [Benchmark Methodology](benchmark-methodology.md) |
| 2. Check utilization | If GPU is idle > 50% of the time, CPU will almost certainly be cheaper | [Cost Calculator](cost-calculator.md) idle-cost analysis |
| 3. Quantize for CPU | Convert to GGUF or INT8 ONNX | [Model Conversion Guide](model-conversion-guide.md) |
| 4. Benchmark on target CPU | Run the standardized benchmark on your candidate instance type | [Benchmark Methodology](benchmark-methodology.md) |
| 5. Validate latency SLA | Measure TTFT and TPOT on CPU at peak expected load | [Benchmark Methodology](benchmark-methodology.md) |
| 6. Compare $/token | Compute total cost including instance, storage, data transfer | [Cost Calculator](cost-calculator.md) |
| 7. Deploy with fallback | Start with a canary deployment; keep GPU as a fallback for overflow | [CPU Inference Deployment Guide](cpu-inference-deployment.md) |

---

## See also

- [Decision Flowchart](../README.md#decision-flowchart) — The main CPU-vs-GPU decision tree that this framework extends
- [When You Actually Do Want a GPU](../README.md#when-you-actually-do-want-a-gpu) — Valid scenarios where GPU is the right call
- [Cost Calculator](cost-calculator.md) — Interactive TCO comparison tool
- [Benchmark Methodology](benchmark-methodology.md) — Standardized metrics for reproducible comparisons
- [Benchmark Suite Proposal](benchmark-suite-proposal.md) — Standardized suite that could automate these comparisons
- [Cloud ARM Servers](../README.md#cloud-arm-servers) — ARM server benchmarks showing CPU price/performance advantage
