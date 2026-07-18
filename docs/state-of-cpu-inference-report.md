# State of CPU Inference Report — Proposal

A proposal for a periodic, public "State of CPU Inference" report that aggregates the project's benchmark suite runs and community hackathon submissions into a single, citable snapshot of where CPU inference stands — tok/s, $/token, and W/token across architectures, runtimes, and workloads.

This is the [Q4 2026 roadmap deliverable](../ROADMAP.md#next--q4-2026-oct-dec) ("State of CPU Inference" report). It turns scattered result files into a narrative practitioners and decision-makers can cite.

---

## Contents

- [Motivation](#motivation)
- [Proposed Scope](#proposed-scope)
- [Report Structure](#report-structure)
- [Data Sources](#data-sources)
- [Headline Metrics](#headline-metrics)
- [Cadence and Publication](#cadence-and-publication)
- [Governance](#governance)
- [Relationship to Existing Assets](#relationship-to-existing-assets)
- [See also](#see-also)

---

## Motivation

The project already produces the raw material for a definitive status report — [standardized benchmarks](benchmark-suite-proposal.md), a [cost methodology](cost-calculator.md), [energy/carbon figures](green-inference.md), and a [per-category gap analysis](cpu-ai-gap-map.md). What's missing is a periodic synthesis that answers, in one place:

- How fast is CPU inference *today*, across the workloads people actually deploy?
- What does it cost per token and per watt, and how has that moved since the last report?
- Which gaps closed, which persist, and what changed in the ecosystem (new runtimes, ISAs, MLPerf rounds)?

A recurring report gives the CPU-first argument a dated, reproducible evidence base — the kind of artifact that gets cited in architecture reviews and procurement decisions, rather than a blog post that goes stale silently.

---

## Proposed Scope

The report covers the workload categories already scored in the [CPU AI Gap Map](cpu-ai-gap-map.md), reported against the [reference hardware tiers](hardware-reference.md#hardware-tiers):

| Dimension | Coverage |
|---|---|
| Workloads | LLM decode + prefill, ASR/STT, TTS, embeddings, vision (detection/segmentation/OCR), diffusion, fine-tuning |
| Hardware tiers | S (laptop), M (server x86), A (server ARM), E (edge ARM) — plus mobile chipsets |
| Runtimes | llama.cpp, ONNX Runtime, OpenVINO, whisper.cpp, and any runtime with published suite results |
| Axes | Throughput (tok/s), cost ($/1M tokens), energy (W/token, gCO₂/query) |

Out of scope: proprietary/unpublished numbers, and any result that does not follow the [benchmark methodology](benchmark-methodology.md).

---

## Report Structure

```
State of CPU Inference <year>
├── Executive summary        # 1 page: the three headline numbers + what changed
├── Methodology              # Links to benchmark-methodology.md; states data cutoff
├── Per-workload chapters    # One per gap-map category: throughput, cost, energy, verdict
├── Cross-cutting trends      # New ISAs (AMX, SME2), quantization, MoE, ternary
├── Cost & sustainability    # $/token and W/token tables, region-adjusted carbon
├── Gap scorecard delta      # Gap-map stage changes since the previous report
└── Appendix                 # Full result tables, hardware profiles, contributor credits
```

Each per-workload chapter ends with a one-line **verdict** ("CPU-native", "viable with caveats", "GPU still required") consistent with the gap-map maturity stages.

---

## Data Sources

| Source | Contribution |
|---|---|
| [Benchmark Suite](benchmark-suite-proposal.md) results repository | Throughput, TTFT/TPOT, peak RAM per hardware/runtime/workload |
| [Community Hackathon](community-hackathon.md) submissions | Real-world deployment case studies and reproduction runs |
| [Cost Calculator](cost-calculator.md) | $/1M-token figures from current cloud pricing |
| [Green Inference Guide](green-inference.md) | W/token and gCO₂/query from RAPL/IPMI measurements |
| [CPU AI Gap Map](cpu-ai-gap-map.md) | Per-category maturity stages and gap classification |

All numbers must trace back to a published, versioned result file — no hand-entered figures in the report body.

---

## Headline Metrics

The executive summary leads with three comparable, year-over-year numbers:

1. **Throughput** — median tg128 for a 7B Q4 model on the M (server x86) and A (server ARM) tiers.
2. **Cost** — $/1M tokens for that same workload at batch = 1 and at the batch where CPU/GPU cross over.
3. **Energy** — W/token and gCO₂/query on the reference server tier, US-grid and green-grid variants.

Each is reported as `value (Δ vs previous report)` so the trajectory is visible at a glance.

---

## Cadence and Publication

- **Cadence**: annual full report, with an optional mid-year data refresh if the results repository grows > 50%.
- **Format**: Markdown in this repository (`reports/state-of-cpu-inference-<year>.md`), rendered to the GitHub Pages [site](../index.html), plus a PDF export for citation.
- **Versioning**: each report is tagged with the benchmark suite version and a hard data-cutoff date.
- **Reproducibility**: every figure links to the result file and the suite version that produced it.

---

## Governance

- **Editors**: the benchmark suite stewards (see [Benchmark Suite Proposal — Governance](benchmark-suite-proposal.md#governance)) act as report editors.
- **Contributions**: anyone whose submitted results or hackathon projects are included is credited in the appendix.
- **Neutrality**: hardware and cloud sponsors are acknowledged but receive no editorial control or preferential framing, consistent with the suite's sponsorship rules.

---

## Relationship to Existing Assets

| Existing Asset | How the Report Builds On It |
|---|---|
| [Benchmark Suite Proposal](benchmark-suite-proposal.md) | The report is the human-readable synthesis of the suite's machine-readable results. |
| [CPU AI Gap Map](cpu-ai-gap-map.md) | The report tracks stage-to-stage deltas over time; the gap map is the point-in-time snapshot. |
| [Cost Calculator](cost-calculator.md) / [Green Inference Guide](green-inference.md) | Supply the canonical cost and energy figures the report quotes. |
| [Community Hackathon](community-hackathon.md) | Feeds real-world case studies into the per-workload chapters. |

---

## See also

- [Benchmark Suite Proposal](benchmark-suite-proposal.md) — The results this report synthesizes
- [CPU AI Gap Map](cpu-ai-gap-map.md) — Per-category maturity the report tracks over time
- [Cost Calculator](cost-calculator.md) — Canonical $/token figures
- [Green Inference Guide](green-inference.md) — Canonical W/token and carbon figures
- [Community Hackathon](community-hackathon.md) — Case-study source
- [Roadmap](../ROADMAP.md) — Where this deliverable is scheduled
