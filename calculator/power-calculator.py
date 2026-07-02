"""Streamlit app: CPU vs GPU power, water, and carbon calculator.

Run with:
    uv run streamlit run calculator/power-calculator.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.constants import HOURS_PER_MONTH
from lib.power import (
    effective_load_w,
    facility_w,
    monthly_co2_kg,
    monthly_energy_cost,
    monthly_kwh,
    monthly_water_litres,
)
from lib.presets import GRID_PRESETS, HARDWARE_PRESETS, PUE_PRESETS, WUE_PRESETS


# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="CPU vs GPU Power & Sustainability Calculator",
    page_icon="🌱",
    layout="wide",
)

st.title("CPU vs GPU Power & Sustainability Calculator")
st.caption(
    "Companion to [docs/green-inference.md](../docs/green-inference.md). "
    "Estimates power draw (W), monthly energy (kWh), electricity cost, water "
    "consumption, and CO₂ emissions for sustained inference workloads."
)

# ----------------------------------------------------------------------------
# Sidebar: hardware + facility config
# ----------------------------------------------------------------------------
st.sidebar.header("Configuration")

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
    st.sidebar.slider("Sustained load factor (% of TDP)", 20, 100, 80, step=5) / 100.0
)
hw_a["tdp_w"] = st.sidebar.number_input(
    "Hardware A TDP (W)", value=hw_a["tdp_w"], min_value=0.0, key="tdp_a"
)
hw_b["tdp_w"] = st.sidebar.number_input(
    "Hardware B TDP (W)", value=hw_b["tdp_w"], min_value=0.0, key="tdp_b"
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

# ----------------------------------------------------------------------------
# Compute
# ----------------------------------------------------------------------------
rows = []
for label, hw in [(hw_label_a, hw_a), (hw_label_b, hw_b)]:
    eff_w = effective_load_w(hw["tdp_w"], load_factor)
    fac_w = facility_w(eff_w, pue)
    kwh = monthly_kwh(fac_w, hours_per_month)
    energy_cost = monthly_energy_cost(kwh, price_per_kwh)
    water_l = monthly_water_litres(kwh, wue)
    co2_kg = monthly_co2_kg(kwh, grid_intensity)
    rows.append(
        {
            "Hardware": label,
            "TDP (W)": hw["tdp_w"],
            "Sustained (W)": round(eff_w, 1),
            "Facility (W)": round(fac_w, 1),
            "Energy (kWh/mo)": round(kwh, 1),
            "Energy cost ($/mo)": round(energy_cost, 2),
            "Water (L/mo)": round(water_l, 0),
            "CO2 (kg/mo)": round(co2_kg, 1),
        }
    )

results = pd.DataFrame(rows).set_index("Hardware")

# ----------------------------------------------------------------------------
# Headline metrics
# ----------------------------------------------------------------------------
st.subheader("Headline comparison")

col1, col2 = st.columns(2)
with col1:
    st.metric(
        "Hardware A — monthly energy", f"{results.iloc[0]['Energy (kWh/mo)']:.0f} kWh"
    )
    st.metric("Hardware A — monthly CO₂", f"{results.iloc[0]['CO2 (kg/mo)']:.0f} kg")
with col2:
    st.metric(
        "Hardware B — monthly energy", f"{results.iloc[1]['Energy (kWh/mo)']:.0f} kWh"
    )
    st.metric("Hardware B — monthly CO₂", f"{results.iloc[1]['CO2 (kg/mo)']:.0f} kg")

delta_energy = results.iloc[1]["Energy (kWh/mo)"] - results.iloc[0]["Energy (kWh/mo)"]
delta_co2 = results.iloc[1]["CO2 (kg/mo)"] - results.iloc[0]["CO2 (kg/mo)"]
delta_water = results.iloc[1]["Water (L/mo)"] - results.iloc[0]["Water (L/mo)"]
delta_cost = (
    results.iloc[1]["Energy cost ($/mo)"] - results.iloc[0]["Energy cost ($/mo)"]
)

if delta_energy > 0:
    st.success(
        f"Hardware A (CPU) saves **{delta_energy:.0f} kWh/mo**, "
        f"**{delta_water:.0f} L water/mo**, "
        f"**{delta_co2:.0f} kg CO₂/mo**, "
        f"and **${delta_cost:.2f}/mo** in energy costs "
        f"vs Hardware B."
    )
elif delta_energy < 0:
    st.warning(
        f"Hardware A draws {-delta_energy:.0f} kWh/mo more than Hardware B — "
        f"the CPU path is not always greener at this load factor."
    )

# ----------------------------------------------------------------------------
# Comparison table
# ----------------------------------------------------------------------------
st.subheader("Detailed comparison")
st.dataframe(results, use_container_width=True)

# ----------------------------------------------------------------------------
# Annual totals
# ----------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------
# Sensitivity: load factor sweep
# ----------------------------------------------------------------------------
st.subheader("Energy consumption vs load factor")
load_sweep = pd.DataFrame({"load": [pct / 100.0 for pct in range(20, 105, 5)]})
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
    "X-axis: sustained load factor (% of TDP). Y-axis: monthly kWh. The crossing point shows where the CPU/GPU power balance flips."
)

with st.expander("Show raw load-sweep table"):
    st.dataframe(load_sweep.style.format("{:,.1f}"), use_container_width=True)

# ----------------------------------------------------------------------------
# Per-region carbon comparison
# ----------------------------------------------------------------------------
st.subheader("CO₂ by region")
regions = {k: v for k, v in GRID_PRESETS.items() if k != "Custom grid intensity"}
region_rows = []
for region, intensity in regions.items():
    co2_a = monthly_co2_kg(results.iloc[0]["Energy (kWh/mo)"], intensity)
    co2_b = monthly_co2_kg(results.iloc[1]["Energy (kWh/mo)"], intensity)
    region_rows.append(
        {
            "Region": region,
            "gCO₂/kWh": intensity,
            "Hardware A (kg/mo)": round(co2_a, 1),
            "Hardware B (kg/mo)": round(co2_b, 1),
            "Δ saved (kg/mo)": round(co2_b - co2_a, 1),
        }
    )
st.dataframe(pd.DataFrame(region_rows), use_container_width=True)

# ----------------------------------------------------------------------------
# Formula reference
# ----------------------------------------------------------------------------
with st.expander("Formula reference"):
    st.markdown(
        """
        **Effective load (W)** = TDP × load factor

        **Facility power (W)** = effective load × PUE

        **Monthly energy (kWh)** = facility W × hours / 1000

        **Monthly energy cost ($)** = kWh × price per kWh

        **Monthly water (L)** = kWh × WUE

        **Monthly CO₂ (kg)** = kWh × grid intensity (g/kWh) / 1000

        See [green-inference.md](../docs/green-inference.md) for the underlying
        methodology, TDP data, WUE/PUE reference tables, and worked examples.
        """
    )

st.markdown("---")
st.caption(
    "See [green-inference.md](../docs/green-inference.md) for the full energy "
    "methodology, TDP reference table, PUE/WUE data sources, and CPU power "
    "management tuning. See [green-inference-cheat-sheet.md](../docs/green-inference-cheat-sheet.md) "
    "for the one-page quick reference."
)
