"""Streamlit app: CPU vs GPU inference cost calculator.

Run with:
    uv run streamlit run calculator/cost-calculator.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.constants import HOURS_PER_MONTH
from lib.cost import cost_per_million, cost_per_request, monthly_cost
from lib.presets import CPU_PRESETS, GPU_PRESETS


# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="CPU vs GPU Inference Cost Calculator",
    page_icon="💰",
    layout="wide",
)

st.title("CPU vs GPU Inference Cost Calculator")
st.caption(
    "Interactive companion to [docs/cost-calculator.md](../docs/cost-calculator.md). "
    "Defaults reflect us-east-1 on-demand pricing (June 2026) and llama.cpp "
    "benchmarks for Llama-3-8B Q4_K_M. Verify current pricing at "
    "[aws.amazon.com/ec2/pricing](https://aws.amazon.com/ec2/pricing/on-demand/)."
)

# ----------------------------------------------------------------------------
# Sidebar: instance selection
# ----------------------------------------------------------------------------
st.sidebar.header("Instance configuration")

cpu_keys = list(CPU_PRESETS.keys())
gpu_keys = list(GPU_PRESETS.keys())
default_gpu_key = "g5.xlarge (4 vCPU + A10G 24 GB)"

cpu_label = st.sidebar.selectbox("CPU instance", cpu_keys, index=2)
gpu_label = st.sidebar.selectbox(
    "GPU instance",
    gpu_keys,
    index=gpu_keys.index(default_gpu_key) if default_gpu_key in gpu_keys else 0,
)

cpu = dict(CPU_PRESETS[cpu_label])
gpu = dict(GPU_PRESETS[gpu_label])

st.sidebar.subheader("CPU — editable")
cpu["price"] = st.sidebar.number_input(
    "CPU $/hr", value=cpu["price"], min_value=0.0, format="%.3f", key="cpu_price"
)
cpu["tok_s"] = st.sidebar.number_input(
    "CPU tok/s (batch=1)",
    value=cpu["tok_s"],
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
    value=gpu["tok_s"],
    min_value=0.0,
    format="%.1f",
    key="gpu_tok",
)
gpu["tok_s_batch"] = st.sidebar.number_input(
    "GPU tok/s (batch=32)",
    value=gpu.get("tok_s_batch", 0.0),
    min_value=0.0,
    format="%.1f",
    key="gpu_tok_batch",
)

# ----------------------------------------------------------------------------
# Utilization sweep
# ----------------------------------------------------------------------------
st.sidebar.subheader("Utilization")
util = st.sidebar.slider("Utilization (%)", 10, 100, 100, step=5) / 100.0

# ----------------------------------------------------------------------------
# Headline metrics
# ----------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    cpu_cpt = cost_per_million(cpu["price"], cpu["tok_s"], util)
    st.metric("CPU $/1M tokens", f"${cpu_cpt:,.2f}")
with col2:
    gpu_cpt = cost_per_million(gpu["price"], gpu["tok_s"], util)
    st.metric("GPU $/1M tokens (batch=1)", f"${gpu_cpt:,.2f}")
with col3:
    gpu_cpt_batch = cost_per_million(gpu["price"], gpu["tok_s_batch"], util)
    st.metric("GPU $/1M tokens (batch=32)", f"${gpu_cpt_batch:,.2f}")

st.caption(
    "At sustained batch=32 the GPU arithmetic advantage dominates. "
    "At batch=1 or low utilisation the picture reverses — see the break-even sweep below."
)

# ----------------------------------------------------------------------------
# Break-even sweep across utilization
# ----------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------
# TCO worked example
# ----------------------------------------------------------------------------
st.subheader("Production TCO worked example")
st.caption(
    "Simulates a sustained 730 hrs/month workload. GPU is billed regardless of "
    "idle time; CPU serverless (Lambda/Fly/Modal) bills per-invocation instead."
)

col_tco1, col_tco2 = st.columns(2)
with col_tco1:
    req_per_s = st.number_input(
        "Average requests/sec", value=1.0, min_value=0.0, format="%.2f"
    )
    idle_pct = st.slider("GPU idle fraction (%)", 0, 100, 60, step=5) / 100.0
with col_tco2:
    hours_per_month = st.number_input(
        "Hours/month", value=HOURS_PER_MONTH, min_value=1, step=10
    )

cpu_month = monthly_cost(cpu["price"], hours_per_month)
gpu_month = monthly_cost(gpu["price"], hours_per_month)
cpu_year = cpu_month * 12
gpu_year = gpu_month * 12
savings = gpu_year - cpu_year

st.markdown("#### 12-month TCO")
tco = pd.DataFrame(
    {
        "CPU": [f"${cpu_month:,.2f}", "—", f"${cpu_year:,.2f}"],
        "GPU": [
            f"${gpu_month:,.2f}",
            f"{int(idle_pct * 100)}% idle (paid regardless)",
            f"${gpu_year:,.2f}",
        ],
    },
    index=["Monthly instance cost", "Idle hours", "12-month TCO"],
)
st.table(tco)

if savings > 0:
    st.success(f"**CPU saves ${savings:,.0f}/yr** on this workload.")
elif savings < 0:
    st.warning(
        f"GPU is cheaper by ${-savings:,.0f}/yr — likely the right choice at sustained load."
    )
else:
    st.info("Break-even — both options cost the same at this utilisation.")

# ----------------------------------------------------------------------------
# Per-request cost (using user's throughput)
# ----------------------------------------------------------------------------
st.subheader("Effective cost per request")
st.caption("Assumes 1 request = 1 generation of `tokens_per_req` tokens.")
tokens_per_req = st.number_input("Tokens per request", value=256, min_value=1, step=16)

cpu_per_req = cost_per_request(tokens_per_req, cpu["tok_s"], util, cpu["price"])
gpu_per_req = cost_per_request(tokens_per_req, gpu["tok_s"], util, gpu["price"])

c1, c2 = st.columns(2)
with c1:
    st.metric("CPU $/req", f"${cpu_per_req:.4f}")
with c2:
    st.metric("GPU $/req (batch=1)", f"${gpu_per_req:.4f}")

# ----------------------------------------------------------------------------
# Break-even formula reference
# ----------------------------------------------------------------------------
with st.expander("Break-even formula"):
    st.markdown(
        """
        **$/1M tokens** = (instance $/hr × 1,000,000) / (tok/s × 3,600 × utilisation)

        CPU wins when:
        1. Idle time > 40% — GPU paid regardless, CPU costs scale with work done
        2. Model fits in RAM but not VRAM — GPU forces a more expensive instance class
        3. Sporadic traffic — serverless CPU charges per-invocation only
        4. Batch = 1 — GPU memory bandwidth advantage shrinks at single-request throughput

        To find your break-even: divide GPU instance cost by CPU instance cost,
        then multiply by the CPU/GPU throughput ratio. If the result is < 1, GPU
        wins at full utilisation.
        """
    )

st.markdown("---")
st.caption(
    "See [docs/cost-calculator.md](../docs/cost-calculator.md) for the full methodology, "
    "pricing reference, throughput benchmarks, and a worked production example."
)
