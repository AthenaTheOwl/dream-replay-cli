# PRODUCT BRIEF — DreamReplay

## One-line pitch

DreamReplay is the offline-cognition CLI agent frameworks forgot to ship:
take a week of traces, a spec ledger, and a decision ledger, and emit a
human-reviewable folder of candidate skills, candidate memory updates,
candidate tests, and candidate spec amendments. A person promotes; the
tool never does.

## Why this exists

Every agent runtime in 2026 — LangGraph, CrewAI, Bedrock Agents, OpenAI
Agents SDK — ships an online execution loop. None of them ship a
*Dream / Replay* plane: a deliberate weekly pass over the corpus of
traces that proposes promotions to the durable system (skills, memory,
specs, tests) instead of mutating the system in place. The result is
that long-running agents drift, regress, and accumulate the kind of
silent failure that only a quarterly post-mortem catches.

DreamReplay extracts that plane from the CDCP operating model the rest
of the author's portfolio runs on. It is not a service. It writes
files. It runs on your laptop, against your trace dump, in under a
minute.

## Who this is for

- **AI platform teams** with traces but no review cadence over them.
  They have observability; they don't have a weekly "what should we
  promote into the long-running system" meeting.
- **Individual builders running multi-agent portfolios.** The author
  runs one. The CLI is dogfooded on it before any external user touches
  it.
- **Researchers studying continual-learning for agents** who want a
  checked-in corpus they can study, not a black-box hosted service.

## What it produces

For each weekly run, one `dreams/YYYY-WNN/` directory containing:

- `candidate_skills.md` — repeated event-kind sequences worth naming
  as a reusable skill.
- `candidate_memory.md` — payload values appearing in ≥3 distinct
  events, candidates for the durable memory store.
- `candidate_tests.md` — one entry per failure event, so regressions
  cannot silently roll off the radar.
- `candidate_spec_amendments.md` — requirement IDs referenced in
  traces but missing from the spec ledger.
- `index.json` — schema-validated machine-readable summary, totals,
  and input hashes, so the promotion gate can iterate without parsing
  Markdown.

## What success looks like at v0.1

- A single `python -m uv run dreamreplay run …` produces all five
  output files deterministically (byte-equal across re-runs).
- The committed `dreams/2026-W25/` corpus is the first scoring /
  calibration row, generated from the in-repo portfolio fixture.
- A human can read all four candidate files end-to-end in under thirty
  minutes a week.
- All three gate scripts (`voice_lint`, `spec_check`,
  `validate_schemas`) exit clean on every PR.

## What this is not

- **Not a hosted service.** The CLI runs on your machine, against your
  files. There is no DreamReplay cloud, ever.
- **Not auto-promotion.** The CLI proposes; a human reads and merges.
  The gate is a person, not a confidence score.
- **Not a trace store.** Traces live wherever you already keep them.
  This repo reads them through an adapter.
- **Not an LLM wrapper.** v0.1 synthesis is rule-based pattern
  counting. LLM-assisted synthesis is queued behind a `--llm` flag
  that does not exist yet.

## Cadence

DreamReplay is monthly-to-quarterly tooling. A typical use is: run on
Friday, read on Monday, open PRs Tuesday for the candidates that
survive review, write a regret note for any candidate that was
promoted and later walked back.

## Related artifacts in this repo

- `SYSTEM_MAP.md` — the module-and-data-flow view of how the CLI is
  put together.
- `docs/METHODOLOGY.md` — what the rules score, why the thresholds are
  what they are, what triggers a re-run.
- `decisions/DEC-001-promotion-gate-rules.md` — the rules the human
  reviewer applies when promoting a candidate.
- `STATUS.md` — what is shipped, what is missing, what is queued.
