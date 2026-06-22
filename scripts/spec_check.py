"""spec_check — every R-DRM-NNN ID under specs/ is implemented or tested.

Implements R-DRM-007 (gates: spec_check).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQ_RE = re.compile(r"^##\s+(R-[A-Z]+-\d{3})\b", re.MULTILINE)
REF_RE = re.compile(r"R-[A-Z]+-\d{3}")


def collect_required_ids() -> set[str]:
    """Every `## R-XXX-NNN` heading in any `specs/*/requirements.md`."""
    ids: set[str] = set()
    for req_file in (REPO_ROOT / "specs").rglob("requirements.md"):
        text = req_file.read_text(encoding="utf-8")
        ids.update(REQ_RE.findall(text))
    return ids


def collect_referenced_ids() -> set[str]:
    """Walk every place a requirement ID can legitimately appear as
    satisfied — code, tests, scripts, decisions, the status / coverage
    docs, plus checked task rows in `specs/*/tasks.md`. The
    `requirements.md` files themselves are excluded; a requirement
    cannot satisfy itself by being declared.
    """
    ids: set[str] = set()

    for tasks_file in (REPO_ROOT / "specs").rglob("tasks.md"):
        for line in tasks_file.read_text(encoding="utf-8").splitlines():
            stripped = line.lstrip()
            if stripped.startswith("- [x]") or stripped.startswith("- [X]"):
                ids.update(REF_RE.findall(line))

    dir_roots = [
        REPO_ROOT / "src",
        REPO_ROOT / "tests",
        REPO_ROOT / "scripts",
        REPO_ROOT / "decisions",
        REPO_ROOT / "docs",
    ]
    for root in dir_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".md", ".json"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            ids.update(REF_RE.findall(text))

    for path in (
        REPO_ROOT / "STATUS.md",
        REPO_ROOT / "README.md",
        REPO_ROOT / "AGENTS.md",
    ):
        if path.exists():
            ids.update(REF_RE.findall(path.read_text(encoding="utf-8")))

    return ids


def main() -> int:
    required = collect_required_ids()
    referenced = collect_referenced_ids()
    missing = sorted(required - referenced)
    if missing:
        print("spec_check: missing implementation or test for:")
        for rid in missing:
            print(f"  - {rid}")
        return 1
    print(f"spec_check: clean ({len(required)} IDs satisfied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
