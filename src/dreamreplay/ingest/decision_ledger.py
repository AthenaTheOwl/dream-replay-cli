"""Decision ledger parser.

Implements R-DRM-002 (input contract: decision-ledger directory) and
R-DRM-014 (DEC-NNN-* parsing).
"""

from __future__ import annotations

import re
from pathlib import Path

from dreamreplay.models import DecisionRecord

DEC_FILENAME = re.compile(r"^(DEC-\d{3})-(.+)\.md$")


def parse_decision_ledger(decision_dir: Path) -> list[DecisionRecord]:
    """Walk `decision_dir` for files matching `DEC-NNN-*.md`."""
    if not decision_dir.exists():
        return []
    records: list[DecisionRecord] = []
    for path in sorted(decision_dir.glob("DEC-*.md")):
        m = DEC_FILENAME.match(path.name)
        if not m:
            continue
        body = path.read_text(encoding="utf-8")
        first_h1 = next(
            (
                line[2:].strip()
                for line in body.splitlines()
                if line.startswith("# ")
            ),
            m.group(2).replace("-", " "),
        )
        records.append(
            DecisionRecord(id=m.group(1), title=first_h1, body=body)
        )
    records.sort(key=lambda r: r.id)
    return records
