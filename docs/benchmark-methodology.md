# Benchmark Methodology

Standardized procedure for running and reporting CPU inference benchmarks. Following this ensures results across the community are comparable and reproducible.

---

## Contents

- [Metrics](#metrics)
  - [Which metric to use](#which-metric-to-use)
- [Reporting Template](#reporting-template)
- [Procedure](#procedure)
  - [Preparation](#preparation)
  - [Running the Benchmark](#running-the-benchmark)
  - [Warmup](#warmup)
  - [Reporting](#reporting)
- [Common Pitfalls](#common-pitfalls)
- [See also](#see-also)

---

## Metrics

| Metric | Definition | What it tells you |
|---|---|---|
| **pp512** | Prompt processing, 512 tokens | How fast the model ingests prompts (prefill). Memory-bandwidth bound. |
| **tg128** | Token generation, 128 tokens | How fast the model generates each output token. Memory-bandwidth bound. |
| **TTFT** | Time to first token | Latency from sending prompt to receiving first output token. Includes prefill. |
| **TPOT** | Time per output token | Average latency per generated token after the first. |
| **t/s** | Tokens per second | Overall throughput: `generated_tokens / wall_clock_time`. |

### Which metric to use

- **Interactive use** (chatbots, coding assistants): optimize for TTFT + TPOT at batch=1.
- **Batch/offline** (embeddings, document processing): optimize for t/s at larger batch sizes.

---

## Reporting Template

When submitting benchmark results, include:

```yaml
hardware:
  cpu: "AMD EPYC 7B12 @ 2.25 GHz"
  cores: 16
  threads: 32
  ram: 64 GB DDR4-3200
  l3_cache: 64 MB
  numa_nodes: 2
  governor: performance

software:
  runtime: "llama.cpp b4043"
  build: "cmake -DCMAKE_BUILD_TYPE=Release"
  model: "Llama-3.2-3B-Instruct Q4_K_M"
  threads: 16
  batch_size: 1

results:
  pp512: 45.2 t/s
  tg128: 24.8 t/s
  ttft: 480 ms
  tpot: 40.3 ms
  tokens_per_second: 24.8
```

---

## Procedure

```mermaid
flowchart LR
    A[Preparation\ngovernor · turbo · NUMA pin] --> B[Warmup\ndiscard first run]
    B --> C[Run Benchmark\nllama-bench, 5+ runs]
    C --> D[Reporting\nmean ± stddev, pp512/tg128]
```

### Preparation

1. Set CPU governor to `performance`:
   ```bash
   sudo cpupower frequency-set -g performance
   ```

2. Disable frequency scaling and turbo boost for reproducible results (optional but recommended):
   ```bash
   echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
   ```

3. Pin to a single NUMA node:
   ```bash
   numactl --cpunodebind=0 --membind=0
   ```

4. Record system state:
   ```bash
   cat /proc/cpuinfo | grep "model name" | head -1
   numactl --hardware | head -3
   free -h
   ```

### Running the Benchmark

```bash
numactl --cpunodebind=0 --membind=0 \
  ./llama-bench \
    --model /models/llama-3.2-3b-q4_k_m.gguf \
    --threads 16 \
    --numa distribute \
    --n-gpu-layers 0 \
    --output json
```

### Warmup

Run at least one inference before recording results. The first run includes compilation/cache effects that do not reflect steady-state throughput:

```bash
# Discard first run
./llama-cli --model model.gguf --prompt "warmup" -n 1
```

### Reporting

- Report the **mean** and **standard deviation** across 5+ runs.
- Always report `pp512` and `tg128` values.
- If reporting throughput at batch > 1, state the batch size explicitly.
- Note the quantization level and context length used.

---

## Common Pitfalls

| Pitfall | Effect | Fix |
|---|---|---|
| `powersave` governor active | 20–50% lower throughput | `cpupower frequency-set -g performance` |
| Cross-socket memory access | 30–50% throughput loss | `numactl --cpunodebind=0 --membind=0` |
| SMT enabled + thread count > physical cores | 10–20% throughput variability | Disable SMT or limit threads to physical cores |
| Cold start (first run included) | Results 2–5× slower than steady-state | Discard first 1–2 runs |
| Benchmarking while system is under load | Unpredictable results | Isolate the system or use `cset shield` |
| Different input/output lengths | Non-comparable t/s values | Standardize on pp512/tg128 |

---

## See also

- [Cost Calculator](cost-calculator.md)
- [CPU Inference Deployment Guide](cpu-inference-deployment.md)
- [Troubleshooting](troubleshooting.md)
- [Model Conversion Guide](model-conversion-guide.md)
