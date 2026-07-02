#!/usr/bin/env python3
"""
Check GitHub repository staleness for every repo listed in README.md.

Exit 0 — all repos updated within STALE_THRESHOLD_DAYS.
Exit 1 — one or more repos are stale or archived; prints a markdown summary
         suitable for use as a GitHub issue body.

Requires the `gh` CLI, authenticated via GH_TOKEN in the environment.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from _staleness_common import STALE_THRESHOLD_DAYS, checklist_line, report_header

README = Path("README.md")


def extract_repos(text: str) -> list[str]:
    """Return sorted unique 'owner/repo' slugs found in github.com URLs."""
    # Stop the capture group before any further path segment, query, or fragment.
    matches = re.findall(
        r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:[/#?]|$)",
        text,
    )
    return sorted(set(matches))


def gh_api(path: str) -> dict | None:
    result = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def main() -> int:
    text = README.read_text()
    repos = extract_repos(text)
    now = datetime.now(timezone.utc)

    stale: list[tuple[str, int]] = []
    archived: list[tuple[str, int]] = []
    errors: list[str] = []

    for repo in repos:
        data = gh_api(f"repos/{repo}")
        if data is None:
            errors.append(repo)
            continue

        pushed_at = data.get("pushed_at") or data.get("updated_at")
        is_archived = data.get("archived", False)

        if not pushed_at:
            errors.append(repo)
            continue

        last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        age_days = (now - last_push).days

        if is_archived:
            archived.append((repo, age_days))
        elif age_days > STALE_THRESHOLD_DAYS:
            stale.append((repo, age_days))

    if not stale and not archived:
        print(
            f"✅ All {len(repos)} listed repositories "
            f"updated within the last {STALE_THRESHOLD_DAYS} days."
        )
        return 0

    lines = report_header("Staleness Report", now)

    if stale:
        lines += [
            f"### Not updated in > {STALE_THRESHOLD_DAYS} days",
            "",
        ]
        for repo, age in sorted(stale, key=lambda x: -x[1]):
            lines.append(
                checklist_line(
                    repo, f"https://github.com/{repo}", f"{age} days since last push"
                )
            )

    if archived:
        lines += ["", "### Archived", ""]
        for repo, age in sorted(archived, key=lambda x: -x[1]):
            lines.append(
                checklist_line(
                    repo,
                    f"https://github.com/{repo}",
                    f"archived ({age} days since last push)",
                )
            )

    if errors:
        lines += ["", "### Could not fetch", ""]
        for repo in sorted(errors):
            lines.append(f"- {repo}")

    print("\n".join(lines))
    return 1


if __name__ == "__main__":
    sys.exit(main())
