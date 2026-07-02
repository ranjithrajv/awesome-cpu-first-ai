# Hardware Reference

Canonical hardware performance data for CPU inference. This is the single source of truth — all other docs reference this page rather than maintaining their own figures.

---

## Contents

- [Hardware Tiers](#hardware-tiers)
- [Mobile Phones](#mobile-phones)
- [Laptops / Edge Servers](#laptops--edge-servers)
- [Single-Board Computers](#single-board-computers)
- [Server Instances](#server-instances)
- [See also](#see-also)

---

## Hardware Tiers

Abstract tiers used by the [benchmark suite](benchmark-suite-proposal.md) and [edge/mobile playbook](edge-mobile-playbook.md). Each tier maps to representative hardware.

| Tier | Form Factor | Example Hardware | Expected tg128 (3B Q4) |
|---|---|---|---|
| S (laptop) | x86 laptop | Intel Core Ultra 7, AMD Ryzen 7 8840U | 18–30 tok/s |
| M (server x86) | Xeon / EPYC | c7i.4xlarge (Intel), m7a.4xlarge (AMD) | 30–55 tok/s |
| A (server ARM) | Neoverse V2/V3 | c8g.4xlarge (Graviton4), Cobalt 100 | 30–55 tok/s |
| E (edge ARM) | Cortex-A76/A78 | Raspberry Pi 5, Orange Pi 5 | 3–8 tok/s |

Expected throughput for 7B Q4 is approximately 35–45% of the 3B Q4 figure on the same hardware.

---

## Mobile Phones

| Chipset | CPU Cores | RAM | 3B Q4 (tok/s) | 7B Q4 (tok/s) | Recommended Runtime |
|---|---|---|---|---|---|
| Apple A19 Pro | 6-core | 8–12 GB | 25–38 | 7–12 | MLC-LLM, Core AI |
| Apple A18 Pro | 6-core | 8 GB | 20–30 | 6–10 | MLC-LLM |
| Snapdragon 8 Elite | 8-core Oryon | 8–16 GB | 18–25 | 8–12 | llama.cpp, ExecuTorch |
| Snapdragon 8 Gen 3 | 8-core | 8–16 GB | 15–22 | 5–9 | llama.cpp |
| Exynos 2500 | 10-core Arm | 8–16 GB | 14–20 | 5–8 | ExecuTorch |
| Dimensity 9500 | 8-core Arm | 8–16 GB | 12–18 | 5–8 | MLC-LLM, ExecuTorch |
| Tensor G5 | 8-core Arm | 8–12 GB | 10–14 | 3–6 | LiteRT (CPU) |

*Source: [Mobile Phone CPU Inference](mobile-cpu-inference.md)*

---

## Laptops / Edge Servers

| Device | CPU | RAM | 3B Q4 (tok/s) | 7B Q4 (tok/s) |
|---|---|---|---|---|
| MacBook Air M3 | M3 (8-core) | 8–24 GB | 30–45 | 12–18 |
| MacBook Pro M4 | M4 Pro/Max | 16–48 GB | 35–50 | 14–22 |
| Intel Core Ultra 7 | Meteor Lake (16-core) | 16–32 GB | 18–28 | 8–14 |
| AMD Ryzen 7 8840U | Zen 4 (8-core) | 16–32 GB | 18–28 | 7–12 |

---

## Single-Board Computers

| Board | CPU | RAM | 3B Q4 (tok/s) | Notes |
|---|---|---|---|---|
| Raspberry Pi 5 | Cortex-A76 (4-core) | 8 GB | 3–6 | llama.cpp, whisper.cpp |
| Orange Pi 5 | Cortex-A76 (4) + A55 (4) | 8–16 GB | 4–8 | RKNPU not required |
| Jetson Orin NX (CPU) | Cortex-A78AE (8) | 8–16 GB | 6–10 | GPU available but optional |

---

## Server Instances

| Instance | Architecture | vCPU | RAM | 3B Q4 (tok/s) | 7B Q4 (tok/s) | $/hr |
|---|---|---|---|---|---|---|
| c7g.4xlarge (Graviton3) | ARM Neoverse V1 | 16 | 32 GB | 30–40 | 12–18 | $0.58 |
| c8g.4xlarge (Graviton4) | ARM Neoverse V2 | 16 | 32 GB | 35–50 | 14–22 | $0.62 |
| c7i.4xlarge (Xeon) | x86 Sapphire Rapids | 16 | 32 GB | 30–45 | 12–18 | $0.68 |
| m7a.4xlarge (EPYC) | x86 Zen 4 | 16 | 64 GB | 30–50 | 12–20 | $0.70 |

*(pricing snapshot: 2026-07)*

---

## See also

- [Benchmark Methodology](benchmark-methodology.md) — How throughput is measured (pp512/tg128)
- [Mobile Phone CPU Inference](mobile-cpu-inference.md) — Full chipset catalogue with references
- [Benchmark Suite Proposal](benchmark-suite-proposal.md) — Standardized suite using these tiers
- [Edge & Mobile CPU Inference Playbook](edge-mobile-playbook.md) — Deployment guide for edge/mobile hardware
