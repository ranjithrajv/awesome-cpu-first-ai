# Green Inference Cheat Sheet

Quick-reference summary of CPU vs GPU energy, water, and carbon costs for sustainability reporting and capacity planning. Full methodology at [green-inference.md](green-inference.md).

> **Long form**: see [green-inference.md](green-inference.md) for worked examples, code snippets, and the full data-center arithmetic methodology.

## Power per Inference (Whisper STT, batch=1)

| Hardware | Relative power | Absolute TDP |
|---|---|---|
| Ampere Altra 128-core | **1× (baseline)** | 250 W |
| Nvidia A10 | **3.6×** more power | 150 W |
| Nvidia Tesla T4 | **5.6×** more power | 70 W |

CPU wins at batch=1 because GPU idle power dominates. Advantage reverses as batch size grows above ~32.

Source: Ampere CTO interview with Scaleway.

## TDP Reference

| Processor | TDP | Role |
|---|---|---|
| Ampere Altra Max 128-core | 250 W | Arm server |
| AWS Graviton3 (c7g.16xlarge) | ~150 W | Arm cloud |
| Intel Xeon 6 (144 E-core) | 330 W | Efficiency x86 |
| Nvidia A10 | 150 W | GPU inference |
| Nvidia A100 SXM4 | 400 W | GPU heavy inference |
| Nvidia H100 SXM5 | 700 W | GPU heavy inference |

## Energy Cost per Server-Month (24×7, $0.10/kWh, PUE 1.3)

| Configuration | Facility W | kWh/mo | $/mo |
|---|---|---|---|
| Altra 128-core server | 260 W | 187 kWh | **$18.72** |
| Server + A10 (CPU+GPU) | 455 W | 328 kWh | **$32.76** |
| Server + A100 | 754 W | 543 kWh | **$54.29** |

GPU adds **$14–35/mo per server** in electricity before hardware amortisation.

## Water Consumption per Server-Month

| Configuration | WUE 0.5 (hyperscale) | WUE 1.5 (on-prem) |
|---|---|---|
| CPU-only (Altra) | **94 L** | **281 L** |
| + A10 | **164 L** | **491 L** |
| + A100 | **272 L** | **815 L** |

CPU saves **70–215 L/month** at hyperscale, up to 534 L in older facilities.

## CO₂ per Server-Month

| Configuration | US grid (386 g/kWh) | France (52 g/kWh) |
|---|---|---|
| CPU-only (Altra) | **72 kg** | **10 kg** |
| + A10 | **127 kg** | **17 kg** |
| + A100 | **210 kg** | **28 kg** |

CPU saves **55 kg CO₂/mo vs A10** on US grid — 660 kg/year per server.

## Grid Carbon Intensity Reference

| Region | gCO₂eq/kWh |
|---|---|
| Norway / Iceland | 20–30 |
| France | ~52 |
| UK | ~148 |
| California | ~200 |
| EU avg | ~231 |
| US avg | ~386 |
| Texas (ERCOT) | ~400 |
| Poland | ~700 |

## Quick Commands

```bash
# Set performance governor (inference throughput +30% vs powersave)
sudo cpupower frequency-set -g performance

# Read RAPL package power (Intel)
cat /sys/class/powercap/intrapl/intrapl:0/energy_uj

# Measure inference energy with perf
sudo perf stat -e power/energy-pkg/ ./llama-cli -m model.gguf -p "Hello" -n 100

# Check CPU temperature
sensors
```

## Key Insight

**GPU power efficiency improves with batch size; CPU efficiency is flatter.** At batch=1 or bursty traffic, CPU wins on every axis (energy, water, carbon). At sustained high batch, GPU arithmetic density wins. The cross-over point is model- and hardware-specific but typically falls at 30–50% GPU utilisation for 7B models.

---

See also: [Green Inference Guide (long form)](green-inference.md) · [Cost Calculator](cost-calculator.md) · [CPU Inference Deployment Guide](cpu-inference-deployment.md) · [Power Calculator (Streamlit)](../calculator/power-calculator.py)
