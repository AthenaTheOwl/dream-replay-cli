"""R-DRM-020 — re-running on identical inputs yields byte-identical files."""

from __future__ import annotations

from pathlib import Path

from dreamreplay.cli import run_pipeline


def test_two_runs_byte_identical(
    tmp_path: Path,
    traces_dir: Path,
    spec_dir: Path,
    decision_dir: Path,
) -> None:
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    for out in (out_a, out_b):
        run_pipeline(
            traces=traces_dir,
            spec_ledger=spec_dir,
            decision_ledger=decision_dir,
            out=out,
            week_label="2026-W25",
            run_date="2026-06-22",
        )
    files_a = sorted(p.relative_to(out_a) for p in out_a.rglob("*") if p.is_file())
    files_b = sorted(p.relative_to(out_b) for p in out_b.rglob("*") if p.is_file())
    assert files_a == files_b
    for rel in files_a:
        assert (out_a / rel).read_bytes() == (out_b / rel).read_bytes(), rel
