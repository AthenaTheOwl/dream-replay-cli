"""Spec ledger parser.

Implements R-DRM-002 (input contract: spec-ledger directory) and
R-DRM-013 (R-*-NNN extraction).
"""

from __future__ import annotations

import re
from pathlib import Path

from dreamreplay.models import SpecRequirement

REQ_LINE = re.compile(r"^##\s+(R-[A-Z]+-\d{3})\s*[—\-:]\s*(.+?)\s*$")


def parse_spec_ledger(spec_dir: Path) -> list[SpecRequirement]:
    """Walk `spec_dir` and extract `R-*-NNN` requirements from
    `requirements.md` files.

    A requirement line is a Markdown H2 of the shape
    `## R-XXX-NNN — Title` (em-dash, hyphen, or colon as the separator).
    """
    results: list[SpecRequirement] = []
    files = sorted(spec_dir.rglob("requirements.md"))
    for req_file in files:
        rel_dir = req_file.parent.relative_to(spec_dir).as_posix()
        for raw_line in req_file.read_text(encoding="utf-8").splitlines():
            m = REQ_LINE.match(raw_line)
            if not m:
                continue
            results.append(
                SpecRequirement(
                    id=m.group(1),
                    spec_dir=rel_dir,
                    title=m.group(2).strip(),
                )
            )
    results.sort(key=lambda r: r.id)
    return results
