"""R-DRM-016 — dreams directory renderer."""

from __future__ import annotations

import json
from pathlib import Path

from dreamreplay.models import Candidate
from dreamreplay.render.dreams_dir import (
    KIND_TO_FILENAME,
    RenderInputs,
    group_candidates,
    render_dreams,
)


def _inputs(tmp_path: Path, candidates: list[Candidate]) -> RenderInputs:
    traces = tmp_path / "traces"
    specs = tmp_path / "specs"
    decisions = tmp_path / "decisions"
    for p in (traces, specs, decisions):
        p.mkdir()
    (traces / "x.jsonl").write_text("", encoding="utf-8")
    return RenderInputs(
        week_label="2026-W25",
        run_date="2026-06-22",
        traces_dir=traces,
        spec_dir=specs,
        decision_dir=decisions,
        candidates_by_kind=group_candidates(candidates),
    )


def test_render_writes_all_files(tmp_path: Path) -> None:
    out = tmp_path / "out"
    inputs = _inputs(tmp_path, [])
    render_dreams(inputs, out)
    for filename in KIND_TO_FILENAME.values():
        assert (out / filename).exists()
    assert (out / "index.json").exists()


def test_index_is_sorted_and_newline_terminated(tmp_path: Path) -> None:
    out = tmp_path / "out"
    inputs = _inputs(tmp_path, [])
    render_dreams(inputs, out)
    raw = (out / "index.json").read_text(encoding="utf-8")
    assert raw.endswith("\n")
    parsed = json.loads(raw)
    re_dumped = json.dumps(parsed, sort_keys=True, indent=2) + "\n"
    assert raw == re_dumped


def test_render_includes_candidate_in_markdown(tmp_path: Path) -> None:
    out = tmp_path / "out"
    c = Candidate(
        kind="skill",
        slug="thought-then-action",
        evidence_count=4,
        notes="repeats across 3 actors",
        body="Bigram observed: `thought` then `action`.\n",
    )
    inputs = _inputs(tmp_path, [c])
    render_dreams(inputs, out)
    text = (out / "candidate_skills.md").read_text(encoding="utf-8")
    assert "## thought-then-action" in text
    assert "Evidence count: 4" in text
