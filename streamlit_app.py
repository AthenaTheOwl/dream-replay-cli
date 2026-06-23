"""dream-replay-cli — live demo (Streamlit Community Cloud).

Two halves:

1. Committed view — mirrors the no-arg `show` verb
   (`python -m dream_replay_cli show`): reads the latest committed
   `dreams/YYYY-WNN/index.json` directly and renders the week's candidate
   promotions ranked by trace evidence, plus the spec-drift headline.

2. Live engine — lets the user paste their OWN trace events (JSONL) and the
   known spec requirement IDs, then runs the REAL synthesis pipeline
   (`dreamreplay.synthesize.*` over `InternalEvent.from_dict`) and re-ranks the
   candidate skills / memory / tests / spec-amendments live. Same code the CLI
   `run` verb drives — no lookup, no hardcoded output.

No network, no secrets — runs entirely off committed data and what the user types.

Deploy: Streamlit Community Cloud -> New app -> repo AthenaTheOwl/dream-replay-cli,
branch main, main file streamlit_app.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

REPO = Path(__file__).resolve().parent
DREAMS_DIR = REPO / "dreams"

# Make the real package importable whether or not it's pip-installed (it is,
# via `.` in requirements.txt on Streamlit Cloud; this covers a bare checkout).
_SRC = REPO / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# The real engine — imported, not reimplemented.
from dreamreplay.models import InternalEvent, SpecRequirement
from dreamreplay.synthesize.candidate_memory import synthesize_memory
from dreamreplay.synthesize.candidate_skills import synthesize_skills
from dreamreplay.synthesize.candidate_spec_amendments import synthesize_amendments
from dreamreplay.synthesize.candidate_tests import synthesize_tests

_KIND_LABELS = {
    "skill": "skill",
    "memory": "memory update",
    "spec_amendment": "spec amendment",
    "test": "test",
}
_KIND_ORDER = ["skill", "memory", "spec_amendment", "test"]


def latest_index() -> Path | None:
    paths = sorted(DREAMS_DIR.glob("*/index.json"))
    return paths[-1] if paths else None


st.set_page_config(page_title="dream-replay-cli — weekly candidate review", layout="wide")
st.title("dream-replay-cli")
st.caption(
    "offline pass over a week of agent traces — ranked candidate skills, memory "
    "updates, tests, and spec amendments awaiting human review. promotion is gated."
)

index_path = latest_index()
if index_path is None:
    st.warning("no committed dream run found under dreams/*/index.json")
    st.stop()

data = json.loads(index_path.read_text(encoding="utf-8"))
candidates = data.get("candidates", {})
totals = data.get("totals", {})
week = data.get("week", "?")
run_date = data.get("run_date", "?")
total = sum(totals.values())

st.subheader(f"dream review — {week}  (run {run_date})")

# Flatten every candidate into one ranking, by evidence count — the
# "what should I look at first" view the show verb prints.
ranked = []
for kind, items in candidates.items():
    for item in items:
        ranked.append(
            {
                "evidence": int(item.get("evidence_count", 0)),
                "kind": _KIND_LABELS.get(kind, kind),
                "candidate": item.get("slug", "?"),
                "notes": item.get("notes", ""),
            }
        )
ranked.sort(key=lambda r: (-r["evidence"], r["kind"], r["candidate"]))

amendments = candidates.get("spec_amendment", [])

c1, c2, c3 = st.columns(3)
c1.metric("candidates awaiting review", total)
c2.metric("strongest evidence", max((r["evidence"] for r in ranked), default=0))
c3.metric("spec-drift findings", len(amendments), help="requirement IDs referenced in traces but absent from the spec ledger")

st.info(
    f"**{total} candidate(s) await human review.** promotion is gated: nothing here "
    "ships until a person opens the file and says yes."
)

kinds_present = sorted({r["kind"] for r in ranked})
chosen = st.multiselect(
    "filter by kind",
    options=kinds_present,
    default=kinds_present,
    help="ranking spans all candidate kinds; narrow it here.",
)
shown = [r for r in ranked if r["kind"] in chosen]

df = pd.DataFrame(shown)
if not df.empty:
    df.insert(0, "#", range(1, len(df) + 1))
st.dataframe(df, use_container_width=True, hide_index=True)

# Headline finding: spec drift — requirement IDs the traces act on but the
# spec ledger never defined.
if amendments:
    worst = max(amendments, key=lambda c: int(c.get("evidence_count", 0)))
    slug = worst.get("slug", "?")
    req_id = slug.replace("add-", "").upper()
    st.success(
        f"**headline — spec drift:** `{req_id}` referenced in "
        f"{worst.get('evidence_count', 0)} trace event(s) but absent from the spec "
        "ledger. a reviewer sees the drift before promoting anything."
    )
    with st.expander("spec-drift candidates (referenced but undefined)"):
        for item in sorted(amendments, key=lambda c: -int(c.get("evidence_count", 0))):
            s = item.get("slug", "?")
            st.markdown(
                f"- **{s}** — {item.get('notes', '')} "
                f"(evidence {item.get('evidence_count', 0)})"
            )

with st.expander("per-kind totals"):
    for kind in _KIND_ORDER:
        if kind in totals:
            st.markdown(f"- {_KIND_LABELS.get(kind, kind)}: {totals[kind]}")

st.caption(
    "this page mirrors the CLI `show` verb, reading the committed "
    f"`{index_path.parent.name}/index.json`. the synthesis pipeline lives in "
    "`src/dreamreplay/`. repo: github.com/AthenaTheOwl/dream-replay-cli"
)

# ---------------------------------------------------------------------------
# Live engine — drive the real synthesis pipeline on the user's own traces.
# ---------------------------------------------------------------------------
st.divider()
st.header("run the engine on your own traces")
st.caption(
    "the table above is a committed run. below, paste your OWN agent-trace "
    "events (one JSON object per line — the trace-to-eval-harness JSONL format) "
    "and the spec requirement IDs your ledger already defines. the page calls "
    "the real `dreamreplay.synthesize.*` rules — the same code the CLI `run` "
    "verb runs — and re-derives the candidate skills, memory, tests, and "
    "spec-drift findings live. nothing is looked up; the candidates are "
    "computed from what you type."
)

_DEFAULT_TRACES = """\
{"timestamp": "2026-06-15T09:00:00Z", "kind": "thought", "actor": "agent-alpha", "payload": {"note": "calibration-pass starting"}}
{"timestamp": "2026-06-15T09:00:05Z", "kind": "action", "actor": "agent-alpha", "payload": {"target": "ledger-row write"}}
{"timestamp": "2026-06-15T09:00:10Z", "kind": "observation", "actor": "agent-alpha", "payload": {"result": "audit-log-write ok"}}
{"timestamp": "2026-06-15T09:00:15Z", "kind": "thought", "actor": "agent-alpha", "payload": {"note": "calibration-pass starting"}}
{"timestamp": "2026-06-15T09:00:20Z", "kind": "action", "actor": "agent-alpha", "payload": {"target": "ledger-row write"}}
{"timestamp": "2026-06-15T09:00:25Z", "kind": "observation", "actor": "agent-alpha", "payload": {"result": "audit-log-write ok"}}
{"timestamp": "2026-06-16T10:00:00Z", "kind": "thought", "actor": "agent-beta", "payload": {"note": "calibration-pass starting", "ref": "R-DRM-999"}}
{"timestamp": "2026-06-16T10:00:05Z", "kind": "action", "actor": "agent-beta", "payload": {"target": "ledger-row write"}}
{"timestamp": "2026-06-16T10:00:10Z", "kind": "observation", "actor": "agent-beta", "payload": {"result": "audit-log-write ok"}}
{"timestamp": "2026-06-17T11:00:00Z", "kind": "thought", "actor": "agent-gamma", "payload": {"note": "starting up"}}
{"timestamp": "2026-06-17T11:00:05Z", "kind": "action", "actor": "agent-gamma", "payload": {"target": "ledger-row write"}}
{"timestamp": "2026-06-17T11:00:10Z", "kind": "failure", "actor": "agent-gamma", "payload": {"error": "timeout on audit-log-write"}}
{"timestamp": "2026-06-18T12:00:00Z", "kind": "thought", "actor": "agent-delta", "payload": {"note": "retry attempt"}}
{"timestamp": "2026-06-18T12:00:05Z", "kind": "failure", "actor": "agent-delta", "payload": {"error": "missing R-DRM-999 implementation"}}
"""

_DEFAULT_SPEC_IDS = "R-DRM-001, R-DRM-002, R-DRM-005"

col_t, col_s = st.columns([3, 1])
with col_t:
    traces_text = st.text_area(
        "trace events (JSONL — one event per line)",
        value=_DEFAULT_TRACES,
        height=320,
        help=(
            "each line: an object with `timestamp`, `kind`, `actor`, and an "
            "optional `payload` map of string→string. edit a line, add one, "
            "delete one — the candidates below recompute."
        ),
    )
with col_s:
    spec_ids_text = st.text_area(
        "known spec requirement IDs",
        value=_DEFAULT_SPEC_IDS,
        height=320,
        help=(
            "the `R-XXX-NNN` IDs your spec ledger already defines (comma- or "
            "newline-separated). any ID a trace references but that is NOT "
            "listed here becomes a spec-drift / amendment candidate."
        ),
    )


def _parse_events(text: str) -> tuple[list[InternalEvent], list[str]]:
    """Parse pasted JSONL into real InternalEvent objects via the engine's
    own `from_dict`. Returns (events, per-line errors)."""
    events: list[InternalEvent] = []
    errors: list[str] = []
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {n}: invalid JSON ({exc.msg})")
            continue
        if not isinstance(record, dict):
            errors.append(f"line {n}: expected a JSON object, got {type(record).__name__}")
            continue
        events.append(InternalEvent.from_dict(record))
    return events, errors


def _parse_spec_ids(text: str) -> list[SpecRequirement]:
    ids = [tok.strip() for tok in text.replace("\n", ",").split(",")]
    return [
        SpecRequirement(id=i, spec_dir="(user)", title="(declared by user)")
        for i in ids
        if i
    ]


events, parse_errors = _parse_events(traces_text)
spec_reqs = _parse_spec_ids(spec_ids_text)

if parse_errors:
    st.error("could not parse some trace lines:\n\n" + "\n".join(f"- {e}" for e in parse_errors))

if not events:
    st.warning("no valid trace events parsed — paste at least one JSON event line above.")
    st.stop()

# Drive the REAL engine: the four synthesis rules + the same final sort the
# `show` verb and `run` pipeline use.
live_candidates = (
    synthesize_skills(events)
    + synthesize_memory(events)
    + synthesize_tests(events)
    + synthesize_amendments(events, spec_reqs)
)
live_candidates.sort(key=lambda c: (-c.evidence_count, c.kind, c.slug))

m1, m2, m3, m4 = st.columns(4)
m1.metric("events ingested", len(events))
m2.metric("candidates derived", len(live_candidates))
m3.metric(
    "strongest evidence",
    max((c.evidence_count for c in live_candidates), default=0),
)
m4.metric(
    "spec-drift findings",
    sum(1 for c in live_candidates if c.kind == "spec_amendment"),
)

if live_candidates:
    live_df = pd.DataFrame(
        {
            "#": range(1, len(live_candidates) + 1),
            "evidence": [c.evidence_count for c in live_candidates],
            "kind": [_KIND_LABELS.get(c.kind, c.kind) for c in live_candidates],
            "candidate": [c.slug for c in live_candidates],
            "notes": [c.notes for c in live_candidates],
        }
    )
    st.dataframe(live_df, use_container_width=True, hide_index=True)
else:
    st.info(
        "the engine ran but proposed nothing: no `kind` bigram repeats "
        "3+ times, no payload value (length ≥ 8) recurs across 3+ events, "
        "no `failure` events, and every referenced `R-*-NNN` is already in "
        "your spec list. add repetition or a failure to see candidates appear."
    )

live_amendments = [c for c in live_candidates if c.kind == "spec_amendment"]
if live_amendments:
    worst = max(live_amendments, key=lambda c: c.evidence_count)
    req_id = worst.slug.replace("add-", "").upper()
    st.warning(
        f"**spec drift:** `{req_id}` is referenced in {worst.evidence_count} "
        "of your trace event(s) but is not in your spec ledger. add it to the "
        "ID box on the right and watch the finding clear."
    )

with st.expander("what each rule is doing (the real thresholds)"):
    st.markdown(
        "- **skill** — `synthesize_skills`: per-actor bigrams of event `kind`; "
        "any pair seen **3+** times becomes a candidate skill.\n"
        "- **memory update** — `synthesize_memory`: payload string values of "
        "length **≥ 8** that appear in **3+** distinct events.\n"
        "- **test** — `synthesize_tests`: every `kind == \"failure\"` event "
        "becomes one regression-test candidate.\n"
        "- **spec amendment** — `synthesize_amendments`: any `R-XXX-NNN` a "
        "payload references that is **absent** from your spec-ID list.\n\n"
        "all four are imported from `dreamreplay.synthesize.*` and run on the "
        "events you paste — this is the engine, not a mock."
    )
