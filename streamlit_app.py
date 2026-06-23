"""dream-replay-cli — live demo (Streamlit Community Cloud).

Mirrors the no-arg `show` verb (`python -m dream_replay_cli show`): reads the
latest committed `dreams/YYYY-WNN/index.json` directly and renders the week's
candidate promotions ranked by trace evidence, plus the spec-drift headline.
No network, no secrets — runs entirely off the committed dream corpus.

Deploy: Streamlit Community Cloud -> New app -> repo AthenaTheOwl/dream-replay-cli,
branch main, main file streamlit_app.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

REPO = Path(__file__).resolve().parent
DREAMS_DIR = REPO / "dreams"

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
