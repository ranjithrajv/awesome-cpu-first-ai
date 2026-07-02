"""Pure power, water, and carbon calculation functions."""

from __future__ import annotations

from .constants import HOURS_PER_MONTH, SECONDS_PER_HOUR, TOKENS_PER_MILLION


def effective_load_w(tdp_w: float, load_factor: float) -> float:
    """Sustained draw is below TDP; load_factor (0–1) models this."""
    return tdp_w * load_factor


def facility_w(it_w: float, pue: float) -> float:
    return it_w * pue


def monthly_kwh(facility_watts: float, hours: float = HOURS_PER_MONTH) -> float:
    return facility_watts * hours / 1_000.0


def monthly_energy_cost(kwh: float, price_per_kwh: float) -> float:
    return kwh * price_per_kwh


def monthly_water_litres(kwh: float, wue: float) -> float:
    return kwh * wue


def monthly_co2_kg(kwh: float, grid_intensity_g_per_kwh: float) -> float:
    return kwh * grid_intensity_g_per_kwh / 1_000.0


def tok_s_per_watt(tok_s: float, facility_watts: float) -> float:
    """Tokens per second per facility watt — higher is more compute-efficient."""
    if facility_watts <= 0:
        return 0.0
    return tok_s / facility_watts


def co2_per_million_tokens(
    facility_watts: float, tok_s: float, grid_intensity_g_per_kwh: float
) -> float:
    """kgCO₂ per 1M tokens.

    Derivation: kgCO₂/hr = facility_W/1000 × grid_g/kWh / 1000
                tokens/hr = tok/s × 3600
                kgCO₂/1M = kgCO₂/hr / (tokens/hr) × 1e6
                          = facility_W × grid_g/kWh / (tok/s × 3600)
    """
    if tok_s <= 0 or facility_watts <= 0:
        return float("inf")
    return facility_watts * grid_intensity_g_per_kwh / (tok_s * SECONDS_PER_HOUR)


def water_per_million_tokens(
    facility_watts: float, tok_s: float, wue_l_per_kwh: float
) -> float:
    """Litres of water per 1M tokens."""
    if tok_s <= 0 or facility_watts <= 0:
        return float("inf")
    kwh_per_hr = facility_watts / 1_000.0
    litres_per_hr = kwh_per_hr * wue_l_per_kwh
    tokens_per_hr = tok_s * SECONDS_PER_HOUR
    return litres_per_hr / tokens_per_hr * TOKENS_PER_MILLION
