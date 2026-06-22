"""voice_lint — refuse marketing language and antithetical reversals.

Mirrors the portfolio-wide voice rule. Walks every committed Markdown
file outside of `tests/fixtures/` and exits non-zero on a hit.

Implements R-DRM-007 (gates: voice_lint) and R-DRM-018 (gate scripts).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

BANLIST = (
    "leverage",
    "synergy",
    "unlock value",
    "best-in-class",
    "world-class",
    "seamless",
    "game-changer",
    "revolutionize",
    "supercharge",
    "next-generation",
    "cutting-edge",
)

ANTITHETICAL = re.compile(
    r"\bit'?s not (?:just |only )?\w[\w\s]{0,40}?[,;]\s*it'?s\b",
    re.IGNORECASE,
)

IGNORED_DIRS = (
    "tests/fixtures",
    ".git",
    "dist",
    "build",
    ".venv",
)


def _ignored(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return any(rel.startswith(prefix) for prefix in IGNORED_DIRS)


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    hits: list[str] = []
    for term in BANLIST:
        if term in lower:
            hits.append(f"{path}: banlist hit: '{term}'")
    if ANTITHETICAL.search(text):
        hits.append(f"{path}: antithetical reversal sentence shape")
    return hits


def main() -> int:
    md_files = sorted(REPO_ROOT.rglob("*.md"))
    all_hits: list[str] = []
    for path in md_files:
        if _ignored(path):
            continue
        all_hits.extend(check_file(path))
    if all_hits:
        for hit in all_hits:
            print(hit)
        return 1
    print("voice_lint: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
