# First PR after the scaffold

This document describes the literal next PR after the v0 scaffold lands.
Spec 0002 is the work plan; this file is the file-level changeset.

## Goal

A `dreamreplay run` command that ingests synthetic fixture traces, a
fixture spec ledger, and a fixture decision ledger, and writes a
`dreams/test-run/` directory containing four candidate Markdown files
plus a schema-validated `index.json`.

No LLM call in this PR. Synthesis is rule-based on the fixture so the
test suite is deterministic and offline.

## Files changed

New:

- `pyproject.toml` — Python 3.11, `uv` discipline, pinned deps
  (`pydantic`, `jsonschema`, `click`)
- `cli/main.py` — `click` group with one command, `run`
- `src/__init__.py`
- `src/ingest/__init__.py`
- `src/ingest/trace_loader.py` — `TraceAdapter` protocol + reference
  adapter for the trace-to-eval-harness event format
- `src/ingest/spec_ledger.py` — Markdown parser extracting `R-*-NNN` IDs
- `src/ingest/decision_ledger.py` — Markdown parser for `DEC-NNN-*` files
- `src/synthesize/__init__.py`
- `src/synthesize/candidate_skills.py` — pattern-frequency rule
- `src/synthesize/candidate_memory.py` — fact-recurrence rule
- `src/synthesize/candidate_tests.py` — failed-trace promotion rule
- `src/synthesize/candidate_spec_amendments.py` — decision-evidence
  mismatch rule
- `src/render/dreams_dir.py` — file writer + index.json emitter
- `schemas/dream.schema.json`
- `tests/fixtures/portfolio_sample/traces/event_log_2026-W25.jsonl`
- `tests/fixtures/portfolio_sample/specs/0001-foundation/requirements.md`
- `tests/fixtures/portfolio_sample/decisions/DEC-001-example.md`
- `tests/fixtures/expected_dreams/test-run/index.json`
- `tests/fixtures/expected_dreams/test-run/candidate_*.md` (4 files)
- `tests/test_ingest_traces.py`
- `tests/test_ingest_specs.py`
- `tests/test_ingest_decisions.py`
- `tests/test_synthesize.py`
- `tests/test_render.py`
- `tests/test_end_to_end.py` — integration test that runs the full
  pipeline and diffs against `expected_dreams/`
- `tests/test_determinism.py` — runs twice, asserts byte-identical
- `scripts/voice_lint.py`
- `scripts/spec_check.py`
- `scripts/validate_schemas.py`
- `decisions/DEC-001-promotion-gate-rules.md`
- `dreams/.gitkeep`

Modified:

- `README.md` — replace "How to run" placeholder with the real command
- `specs/0001-foundation/tasks.md` — check off the spec-0002 rows
- `AGENTS.md` — point Gates section at the real scripts

## Verification

```bash
uv sync
uv run pytest -v                                         # all green
uv run dreamreplay run \
    --traces tests/fixtures/portfolio_sample/traces \
    --spec-ledger tests/fixtures/portfolio_sample/specs \
    --decision-ledger tests/fixtures/portfolio_sample/decisions \
    --out dreams/test-run
diff -r dreams/test-run tests/fixtures/expected_dreams/test-run   # empty
uv run python scripts/voice_lint.py
uv run python scripts/spec_check.py
uv run python scripts/validate_schemas.py dreams/test-run/index.json
```

## Out of scope for this PR

- Real LLM-driven synthesis (lands in spec 0003)
- LangGraph / CrewAI / Bedrock adapters (spec 0003)
- The first dogfood run on the author's own portfolio (spec 0003)
- A `dreams/` auto-archiver (spec 0003)
