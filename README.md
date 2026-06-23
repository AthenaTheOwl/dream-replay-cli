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


v0.1 shipped and runs end to end. Three verbs work today: `show` (no-arg
ranked digest of the committed corpus), `validate` (no-arg schema check of
the committed corpus), and `run` (synthesize a fresh `dreams/YYYY-WNN/`
from your own traces). See the `try it` section below and `STATUS.md` for
the current state and next-feature queue.

## try it

No setup, no args. Reads the committed `dreams/2026-W25/` corpus and
prints the week's candidates ranked by how much trace evidence backs
each one:

```bash
uv run python -m dream_replay_cli show
```

```
dream review -- 2026-W25  (run 2026-06-22)

8 candidate(s) await human review. Promotion is gated.

ranked by evidence (strongest first):
   #  evid  kind            candidate
   1     4  memory update   ledger-row-write
   2     4  skill           thought-then-action
   6     2  spec amendment  add-r-drm-999

headline -- spec drift (referenced but undefined):
  - add-r-drm-999: R-DRM-999 referenced in 2 trace event(s) but absent from the spec ledger
```

The headline is the point: the traces show agents acting on a
requirement (`R-DRM-999`) the spec ledger never defined, so a reviewer
sees the drift before promoting anything.

## how to run a fresh week

```bash
uv sync
uv run python -m dream_replay_cli run \
    --traces ./tests/fixtures/portfolio_sample/traces \
    --spec-ledger ./tests/fixtures/portfolio_sample/specs \
    --decision-ledger ./tests/fixtures/portfolio_sample/decisions \
    --week 2026-W26 \
    --run-date 2026-06-26 \
    --out ./dreams/2026-W26
```

`run` requires `--week` and `--run-date`; `show` and `validate` take no
args and read only the committed corpus.

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
