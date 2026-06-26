# CPU vs GPU Cost Calculator

A reusable methodology for comparing inference costs across CPU and GPU instances. Use this to build your own estimates with current cloud pricing.

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

## Calculator Script

Save as `calc-cost.sh` and run with `bash calc-cost.sh`:

```bash
#!/usr/bin/env bash
# CPU vs GPU inference cost comparison
# Usage: ./calc-cost.sh [tokens_per_second_cpu] [tokens_per_second_gpu]

CPU_TOK=${1:-25}
GPU_TOK=${2:-63}
CPU_PRICE=${3:-0.35}     # c7g.2xlarge $/hr
GPU_PRICE=${4:-1.006}    # g5.xlarge $/hr
HOURS=${5:-730}          # monthly hours

echo "=== CPU vs GPU Inference Cost ==="
echo "Model: Llama-3-8B Q4_K_M"
echo "CPU: ${CPU_TOK} tok/s at \$${CPU_PRICE}/hr"
echo "GPU: ${GPU_TOK} tok/s at \$${GPU_PRICE}/hr"
echo ""

for UTIL in 1.0 0.5 0.25 0.1; do
  CPU_COST=$(echo "scale=4; $CPU_PRICE * 1000000 / ($CPU_TOK * 3600 * $UTIL)" | bc)
  GPU_COST=$(echo "scale=4; $GPU_PRICE * 1000000 / ($GPU_TOK * 3600 * $UTIL)" | bc)
  CPU_MONTHLY=$(echo "scale=2; $CPU_PRICE * $HOURS" | bc)
  GPU_MONTHLY=$(echo "scale=2; $GPU_PRICE * $HOURS" | bc)
  echo "At ${UTIL}x utilization ($((UTIL * 100))%):"
  echo "  CPU: \$${CPU_COST}/1M tokens  | \$${CPU_MONTHLY}/mo"
  echo "  GPU: \$${GPU_COST}/1M tokens  | \$${GPU_MONTHLY}/mo"
  echo ""
done
```

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
