"""Dreams directory renderer.

Implements R-DRM-003 (output contract: 4 .md + index.json),
R-DRM-006 (schema-validated index emission), R-DRM-009 (determinism via
sorted keys and explicit newlines), and R-DRM-016 (renderer module).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from dreamreplay.models import Candidate

KIND_TO_FILENAME = {
    "skill": "candidate_skills.md",
    "memory": "candidate_memory.md",
    "test": "candidate_tests.md",
    "spec_amendment": "candidate_spec_amendments.md",
}

KIND_TO_HEADING = {
    "skill": "Skill candidates",
    "memory": "Memory candidates",
    "test": "Test candidates",
    "spec_amendment": "Spec amendment candidates",
}

KIND_TO_THRESHOLD = {
    "skill": "bigram count >= 3",
    "memory": "value length >= 8, appears in >= 3 events",
    "test": "one candidate per failure event",
    "spec_amendment": "ID referenced in traces but absent from spec ledger",
}


@dataclass(frozen=True)
class RenderInputs:
    week_label: str
    run_date: str
    traces_dir: Path
    spec_dir: Path
    decision_dir: Path
    candidates_by_kind: dict[str, list[Candidate]]


def _render_md(kind: str, week_label: str, candidates: Sequence[Candidate]) -> str:
    heading = KIND_TO_HEADING[kind]
    threshold = KIND_TO_THRESHOLD[kind]
    n = len(candidates)
    lines: list[str] = []
    lines.append(f"# {heading} — {week_label}")
    lines.append("")
    lines.append(f"> {n} candidate(s). Threshold: {threshold}.")
    lines.append("")
    if n == 0:
        lines.append("No candidates this run.")
        lines.append("")
        return "\n".join(lines)
    for c in candidates:
        lines.append(f"## {c.slug}")
        lines.append("")
        lines.append(f"- Evidence count: {c.evidence_count}")
        lines.append(f"- Notes: {c.notes}")
        lines.append("")
        lines.append(c.body.rstrip("\n"))
        lines.append("")
    return "\n".join(lines)


def _hash_dir(path: Path) -> str:
    """SHA-256 over `<relpath>\\0<bytes>` for every file, sorted by relpath."""
    if not path.exists():
        return "sha256:empty"
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = f.relative_to(path).as_posix().encode("utf-8")
        h.update(rel)
        h.update(b"\x00")
        h.update(f.read_bytes())
        h.update(b"\x00")
    return f"sha256:{h.hexdigest()}"


def render_dreams(inputs: RenderInputs, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for kind, filename in KIND_TO_FILENAME.items():
        text = _render_md(
            kind,
            inputs.week_label,
            inputs.candidates_by_kind.get(kind, []),
        )
        (out_dir / filename).write_text(text, encoding="utf-8", newline="\n")

    index = {
        "schema_version": "1.0.0",
        "week": inputs.week_label,
        "run_date": inputs.run_date,
        "inputs": {
            "traces": {
                "path": inputs.traces_dir.as_posix(),
                "hash": _hash_dir(inputs.traces_dir),
            },
            "spec_ledger": {
                "path": inputs.spec_dir.as_posix(),
                "hash": _hash_dir(inputs.spec_dir),
            },
            "decision_ledger": {
                "path": inputs.decision_dir.as_posix(),
                "hash": _hash_dir(inputs.decision_dir),
            },
        },
        "candidates": {
            kind: [
                {
                    "slug": c.slug,
                    "evidence_count": c.evidence_count,
                    "notes": c.notes,
                    "file": KIND_TO_FILENAME[kind],
                }
                for c in inputs.candidates_by_kind.get(kind, [])
            ]
            for kind in KIND_TO_FILENAME
        },
        "totals": {
            kind: len(inputs.candidates_by_kind.get(kind, []))
            for kind in KIND_TO_FILENAME
        },
    }
    index_text = json.dumps(index, sort_keys=True, indent=2) + "\n"
    (out_dir / "index.json").write_text(index_text, encoding="utf-8", newline="\n")
    return out_dir


def group_candidates(
    candidates: Iterable[Candidate],
) -> dict[str, list[Candidate]]:
    grouped: dict[str, list[Candidate]] = {k: [] for k in KIND_TO_FILENAME}
    for c in candidates:
        grouped.setdefault(c.kind, []).append(c)
    return grouped
