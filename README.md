# DreamReplay — Open-Source Offline-Cognition CLI

An open-source CLI that ingests a trace log plus a spec ledger plus a
decision ledger and emits a weekly `dreams/YYYY-WNN/` directory of
candidate skills, candidate memory updates, candidate tests, and candidate
spec amendments. Promotion is human-gated. Nothing in `dreams/` ships
without a person opening the file and saying yes.

## What this is

Every agent framework in 2026 ships a runtime — LangGraph, CrewAI,
Bedrock Agents, OpenAI Agents SDK. None ship a Dream / Replay plane: a
deliberate offline pass over the week's traces that proposes promotions
to the long-running system instead of mutating it in place.

DreamReplay is that plane, extracted from the CDCP operating model the
rest of the portfolio runs on. It is a CLI, not a service. It writes
files, not database rows. The output is review-able by a human in under
thirty minutes a week.

Three inputs:

- A trace log directory (any format with an adapter)
- A spec ledger (`specs/NNNN-*/requirements.md`-shaped Markdown)
- A decision ledger (`decisions/DEC-NNN-*.md`-shaped Markdown)

One output per run:

- `dreams/YYYY-WNN/` with `candidate_skills.md`, `candidate_memory.md`,
  `candidate_tests.md`, `candidate_spec_amendments.md`, and a
  machine-readable `index.json` so the promotion gate can iterate.

## Status

v0 scaffold. No implementation yet — only the spec ledger, the AGENTS
contract, and the file layout below. First runnable code lands in
spec 0002.

- [x] Repo scaffold + LICENSE + AGENTS.md
- [x] Spec 0001 (foundation) — requirements, design, tasks, acceptance
- [x] First-PR plan in `docs/first-pr.md`
- [ ] Schema for `dream.schema.json`
- [ ] Reference adapter (trace-to-eval-harness format)
- [ ] Dry-run on a portfolio fixture
- [ ] First published quarterly corpus

## How to run

Placeholder. The runnable CLI lands in spec 0002. The intended shape:

```bash
uv sync
uv run dreamreplay run \
    --traces ./fixtures/traces \
    --spec-ledger ./fixtures/specs \
    --decision-ledger ./fixtures/decisions \
    --out ./dreams/2026-W26
```

Until spec 0002 lands, the only thing in this repo that runs is
`python -c "print('scaffold')"`.

## Layout

```
dream-replay-cli/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
```

Planned but not yet present (lands across spec 0002 + 0003):

```
  cli/
    main.py
  src/
    ingest/
      trace_loader.py
      spec_ledger.py
      decision_ledger.py
    synthesize/
      candidate_skills.py
      candidate_memory.py
      candidate_tests.py
    render/
      dreams_dir.py
  schemas/
    dream.schema.json
  decisions/
    DEC-001-promotion-gate-rules.md
  dreams/
    .gitkeep
  tests/
    fixtures/
  pyproject.toml
```

## Who this is for

- AI platform teams who already have traces but no review cadence over
  them.
- Individual builders running multi-agent portfolios. The author runs
  one; the CLI is dogfooded on it before any external user touches it.
- Researchers studying continual-learning patterns for agents who want
  a checked-in corpus instead of a black-box service.

## What this is not

- Not a hosted service. The CLI runs on your machine, against your
  files. There is no DreamReplay cloud.
- Not auto-promotion. The CLI proposes; a human reads and merges. The
  gate is a person, not a confidence score.
- Not a trace store. Traces live wherever you already keep them. This
  repo reads them through an adapter.

## License

MIT. See `LICENSE`.
