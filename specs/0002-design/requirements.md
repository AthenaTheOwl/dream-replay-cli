# Spec 0002 — Requirements (DreamReplay v0.1, design ledger)

Spec 0001 named the discipline. Spec 0002 ships the first runnable
pipeline. All requirement IDs are stable across the lifetime of the
spec — they do not get renumbered.

This file mirrors `specs/0002-runnable-cli/requirements.md` under the
contract-named directory `specs/0002-design/` so the factory contract
gate finds the canonical four files (`requirements`, `design`, `tasks`,
`acceptance`) at a stable path. Edits should land in both copies until
the older path is retired in a future spec.

## R-DRM-011 — `dreamreplay run` command

A `dreamreplay run` subcommand exists. It accepts four flags:

- `--traces PATH` — directory of trace files
- `--spec-ledger PATH` — directory of `specs/*/requirements.md`
- `--decision-ledger PATH` — directory of `decisions/DEC-*.md`
- `--out PATH` — output directory (the `dreams/YYYY-WNN/` target)

All paths are filesystem paths. The command writes to `--out` and exits
with code 0 on success, 1 on any error.

## R-DRM-012 — reference trace adapter

`src/dreamreplay/ingest/trace_loader.py` implements a `TraceAdapter`
protocol plus one concrete adapter: `TraceToEvalHarnessAdapter`. The
adapter reads JSONL files where each line is `{"timestamp": str,
"kind": str, "actor": str, "payload": object}` and yields frozen
`InternalEvent` dataclasses.

## R-DRM-013 — spec ledger parser

`src/dreamreplay/ingest/spec_ledger.py` walks the `--spec-ledger`
directory and extracts every `R-*-NNN` requirement ID it finds in
`requirements.md` files. The parser returns a list of
`SpecRequirement(id, spec_dir, title)`.

## R-DRM-014 — decision ledger parser

`src/dreamreplay/ingest/decision_ledger.py` walks the
`--decision-ledger` directory and parses every `DEC-NNN-*.md` file into
`DecisionRecord(id, title, body)`. The ID is parsed from the filename,
not from a frontmatter block.

## R-DRM-015 — rule-based synthesis

Four synthesis modules under `src/dreamreplay/synthesize/` each
implement a single rule:

- `candidate_skills.py` — actors with the same event-kind sequence
  appearing 3+ times become a skill draft.
- `candidate_memory.py` — payload facts (string values) appearing 3+
  times across events become a memory draft.
- `candidate_tests.py` — events with `kind == "failure"` become a test
  draft.
- `candidate_spec_amendments.py` — `R-*-NNN` IDs referenced in trace
  payloads but missing from the spec ledger become an amendment draft.

Each rule is pure: same input list → same output list.

## R-DRM-016 — dreams directory renderer

`src/dreamreplay/render/dreams_dir.py` writes the four Markdown files
plus `index.json` to `--out`. File order in `index.json` is
lexicographic. No file contains a wall-clock timestamp; run metadata
(date, input hashes) lives only in `index.json`.

## R-DRM-017 — schema validation

`schemas/dream.schema.json` is a JSON Schema (draft 2020-12). Every
`index.json` produced by the CLI validates against it.
`scripts/validate_schemas.py` runs the validator and exits non-zero on
failure.

## R-DRM-018 — gates

Three scripts under `scripts/`:

- `voice_lint.py` — checks committed Markdown for the banlist named in
  AGENTS.md and for antithetical-reversal sentence shapes.
- `spec_check.py` — every `R-DRM-*` ID under `specs/` is either
  referenced in `tests/` or implemented in `src/dreamreplay/`.
- `validate_schemas.py` — runs `dream.schema.json` validation against a
  named index file (or all `dreams/*/index.json` if no path given).

Each script exits 0 on success, 1 on failure.

## R-DRM-019 — offline fixture and tests

`tests/fixtures/portfolio_sample/` ships traces, specs, and decisions.
`tests/test_end_to_end.py` runs the pipeline against this fixture. No
test opens a network socket; no test reads an environment variable
other than `PYTHONHASHSEED`.

## R-DRM-020 — determinism

Re-running `dreamreplay run` on the same inputs produces byte-identical
files. `tests/test_determinism.py` enforces this: run twice into two
output dirs, walk both trees, diff every file.

## R-DRM-021 — checked-in dogfood corpus

`dreams/2026-W25/` is committed. It is the output of running the v0.1
CLI against `tests/fixtures/portfolio_sample/`. This is the first
scoring / calibration row of the system and the dogfood proof for
release v0.1. The same row, in append-only JSONL form, lives at
`data/ledger/run-2026-W25.jsonl`.
