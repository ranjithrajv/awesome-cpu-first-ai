"""Hardware, grid, and facility presets used across calculators."""

from __future__ import annotations

CPU_PRESETS: dict[str, dict] = {
    "c7g.large (2 vCPU, 4 GB)": {"price": 0.085, "vcpu": 2, "ram": 4, "tok_s": 30},
    "c7g.xlarge (4 vCPU, 8 GB)": {"price": 0.170, "vcpu": 4, "ram": 8, "tok_s": 45},
    "c7g.2xlarge (8 vCPU, 16 GB)": {"price": 0.350, "vcpu": 8, "ram": 16, "tok_s": 25},
    "c7g.4xlarge (16 vCPU, 32 GB)": {
        "price": 0.580,
        "vcpu": 16,
        "ram": 32,
        "tok_s": 35,
    },
    "c7g.16xlarge (64 vCPU, 128 GB)": {
        "price": 2.320,
        "vcpu": 64,
        "ram": 128,
        "tok_s": 17,
    },
    "Custom CPU instance": {"price": 0.0, "vcpu": 0, "ram": 0, "tok_s": 0},
}

GPU_PRESETS: dict[str, dict] = {
    "g4dn.xlarge (4 vCPU + T4 16 GB)": {
        "price": 0.526,
        "vcpu": 4,
        "ram": 16,
        "tok_s": 28,
        "tok_s_batch": 450,
    },
    "g5.xlarge (4 vCPU + A10G 24 GB)": {
        "price": 1.006,
        "vcpu": 4,
        "ram": 24,
        "tok_s": 63,
        "tok_s_batch": 1820,
    },
    "g5.2xlarge (8 vCPU + A10G 24 GB)": {
        "price": 1.212,
        "vcpu": 8,
        "ram": 24,
        "tok_s": 90,
        "tok_s_batch": 1820,
    },
    "g6.xlarge (4 vCPU + L40S 48 GB)": {
        "price": 1.323,
        "vcpu": 4,
        "ram": 48,
        "tok_s": 95,
        "tok_s_batch": 3200,
    },
    "Custom GPU instance": {
        "price": 0.0,
        "vcpu": 0,
        "ram": 0,
        "tok_s": 0,
        "tok_s_batch": 0,
    },
}

# TDP is peak; sustained load is lower — see docs/green-inference.md
# tok_s: llama.cpp single-batch throughput on Llama-3-8B Q4_K_M (approximate)
HARDWARE_PRESETS: dict[str, dict] = {
    "Ampere Altra Max 128-core (CPU)": {"tdp_w": 250, "tok_s": 20, "type": "cpu"},
    "AWS Graviton3 c7g.16xlarge (CPU)": {"tdp_w": 150, "tok_s": 17, "type": "cpu"},
    "Intel Xeon w9-3595X 60-core (CPU)": {"tdp_w": 350, "tok_s": 28, "type": "cpu"},
    "Intel Xeon 6 144-core (CPU)": {"tdp_w": 330, "tok_s": 35, "type": "cpu"},
    "Nvidia Tesla T4 (GPU only)": {"tdp_w": 70, "tok_s": 28, "type": "gpu"},
    "Nvidia A10 (GPU only)": {"tdp_w": 150, "tok_s": 63, "type": "gpu"},
    "Nvidia A100 SXM4 (GPU only)": {"tdp_w": 400, "tok_s": 120, "type": "gpu"},
    "Nvidia H100 SXM5 (GPU only)": {"tdp_w": 700, "tok_s": 200, "type": "gpu"},
    "Custom hardware": {"tdp_w": 0, "tok_s": 0, "type": "cpu"},
}

# Combined presets for the Decision Dashboard — all metrics in one place.
# CPU tdp_w ≈ (vcpu / host_vcpu) × host_TDP. GPU tdp_w = GPU TDP + ~100 W system.
# Pricing: us-east-1 on-demand (June 2026). Verify at aws.amazon.com/ec2/pricing.
# tok_s / tok_s_batch: llama.cpp on Llama-3-8B Q4_K_M (approximate).
COMBINED_PRESETS: dict[str, dict] = {
    "c7g.2xlarge — Graviton3 (8 vCPU)": {
        "price": 0.350,
        "tok_s": 25,
        "tok_s_batch": 25,
        "tdp_w": 19,
        "type": "cpu",
    },
    "c7g.4xlarge — Graviton3 (16 vCPU)": {
        "price": 0.580,
        "tok_s": 35,
        "tok_s_batch": 35,
        "tdp_w": 38,
        "type": "cpu",
    },
    "c7g.16xlarge — Graviton3 (64 vCPU, full host)": {
        "price": 2.320,
        "tok_s": 17,
        "tok_s_batch": 17,
        "tdp_w": 150,
        "type": "cpu",
    },
    "g4dn.xlarge — T4 16 GB": {
        "price": 0.526,
        "tok_s": 28,
        "tok_s_batch": 450,
        "tdp_w": 170,
        "type": "gpu",
    },
    "g5.xlarge — A10G 24 GB": {
        "price": 1.006,
        "tok_s": 63,
        "tok_s_batch": 1820,
        "tdp_w": 250,
        "type": "gpu",
    },
    "g6.xlarge — L40S 48 GB": {
        "price": 1.323,
        "tok_s": 95,
        "tok_s_batch": 3200,
        "tdp_w": 330,
        "type": "gpu",
    },
    "Custom": {
        "price": 0.0,
        "tok_s": 0.0,
        "tok_s_batch": 0.0,
        "tdp_w": 0,
        "type": "cpu",
    },
}

# gCO2eq/kWh — source: docs/green-inference.md
GRID_PRESETS: dict[str, float] = {
    "Norway / Iceland (hydro)": 25,
    "France (nuclear)": 52,
    "UK (2023 avg)": 148,
    "California (CAISO)": 200,
    "EU average": 231,
    "US average (EPA eGRID 2022)": 386,
    "Germany": 350,
    "Texas (ERCOT)": 400,
    "Poland (coal-heavy)": 700,
    "Custom grid intensity": 0,
}

PUE_PRESETS: dict[str, float] = {
    "Hyperscale (AWS/Azure/GCP) — 1.15": 1.15,
    "Modern co-location — 1.30": 1.30,
    "Enterprise on-prem (older) — 1.50": 1.50,
    "Custom PUE": 1.00,
}

WUE_PRESETS: dict[str, float] = {
    "Hyperscale best-practice — 0.5 L/kWh": 0.5,
    "Modern co-location — 1.0 L/kWh": 1.0,
    "Enterprise on-prem (older) — 1.5 L/kWh": 1.5,
    "Custom WUE": 0.5,
}
