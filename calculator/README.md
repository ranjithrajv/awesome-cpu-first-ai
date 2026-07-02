# CPU vs GPU Inference Cost Calculator

Interactive calculators for comparing CPU and GPU inference costs. Run any of the scripts in this folder with [`uv`](https://docs.astral.sh/uv/) — no manual venv or pip needed.

## Available calculators

| Script | Purpose | Run |
|---|---|---|
| [cost-calculator.py](cost-calculator.py) | CPU vs GPU TCO, $/1M tokens, utilisation sweep, per-request cost | `uv run streamlit run calculator/cost-calculator.py` |
| [power-calculator.py](power-calculator.py) | Power (W), energy (kWh), water (L), CO₂ (kg) — with PUE/WUE and grid-region carbon sweep | `uv run streamlit run calculator/power-calculator.py` |

## Quick start

```bash
uv run streamlit run calculator/cost-calculator.py
uv run streamlit run calculator/power-calculator.py
```

`uv` reads [pyproject.toml](pyproject.toml), resolves dependencies, and launches the app in one command. No virtualenv, no `pip install` — uv caches everything locally. If you don't have uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Defaults reflect us-east-1 on-demand pricing (June 2026) and llama.cpp benchmarks for Llama-3-8B Q4_K_M. Verify current pricing at [aws.amazon.com/ec2/pricing](https://aws.amazon.com/ec2/pricing/on-demand/). Power data sourced from [green-inference.md](../docs/green-inference.md).

## Companion documentation

See [docs/cost-calculator.md](../docs/cost-calculator.md) for the full methodology, pricing reference, throughput benchmarks, and a worked production example.

## Adding a new calculator

1. Add any new runtime dependencies to [pyproject.toml](pyproject.toml).
2. Create a new `.py` file in `calculator/`.
3. Use the same Streamlit conventions (sidebar for inputs, `st.metric` for headlines, `st.line_chart` for sweeps).
4. Reference any data tables from the existing `docs/cost-calculator.md` to avoid duplication.
5. Add the script to the table above.