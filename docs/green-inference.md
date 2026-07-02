# Energy Efficiency and Power Cost in CPU Inference

Monetary $/token analysis (see [cost-calculator.md](cost-calculator.md)) captures instance price but misses energy cost — a significant factor for on-prem deployments and hyperscale cloud operators who pay directly for power. This guide covers power-per-inference comparisons, data-center energy arithmetic, and CPU power-management tuning.

> **Quick-reference summary**: see [green-inference-cheat-sheet.md](green-inference-cheat-sheet.md) for the one-page distillation of power, water, and carbon tables.

---

## Contents

- [Why Power Cost Matters](#why-power-cost-matters)
- [TDP Reference Table](#tdp-reference-table)
- [Power-Per-Inference: The Ampere Anchor](#power-per-inference-the-ampere-anchor)
- [Data-Center Energy Arithmetic](#data-center-energy-arithmetic)
- [CPU Power Management for Inference](#cpu-power-management-for-inference)
- [Measuring Actual Power Draw](#measuring-actual-power-draw)
- [Cloud Instance Energy Transparency](#cloud-instance-energy-transparency)
- [Water Consumption](#water-consumption)
- [Carbon Footprint](#carbon-footprint)
- [Energy Efficiency Summary](#energy-efficiency-summary)
- [See also](#see-also)
- [References](#references)

---

## Why Power Cost Matters

Cloud users pay for it indirectly (it is baked into the $/hr rate). On-prem operators pay for it directly and continuously. At scale:

- A single A100 SXM4 draws up to 400 W under load.
- A data center PUE of 1.3 means every 400 W of GPU load costs 520 W at the meter.
- At $0.10 / kWh (US enterprise average), that is ~$0.052 / hr just for the energy bill on one GPU — before amortising hardware cost or cooling overhead.

For CPU inference the math looks different because CPU TDP is spread across many independent tasks and the chip rarely sustains peak TDP during memory-bound workloads.

---

## TDP Reference Table

| Processor | TDP (W) | Core count | Primary inference use |
|---|---|---|---|
| Ampere Altra Max 128-core | 250 W | 128 | Arm server — Neoverse N1 |
| AWS Graviton3 (c7g.16xlarge) | ~150 W (est.) | 64 vCPU | Arm cloud |
| Intel Xeon w9-3595X (60-core, Emerald Rapids) | 350 W | 60 | x86 server |
| Intel Xeon 6 (144-core, Sierra Forest) | 330 W | 144 E-cores | Efficiency-optimised x86 |
| Nvidia Tesla T4 | 70 W | — | GPU inference (PCIe) |
| Nvidia A10 | 150 W | — | GPU inference (PCIe) |
| Nvidia A100 SXM4 | 400 W | — | GPU training / heavy inference |
| Nvidia H100 SXM5 | 700 W | — | GPU training / heavy inference |

*TDP is peak; sustained workload power is lower for both CPUs and GPUs. Use as an order-of-magnitude guide, not an accounting figure.*

---

## Power-Per-Inference: The Ampere Anchor

Ampere Computing CTO Jeff Wittich (interviewed by Scaleway, 2023) published the following figures for **OpenAI Whisper** speech-to-text inference:

| Processor | Relative power per inference |
|---|---|
| Ampere Altra 128-core | 1× (baseline) |
| Nvidia A10 | **3.6× more power** per inference |
| Nvidia Tesla T4 | **5.6× more power** per inference |

Source: [Scaleway blog — "Why CPUs also make sense for AI inference"](https://www.scaleway.com/en/blog/why-cpus-also-make-sense-for-ai-inference/)

**Why the T4 comes out worse than the A10 despite lower TDP.** The T4's 70 W TDP looks efficient in isolation, but at low batch sizes (batch = 1 or small bursts) the GPU is power-on and drawing substantial idle power while delivering no throughput advantage over CPU. The Altra, running the same task on many cores in parallel, delivers the inference faster *and* at lower total joules per output token.

This batch-size sensitivity is the key insight: GPU power efficiency improves rapidly as batch size grows (GPU utilisation rises, cost per inference falls). At batch = 1 or low-traffic deployments, CPU power-per-inference is competitive or superior.

---

## Data-Center Energy Arithmetic

### PUE multiplier

Every watt consumed by a server draws additional power for cooling, UPS losses, and lighting. Power Usage Effectiveness (PUE) captures this:

```
Total facility power = IT load × PUE
```

| Facility type | Typical PUE |
|---|---|
| Hyperscale (AWS / Azure / Google) | 1.10 – 1.20 |
| Modern co-location | 1.20 – 1.35 |
| Enterprise on-prem (older) | 1.40 – 1.80 |

### Worked example — monthly energy cost comparison

Scenario: sustained single-task Whisper inference, 24 × 7, on-prem, $0.10 / kWh, PUE 1.3.

| Hardware | TDP | Effective load (W) | Facility W (×1.3) | $/month (720 hr) |
|---|---|---|---|---|
| Altra 128-core server | 250 W | ~200 W | 260 W | **$18.72** |
| Server + Nvidia A10 | 250 + 150 W | ~350 W | 455 W | **$32.76** |
| Server + Nvidia A100 | 250 + 400 W | ~580 W | 754 W | **$54.29** |

The GPU adds $14–35 / month in energy overhead per server, before any hardware amortisation. For a rack of 10 servers this becomes $140–350 / month purely in electricity — and these are conservative numbers at $0.10 / kWh. European tariffs of $0.25–0.35 / kWh triple the delta.

---

## CPU Power Management for Inference

Modern CPUs have multiple knobs that affect sustained inference throughput and energy draw. Getting these wrong (e.g. leaving the governor on `powersave`) can reduce decode throughput 30–50%.

### Linux cpufreq governor

```bash
# Check current governor on all cores
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort -u

# Set performance governor (recommended for inference servers)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Verify frequency is pinned at max
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
```

### Intel turbo boost

Turbo Boost lets cores exceed base frequency for short bursts. It is beneficial for prefill (matrix multiply) but can cause thermal throttling during sustained decode. On multi-socket servers, disable turbo if you observe frequency drops mid-benchmark:

```bash
# Disable turbo (Intel)
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo

# AMD equivalent
echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost
```

### Intel RAPL power capping

Running Average Power Limit (RAPL) lets you cap package TDP, which can improve throughput-per-watt at the cost of peak throughput:

```bash
# Read current RAPL package power limit (microwatts)
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw

# Cap to 200 W (example — tune to your thermal envelope)
echo 200000000 | sudo tee \
  /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
```

### Arm frequency scaling

On Arm servers (Graviton, Altra, Cobalt), the equivalent tuning is:

```bash
# Use cpupower for Arm
sudo cpupower frequency-set -g performance

# Verify with lscpu
lscpu | grep "CPU MHz"
```

---

## Measuring Actual Power Draw

### RAPL (Intel, in-process)

```python
import subprocess, time

def read_rapl_uj(domain="/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"):
    return int(open(domain).read())

t0 = time.time(); e0 = read_rapl_uj()
# ... run inference here ...
t1 = time.time(); e1 = read_rapl_uj()

joules = (e1 - e0) / 1e6
watts  = joules / (t1 - t0)
print(f"{joules:.2f} J — {watts:.1f} W average")
```

### IPMI / BMC (server)

```bash
# Read chassis power via ipmitool
ipmitool dcmi power reading

# Or via Redfish API
curl -sk -u admin:password \
  https://<bmc-ip>/redfish/v1/Chassis/System.Embedded.1/Power \
  | python3 -m json.tool | grep -i "powerconsumedwatts"
```

### perf stat (Linux)

```bash
# Power events (requires MSR access)
sudo perf stat -e power/energy-pkg/ \
  llama-cli -m model.gguf -p "Hello" -n 100
```

---

## Cloud Instance Energy Transparency

Cloud providers do not expose per-instance wattage. Use CPU utilisation as a proxy:

| Cloud provider | Power data available |
|---|---|
| AWS | CloudWatch `CPUUtilization`; Carbon Footprint tool (aggregate, monthly) |
| Azure | Azure Monitor `Percentage CPU`; Emissions Impact Dashboard |
| Google Cloud | Carbon Footprint dashboard; no per-VM wattage |
| Scaleway | No per-VM power API; data-center PUE published (1.3 for DC3 AMS) |

For Arm instances specifically, low utilisation at steady-state is expected — Neoverse cores reach peak throughput at moderate clock utilisation due to wide SIMD, so 60–70% CPU util on a c7g or Altra instance during inference is not waste.

---

## Water Consumption

Data centers cool servers with water — either directly (liquid cooling loops) or indirectly (evaporative cooling towers that reject heat to atmosphere). The metric is **Water Usage Effectiveness (WUE)**:

```
WUE (L/kWh) = annual site water usage (litres) / IT equipment energy (kWh)
```

Lower is better. Water used this way is largely non-recoverable (it evaporates).

### WUE reference table

| Facility type | Typical WUE (L/kWh) | Notes |
|---|---|---|
| Hyperscale (Google, Microsoft, AWS) | 0.2 – 0.5 | Best-practice liquid/air-side economisers |
| Modern co-location | 0.5 – 1.0 | Varies by climate and cooling design |
| Enterprise on-prem (older) | 1.5 – 2.5 | Older CRAC units, no economisation |
| Global average (Uptime Institute 2023) | ~1.5 | Survey of ~900 operators |

Sources: Uptime Institute 2023 Global Data Center Survey; Google Environmental Report 2023 (company-average WUE ~0.49 L/kWh); Microsoft Sustainability Report 2022.

### Worked example — water per server-month

Using the same scenario as the energy cost table (sustained inference, 24 × 7), with a mid-range WUE of 0.5 L/kWh:

| Hardware | Facility kWh/month | Water used (WUE 0.5) | Water used (WUE 1.5) |
|---|---|---|---|
| Altra 128-core server | 260 W × 720 h = **187 kWh** | **94 L** | **281 L** |
| Server + Nvidia A10 | 455 W × 720 h = **328 kWh** | **164 L** | **491 L** |
| Server + Nvidia A100 | 754 W × 720 h = **543 kWh** | **272 L** | **815 L** |

Switching from a GPU-accelerated setup to CPU-only saves **70–215 litres of water per server per month** at best-practice hyperscale WUE — and up to 534 litres in older facilities. Across a 10-server deployment over a year that is 8,400–64,000 litres — the equivalent of 84–640 bathtubs of water.

### Why this matters

Water stress is a real operational risk: data centers in Phoenix, Austin, and Northern Virginia have faced scrutiny and local regulatory pushback over water withdrawal. For organisations with water-usage targets or operating in stressed watersheds, reducing inference power draw is a direct lever on water consumption — no procurement required.

---

## Carbon Footprint

Lower power draw means fewer kWh purchased from the grid, which means fewer tonnes of CO2 emitted. The multiplier is the **grid carbon intensity** of the region where the server runs.

### Grid carbon intensity reference

| Region / grid | Intensity (gCO₂eq/kWh) | Character |
|---|---|---|
| France | ~52 | Nuclear-heavy; almost always the lowest in Europe |
| Norway / Iceland | ~20 – 30 | Hydro-dominant |
| UK (2023 average) | ~148 | Gas + wind mix; improving yearly |
| California (CAISO) | ~200 | Solar + gas; varies by hour |
| EU average | ~231 | Eurostat 2022 |
| US average | ~386 | EPA eGRID 2022 |
| Germany | ~350 | Coal + gas; high but falling |
| Texas (ERCOT) | ~400 | Gas-heavy; very time-of-day–dependent |
| Poland | ~700 | Coal-heavy; among highest in EU |

*Carbon intensity is time-varying. Running inference during peak solar hours in California can halve the effective intensity vs. running at midnight on a coal-heavy day.*

### Worked example — CO₂ per server-month

Using the same monthly kWh figures, at US-average grid intensity (386 gCO₂eq/kWh = 0.386 kg/kWh):

| Hardware | kWh/month (facility) | kg CO₂/month (US avg) | kg CO₂/month (France) |
|---|---|---|---|
| Altra 128-core (CPU only) | 187 kWh | **72 kg** | **10 kg** |
| Server + Nvidia A10 | 328 kWh | **127 kg** | **17 kg** |
| Server + Nvidia A100 | 543 kWh | **210 kg** | **28 kg** |

CPU-only saves **55 kg CO₂/month vs A10** on US grid — 660 kg/year per server. At a 10-server deployment that is 6.6 tonnes CO₂/year, roughly equivalent to driving a petrol car 35,000 km.

### Shift to green regions

The France column illustrates a compounding benefit: running CPU inference in a low-carbon region achieves a 7× additional reduction over running GPU inference in a coal-heavy region. Since CPU servers need no specialised GPU hardware availability, they can be deployed in more regions — including those with the greenest grids.

### Measuring inference carbon in code

**CodeCarbon** (Python) instruments your inference code and reports CO₂eq per run:

```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker(
    project_name="llama-inference",
    measure_power_secs=5,
    country_iso_code="USA",   # uses regional grid mix
)
tracker.start()

# ... run your inference here ...

emissions = tracker.stop()   # kg CO₂eq
print(f"{emissions * 1000:.2f} g CO₂eq")
```

GitHub: [mlco2/codecarbon](https://github.com/mlco2/codecarbon)

**Cloud Carbon Footprint** aggregates cloud billing data across AWS / Azure / GCP and estimates emissions per service:

```bash
# Run locally against exported billing CSVs
npx @cloud-carbon-footprint/cli estimate --startDate 2026-01-01 --endDate 2026-06-01
```

Site: [cloudcarbonfootprint.org](https://www.cloudcarbonfootprint.org/)

**Electricity Maps** provides a real-time API for grid carbon intensity, useful for scheduling batch inference jobs to coincide with low-carbon windows:

```python
import httpx

resp = httpx.get(
    "https://api.electricitymap.org/v3/carbon-intensity/latest",
    params={"zone": "DE"},
    headers={"auth-token": "<your-token>"},
)
print(resp.json()["carbonIntensity"], "gCO₂eq/kWh")
```

Site: [app.electricitymaps.com](https://app.electricitymaps.com/)

### Green AI context

The compute cost of AI inference is an active research area. Strubell et al. (2019) — ["Energy and Policy Considerations for Deep Learning in NLP"](https://arxiv.org/abs/1906.02629) — first brought carbon costs of model training to wide attention. The same arithmetic applies to inference at scale: energy × time × carbon intensity = emissions. Choosing CPU inference where it is sufficient is the simplest intervention on all three dimensions simultaneously.

---

## Energy Efficiency Summary

| Scenario | CPU advantage |
|---|---|
| **Power** | |
| Batch = 1, bursty traffic | CPU wins — GPU idle power dominates |
| Batch ≥ 32, sustained | Depends on model size; GPU wins above ~50% utilisation |
| Whisper / small audio models | 3.6–5.6× less power vs A10/T4 (Ampere data) |
| 70B+ dense inference | GPU wins — arithmetic demand forces the choice |
| **Water** | |
| On hyperscale (WUE 0.5) | ~70 L/month/server saved vs A10 |
| On-prem older DC (WUE 1.5) | ~210 L/month/server saved vs A10 |
| Low-water-stress regions | Still saves; matters most in Phoenix, N. Virginia, Austin |
| **Carbon** | |
| US grid (386 g/kWh) | ~55 kg CO₂/month/server saved vs A10; 660 kg/yr |
| EU (231 g/kWh) | ~33 kg CO₂/month/server saved |
| Low-carbon grid (France, ~52 g/kWh) | ~7 kg/month — absolute numbers small but compounding |
| Coal-heavy grid (Poland, ~700 g/kWh) | ~100 kg/month saved — strongest case for green scheduling |

The three arguments — energy cost, water consumption, and carbon emissions — all scale proportionally with power draw and all point in the same direction: **lower inference power is always better, and CPU inference achieves lower power-per-inference at low-to-medium batch sizes**. The monetary, environmental, and sustainability cases reinforce each other.

For organisations with net-zero commitments or scope 2/3 targets, CPU inference is a measurable, immediately deployable intervention that reduces all three metrics without requiring new carbon offsets or renewable energy procurement.

See also: [Green Inference Cheat Sheet](green-inference-cheat-sheet.md) · [Cost Calculator](cost-calculator.md) · [CPU Inference Deployment Guide](cpu-inference-deployment.md) · [Benchmark Methodology](benchmark-methodology.md)

For interactive power, water, and CO₂ modelling see the [Streamlit power calculator](../calculator/power-calculator.py) (`uv run streamlit run calculator/power-calculator.py`).

---

## References

- [Scaleway blog — "Why CPUs also make sense for AI inference"](https://www.scaleway.com/en/blog/why-cpus-also-make-sense-for-ai-inference/)
- [mlco2/codecarbon](https://github.com/mlco2/codecarbon)
- [cloudcarbonfootprint.org](https://www.cloudcarbonfootprint.org/)
- [app.electricitymaps.com](https://app.electricitymaps.com/)
- ["Energy and Policy Considerations for Deep Learning in NLP"](https://arxiv.org/abs/1906.02629)
