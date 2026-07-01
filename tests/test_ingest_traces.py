"""R-DRM-012 — reference trace adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from dreamreplay.ingest.trace_loader import (
    TraceToEvalHarnessAdapter,
    load_events,
)


def test_adapter_handles_jsonl_only(tmp_path: Path) -> None:
    adapter = TraceToEvalHarnessAdapter()
    assert adapter.can_handle(tmp_path / "x.jsonl") is True
    assert adapter.can_handle(tmp_path / "x.json") is False
    assert adapter.can_handle(tmp_path / "x.txt") is False


def test_load_events_parses_fixture(traces_dir: Path) -> None:
    events = load_events(traces_dir)
    assert len(events) == 14
    kinds = {ev.kind for ev in events}
    assert {"thought", "action", "observation", "failure"} <= kinds


def test_load_events_rejects_bad_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    # valid record first so the failure is on line 2, pinning the
    # 1-based line number in the error against off-by-one drift
    bad.write_text(
        '{"timestamp": "t", "kind": "k", "actor": "a"}\n{not json}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=r"bad\.jsonl:2: invalid JSON"):
        load_events(tmp_path)


def test_load_events_rejects_unclaimed_file(tmp_path: Path) -> None:
    (tmp_path / "trace.csv").write_text("a,b,c\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no trace adapter claims"):
        load_events(tmp_path)
