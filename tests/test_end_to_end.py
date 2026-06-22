"""R-DRM-019, R-DRM-021 — end-to-end pipeline + dogfood corpus diff."""

from __future__ import annotations

import json
from pathlib import Path

from dreamreplay.cli import run_pipeline

REPO_ROOT = Path(__file__).resolve().parents[1]
DOGFOOD_DIR = REPO_ROOT / "dreams" / "2026-W25"


def test_pipeline_writes_four_md_files_and_index(
    tmp_path: Path,
    traces_dir: Path,
    spec_dir: Path,
    decision_dir: Path,
) -> None:
    out = tmp_path / "dreams" / "test-run"
    result = run_pipeline(
        traces=traces_dir,
        spec_ledger=spec_dir,
        decision_ledger=decision_dir,
        out=out,
        week_label="2026-W25",
        run_date="2026-06-22",
    )
    assert result.out_dir == out
    for name in (
        "candidate_skills.md",
        "candidate_memory.md",
        "candidate_tests.md",
        "candidate_spec_amendments.md",
        "index.json",
    ):
        assert (out / name).exists(), name


def test_pipeline_matches_committed_dogfood_run(
    tmp_path: Path,
    traces_dir: Path,
    spec_dir: Path,
    decision_dir: Path,
) -> None:
    """Re-running the pipeline against the fixture must produce the same
    bytes as the committed dogfood corpus. This is the calibration check.
    """
    out = tmp_path / "dreams" / "2026-W25"
    run_pipeline(
        traces=traces_dir,
        spec_ledger=spec_dir,
        decision_ledger=decision_dir,
        out=out,
        week_label="2026-W25",
        run_date="2026-06-22",
    )

    expected_files = sorted(p.name for p in DOGFOOD_DIR.iterdir())
    got_files = sorted(p.name for p in out.iterdir())
    assert got_files == expected_files

    for name in expected_files:
        if name == "index.json":
            # inputs.*.path is OS-absolute and so always differs between
            # the committed corpus and a fresh tmp_path run; the hash
            # field in the committed corpus is a placeholder (see
            # docs/methodology.md) and is regenerated whenever the
            # corpus is refreshed. Compare the rest of the document.
            expected = json.loads(
                (DOGFOOD_DIR / name).read_text(encoding="utf-8")
            )
            got = json.loads((out / name).read_text(encoding="utf-8"))
            for d in (expected, got):
                for k in d["inputs"].values():
                    k.pop("path", None)
                    k.pop("hash", None)
            assert got == expected
        else:
            expected_bytes = (DOGFOOD_DIR / name).read_bytes()
            got_bytes = (out / name).read_bytes()
            assert got_bytes == expected_bytes, name
