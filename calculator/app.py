"""Unified CPU-first AI calculator app.

Run with:
    uv run streamlit run calculator/app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.constants import HOURS_PER_MONTH
from lib.cost import cost_per_million, cost_per_request, monthly_cost
from lib.power import (
    co2_per_million_tokens,
    effective_load_w,
    facility_w,
    monthly_co2_kg,
    monthly_energy_cost,
    monthly_kwh,
    monthly_water_litres,
    tok_s_per_watt,
    water_per_million_tokens,
)
from lib.presets import (
    COMBINED_PRESETS,
    CPU_PRESETS,
    GPU_PRESETS,
    GRID_PRESETS,
    HARDWARE_PRESETS,
    PUE_PRESETS,
    WUE_PRESETS,
)

# ----------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="CPU-First AI Calculators",
    page_icon="🖥️",
    layout="wide",
)

# ----------------------------------------------------------------------------
# Top-level navigation
# ----------------------------------------------------------------------------
TOOLS = {
    "🔀 Decision Dashboard": "dashboard",
    "💰 Cost Calculator": "cost",
    "🌱 Power & Sustainability": "power",
}

st.sidebar.title("CPU-First AI Calculators")
tool_label = st.sidebar.radio("Tool", list(TOOLS.keys()), label_visibility="collapsed")
tool = TOOLS[tool_label]

st.sidebar.markdown("---")

# ============================================================================
# DECISION DASHBOARD
# ============================================================================
if tool == "dashboard":
    # -- Sidebar controls ----------------------------------------------------
    st.sidebar.header("Compare two options")
    st.sidebar.caption(
        "Pick any CPU and GPU preset. All metrics are computed from the same "
        "shared settings below."
    )

    cpu_keys = [k for k, v in COMBINED_PRESETS.items() if v["type"] == "cpu"]
    gpu_keys = [k for k, v in COMBINED_PRESETS.items() if v["type"] == "gpu"] + [
        "Custom"
    ]

    cpu_label = st.sidebar.selectbox("CPU option", cpu_keys, index=0)
    gpu_label = st.sidebar.selectbox(
        "GPU option",
        [k for k in COMBINED_PRESETS if COMBINED_PRESETS[k]["type"] == "gpu"],
        index=1,
    )

    cpu = dict(COMBINED_PRESETS[cpu_label])
    gpu = dict(COMBINED_PRESETS[gpu_label])

    st.sidebar.subheader("Workload")
    util = (
        st.sidebar.slider("Utilisation (%)", 10, 100, 80, step=5, key="dash_util")
        / 100.0
    )
    load_factor = (
        st.sidebar.slider(
            "Sustained load factor (% of TDP)", 20, 100, 80, step=5, key="dash_lf"
        )
        / 100.0
    )

    st.sidebar.subheader("Facility & region")
    pue_label = st.sidebar.selectbox(
        "PUE", list(PUE_PRESETS.keys()), index=0, key="dash_pue"
    )
    pue = PUE_PRESETS[pue_label]
    if pue_label.startswith("Custom"):
        pue = st.sidebar.number_input(
            "Custom PUE", value=1.15, min_value=1.0, format="%.2f", key="dash_pue_val"
        )

    wue_label = st.sidebar.selectbox(
        "WUE (L/kWh)", list(WUE_PRESETS.keys()), index=0, key="dash_wue"
    )
    wue = WUE_PRESETS[wue_label]
    if wue_label.startswith("Custom"):
        wue = st.sidebar.number_input(
            "Custom WUE", value=0.5, min_value=0.0, format="%.2f", key="dash_wue_val"
        )

    grid_label = st.sidebar.selectbox(
        "Grid carbon intensity", list(GRID_PRESETS.keys()), index=5, key="dash_grid"
    )
    grid_intensity = GRID_PRESETS[grid_label]
    if grid_label == "Custom grid intensity":
        grid_intensity = st.sidebar.number_input(
            "Custom gCO2eq/kWh",
            value=386.0,
            min_value=0.0,
            format="%.1f",
            key="dash_grid_val",
        )

    price_per_kwh = st.sidebar.number_input(
        "Electricity price ($/kWh)",
        value=0.10,
        min_value=0.0,
        format="%.3f",
        key="dash_elec",
    )

    # -- Compute all metrics -------------------------------------------------
    def _dash_metrics(hw: dict, is_batch: bool = False) -> dict:
        tok = hw["tok_s_batch"] if is_batch else hw["tok_s"]
        fac_w = facility_w(effective_load_w(hw["tdp_w"], load_factor), pue)
        cpm = cost_per_million(hw["price"], tok, util)
        co2 = co2_per_million_tokens(fac_w, tok, grid_intensity)
        water = water_per_million_tokens(fac_w, tok, wue)
        tpw = tok_s_per_watt(tok, fac_w)
        monthly = monthly_cost(hw["price"], HOURS_PER_MONTH)
        elec = monthly_energy_cost(monthly_kwh(fac_w), price_per_kwh)
        return {
            "$/1M tokens": cpm,
            "kgCO₂/1M tokens": co2,
            "L water/1M tokens": water,
            "tok/s per facility W": tpw,
            "monthly instance $": monthly,
            "monthly energy $": elec,
        }

    cpu_m = _dash_metrics(cpu)
    gpu_m1 = _dash_metrics(gpu, is_batch=False)
    gpu_m32 = _dash_metrics(gpu, is_batch=True)

    # -- Main content --------------------------------------------------------
    st.title("CPU vs GPU Decision Dashboard")
    st.caption(
        "All metrics use the same PUE, WUE, grid intensity, and utilisation. "
        "GPU tok/s are shown at both batch=1 (latency mode) and batch=32 (throughput mode). "
        "Pricing: us-east-1 on-demand (June 2026) — verify at "
        "[aws.amazon.com/ec2/pricing](https://aws.amazon.com/ec2/pricing/on-demand/)."
    )

    # Headline metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("CPU $/1M tokens", f"${cpu_m['$/1M tokens']:,.2f}")
        st.metric("CPU kgCO₂/1M tokens", f"{cpu_m['kgCO₂/1M tokens']:.3f}")
    with c2:
        st.metric("GPU $/1M tokens (batch=1)", f"${gpu_m1['$/1M tokens']:,.2f}")
        st.metric("GPU kgCO₂/1M tokens (batch=1)", f"{gpu_m1['kgCO₂/1M tokens']:.3f}")
    with c3:
        st.metric("GPU $/1M tokens (batch=32)", f"${gpu_m32['$/1M tokens']:,.2f}")
        st.metric("GPU kgCO₂/1M tokens (batch=32)", f"{gpu_m32['kgCO₂/1M tokens']:.3f}")

    st.markdown("---")

    # Full comparison table
    st.subheader("Full metric comparison")

    def _winner(cpu_val: float, gpu_val: float, lower_better: bool = True) -> str:
        if lower_better:
            return "✅ CPU" if cpu_val < gpu_val else "✅ GPU (b=1)"
        return "✅ CPU" if cpu_val > gpu_val else "✅ GPU (b=1)"

    rows = []
    for metric in [
        "$/1M tokens",
        "kgCO₂/1M tokens",
        "L water/1M tokens",
        "tok/s per facility W",
        "monthly instance $",
        "monthly energy $",
    ]:
        lower = metric != "tok/s per facility W"
        rows.append(
            {
                "Metric": metric,
                cpu_label: f"{cpu_m[metric]:,.3f}",
                f"{gpu_label} (b=1)": f"{gpu_m1[metric]:,.3f}",
                f"{gpu_label} (b=32)": f"{gpu_m32[metric]:,.3f}",
                "Winner (b=1)": _winner(cpu_m[metric], gpu_m1[metric], lower),
            }
        )
    st.dataframe(pd.DataFrame(rows).set_index("Metric"), use_container_width=True)

    # Bar charts
    st.subheader("$/1M tokens — CPU vs GPU")
    cost_chart = pd.DataFrame(
        {
            "CPU (batch=1)": [cpu_m["$/1M tokens"]],
            "GPU (batch=1)": [gpu_m1["$/1M tokens"]],
            "GPU (batch=32)": [gpu_m32["$/1M tokens"]],
        }
    )
    st.bar_chart(cost_chart.T.rename(columns={0: "$/1M tokens"}), height=280)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("kgCO₂ per 1M tokens")
        co2_chart = pd.DataFrame(
            {
                "CPU (b=1)": [cpu_m["kgCO₂/1M tokens"]],
                "GPU (b=1)": [gpu_m1["kgCO₂/1M tokens"]],
                "GPU (b=32)": [gpu_m32["kgCO₂/1M tokens"]],
            }
        )
        st.bar_chart(co2_chart.T.rename(columns={0: "kgCO₂/1M tokens"}), height=260)

    with col_right:
        st.subheader("tok/s per facility watt")
        tpw_chart = pd.DataFrame(
            {
                "CPU (b=1)": [cpu_m["tok/s per facility W"]],
                "GPU (b=1)": [gpu_m1["tok/s per facility W"]],
                "GPU (b=32)": [gpu_m32["tok/s per facility W"]],
            }
        )
        st.bar_chart(tpw_chart.T.rename(columns={0: "tok/s per W"}), height=260)

    # Verdict
    st.markdown("---")
    st.subheader("When to choose each")

    cpu_wins_cost = cpu_m["$/1M tokens"] < gpu_m1["$/1M tokens"]
    cpu_wins_carbon = cpu_m["kgCO₂/1M tokens"] < gpu_m1["kgCO₂/1M tokens"]
    gpu_batch_wins_cost = gpu_m32["$/1M tokens"] < cpu_m["$/1M tokens"]

    verdicts = []
    if cpu_wins_cost:
        verdicts.append(
            f"**Cost at batch=1:** CPU wins (${cpu_m['$/1M tokens']:,.2f} vs ${gpu_m1['$/1M tokens']:,.2f}/1M tokens)."
        )
    else:
        verdicts.append(
            f"**Cost at batch=1:** GPU wins (${gpu_m1['$/1M tokens']:,.2f} vs ${cpu_m['$/1M tokens']:,.2f}/1M tokens)."
        )

    if gpu_batch_wins_cost:
        verdicts.append(
            f"**Cost at batch=32:** GPU dominates (${gpu_m32['$/1M tokens']:,.2f}/1M tokens — {cpu_m['$/1M tokens'] / gpu_m32['$/1M tokens']:.1f}× cheaper than CPU)."
        )

    if cpu_wins_carbon:
        verdicts.append(
            f"**Carbon at batch=1:** CPU is greener ({cpu_m['kgCO₂/1M tokens']:.3f} vs {gpu_m1['kgCO₂/1M tokens']:.3f} kgCO₂/1M tokens)."
        )
    else:
        verdicts.append(
            f"**Carbon at batch=32:** GPU is greener at throughput ({gpu_m32['kgCO₂/1M tokens']:.3f} kgCO₂/1M tokens)."
        )

    for v in verdicts:
        st.markdown(f"- {v}")

    with st.expander("Methodology notes"):
        st.markdown(
            f"""
            - **CPU TDP** is estimated as the instance's vCPU fraction of the host (e.g.
              8/64 vCPUs = 12.5% of the 150 W Graviton3 host).
            - **GPU TDP** includes ~100 W of system overhead (CPU, RAM, NVMe).
            - **Facility power** = sustained draw × PUE ({pue}).
            - **Utilisation** ({int(util * 100)}%) only affects the $/1M tokens calculation
              (instance cost is fixed regardless of load).
            - **tok/s** benchmarks: llama.cpp on Llama-3-8B Q4_K_M — approximate,
              your workload will vary.
            """
        )

    st.markdown("---")
    st.caption(
        "See [docs/cost-calculator.md](../docs/cost-calculator.md) and "
        "[docs/green-inference.md](../docs/green-inference.md) for full methodology."
    )

# ============================================================================
# COST CALCULATOR
# ============================================================================
elif tool == "cost":
    # -- Sidebar controls ----------------------------------------------------
    st.sidebar.header("Instance configuration")
    st.sidebar.caption(
        "us-east-1 on-demand pricing (June 2026). "
        "Benchmarks: llama.cpp on Llama-3-8B Q4_K_M."
    )

    cpu_label = st.sidebar.selectbox("CPU instance", list(CPU_PRESETS.keys()), index=2)
    gpu_label = st.sidebar.selectbox("GPU instance", list(GPU_PRESETS.keys()), index=1)

    cpu = dict(CPU_PRESETS[cpu_label])
    gpu = dict(GPU_PRESETS[gpu_label])

    st.sidebar.subheader("CPU — editable")
    cpu["price"] = st.sidebar.number_input(
        "CPU $/hr", value=cpu["price"], min_value=0.0, format="%.3f", key="cpu_price"
    )
    cpu["tok_s"] = st.sidebar.number_input(
        "CPU tok/s (batch=1)",
        value=float(cpu["tok_s"]),
        min_value=0.0,
        format="%.1f",
        key="cpu_tok",
    )

    st.sidebar.subheader("GPU — editable")
    gpu["price"] = st.sidebar.number_input(
        "GPU $/hr", value=gpu["price"], min_value=0.0, format="%.3f", key="gpu_price"
    )
    gpu["tok_s"] = st.sidebar.number_input(
        "GPU tok/s (batch=1)",
        value=float(gpu["tok_s"]),
        min_value=0.0,
        format="%.1f",
        key="gpu_tok",
    )
    gpu["tok_s_batch"] = st.sidebar.number_input(
        "GPU tok/s (batch=32)",
        value=float(gpu.get("tok_s_batch", 0.0)),
        min_value=0.0,
        format="%.1f",
        key="gpu_tok_batch",
    )

    st.sidebar.subheader("Utilization")
    util = st.sidebar.slider("Utilization (%)", 10, 100, 100, step=5) / 100.0

    # -- Main content --------------------------------------------------------
    st.title("CPU vs GPU Inference Cost Calculator")
    st.caption(
        "Interactive companion to [docs/cost-calculator.md](../docs/cost-calculator.md). "
        "Verify current pricing at "
        "[aws.amazon.com/ec2/pricing](https://aws.amazon.com/ec2/pricing/on-demand/)."
    )

    col1, col2, col3 = st.columns(3)
    cpu_cpt = cost_per_million(cpu["price"], cpu["tok_s"], util)
    gpu_cpt = cost_per_million(gpu["price"], gpu["tok_s"], util)
    gpu_cpt_batch = cost_per_million(gpu["price"], gpu["tok_s_batch"], util)

    with col1:
        st.metric("CPU $/1M tokens", f"${cpu_cpt:,.2f}")
    with col2:
        st.metric("GPU $/1M tokens (batch=1)", f"${gpu_cpt:,.2f}")
    with col3:
        st.metric("GPU $/1M tokens (batch=32)", f"${gpu_cpt_batch:,.2f}")

    st.caption(
        "At sustained batch=32 the GPU arithmetic advantage dominates. "
        "At batch=1 or low utilisation the picture reverses — see the sweep below."
    )

    st.subheader("$/1M tokens vs utilisation")
    sweep = pd.DataFrame({"util": [u / 100.0 for u in range(5, 105, 5)]})
    sweep["CPU"] = sweep["util"].apply(
        lambda u: cost_per_million(cpu["price"], cpu["tok_s"], u)
    )
    sweep["GPU (batch=1)"] = sweep["util"].apply(
        lambda u: cost_per_million(gpu["price"], gpu["tok_s"], u)
    )
    sweep["GPU (batch=32)"] = sweep["util"].apply(
        lambda u: cost_per_million(gpu["price"], gpu["tok_s_batch"], u)
    )
    sweep = sweep.set_index("util")
    st.line_chart(sweep, height=320)
    st.caption("X-axis: utilisation (5%→100%). Y-axis: $/1M tokens. Lower is better.")

    with st.expander("Show raw table"):
        st.dataframe(sweep.style.format("${:,.2f}"), use_container_width=True)

    st.subheader("Production TCO worked example")
    st.caption(
        "Simulates a sustained 730 hrs/month workload. GPU is billed regardless of "
        "idle time; CPU serverless (Lambda/Fly/Modal) bills per-invocation instead."
    )

    col_tco1, col_tco2 = st.columns(2)
    with col_tco1:
        st.number_input("Average requests/sec", value=1.0, min_value=0.0, format="%.2f")
        idle_pct = st.slider("GPU idle fraction (%)", 0, 100, 60, step=5) / 100.0
    with col_tco2:
        hours_per_month = st.number_input(
            "Hours/month", value=HOURS_PER_MONTH, min_value=1, step=10
        )

    cpu_month = monthly_cost(cpu["price"], hours_per_month)
    gpu_month = monthly_cost(gpu["price"], hours_per_month)
    savings = (gpu_month - cpu_month) * 12

    st.markdown("#### 12-month TCO")
    tco_df = pd.DataFrame(
        {
            "CPU": [f"${cpu_month:,.2f}", "—", f"${cpu_month * 12:,.2f}"],
            "GPU": [
                f"${gpu_month:,.2f}",
                f"{int(idle_pct * 100)}% idle (paid regardless)",
                f"${gpu_month * 12:,.2f}",
            ],
        },
        index=["Monthly instance cost", "Idle hours", "12-month TCO"],
    )
    st.table(tco_df)

    if savings > 0:
        st.success(f"**CPU saves ${savings:,.0f}/yr** on this workload.")
    elif savings < 0:
        st.warning(
            f"GPU is cheaper by ${-savings:,.0f}/yr — likely the right choice at sustained load."
        )
    else:
        st.info("Break-even — both options cost the same at this utilisation.")

    st.subheader("Effective cost per request")
    st.caption("Assumes 1 request = 1 generation of `tokens_per_req` tokens.")
    tokens_per_req = st.number_input(
        "Tokens per request", value=256, min_value=1, step=16
    )

    cpu_per_req = cost_per_request(tokens_per_req, cpu["tok_s"], util, cpu["price"])
    gpu_per_req = cost_per_request(tokens_per_req, gpu["tok_s"], util, gpu["price"])

    c1, c2 = st.columns(2)
    with c1:
        st.metric("CPU $/req", f"${cpu_per_req:.4f}")
    with c2:
        st.metric("GPU $/req (batch=1)", f"${gpu_per_req:.4f}")

    with st.expander("Break-even formula"):
        st.markdown(
            """
            **$/1M tokens** = (instance $/hr × 1,000,000) / (tok/s × 3,600 × utilisation)

            CPU wins when:
            1. Idle time > 40% — GPU paid regardless, CPU costs scale with work done
            2. Model fits in RAM but not VRAM — GPU forces a more expensive instance class
            3. Sporadic traffic — serverless CPU charges per-invocation only
            4. Batch = 1 — GPU memory bandwidth advantage shrinks at single-request throughput
            """
        )

    st.markdown("---")
    st.caption(
        "See [docs/cost-calculator.md](../docs/cost-calculator.md) for the full methodology, "
        "pricing reference, throughput benchmarks, and a worked production example."
    )

# ============================================================================
# POWER & SUSTAINABILITY CALCULATOR
# ============================================================================
elif tool == "power":
    # -- Sidebar controls ----------------------------------------------------
    st.sidebar.header("Hardware configuration")

    hw_label_a = st.sidebar.selectbox(
        "Hardware A (CPU)", list(HARDWARE_PRESETS.keys()), index=0
    )
    hw_label_b = st.sidebar.selectbox(
        "Hardware B (GPU)", list(HARDWARE_PRESETS.keys()), index=5
    )

    hw_a = dict(HARDWARE_PRESETS[hw_label_a])
    hw_b = dict(HARDWARE_PRESETS[hw_label_b])

    st.sidebar.subheader("Power model")
    load_factor = (
        st.sidebar.slider("Sustained load factor (% of TDP)", 20, 100, 80, step=5)
        / 100.0
    )
    hw_a["tdp_w"] = st.sidebar.number_input(
        "Hardware A TDP (W)", value=float(hw_a["tdp_w"]), min_value=0.0, key="tdp_a"
    )
    hw_b["tdp_w"] = st.sidebar.number_input(
        "Hardware B TDP (W)", value=float(hw_b["tdp_w"]), min_value=0.0, key="tdp_b"
    )

    st.sidebar.subheader("Throughput (for efficiency metrics)")
    hw_a["tok_s"] = st.sidebar.number_input(
        "Hardware A tok/s",
        value=float(hw_a["tok_s"]),
        min_value=0.0,
        format="%.1f",
        key="tok_a",
    )
    hw_b["tok_s"] = st.sidebar.number_input(
        "Hardware B tok/s",
        value=float(hw_b["tok_s"]),
        min_value=0.0,
        format="%.1f",
        key="tok_b",
    )

    st.sidebar.subheader("Facility")
    pue_label = st.sidebar.selectbox(
        "PUE (Power Usage Effectiveness)", list(PUE_PRESETS.keys()), index=1
    )
    pue = PUE_PRESETS[pue_label]
    if pue_label.startswith("Custom"):
        pue = st.sidebar.number_input(
            "Custom PUE", value=1.30, min_value=1.0, format="%.2f"
        )

    wue_label = st.sidebar.selectbox(
        "WUE (Water Usage Effectiveness, L/kWh)", list(WUE_PRESETS.keys()), index=0
    )
    wue = WUE_PRESETS[wue_label]
    if wue_label.startswith("Custom"):
        wue = st.sidebar.number_input(
            "Custom WUE (L/kWh)", value=0.5, min_value=0.0, format="%.2f"
        )

    st.sidebar.subheader("Region")
    grid_label = st.sidebar.selectbox(
        "Grid carbon intensity", list(GRID_PRESETS.keys()), index=5
    )
    grid_intensity = GRID_PRESETS[grid_label]
    if grid_label == "Custom grid intensity":
        grid_intensity = st.sidebar.number_input(
            "Custom gCO2eq/kWh", value=386.0, min_value=0.0, format="%.1f"
        )

    st.sidebar.subheader("Economics")
    price_per_kwh = st.sidebar.number_input(
        "Electricity price ($/kWh)", value=0.10, min_value=0.0, format="%.3f"
    )
    hours_per_month = st.sidebar.number_input(
        "Hours/month (sustained load)", value=HOURS_PER_MONTH, min_value=1, step=10
    )

    # -- Compute -------------------------------------------------------------
    rows = []
    fac_w_vals = []
    for label, hw in [(hw_label_a, hw_a), (hw_label_b, hw_b)]:
        eff_w = effective_load_w(hw["tdp_w"], load_factor)
        fac_w_val = facility_w(eff_w, pue)
        fac_w_vals.append(fac_w_val)
        kwh = monthly_kwh(fac_w_val, hours_per_month)
        rows.append(
            {
                "Hardware": label,
                "TDP (W)": hw["tdp_w"],
                "Sustained (W)": round(eff_w, 1),
                "Facility (W)": round(fac_w_val, 1),
                "Energy (kWh/mo)": round(kwh, 1),
                "Energy cost ($/mo)": round(monthly_energy_cost(kwh, price_per_kwh), 2),
                "Water (L/mo)": round(monthly_water_litres(kwh, wue), 0),
                "CO2 (kg/mo)": round(monthly_co2_kg(kwh, grid_intensity), 1),
            }
        )

    results = pd.DataFrame(rows).set_index("Hardware")

    # -- Main content --------------------------------------------------------
    st.title("CPU vs GPU Power & Sustainability Calculator")
    st.caption(
        "Companion to [docs/green-inference.md](../docs/green-inference.md). "
        "Estimates power draw (W), monthly energy (kWh), electricity cost, water "
        "consumption, and CO₂ emissions for sustained inference workloads."
    )

    st.subheader("Headline comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Hardware A — monthly energy",
            f"{results.iloc[0]['Energy (kWh/mo)']:.0f} kWh",
        )
        st.metric(
            "Hardware A — monthly CO₂", f"{results.iloc[0]['CO2 (kg/mo)']:.0f} kg"
        )
    with col2:
        st.metric(
            "Hardware B — monthly energy",
            f"{results.iloc[1]['Energy (kWh/mo)']:.0f} kWh",
        )
        st.metric(
            "Hardware B — monthly CO₂", f"{results.iloc[1]['CO2 (kg/mo)']:.0f} kg"
        )

    delta_energy = (
        results.iloc[1]["Energy (kWh/mo)"] - results.iloc[0]["Energy (kWh/mo)"]
    )
    delta_co2 = results.iloc[1]["CO2 (kg/mo)"] - results.iloc[0]["CO2 (kg/mo)"]
    delta_water = results.iloc[1]["Water (L/mo)"] - results.iloc[0]["Water (L/mo)"]
    delta_cost = (
        results.iloc[1]["Energy cost ($/mo)"] - results.iloc[0]["Energy cost ($/mo)"]
    )

    if delta_energy > 0:
        st.success(
            f"Hardware A saves **{delta_energy:.0f} kWh/mo**, "
            f"**{delta_water:.0f} L water/mo**, "
            f"**{delta_co2:.0f} kg CO₂/mo**, "
            f"and **${delta_cost:.2f}/mo** in energy costs vs Hardware B."
        )
    elif delta_energy < 0:
        st.warning(
            f"Hardware A draws {-delta_energy:.0f} kWh/mo more than Hardware B — "
            f"the CPU path is not always greener at this load factor."
        )

    st.subheader("Detailed comparison")
    st.dataframe(results, use_container_width=True)

    # Annual totals
    st.subheader("Annualised impact (×12)")
    annual = pd.DataFrame(
        {
            "Metric": [
                "Energy (kWh/yr)",
                "Energy cost ($/yr)",
                "Water (L/yr)",
                "CO₂ (kg/yr)",
            ],
            "Hardware A": [
                results.iloc[0]["Energy (kWh/mo)"] * 12,
                results.iloc[0]["Energy cost ($/mo)"] * 12,
                results.iloc[0]["Water (L/mo)"] * 12,
                results.iloc[0]["CO2 (kg/mo)"] * 12,
            ],
            "Hardware B": [
                results.iloc[1]["Energy (kWh/mo)"] * 12,
                results.iloc[1]["Energy cost ($/mo)"] * 12,
                results.iloc[1]["Water (L/mo)"] * 12,
                results.iloc[1]["CO2 (kg/mo)"] * 12,
            ],
        }
    )
    annual["Δ (A − B)"] = annual["Hardware A"] - annual["Hardware B"]
    annual_fmt = annual.copy()
    for c in ["Hardware A", "Hardware B", "Δ (A − B)"]:
        annual_fmt[c] = annual_fmt[c].map(lambda v: f"{v:,.1f}")
    st.table(annual_fmt)

    # Load factor sweep
    st.subheader("Energy consumption vs load factor")
    load_sweep = pd.DataFrame({"load": [lf / 100.0 for lf in range(20, 105, 5)]})
    load_sweep["Hardware A (kWh/mo)"] = load_sweep["load"].apply(
        lambda lf: monthly_kwh(
            facility_w(effective_load_w(hw_a["tdp_w"], lf), pue), hours_per_month
        )
    )
    load_sweep["Hardware B (kWh/mo)"] = load_sweep["load"].apply(
        lambda lf: monthly_kwh(
            facility_w(effective_load_w(hw_b["tdp_w"], lf), pue), hours_per_month
        )
    )
    load_sweep = load_sweep.set_index("load")
    st.line_chart(load_sweep, height=300)
    st.caption(
        "X-axis: sustained load factor (% of TDP). Y-axis: monthly kWh. "
        "The crossing point shows where the CPU/GPU power balance flips."
    )

    with st.expander("Show raw load-sweep table"):
        st.dataframe(load_sweep.style.format("{:,.1f}"), use_container_width=True)

    # --------------------------------------------------------------------
    # Performance efficiency (new: #4)
    # --------------------------------------------------------------------
    st.subheader("Performance efficiency")
    st.caption(
        "Bridges throughput and power: how much compute do you get per watt, "
        "and how much CO₂ does each generated token cost?"
    )

    eff_rows = []
    for (label, hw), fac_w_val in zip(
        [(hw_label_a, hw_a), (hw_label_b, hw_b)], fac_w_vals
    ):
        tpw = tok_s_per_watt(hw["tok_s"], fac_w_val)
        co2pm = co2_per_million_tokens(fac_w_val, hw["tok_s"], grid_intensity)
        wpm = water_per_million_tokens(fac_w_val, hw["tok_s"], wue)
        eff_rows.append(
            {
                "Hardware": label,
                "tok/s": hw["tok_s"],
                "Facility W": round(fac_w_val, 1),
                "tok/s per facility W": round(tpw, 4),
                "kgCO₂ / 1M tokens": round(co2pm, 3) if co2pm != float("inf") else "∞",
                "L water / 1M tokens": round(wpm, 2) if wpm != float("inf") else "∞",
            }
        )

    eff_df = pd.DataFrame(eff_rows).set_index("Hardware")
    st.dataframe(eff_df, use_container_width=True)

    col_eff1, col_eff2 = st.columns(2)
    with col_eff1:
        st.markdown("**tok/s per facility watt** (higher = more compute-efficient)")
        tpw_chart = pd.DataFrame(
            {
                hw_label_a: [tok_s_per_watt(hw_a["tok_s"], fac_w_vals[0])],
                hw_label_b: [tok_s_per_watt(hw_b["tok_s"], fac_w_vals[1])],
            }
        )
        st.bar_chart(tpw_chart.T.rename(columns={0: "tok/s per W"}), height=240)

    with col_eff2:
        st.markdown("**kgCO₂ per 1M tokens** (lower = greener)")
        co2_a = co2_per_million_tokens(fac_w_vals[0], hw_a["tok_s"], grid_intensity)
        co2_b = co2_per_million_tokens(fac_w_vals[1], hw_b["tok_s"], grid_intensity)
        if co2_a != float("inf") and co2_b != float("inf"):
            co2_chart = pd.DataFrame({hw_label_a: [co2_a], hw_label_b: [co2_b]})
            st.bar_chart(co2_chart.T.rename(columns={0: "kgCO₂/1M tokens"}), height=240)
        else:
            st.info("Set tok/s > 0 in the sidebar to see this chart.")

    # Per-region CO₂
    st.subheader("CO₂ by region")
    regions = {k: v for k, v in GRID_PRESETS.items() if k != "Custom grid intensity"}
    region_rows = []
    for region, intensity in regions.items():
        co2_a_reg = monthly_co2_kg(results.iloc[0]["Energy (kWh/mo)"], intensity)
        co2_b_reg = monthly_co2_kg(results.iloc[1]["Energy (kWh/mo)"], intensity)
        region_rows.append(
            {
                "Region": region,
                "gCO₂/kWh": intensity,
                "Hardware A (kg/mo)": round(co2_a_reg, 1),
                "Hardware B (kg/mo)": round(co2_b_reg, 1),
                "Δ saved (kg/mo)": round(co2_b_reg - co2_a_reg, 1),
            }
        )
    st.dataframe(pd.DataFrame(region_rows), use_container_width=True)

    with st.expander("Formula reference"):
        st.markdown(
            """
            **Effective load (W)** = TDP × load factor

            **Facility power (W)** = effective load × PUE

            **Monthly energy (kWh)** = facility W × hours / 1000

            **Monthly energy cost ($)** = kWh × price per kWh

            **Monthly water (L)** = kWh × WUE

            **Monthly CO₂ (kg)** = kWh × grid intensity (g/kWh) / 1000

            **tok/s per facility W** = tok/s ÷ facility W  *(higher = more compute-efficient)*

            **kgCO₂ / 1M tokens** = facility W × grid g/kWh ÷ (tok/s × 3600)
            """
        )

    st.markdown("---")
    st.caption(
        "See [green-inference.md](../docs/green-inference.md) for the full energy "
        "methodology, TDP reference table, PUE/WUE data sources, and CPU power "
        "management tuning."
    )
