"""DreamReplay CLI entry point.

Implements R-DRM-002 (input contract) and R-DRM-011 (`dreamreplay run`).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import click

from dreamreplay.ingest.decision_ledger import parse_decision_ledger
from dreamreplay.ingest.spec_ledger import parse_spec_ledger
from dreamreplay.ingest.trace_loader import load_events
from dreamreplay.render.dreams_dir import (
    RenderInputs,
    group_candidates,
    render_dreams,
)
from dreamreplay.synthesize.candidate_memory import synthesize_memory
from dreamreplay.synthesize.candidate_skills import synthesize_skills
from dreamreplay.synthesize.candidate_spec_amendments import (
    synthesize_amendments,
)
from dreamreplay.synthesize.candidate_tests import synthesize_tests


@dataclass(frozen=True)
class RunResult:
    out_dir: Path
    total_candidates: int


def run_pipeline(
    traces: Path,
    spec_ledger: Path,
    decision_ledger: Path,
    out: Path,
    week_label: str,
    run_date: str,
) -> RunResult:
    events = load_events(traces)
    spec_requirements = parse_spec_ledger(spec_ledger)
    parse_decision_ledger(decision_ledger)

    all_candidates = (
        synthesize_skills(events)
        + synthesize_memory(events)
        + synthesize_tests(events)
        + synthesize_amendments(events, spec_requirements)
    )
    grouped = group_candidates(all_candidates)
    inputs = RenderInputs(
        week_label=week_label,
        run_date=run_date,
        traces_dir=traces,
        spec_dir=spec_ledger,
        decision_dir=decision_ledger,
        candidates_by_kind=grouped,
    )
    render_dreams(inputs, out)
    return RunResult(out_dir=out, total_candidates=len(all_candidates))


@click.group()
@click.version_option(package_name="dreamreplay")
def main() -> None:
    """DreamReplay CLI — propose candidates, never promote."""


@main.command("run")
@click.option(
    "--traces",
    "traces",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--spec-ledger",
    "spec_ledger",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--decision-ledger",
    "decision_ledger",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--out",
    "out",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
)
@click.option(
    "--week",
    "week",
    required=True,
    help="Week label, e.g. 2026-W25.",
)
@click.option(
    "--run-date",
    "run_date",
    required=True,
    help="ISO date for the run, e.g. 2026-06-22.",
)
def cmd_run(
    traces: Path,
    spec_ledger: Path,
    decision_ledger: Path,
    out: Path,
    week: str,
    run_date: str,
) -> None:
    try:
        result = run_pipeline(
            traces=traces,
            spec_ledger=spec_ledger,
            decision_ledger=decision_ledger,
            out=out,
            week_label=week,
            run_date=run_date,
        )
    except Exception as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)
    click.echo(
        f"wrote {result.total_candidates} candidate(s) to {result.out_dir}"
    )


if __name__ == "__main__":
    main()
