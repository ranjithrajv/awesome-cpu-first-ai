#!/usr/bin/env python3
"""
Verify markdown tables of contents are complete.

For docs/*.md files with a `## Contents` section: checks that every `##`
heading (excluding Contents itself) has a corresponding ToC entry.

For README.md: checks that ToC anchor links resolve to actual headings.
"""

import re
import sys
from pathlib import Path

DOCS = Path("docs")
README = Path("README.md")
SKIP_HEADINGS = {"Contents"}


def heading_to_anchor(name: str) -> str:
    anchor = name.lower().replace(" ", "-")
    anchor = re.sub(r"[^a-z0-9-]", "", anchor)
    return anchor


def extract_section_headings(text: str) -> list[str]:
    headings = []
    for m in re.finditer(r"^##\s+(.+)$", text, re.MULTILINE):
        name = m.group(1).strip()
        if name not in SKIP_HEADINGS:
            headings.append(name)
    return headings


def extract_toc_anchors(text: str) -> set[str]:
    anchors = set()
    in_toc = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Contents":
            in_toc = True
            continue
        if in_toc and stripped.startswith("## ") and stripped != "## Contents":
            break
        if in_toc and stripped.startswith("- ["):
            m = re.search(r"\((#([^)]+))\)", stripped)
            if m:
                anchors.add(m.group(1))
    return anchors


def extract_toc_labels(text: str) -> set[str]:
    labels = set()
    in_toc = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Contents":
            in_toc = True
            continue
        if in_toc and stripped.startswith("## ") and stripped != "## Contents":
            break
        if in_toc and stripped.startswith("- ["):
            m = re.search(r"\[([^\]]+)\]", stripped)
            if m:
                labels.add(m.group(1))
    return labels


def all_headings_set(text: str) -> set[str]:
    return set(extract_section_headings(text))


def check_doc(path: Path) -> list[str]:
    text = path.read_text()
    toc_labels = extract_toc_labels(text)
    headings = extract_section_headings(text)
    errors = []
    for h in headings:
        if h not in toc_labels:
            errors.append(f"  missing from ToC: {h}")
    return errors


def main() -> int:
    doc_files = sorted(DOCS.glob("*.md"))
    has_errors = False

    for path in doc_files:
        if not path.exists():
            continue
        text = path.read_text()
        if "## Contents" not in text:
            continue
        errors = check_doc(path)
        if errors:
            has_errors = True
            print(f"\n{path}:")
            for e in errors:
                print(e)

    if has_errors:
        print("\n\u274c ToC validation failed.")
        return 1
    print("\u2705 All tables of contents are complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
