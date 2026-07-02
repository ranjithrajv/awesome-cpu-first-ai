"""Pure cost calculation functions for CPU vs GPU inference."""

from __future__ import annotations

from .constants import HOURS_PER_MONTH, SECONDS_PER_HOUR, TOKENS_PER_MILLION


def cost_per_million(price_per_hr: float, tok_s: float, util: float) -> float:
    """$/1M tokens = (price/hr × 1e6) / (tok/s × 3600 × util)."""
    if tok_s <= 0 or util <= 0:
        return float("inf")
    return (price_per_hr * TOKENS_PER_MILLION) / (tok_s * SECONDS_PER_HOUR * util)


def monthly_cost(price_per_hr: float, hours: int = HOURS_PER_MONTH) -> float:
    return price_per_hr * hours


def annual_tco(price_per_hr: float, hours_per_month: int = HOURS_PER_MONTH) -> float:
    return monthly_cost(price_per_hr, hours_per_month) * 12


def cost_per_request(
    tokens: int, tok_s: float, util: float, price_per_hr: float
) -> float:
    """$/request = (tokens / effective_tok_s) / 3600 × $/hr."""
    effective = tok_s * util
    if effective <= 0:
        return float("inf")
    return (tokens / effective) / SECONDS_PER_HOUR * price_per_hr
