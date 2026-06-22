"""Trace loader.

Implements R-DRM-005 (adapter shape) and R-DRM-012 (reference adapter
for the trace-to-eval-harness JSONL format).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from dreamreplay.models import InternalEvent


class TraceAdapter(Protocol):
    name: str

    def can_handle(self, path: Path) -> bool: ...

    def load(self, path: Path) -> Iterator[InternalEvent]: ...


class TraceToEvalHarnessAdapter:
    """Reads JSONL files where each line is an event record.

    Each line must decode to an object with `timestamp`, `kind`, `actor`,
    and optionally `payload` (object of string→string).
    """

    name = "trace-to-eval-harness"

    def can_handle(self, path: Path) -> bool:
        return path.suffix == ".jsonl"

    def load(self, path: Path) -> Iterator[InternalEvent]:
        with path.open("r", encoding="utf-8") as f:
            for line_number, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"{path}:{line_number}: invalid JSON ({e.msg})"
                    ) from e
                if not isinstance(record, dict):
                    raise ValueError(
                        f"{path}:{line_number}: expected object, got "
                        f"{type(record).__name__}"
                    )
                yield InternalEvent.from_dict(record)


DEFAULT_ADAPTERS: tuple[TraceAdapter, ...] = (TraceToEvalHarnessAdapter(),)


def load_events(
    trace_dir: Path,
    adapters: Iterable[TraceAdapter] = DEFAULT_ADAPTERS,
) -> list[InternalEvent]:
    """Walk `trace_dir`, dispatch each file to the first matching adapter."""
    adapter_list = list(adapters)
    events: list[InternalEvent] = []
    paths = sorted(p for p in trace_dir.rglob("*") if p.is_file())
    for path in paths:
        matched = next(
            (a for a in adapter_list if a.can_handle(path)),
            None,
        )
        if matched is None:
            raise ValueError(
                f"no trace adapter claims {path} "
                f"(tried: {[a.name for a in adapter_list]})"
            )
        events.extend(matched.load(path))
    return events
