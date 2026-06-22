"""Ledger row read / append helpers.

The contract gate looks for ``data/ledger/*.jsonl``: one JSON-line row
per scoring / calibration run. Each row carries the same totals and
input hashes the rendered ``dreams/YYYY-WNN/index.json`` carries; the
JSONL form is append-only and machine-grepable.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class LedgerRow:
    run_id: str
    week: str
    run_date: str
    schema_version: str = "1.0.0"
    totals: dict[str, int] = field(default_factory=dict)
    inputs: dict[str, dict[str, str]] = field(default_factory=dict)
    out_dir: str = ""

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), sort_keys=True) + "\n"


def append_row(ledger_path: Path, row: LedgerRow) -> None:
    """Append a single row to a ``data/ledger/*.jsonl`` file."""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(row.to_json_line())


def read_rows(ledger_path: Path) -> list[LedgerRow]:
    """Read every row from a ledger file in insertion order."""
    if not ledger_path.exists():
        return []
    rows: list[LedgerRow] = []
    with ledger_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            rows.append(LedgerRow(**data))
    return rows


def row_from_index_json(index_path: Path, run_id: str) -> LedgerRow:
    """Build a ledger row from a rendered ``index.json`` file."""
    data = json.loads(index_path.read_text(encoding="utf-8"))
    return LedgerRow(
        run_id=run_id,
        week=data.get("week", ""),
        run_date=data.get("run_date", ""),
        schema_version=data.get("schema_version", "1.0.0"),
        totals=data.get("totals", {}),
        inputs=data.get("inputs", {}),
        out_dir=str(index_path.parent.as_posix()),
    )


def latest(rows: Iterable[LedgerRow]) -> LedgerRow | None:
    """Return the chronologically last row by ``run_date`` (lexicographic)."""
    rows_list = list(rows)
    if not rows_list:
        return None
    return max(rows_list, key=lambda r: r.run_date)
