"""R-DRM-014 — decision ledger parser."""

from __future__ import annotations

from pathlib import Path

from dreamreplay.ingest.decision_ledger import parse_decision_ledger


def test_parse_decision_ledger(decision_dir: Path) -> None:
    records = parse_decision_ledger(decision_dir)
    assert len(records) == 1
    rec = records[0]
    assert rec.id == "DEC-001"
    assert "Example" in rec.title
    assert "placeholder" in rec.body


def test_parse_missing_directory_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    assert parse_decision_ledger(missing) == []


def test_parse_skips_non_matching_filenames(tmp_path: Path) -> None:
    (tmp_path / "DEC-001-real.md").write_text("# DEC-001\nbody\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("# Not a decision\n", encoding="utf-8")
    records = parse_decision_ledger(tmp_path)
    assert [r.id for r in records] == ["DEC-001"]
