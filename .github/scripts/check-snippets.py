#!/usr/bin/env python3
"""
Validate code snippets in markdown documentation.

Checks:
- Python snippets compile (syntax check via ast.parse)
- Bash snippets avoid common errors (wrong binary names)
- Language tags are valid

Exits 0 if all checks pass, 1 otherwise.
"""

import ast
import re
import sys
from pathlib import Path

DOCS = Path("docs")
README = Path("README.md")

WRONG_BINARIES = {
    "llama-server --prompt": "use llama-cli instead of llama-server for --prompt",
}

LANGUAGE_TAGS = {
    "bash",
    "python",
    "yaml",
    "dockerfile",
    "toml",
    "json",
    "javascript",
    "markdown",
    "text",
    "console",
    "mermaid",
}


def extract_snippets(text: str) -> list[dict]:
    snippets = []
    for m in re.finditer(r"```(\w+)?\n(.*?)```", text, re.DOTALL):
        lang = m.group(1) or ""
        code = m.group(2)
        snippets.append({"lang": lang, "code": code})
    return snippets


def check_python_snippet(code: str, idx: int) -> list[str]:
    try:
        ast.parse(code)
    except SyntaxError as e:
        return [f"  snippet #{idx}: Python syntax error: {e}"]
    return []


def check_bash_snippet(code: str, idx: int) -> list[str]:
    errors = []
    for bad, hint in WRONG_BINARIES.items():
        if bad in code:
            errors.append(f"  snippet #{idx}: {hint}")
    return errors


def check_file(path: Path) -> list[str]:
    text = path.read_text()
    snippets = extract_snippets(text)
    errors = []

    for i, s in enumerate(snippets):
        lang = s["lang"]
        if lang and lang not in LANGUAGE_TAGS:
            errors.append(f"  snippet #{i}: unknown language tag '{lang}'")

        if lang == "python":
            errors.extend(check_python_snippet(s["code"], i))
        elif lang in ("bash", "console"):
            errors.extend(check_bash_snippet(s["code"], i))

    return errors


def main() -> int:
    files = [README] + sorted(DOCS.glob("*.md"))
    has_errors = False

    for path in files:
        if not path.exists():
            continue
        errors = check_file(path)
        if errors:
            has_errors = True
            print(f"\n{path}:")
            for e in errors:
                print(e)

    if has_errors:
        print("\n\u274c Snippet validation failed.")
        return 1
    print("\u2705 All code snippets pass validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
