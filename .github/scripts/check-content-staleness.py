#!/usr/bin/env python3
"""
Check content staleness for entries carrying an explicit
`*(last verified: YYYY-MM)*` tag.

Exit 0 — no tagged entry is older than STALE_THRESHOLD_DAYS.
Exit 1 — one or more tagged entries need re-verification; prints a markdown
         summary suitable for use as a GitHub issue body.

Unlike check-staleness.py (which checks whether a linked *repository* is
still active), this script checks whether a *claim in the text* — a
benchmark figure, price, or availability statement — was last confirmed
against its source within the threshold. Only entries explicitly tagged
with `*(last verified: YYYY-MM)*` are considered; citation dates like
"(MLCommons, Apr 2025)" are a source's publication date and do not go
stale the same way, so they are intentionally not flagged here.
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from _staleness_common import STALE_THRESHOLD_DAYS, checklist_line, report_header

DOC_FILES = [Path("README.md"), *sorted(Path("docs").glob("*.md"))]

TAG_RE = re.compile(r"\*\(last verified:\s*(\d{4})-(\d{2})\)\*")
LINK_RE = re.compile(r"\[([^\]]+)\]\(https?://[^)]+\)")


def find_tagged_entries(path: Path, now: datetime) -> list[tuple[str, str, int]]:
    """Return (file, entry_title, age_days) for each last-verified tag in path."""
    results = []
    for line in path.read_text().splitlines():
        match = TAG_RE.search(line)
        if not match:
            continue
        year, month = int(match.group(1)), int(match.group(2))
        verified_at = datetime(year, month, 1, tzinfo=timezone.utc)
        age_days = (now - verified_at).days
        title_match = LINK_RE.search(line)
        title = title_match.group(1) if title_match else line.strip()[:80]
        results.append((str(path), title, age_days))
    return results


def main() -> int:
    now = datetime.now(timezone.utc)
    all_entries = []
    for path in DOC_FILES:
        if path.exists():
            all_entries.extend(find_tagged_entries(path, now))

    if not all_entries:
        print("No `*(last verified: YYYY-MM)*` tags found — nothing to check.")
        return 0

    stale = [e for e in all_entries if e[2] > STALE_THRESHOLD_DAYS]

    if not stale:
        print(
            f"✅ All {len(all_entries)} tagged entries verified within "
            f"the last {STALE_THRESHOLD_DAYS} days."
        )
        return 0

    lines = report_header("Content Staleness Report", now)
    lines += [
        f"### Needs re-verification (> {STALE_THRESHOLD_DAYS} days since last check)",
        "",
    ]
    for file, title, age in sorted(stale, key=lambda x: -x[2]):
        lines.append(
            checklist_line(file, None, f"{title} — {age} days since last verified")
        )

    print("\n".join(lines))
    return 1


if __name__ == "__main__":
    sys.exit(main())
