"""R-DRM-013 — spec ledger parser."""

from __future__ import annotations

from pathlib import Path

from dreamreplay.ingest.spec_ledger import parse_spec_ledger


def test_parse_extracts_all_ids(spec_dir: Path) -> None:
    reqs = parse_spec_ledger(spec_dir)
    ids = [r.id for r in reqs]
    assert ids == [
        "R-SMP-001",
        "R-SMP-002",
        "R-SMP-003",
        "R-SMP-004",
    ]
    assert reqs[0].title.startswith("repo scaffold")


def test_parse_ignores_non_requirements_files(tmp_path: Path) -> None:
    (tmp_path / "0001-foundation").mkdir()
    (tmp_path / "0001-foundation" / "requirements.md").write_text(
        "# Spec 0001\n\n## R-XYZ-001 — Title\nbody\n",
        encoding="utf-8",
    )
    (tmp_path / "0001-foundation" / "design.md").write_text(
        "## R-XYZ-002 — should be ignored\n",
        encoding="utf-8",
    )
    reqs = parse_spec_ledger(tmp_path)
    assert [r.id for r in reqs] == ["R-XYZ-001"]
