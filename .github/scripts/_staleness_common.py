"""Shared conventions for the staleness-checking scripts.

check-staleness.py (linked GitHub repos) and check-content-staleness.py
(`*(last verified: YYYY-MM)*` tags) detect staleness differently, but both
report it the same way — this module holds only that shared reporting
shape, not any detection logic.
"""
from __future__ import annotations

from datetime import datetime

STALE_THRESHOLD_DAYS = 365


def report_header(title: str, now: datetime, threshold: int = STALE_THRESHOLD_DAYS) -> list[str]:
    return [
        f"## {title}",
        f"_Generated {now.strftime('%Y-%m-%d')} · threshold: {threshold} days_",
        "",
    ]


def checklist_line(label: str, url: str | None, note: str) -> str:
    target = f"[{label}]({url})" if url else f"`{label}`"
    return f"- [ ] {target} — {note}"
