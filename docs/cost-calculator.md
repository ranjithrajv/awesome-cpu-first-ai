# CPU vs GPU Cost Calculator

A reusable methodology for comparing inference costs across CPU and GPU instances. Use this to build your own estimates with current cloud pricing.

---

## Contents

- [Quick Formula](#quick-formula)
- [Calculator App](#calculator-app)
- [Cloud Pricing Reference (us-east-1, June 2026)](#cloud-pricing-reference-us-east-1-june-2026)
- [Throughput Reference](#throughput-reference)
- [Break-even Analysis](#break-even-analysis)
- [Production Worked Example (Llama-3 8B, us-east-1, June 2026)](#production-worked-example-llama-3-8b-us-east-1-june-2026)
  - [Cost-per-token reference](#cost-per-token-reference)
  - [Worked TCO example — 1 req/s, 730 hrs/month](#worked-tco-example--1-reqs-730-hrsmonth)
  - [Footnotes](#footnotes)
- [See also](#see-also)
- [References](#references)

---

## Quick Formula

```
$/1M tokens = (instance $/hr × 1,000,000) / (tok/s × 3,600 × utilization%)
```

For CPU:
```
$/1M tokens = ($0.35/hr × 1,000,000) / (25 tok/s × 3,600 × 1.0) = $3.89
```

For GPU:
```
$/1M tokens = ($1.006/hr × 1,000,000) / (63 tok/s × 3,600 × 1.0) = $4.43
```

At 100% utilization they're close. At 50% GPU utilization the effective GPU cost doubles to $8.86 — CPU wins.

---

## Calculator App

Interactive Streamlit app with utilisation sweep, TCO worked example, and per-request cost.

```bash
uv run streamlit run calculator/cost-calculator.py
```

`uv` resolves dependencies from [calculator/pyproject.toml](../calculator/pyproject.toml) automatically — no `pip install` or virtualenv needed. Source: [calculator/cost-calculator.py](../calculator/cost-calculator.py) · Folder docs: [calculator/README.md](../calculator/README.md)

---

## Cloud Pricing Reference (us-east-1, June 2026)

| Instance | vCPU | RAM | $/hr | Use case |
|---|---|---|---|---|
| c7g.large | 2 | 4 GB | $0.085 | Embeddings, small models |
| c7g.xlarge | 4 | 8 GB | $0.170 | 1–3B Q4 models |
| c7g.2xlarge | 8 | 16 GB | $0.35 | 7–8B Q4 models |
| c7g.4xlarge | 16 | 32 GB | $0.58 | 7–8B Q4 + throughput |
| c7g.16xlarge | 64 | 128 GB | ~$2.32 | 13B Q4, high throughput |
| g5.xlarge | 4 + A10G | 24 GB VRAM | $1.006 | Small LLM inference |
| g5.2xlarge | 8 + A10G | 24 GB VRAM | $1.212 | Higher throughput |

Verify at [aws.amazon.com/ec2/pricing](https://aws.amazon.com/ec2/pricing/on-demand/).

---

## Throughput Reference

| Model | Quant | CPU (c7g, Graviton3) | GPU (g5, A10G) |
|---|---|---|---|
| Llama-3-8B | Q4_K_M | ~25 tok/s | ~63 tok/s |
| Llama-3-8B | FP16 | ~10 tok/s | ~180 tok/s |
| Llama-3-8B | FP16 batch=32 | ~106 tok/s | ~1,820 tok/s |
| Llama-3.2-3B | Q4_K_M | ~55 tok/s | ~120 tok/s |
| Llama-3.2-1B | Q4_K_M | ~110 tok/s | ~250 tok/s |

---

## Break-even Analysis

GPU wins on raw $/token when utilization is high. CPU wins when:

1. **Idle time > 40%** — GPU paid regardless, CPU costs scale with work done
2. **Model fits in RAM but not VRAM** — GPU forces a more expensive instance class
3. **Sporadic traffic** — serverless CPU charges per-invocation only
4. **Batch = 1** — GPU memory bandwidth advantage shrinks at single-request throughput

To find your break-even: divide GPU instance cost by CPU instance cost, then multiply by the CPU/GPU throughput ratio. If the result is < 1, GPU wins at full utilization.

---

## Production Worked Example (Llama-3 8B, us-east-1, June 2026)

### Cost-per-token reference

| Instance | $/hr | Accelerator | Decode, batch=1 | Decode, batch=32 | $/1M tokens (batch=32, 100% util) |
|---|---|---|---|---|---|
| c7g.16xlarge (Graviton3) | ~$2.32 ¹ | 64 vCPU, CPU only | ~17 tok/s ² | ~106 tok/s ² | ~$6.10 |
| g5.xlarge | $1.006 ³ | 4 vCPU + A10G 24 GB | ~63 tok/s ⁴ | ~1,820 tok/s ⁴ | ~$0.15 (~$0.55 at 50% util) ⁴ |

**Reading this table correctly.** At sustained batch load the GPU has a ~40× $/token advantage — that is not a rounding error. The economic case for CPU rests on factors the table does not capture:

1. **Idle cost dominates sporadic workloads.** A c7g.4xlarge at $0.58/hr is 42% cheaper than a g5.xlarge simply sitting idle. At < 10% GPU utilization the effective $/token gap shrinks proportionally; at near-zero traffic the GPU minimum cost is pure overhead.
2. **Serverless CPU eliminates the idle floor entirely.** AWS Lambda (arm64), Fly.io CPU machines, and Modal CPU workers are billed per-invocation — there is no standing charge when inference is not happening.
3. **VRAM is a hard ceiling; system RAM is not.** A 12 GB quantized model runs on any instance with ≥ 16 GB RAM at commodity pricing; on GPU it requires a VRAM class that costs $1+/hr regardless of utilization. Larger quantized models hit this ceiling repeatedly.

### Worked TCO example — 1 req/s, 730 hrs/month

Suppose you serve a 7B Q4 model with moderate traffic averaging 1 req/s (peak 5 req/s), batch = 1, over 730 hrs/month:

| Cost component | CPU (c7g.2xlarge, 8 vCPU, 16 GB) | GPU (g5.xlarge, A10G 24 GB) |
|---|---|---|
| Instance cost | $0.35/hr × 730 = $256/mo | $1.006/hr × 730 = $734/mo |
| Idle hours (60% of time @ 1 req/s) | $0 — CPU is doing useful work | $0 but GPU paid regardless |
| Effective $/req (incl. throughput) | ~$0.0035/req | ~$0.010/req |
| 12-month TCO | ~$3,070 | ~$8,810 |

CPU saves **$5,740/yr** on this workload. At 5 req/s peak the gap narrows but does not close until GPU utilization exceeds ~50%. Below that, CPU wins on every economic axis. (Assumes Llama-3-8B Q4_K_M at ~25 tok/s on c7g.2xlarge and ~63 tok/s on g5.xlarge.)

### Footnotes

1. Price extrapolated linearly from verified c7g.4xlarge ($0.58/hr, 16 vCPU) — verify at [aws.amazon.com/ec2/pricing](https://aws.amazon.com/ec2/pricing/on-demand/).
2. 64-core Graviton3 (Neoverse V1), Llama-3 8B, FP16 implementation; decode improves further with Q4_0_8_8 quantization. Source: [arxiv:2501.00032](https://arxiv.org/abs/2501.00032).
3. [economize.cloud](https://www.economize.cloud/resources/aws/pricing/ec2/g5.xlarge/), us-east-1 on-demand, June 2026.
4. SGLang on g5.xlarge; $0.55/1M at 50% utilization cited directly. Sources: [markaicode](https://markaicode.com/pricing/amazon-ec2-self-hosted-llm-inference-cost-analysis/) and [Medium benchmark](https://medium.com/@me.shivansh007/benchmarking-sglang-vllm-and-ollama-0179e3a5cbaa) (April–June 2026).

---

See also: [CPU vs NVIDIA Decision Framework](cpu-vs-nvidia-decision-framework.md) · [Serverless CPU Patterns](serverless-patterns.md) · [Green Inference Guide](green-inference.md) · [CPU Inference Deployment Guide](cpu-inference-deployment.md)

---

## References

- [aws.amazon.com/ec2/pricing](https://aws.amazon.com/ec2/pricing/on-demand/)
- [arxiv:2501.00032](https://arxiv.org/abs/2501.00032)
- [economize.cloud](https://www.economize.cloud/resources/aws/pricing/ec2/g5.xlarge/)
- [markaicode](https://markaicode.com/pricing/amazon-ec2-self-hosted-llm-inference-cost-analysis/)
- [Medium benchmark](https://medium.com/@me.shivansh007/benchmarking-sglang-vllm-and-ollama-0179e3a5cbaa)
