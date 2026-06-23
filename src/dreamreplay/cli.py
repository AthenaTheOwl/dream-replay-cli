"""DreamReplay CLI entry point.

Implements R-DRM-002 (input contract) and R-DRM-011 (`dreamreplay run`).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import click
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "dream.schema.json"
DREAMS_DIR = REPO_ROOT / "dreams"

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


@main.command("validate")
def cmd_validate() -> None:
    """Validate the committed dream corpus against dream.schema.json.

    No args. Reads only the committed `dreams/*/index.json` files and
    checks each against the schema. Writes nothing, needs no network or
    secrets. Exits 0 when every committed index validates clean.
    """
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        click.echo(f"validate: missing schema {SCHEMA_PATH}", err=True)
        sys.exit(1)
    validator = Draft202012Validator(schema)

    paths = sorted(DREAMS_DIR.glob("*/index.json"))
    if not paths:
        click.echo("validate: no committed dream corpus to check")
        return

    errors: list[str] = []
    for path in paths:
        try:
            instance = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON ({exc.msg})")
            continue
        for err in validator.iter_errors(instance):
            loc = ".".join(str(p) for p in err.absolute_path)
            errors.append(f"{path}: {loc}: {err.message}")

    if errors:
        for line in errors:
            click.echo(line, err=True)
        sys.exit(1)
    click.echo(f"validate: {len(paths)} dream index file(s) clean")


_KIND_LABELS = {
    "skill": "skill",
    "memory": "memory update",
    "spec_amendment": "spec amendment",
    "test": "test",
}
_KIND_ORDER = ["skill", "memory", "spec_amendment", "test"]


def _latest_index() -> Path | None:
    paths = sorted(DREAMS_DIR.glob("*/index.json"))
    return paths[-1] if paths else None


def render_show(index_path: Path) -> str:
    """Render the human-readable review summary for one committed run.

    Reads a single ``dreams/YYYY-WNN/index.json`` and returns the ranked,
    one-screen digest a reviewer reads before opening the per-kind files.
    """
    data = json.loads(index_path.read_text(encoding="utf-8"))
    candidates = data.get("candidates", {})
    totals = data.get("totals", {})
    total = sum(totals.values())

    lines: list[str] = []
    week = data.get("week", "?")
    run_date = data.get("run_date", "?")
    lines.append(f"dream review -- {week}  (run {run_date})")
    lines.append(f"folder: {index_path.parent.as_posix()}")
    lines.append("")
    lines.append(
        f"{total} candidate(s) await human review. Promotion is gated: "
        "nothing here ships until a person says yes."
    )
    lines.append("")

    # Single flat ranking across all kinds, by evidence count — the
    # "what should I look at first" view.
    ranked: list[tuple[int, str, str, str]] = []
    for kind, items in candidates.items():
        for item in items:
            ranked.append(
                (
                    int(item.get("evidence_count", 0)),
                    _KIND_LABELS.get(kind, kind),
                    item.get("slug", "?"),
                    item.get("notes", ""),
                )
            )
    ranked.sort(key=lambda r: (-r[0], r[1], r[2]))

    lines.append("ranked by evidence (strongest first):")
    lines.append("")
    lines.append(f"  {'#':>2}  {'evid':>4}  {'kind':<14}  candidate")
    lines.append(f"  {'--':>2}  {'----':>4}  {'-' * 14}  {'-' * 30}")
    for i, (evid, label, slug, _notes) in enumerate(ranked, start=1):
        lines.append(f"  {i:>2}  {evid:>4}  {label:<14}  {slug}")
    lines.append("")

    # The headline finding: spec amendments are references to requirement
    # IDs that the traces use but the spec ledger never defined — drift
    # between what agents act on and what the spec says exists.
    amendments = candidates.get("spec_amendment", [])
    if amendments:
        lines.append("headline -- spec drift (referenced but undefined):")
        for item in sorted(
            amendments,
            key=lambda c: -int(c.get("evidence_count", 0)),
        ):
            slug = item.get("slug", "?")
            evid = item.get("evidence_count", 0)
            req_id = slug.replace("add-", "").upper().replace("-", "-")
            lines.append(
                f"  - {slug}: {req_id} referenced in {evid} trace event(s) "
                "but absent from the spec ledger"
            )
        lines.append("")

    lines.append("per-kind totals:")
    for kind in _KIND_ORDER:
        if kind in totals:
            lines.append(f"  - {_KIND_LABELS.get(kind, kind)}: {totals[kind]}")
    lines.append("")
    lines.append(
        f"open {index_path.parent.as_posix()}/ to read the full proposals."
    )
    return "\n".join(lines)


@main.command("show")
def cmd_show() -> None:
    """Print a ranked, human-readable digest of the committed dream run.

    No args. Reads only the latest committed ``dreams/*/index.json`` and
    prints the candidates ranked by evidence, the spec-drift headline, and
    per-kind totals. Writes nothing, needs no network or secrets. Exits 0.
    """
    index_path = _latest_index()
    if index_path is None:
        click.echo("show: no committed dream run to display")
        return
    click.echo(render_show(index_path))


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
