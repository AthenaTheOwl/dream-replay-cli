# SYSTEM MAP — DreamReplay

How the runnable v0.1 CLI is laid out on disk, and how data flows
through it. The view here is *physical* (files and modules), not
conceptual — for the conceptual view of what the rules score and why,
read `docs/METHODOLOGY.md`.

## Repo map

```
dream-replay-cli/
  PRODUCT_BRIEF.md             # what + why + who
  SYSTEM_MAP.md                # this file
  STATUS.md                    # shipped / known limits / next queue
  README.md                    # external-facing pitch
  LICENSE                      # MIT
  AGENTS.md                    # contributor / voice contract
  pyproject.toml               # uv + hatchling, dependency-groups

  src/dreamreplay/             # installed Python package (real impl)
    __init__.py
    __main__.py                # python -m dreamreplay
    cli.py                     # click group with `run` subcommand
    models.py                  # InternalEvent, SpecRequirement,
                               # DecisionRecord, Candidate
    ingest/
      trace_loader.py          # adapter protocol + JSONL adapter
      spec_ledger.py           # R-*-NNN extractor
      decision_ledger.py       # DEC-NNN-* parser
    synthesize/
      candidate_skills.py
      candidate_memory.py
      candidate_tests.py
      candidate_spec_amendments.py
    render/
      dreams_dir.py            # writes 4 .md files + index.json

  dream_replay_cli/            # contract-stable shim (re-exports)
    __init__.py
    cli.py                     # thin re-export of dreamreplay.cli
    ledger.py                  # ledger row read/write helpers
    score.py                   # candidate scoring helpers
    report.py                  # human-facing summary report

  schemas/
    dream.schema.json          # JSON Schema draft 2020-12 for index.json

  scripts/
    voice_lint.py              # Markdown banlist + antithetical-reversal
    spec_check.py              # R-DRM-* coverage gate
    validate_schemas.py        # JSON Schema gate

  specs/
    0001-foundation/           # scaffold spec (v0)
    0002-runnable-cli/         # the original v0.1 spec (kept)
    0002-design/               # contract-named copy of v0.1 spec

  decisions/
    DEC-001-promotion-gate-rules.md

  docs/
    METHODOLOGY.md             # rules, thresholds, calibration loop
    first-pr.md                # spec 0001 PR plan

  data/
    ledger/                    # one JSONL row per scoring run
      run-2026-W25.jsonl

  dreams/                      # rendered output of past runs
    2026-W25/                  # first dogfood corpus
      candidate_skills.md
      candidate_memory.md
      candidate_tests.md
      candidate_spec_amendments.md
      index.json

  tests/                       # pytest suite + offline fixtures
    fixtures/portfolio_sample/
    test_*.py
```

## Data flow

```
┌──────────────┐    ┌──────────────┐    ┌─────────────────┐
│  traces/*    │    │  specs/*     │    │  decisions/*    │
│  (JSONL)     │    │  (Markdown)  │    │  (Markdown)     │
└──────┬───────┘    └──────┬───────┘    └────────┬────────┘
       │                   │                     │
       ▼                   ▼                     ▼
 trace_loader.py    spec_ledger.py        decision_ledger.py
       │                   │                     │
       └─────────┬─────────┴──────────┬──────────┘
                 │                    │
                 ▼                    ▼
        ┌────────────────────────────────────┐
        │   synthesize/  (four pure rules)   │
        │   skills · memory · tests · specs  │
        └─────────────────┬──────────────────┘
                          │
                          ▼
                 render/dreams_dir.py
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            ▼             ▼             ▼
       4 × .md       index.json     data/ledger/*.jsonl
                                    (one row per run)
```

## Module responsibilities

| Module                        | Responsibility                                       |
|-------------------------------|------------------------------------------------------|
| `cli.py`                      | Click group, one `run` command, flag parsing.        |
| `models.py`                   | Frozen dataclasses; no logic.                        |
| `ingest/trace_loader.py`      | `TraceAdapter` protocol + JSONL reference adapter.   |
| `ingest/spec_ledger.py`       | Walk Markdown, extract `R-*-NNN` IDs and titles.     |
| `ingest/decision_ledger.py`   | Walk `DEC-NNN-*.md` files, parse ID from filename.   |
| `synthesize/candidate_*.py`   | One file = one rule. Pure, deterministic.            |
| `render/dreams_dir.py`        | Writes the four `.md` files + `index.json`.          |
| `scripts/*.py`                | Pre-merge gates. Each one exits 0 / 1.               |

## External dependencies

- `click` — CLI argument parsing.
- `jsonschema` — `index.json` validation against `dream.schema.json`.
- `pytest` (dev only) — test runner.

That is the whole dependency surface. No HTTP client, no LLM SDK, no
database driver. The "offline" in offline-cognition is structural.

## Determinism contract

- `models.InternalEvent.payload` is a sorted tuple of pairs, not a
  dict, so iteration order is stable.
- All synthesis rules sort their outputs by
  `(evidence_count desc, slug asc)` before returning.
- `index.json` is written with `json.dumps(..., sort_keys=True,
  indent=2)` and a trailing `\n`.
- File writes use explicit `\n` line endings regardless of OS.
- Windows path separators are normalized to `/` in `index.json` so
  diffs are platform-stable.

`tests/test_determinism.py` runs the pipeline twice into separate
output directories, walks both trees, and asserts byte-equal on every
file. If a future change breaks determinism, that test fails before
the PR merges.

## Where the ledger row lives

The contract gate looks at `data/ledger/*.jsonl`. One JSON line per
scoring / calibration run, with the same totals and input hashes the
rendered `dreams/YYYY-WNN/index.json` carries — the JSONL form is
append-only and machine-grepable; the directory form is human-readable.

## Where to start reading

1. `PRODUCT_BRIEF.md` — what this is and why.
2. `STATUS.md` — what's shipped, what's missing.
3. `docs/METHODOLOGY.md` — how the four rules work.
4. `src/dreamreplay/cli.py` — the runnable entry point.
5. `tests/test_end_to_end.py` — the pipeline pinned to fixtures.
