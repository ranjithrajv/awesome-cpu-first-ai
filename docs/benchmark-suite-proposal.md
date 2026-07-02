# Benchmark Suite Proposal — Standardized CPU Inference Benchmarks

A proposal for a community-maintained, standardized CPU inference benchmark suite. The goal is to produce comparable, reproducible results across runtimes, CPU architectures, and quantization levels — reducing fragmentation (T5) by rallying behind a shared methodology and data format.

---

## Contents

- [Motivation](#motivation)
- [Proposed Scope](#proposed-scope)
- [Reference Workloads](#reference-workloads)
- [Output Format](#output-format)
- [Repository Structure](#repository-structure)
- [Governance](#governance)
- [Relationship to Existing Tools](#relationship-to-existing-tools)
- [See also](#see-also)

---

## Motivation

Today, CPU inference benchmarks are scattered across blog posts, GitHub issues, and vendor whitepapers — each using different models, batch sizes, context lengths, and reporting conventions. This fragmentation makes it hard for practitioners to:

- Compare runtimes (llama.cpp vs ONNX Runtime vs OpenVINO) on equal footing.
- Predict real-world throughput before buying cloud instances or hardware.
- Trust that published numbers are reproducible, not cherry-picked.

A standardized suite solves this by defining _what_ to benchmark, _how_ to benchmark it, and _where_ to publish the results — so the community builds a shared evidence base instead of maintaining private spreadsheets.

---

## Proposed Scope

The suite targets three deployment scenarios that cover the majority of CPU inference use cases:

| Scenario | Representative Model | Quantization | Key Metric |
|---|---|---|---|
| Desktop / laptop | Llama-3.2-3B-Instruct | Q4_K_M | tg128 (tok/s), TTFT (ms) |
| Server batch | Llama-3.1-8B | Q4_K_M, Q8_0 | Throughput at batch=1,4,8 |
| Edge / mobile | Phi-3.5-mini-3.8B | Q4, INT8 | tg128, peak memory (MB) |
| Embedding | BGE-small-en-v1.5 | FP32, INT8 | Latency p50/p95, throughput |

Additional workloads (vision, multimodal, speech) are added in a second phase.

### Reference Hardware Tiers

| Tier | Form Factor | Example Hardware | Expected tg128 (3B Q4) |
|---|---|---|---|
| S (laptop) | x86 laptop | Intel Core Ultra 7, AMD Ryzen 7 8840U | 18–30 tok/s |
| M (server x86) | Xeon / EPYC | c7i.4xlarge (Intel), m7a.4xlarge (AMD) | 30–55 tok/s |
| A (server ARM) | Neoverse V2/V3 | c8g.4xlarge (Graviton4), Cobalt 100 | 30–55 tok/s |
| E (edge ARM) | Cortex-A76/A78 | Raspberry Pi 5, Orange Pi 5 | 3–8 tok/s |

See [Hardware Reference](hardware-reference.md) for the full performance catalogue across all tiers, including mobile chipsets, laptops, SBCs, and server instances with pricing.

---

## Output Format

Every benchmark result is published as a structured YAML file following the [existing reporting template](benchmark-methodology.md#reporting-template), extended with:

```yaml
suite_version: 1.0
workload:
  scenario: server
  model: meta-llama/Llama-3.1-8B
  quantization: Q4_K_M
  context_length: 2048
  batch_size: 1
  num_runs: 5

hardware:
  tier: M
  cpu: "Intel Xeon Platinum 8480C @ 2.0 GHz"
  cores: 32
  threads: 64
  ram: 128 GB DDR5-4800
  numa_nodes: 2
  governor: performance
  microcode: "0x2b0004b1"

software:
  runtime: "llama.cpp b4043"
  build_flags: "-DCMAKE_BUILD_TYPE=Release -DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
  threads: 32
  numa: "distribute"

results:
  pp512: { mean: 420.3, stddev: 8.1, unit: "tok/s" }
  tg128: { mean: 34.7, stddev: 1.2, unit: "tok/s" }
  ttft:  { mean: 482,   stddev: 12,  unit: "ms" }
  tpot:  { mean: 28.8,  stddev: 1.0, unit: "ms" }
  peak_ram_mb: 6144
```

Results are collected in a public repository (see [Repository Structure](#repository-structure)) and displayed in the [Cost Calculator](cost-calculator.md) and [Power Calculator](../calculator/power-calculator.py) as selectable hardware profiles.

---

## Repository Structure

```
cpu-inference-benchmarks/
├── suite/
│   ├── v1.0.yaml              # Workload definitions, hardware tiers, pass/fail criteria
│   └── README.md              # How to run the suite locally
├── results/
│   ├── x86-server/
│   │   ├── intel-xeon-8480c-llamacpp-b4043.yaml
│   │   ├── amd-epyc-7b12-onnxruntime-1.20.yaml
│   │   └── ...
│   ├── arm-server/
│   │   ├── graviton4-c8g-llamacpp-b4043.yaml
│   │   └── ...
│   └── edge/
│       ├── rpi5-llamacpp-b4043.yaml
│       └── ...
├── aggregator/
│   ├── aggregator.py          # Generates summary tables from results/
│   └── outputs/
│       └── README.md           # Links to published summary (GitHub Pages or similar)
├── CONTRIBUTING.md            # How to submit new results
└── LICENSE
```

A companion GitHub Actions workflow runs the suite weekly on sponsored hardware (see [Governance](#governance)), auto-submits results, and re-generates the summary.

---

## Governance

- **Stewards**: 2–3 maintainers from this project, elected annually. Responsible for approving workload definition changes, reviewing result submissions, and managing the hardware sponsorship pool.
- **Result submissions**: Open to anyone via PR. Submissions must include the exact YAML output from the suite runner. Hardware providers (cloud vendors, hardware vendors) may submit results for their own platforms but must disclose the relationship.
- **Hardware sponsorship**: Cloud credits or loaner hardware from AWS, GCP, Azure, Oracle, Hetzner, and hardware vendors (Intel, AMD, Arm, Ampere) to run the suite on a regular cadence. Sponsors get a tier-agnostic "supported by" acknowledgement — no preferential placement or editorial control.
- **Versioning**: Suite definitions are versioned (v1.0, v1.1, …). Results are tagged with the suite version they were produced against. Breaking changes (new workloads, changed metrics) bump the major version.

---

## Relationship to Existing Tools

| Existing Asset | How the Suite Builds On It |
|---|---|
| [Benchmark Methodology](benchmark-methodology.md) | The suite adopts pp512/tg128/TTFT/TPOT and the reporting YAML schema as-is, extending only with suite-specific metadata. |
| [Cost Calculator](cost-calculator.md) | Suite results feed directly into the calculator as selectable hardware presets, replacing the current manual-entry model. |
| [Performance Tuning section](../README.md#performance-tuning) | Tuning best practices (numactl, governor, thread affinity) are codified in the suite runner script so all results follow them automatically. |
| MLPerf Inference | The suite targets _practitioner-friendly_ workloads that MLPerf does not cover (small models on laptop/edge, specific quant levels). The two are complementary. |

---

## See also

- [Benchmark Methodology](benchmark-methodology.md) — Existing standardized procedure this suite extends
- [Cost Calculator](cost-calculator.md) — TCO tool that can consume suite results
- [Green Inference Guide](green-inference.md) — Power/perf metrics the suite could adopt in v2.0
- [CPU Inference Deployment Guide](cpu-inference-deployment.md) — Tuning reference codified in the suite runner
