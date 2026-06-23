"""Tests for the no-arg `show` digest command."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from dreamreplay.cli import _latest_index, main, render_show

REPO_ROOT = Path(__file__).resolve().parents[1]
DOGFOOD_INDEX = REPO_ROOT / "dreams" / "2026-W25" / "index.json"


def test_show_runs_with_no_args_and_exits_zero() -> None:
    result = CliRunner().invoke(main, ["show"])
    assert result.exit_code == 0
    assert "dream review" in result.output


def test_show_ranks_candidates_by_evidence() -> None:
    out = render_show(DOGFOOD_INDEX)
    # The strongest candidate (evidence 4) must appear before a weaker one.
    assert out.index("ledger-row-write") < out.index("add-r-drm-999")
    # Header and the spec-drift headline are present.
    assert "ranked by evidence" in out
    assert "spec drift" in out
    assert "R-DRM-999" in out


def test_show_is_not_a_raw_json_dump() -> None:
    out = render_show(DOGFOOD_INDEX)
    # A readable digest, not the raw index.json.
    assert '"schema_version"' not in out
    assert "per-kind totals:" in out


def test_latest_index_points_at_committed_corpus() -> None:
    assert _latest_index() == DOGFOOD_INDEX
