# CPU Inference Hackathon — Proposal

A structured, remote-first hackathon to generate real-world CPU inference examples, benchmark data, and deployment patterns — sponsored by serverless and cloud CPU providers. The goal is to build community engagement (W4) while creating a durable evidence base that makes CPU inference visible and credible against dropping GPU prices (T1) and runtime fragmentation (T5).

---

## Contents

- [Format](#format)
- [Tracks](#tracks)
- [Sponsorship Model](#sponsorship-model)
- [Deliverables](#deliverables)
- [Judging Criteria](#judging-criteria)
- [Timeline](#timeline)
- [Prizes](#prizes)
- [Post-Hackathon](#post-hackathon)
- [See also](#see-also)

---

## Format

- **Duration**: 2 weeks (including a kickoff weekend + closing showcase).
- **Location**: Fully remote — participants work from anywhere. Coordination via a dedicated Discord server and GitHub Discussions.
- **Team size**: 1–4 people.
- **Cost to participate**: Free. Cloud credits provided by sponsors.

Participants build and document a real CPU inference deployment, then submit a PR to this repository adding their project, methodology, and results to a new `Community Submissions` section.

---

## Tracks

### Track 1: Production Deployment

Deploy a real inference workload on CPU infrastructure (server, serverless, or edge) and document the full stack:

| Element | Required | Bonus |
|---|---|---|
| Model + runtime selection | Chosen model fits RAM with quant to spare | Comparison vs a GPU baseline on cost-per-1M-tokens |
| Infrastructure-as-code | Dockerfile or Terraform/Pulumi | Kubernetes deployment with NUMA-aware scheduling |
| Load test | Sustained 30-min run with k6 or similar | Latency heatmap across NUMA nodes |
| Cost analysis | Instance pricing × duration | Break-even point vs smallest viable GPU instance |
| Reproducibility | `README.md` with exact commands | Automated CI pipeline that re-deploys and tests |

### Track 2: Benchmark Contribution

Run the [standardized benchmark suite](benchmark-suite-proposal.md) on hardware not yet represented in the results repository:

- Target unrepresented hardware tiers (e.g., AMD Bergamo, Apple M4 Ultra, AmpereOne, RISC-V).
- Submit the structured YAML output plus a brief hardware profile.
- Bonus: run on all three runtimes (llama.cpp, ONNX Runtime, OpenVINO) for an apples-to-apples comparison.

### Track 3: Integration

Build a tool, adapter, or integration that makes CPU inference easier for a specific ecosystem:

| Idea | Description |
|---|---|
| GitHub Action for CPU inference CI | Run model inference as a CI step on GitHub-hosted runners (ARM64) — no GPU needed |
| VS Code extension | Inline model completions using a local CPU runtime |
| Home Assistant add-on | Voice assistant (whisper.cpp + llama.cpp) running on a Raspberry Pi 5 |
| Slack bot | Deploy a CPU-hosted Slack bot using Modal or Fly.io |
| OpenTelemetry instrumentation | Trace CPU inference spans and export metrics for observability |

---

## Sponsorship Model

### Tier 1 — Cloud Credits ($5,000+ equivalent)

| Sponsor | Contribution | Recipient |
|---|---|---|
| AWS | $200 credits per team × 25 teams | Teams in Track 1 deploying on AWS Graviton |
| GCP | $200 credits per team × 25 teams | Teams deploying on Axion C4A |
| Azure | $200 credits per team × 25 teams | Teams deploying on Cobalt 100/200 |
| Oracle | Free-tier Ampere A1 for all participants | All teams for the duration |
| Fly.io / Modal | Free-tier or waived compute | Serverless-track teams |

### Tier 2 — Hardware Loans

| Sponsor | Contribution | Purpose |
|---|---|---|
| Intel | Loaner Xeon 6 Granite Rapids nodes | Track 2 benchmark submissions |
| Ampere | Loaner AmpereOne dev kit | ARM server benchmark submissions |
| Raspberry Pi Foundation | Raspberry Pi 5 units | Edge/mobile-track teams |

### Tier 3 — Community Partners

| Partner | Contribution |
|---|---|
| Hugging Face | Feature on HF Daily Papers or Gradio showcase |
| MLCommons | Certificate of participation for MLPerf-style submissions |
| CNCF / TAG Runtime | Cross-post to Kubernetes and serverless communities |

---

## Deliverables

Each team submits a PR to this repository that adds:

1. **Project entry** in a new `## Community Submissions` section of the README — one-line description linking to their write-up.
2. **Write-up** in `docs/community/<team-name>/README.md` covering architecture, deployment steps, load test results, cost breakdown, and lessons learned.
3. **Reproducibility artifacts** — scripts, configs, or IaC templates in the same directory.
4. **Benchmark results** (if Track 2) in the suite's YAML format.

A successful PR must pass the same CI checks as any other contribution: link check, ToC validation, and snippet syntax validation.

---

## Judging Criteria

| Criterion | Weight | What the judges look for |
|---|---|---|
| Reproducibility | 30% | Can a stranger re-deploy from the write-up? |
| Rigor | 25% | Are load tests, cost analysis, and methodology documented? |
| Real-world relevance | 20% | Does this solve a genuine problem a practitioner would face? |
| CPU-first philosophy | 15% | Does the submission demonstrate a clear CPU-vs-GPU rationale? |
| Presentation | 10% | Clarity of writing, diagrams, and project structure |

Judges are drawn from the project maintainers, sponsor technical staff, and one external community member.

---

## Timeline

| Milestone | Date (example) |
|---|---|
| Announcement + registration opens | **Week 0 — Mon** |
| Kickoff stream / AMA with sponsors | **Week 0 — Fri** |
| Hacking period | **Weeks 1–2** |
| Mid-point check-in (Discord office hours) | **Week 1 — Wed** |
| Submission deadline | **Week 2 — Fri 23:59 AoE** |
| Judging period | **Week 3** |
| Winners announced + showcase stream | **Week 4 — Fri** |

---

## Prizes

| Place | Prize |
|---|---|
| **1st — Best Overall** | $2,000 cash + featured write-up on the project README (Community Spotlight) + 1 year of cloud credits from each sponsor |
| **2nd — Best Production Deployment** | $1,000 cash + featured write-up |
| **3rd — Most Reproducible** | $500 cash + featured write-up |
| **Best Benchmark Submission** | Cloud credits + hardware loaner kit |
| **Best Integration** | $500 cash + project featured in docs |

All participants receive a digital badge and are listed in the `## Community Submissions` section.

---

## Post-Hackathon

1. Winning and notable submissions are added to a new `## Community Submissions` section in the README, under a subheading like `### Hackathon Projects`.
2. Benchmark contributions from Track 2 are merged into the [standardized benchmark suite](benchmark-suite-proposal.md) results repository.
3. The hackathon produces an aggregated report: "State of CPU Inference 2026" — summarizing the hardware tested, runtimes used, cost findings, and lessons learned.
4. If successful, the hackathon becomes a biannual event (spring and autumn), with each edition targeting a different theme (e.g., H1: serverless, H2: edge).

---

## See also

- [Benchmark Suite Proposal](benchmark-suite-proposal.md) — Standardized benchmarks Track 2 participants use
- [Quick Start Guide](quickstart.md) — Entry point for new participants
- [CPU Inference Deployment Guide](cpu-inference-deployment.md) — Deployment patterns Track 1 participants reference
- [Serverless CPU Patterns](serverless-patterns.md) — Serverless deployment reference for Track 1/3
- [Cost Calculator](cost-calculator.md) — Cost analysis reference for Track 1 submissions
