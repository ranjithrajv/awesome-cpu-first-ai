# Serverless CPU Cost Dashboard — Proposal

A proposal for an interactive dashboard that compares per-1M-token inference cost across serverless platforms — AWS Lambda (arm64), Fly.io, Modal, and GPU serverless — under a single, consistent cost model. It turns the static tables in [Serverless CPU Patterns](serverless-patterns.md) and the [Cost Calculator](cost-calculator.md) into a live tool that reflects a user's own traffic shape.

This is the [H1 2027 roadmap deliverable](../ROADMAP.md#later--h1-2027-jan-jun) ("Serverless cost comparison dashboard").

---

## Contents

- [Motivation](#motivation)
- [Proposed Scope](#proposed-scope)
- [Cost Model](#cost-model)
- [Inputs and Outputs](#inputs-and-outputs)
- [Dashboard Features](#dashboard-features)
- [Data Sources](#data-sources)
- [Implementation Sketch](#implementation-sketch)
- [Maintenance](#maintenance)
- [Relationship to Existing Assets](#relationship-to-existing-assets)
- [See also](#see-also)

---

## Motivation

Serverless cost is dominated by **traffic shape**, not sticker price. A workload with bursty, low-average traffic behaves completely differently on per-invocation billing (Lambda), per-second machine billing (Fly.io), and per-container-second billing (Modal) — and differently again against a GPU serverless minimum. The existing docs give worked examples at fixed traffic levels; what they can't do is let a reader plug in *their* request distribution and see the cross-over.

A dashboard closes that gap: enter average and peak req/s, model size, and token counts, and see the cheapest platform for that exact profile — including the point where a persistent CPU instance or a GPU beats serverless entirely.

---

## Proposed Scope

| Platform | Billing Model | Path |
|---|---|---|
| AWS Lambda (arm64/Graviton) | Per-request + GB-second | CPU |
| Fly.io CPU machines | Per-second machine time (scale-to-zero) | CPU |
| Modal CPU functions | Per-container-second | CPU |
| GPU serverless (baseline) | Per-second GPU time + cold-start floor | GPU |
| Persistent CPU instance (baseline) | Hourly (from [Cost Calculator](cost-calculator.md)) | CPU |

The two baselines matter: the dashboard's job is partly to show *when serverless stops being the answer*.

---

## Cost Model

Every platform is normalized to **$/1M tokens at the user's traffic profile**:

```
monthly_cost = Σ over requests [ per_request_charge + duration_s × per_second_rate ]
             + cold_start_overhead × cold_starts_per_month
             + fixed_floor

$/1M tokens  = monthly_cost / (monthly_tokens / 1_000_000)
```

Where:

- `duration_s` derives from model throughput (tok/s from the [Hardware Reference](hardware-reference.md)) and tokens per request.
- `cold_start_overhead` is platform-specific: ~100 ms for CPU page-cache warm starts, seconds for GPU VRAM load (see the [Decision Framework](cpu-vs-nvidia-decision-framework.md#total-cost-of-inference)).
- `fixed_floor` captures any minimum spend (provisioned concurrency, min machine count).

The formula is a direct extension of the [Cost Calculator's quick formula](cost-calculator.md#quick-formula), adding cold-start and per-invocation terms that only matter in the serverless regime.

---

## Inputs and Outputs

**Inputs (sliders / fields):**

- Model + quantization (drives tok/s via hardware presets)
- Average req/s and peak req/s (traffic shape)
- Input and output tokens per request
- Cold-start sensitivity (does the workload tolerate seconds of latency?)

**Outputs:**

- Ranked $/1M-token table across all platforms for the entered profile
- Cross-over chart: cost vs average req/s, one line per platform, cross-over points annotated
- A one-line verdict ("Lambda cheapest below ~2 req/s; persistent c7g.2xlarge cheapest above ~8 req/s")

---

## Dashboard Features

- **Traffic-shape sweep** — vary average req/s and watch the ranking reorder live.
- **Cold-start toggle** — show how GPU serverless economics collapse when traffic is bursty.
- **Break-even markers** — annotate where serverless loses to a persistent CPU instance and where CPU loses to GPU.
- **Shareable state** — encode inputs in the URL so a cost estimate can be linked in a design doc.
- **Pricing transparency** — every rate cites its source and last-verified date.

---

## Data Sources

| Source | Contribution |
|---|---|
| [Serverless CPU Patterns](serverless-patterns.md) | Per-platform billing models and cost-per-invocation worked examples |
| [Cost Calculator](cost-calculator.md) | Persistent-instance pricing and the base $/token formula |
| [Hardware Reference](hardware-reference.md) | tok/s presets that convert tokens into billable duration |
| [Benchmark Suite](benchmark-suite-proposal.md) results | Real throughput to replace hand-estimated tok/s over time |

---

## Implementation Sketch

Built as a Streamlit app alongside the existing [cost](../calculator/cost-calculator.py) and [power](../calculator/power-calculator.py) calculators, so it shares the `uv`-managed environment and needs no new toolchain:

```bash
uv run streamlit run calculator/serverless-dashboard.py
```

- Pricing lives in a versioned `calculator/serverless-pricing.yaml` with `last_verified` dates, not hardcoded in the app.
- Throughput presets are read from the benchmark results repository once it exists; until then, from the [Hardware Reference](hardware-reference.md) tables.
- No external API calls at runtime — pricing is a static, reviewed file so the tool is reproducible and offline-capable.

---

## Maintenance

- **Pricing refresh**: quarterly, tied to the same staleness cadence as the rest of the list; each rate carries a `last_verified` date surfaced in the UI.
- **Ownership**: the Cost Calculator maintainers, since the models are shared.
- **Drift guard**: the dashboard imports the Cost Calculator's formula module rather than reimplementing it, so the two never disagree.

---

## Relationship to Existing Assets

| Existing Asset | How This Builds On It |
|---|---|
| [Serverless CPU Patterns](serverless-patterns.md) | Promotes its static per-platform examples into an interactive, traffic-aware tool. |
| [Cost Calculator](cost-calculator.md) | Reuses its formula and pricing reference; adds serverless-only cold-start and per-invocation terms. |
| [CPU vs NVIDIA Decision Framework](cpu-vs-nvidia-decision-framework.md) | Supplies the GPU-serverless baseline and cold-start figures. |

---

## See also

- [Serverless CPU Patterns](serverless-patterns.md) — Per-platform billing models this dashboard operationalizes
- [Cost Calculator](cost-calculator.md) — Shared cost formula and pricing reference
- [CPU vs NVIDIA Decision Framework](cpu-vs-nvidia-decision-framework.md) — GPU-serverless baseline
- [Hardware Reference](hardware-reference.md) — Throughput presets
- [Roadmap](../ROADMAP.md) — Where this deliverable is scheduled
