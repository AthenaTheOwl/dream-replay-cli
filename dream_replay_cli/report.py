"""Human-facing report renderer.

Turns a ledger row plus the candidate totals into the one-screen
summary a reviewer reads before opening the per-kind Markdown files.
The Markdown files themselves are written by
``dreamreplay.render.dreams_dir``; this module only summarises a run.
"""

from __future__ import annotations

from dream_replay_cli.ledger import LedgerRow


def render_summary(row: LedgerRow) -> str:
    """Render the one-screen Markdown summary for a single run."""
    lines: list[str] = []
    lines.append(f"# Run report — {row.week}")
    lines.append("")
    lines.append(f"- Run ID: `{row.run_id}`")
    lines.append(f"- Run date: {row.run_date}")
    lines.append(f"- Schema version: {row.schema_version}")
    lines.append(f"- Output directory: `{row.out_dir}`")
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    if row.totals:
        for kind in sorted(row.totals):
            lines.append(f"- {kind}: {row.totals[kind]}")
    else:
        lines.append("- (no candidates produced)")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    if row.inputs:
        for source in sorted(row.inputs):
            entry = row.inputs[source]
            path = entry.get("path", "?")
            digest = entry.get("hash", "?")
            lines.append(f"- {source}: `{path}` ({digest})")
    else:
        lines.append("- (no input hashes recorded)")
    lines.append("")
    return "\n".join(lines)
