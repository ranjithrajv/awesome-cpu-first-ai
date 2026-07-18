# Roadmap

Quarterly milestones for Awesome CPU-First AI, aligned with enterprise inference adoption cycles. This document is a living plan — priorities shift as the ecosystem evolves. Every quarter, the maintainers review and publish the next quarter's commits.

---

## Contents

- [Now — Q3 2026 (Jul–Sep)](#now--q3-2026-jul-sep)
- [Next — Q4 2026 (Oct–Dec)](#next--q4-2026-oct-dec)
- [Later — H1 2027 (Jan–Jun)](#later--h1-2027-jan-jun)
- [How to Influence the Roadmap](#how-to-influence-the-roadmap)

---

## Now — Q3 2026 (Jul–Sep)

| Theme | Deliverable | Status |
|---|---|---|
| **Standardized benchmarks** | Publish [Benchmark Suite Proposal](docs/benchmark-suite-proposal.md) and seed the results repository with sponsor-provided hardware runs | In progress |
| **Community engagement** | Launch [CPU Inference Hackathon](docs/community-hackathon.md) — recruit sponsors, open registration | In progress |
| **Enterprise TCO tools** | Extend [Cost Calculator](calculator/cost-calculator.py) with hardware-preset selection driven by benchmark suite results | Planned |
| **ARM server coverage** | Add dedicated section for AmpereOne, Azure Cobalt 200 benchmarks, and Google Axion C4A production case studies | Planned |
| **Tooling — CI staleness** | Migrate staleness checks from monthly issues to auto-generated PRs that update `(last verified: …)` tags | Planned |

**Exit criteria for Q3:**
- Benchmark suite proposal merged and accepted by the community.
- Hackathon launched with at least 3 sponsors and 50 registered participants.
- Cost calculator updated with at least 10 hardware presets from benchmark suite results.

---

## Next — Q4 2026 (Oct–Dec)

| Theme | Deliverable | Target |
|---|---|---|
| **Benchmark suite v1.0** | Release v1.0 of the suite with 20+ hardware/software combinations published in the results repository | Oct |
| **Community spotlight** | Publish winning hackathon projects in a new `## Community Submissions` README section | Oct |
| **"State of CPU Inference" report** | Publish the [State of CPU Inference Report](docs/state-of-cpu-inference-report.md) aggregating hackathon and benchmark results into tok/s, $/token, and W/token across architectures | Nov |
| **Green inference expansion** | Add per-model CO₂ estimates (g/query) to the [Power Calculator](calculator/power-calculator.py), using benchmark suite power measurements | Nov |
| **vLLM CPU backend** | If the [vLLM CPU backend](https://github.com/vllm-project/vllm/issues/10856) reaches production stability, add a dedicated section with deployment guide | Dec |
| **Release v2.0 of the list** | Tagged release with changelog, incorporating all Q3–Q4 additions | Dec |

**Exit criteria for Q4:**
- 20+ hardware profiles in the benchmark results repository.
- At least 5 community-submitted projects merged.
- v2.0 release published on GitHub.

---

## Later — H1 2027 (Jan–Jun)

| Theme | Deliverable | Target |
|---|---|---|
| **Hackathon v2** | Second edition focused on edge / mobile / RISC-V | Mar |
| **CPU fine-tuning benchmarks** | Execute the [CPU Fine-Tuning Benchmarks](docs/cpu-finetuning-benchmarks.md) proposal — LoRA/QLoRA throughput and cost on CPU (1B–8B models) | Mar |
| **Automated nightly benchmarks** | GitHub Actions workflow running the suite on sponsored hardware, publishing results automatically | Apr |
| **Multimodal benchmark expansion** | Extend benchmark suite to cover whisper.cpp, Piper TTS, and YOLO/OpenVINO inference | May |
| **Serverless cost comparison dashboard** | Ship the [Serverless CPU Cost Dashboard](docs/serverless-cost-dashboard.md) — interactive per-1M-token cost across Lambda, Fly.io, Modal, and GPU serverless | Jun |
| **Release v2.1** | Tagged release with H1 additions | Jun |

**Exit criteria for H1 2027:**
- Nightly benchmark pipeline running with auto-published results.
- Multimodal benchmark coverage added to suite v2.0.
- Serverless cost dashboard published.

---

## How to Influence the Roadmap

- **Open an issue** with the `roadmap` label to propose a new milestone or reprioritize an existing one.
- **Submit a PR** that directly addresses a planned deliverable — early contributions are merged faster.
- **Join the discussion** in GitHub Discussions (once launched) for roadmap threads tagged `roadmap`.
- **Sponsor hardware or cloud credits** by reaching out to the maintainers — this directly accelerates the benchmark suite and automated pipeline milestones.

The roadmap is updated at the start of each quarter. The maintainers review open issues, community signals, and ecosystem developments (new runtimes, CPU architectures, MLPerf rounds) to set priorities for the next 90 days.
