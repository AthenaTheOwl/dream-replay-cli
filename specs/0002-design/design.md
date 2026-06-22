# Spec 0002 — Design (DreamReplay v0.1, design ledger)

This file mirrors `specs/0002-runnable-cli/design.md` under the
contract-named `specs/0002-design/` path.

## Module map

```
src/dreamreplay/
  __init__.py
  __main__.py            # python -m dreamreplay
  cli.py                 # click group; one command, `run`
  models.py              # InternalEvent, SpecRequirement,
                         # DecisionRecord, Candidate dataclasses
  ingest/
    trace_loader.py      # TraceAdapter protocol + reference adapter
    spec_ledger.py       # R-*-NNN parser
    decision_ledger.py   # DEC-NNN-* parser
  synthesize/
    candidate_skills.py
    candidate_memory.py
    candidate_tests.py
    candidate_spec_amendments.py
  render/
    dreams_dir.py        # 4 .md files + index.json writer

dream_replay_cli/        # contract-stable shim
  __init__.py
  cli.py                 # re-exports dreamreplay.cli
  score.py               # candidate scoring helpers
  ledger.py              # data/ledger/*.jsonl read + append
  report.py              # one-screen run summary

schemas/
  dream.schema.json
scripts/
  voice_lint.py
  spec_check.py
  validate_schemas.py
data/
  ledger/                # one JSONL row per scoring run
```

## Data model

```python
@dataclass(frozen=True)
class InternalEvent:
    timestamp: str
    kind: str         # "thought" | "action" | "observation" | "failure"
    actor: str
    payload: tuple[tuple[str, str], ...]

@dataclass(frozen=True)
class SpecRequirement:
    id: str           # e.g. "R-DRM-011"
    spec_dir: str
    title: str

@dataclass(frozen=True)
class DecisionRecord:
    id: str           # e.g. "DEC-001"
    title: str
    body: str

@dataclass(frozen=True)
class Candidate:
    kind: str         # "skill" | "memory" | "test" | "spec_amendment"
    slug: str
    evidence_count: int
    notes: str
    body: str

@dataclass(frozen=True)
class LedgerRow:
    run_id: str
    week: str
    run_date: str
    schema_version: str
    totals: dict[str, int]
    inputs: dict[str, dict[str, str]]
    out_dir: str
```

## Pipeline

```
load events  ──┐
load specs   ──┼──► run 4 synthesis rules ──► render(out_dir)
load dec     ──┘                                  │
                                                  ├──► index.json
                                                  └──► data/ledger/*.jsonl row
```

The pipeline is a single `run_pipeline(traces, specs, decisions, out)`
function. The CLI is a thin click wrapper. No shared mutable state.

## Synthesis rules (precise)

- **Skills**: group events by `actor`, project to the sequence of
  `kind` values, count contiguous repetitions of length ≥ 2 that
  appear ≥ 3 times across actors. Each surviving sequence becomes one
  skill candidate.
- **Memory**: collect all `payload[*]` string values where length ≥ 8
  and the value appears in ≥ 3 distinct events. Each surviving value
  becomes one memory candidate.
- **Tests**: every event with `kind == "failure"` becomes one test
  candidate. Slug is built from `actor` plus a short payload hash.
- **Spec amendments**: scan all payload string values for matches
  against the regex `R-[A-Z]+-\d{3}`. Any ID matched in traces but
  absent from `SpecRequirement.id` becomes one amendment candidate.

Every rule returns a list sorted by `(evidence_count desc, slug asc)`
so output ordering is stable.

## Scoring and the ledger

v0.1 scoring is intentionally arithmetic: a candidate's score is its
`evidence_count`, namespaced by rule. `dream_replay_cli.score`
formalises this so a future probabilistic-scoring upgrade can land
without touching the synthesis rules. Every run appends one
`LedgerRow` to `data/ledger/run-<week>.jsonl`; reading those rows is
how `dream_replay_cli.report` produces a human-readable summary
without re-walking the rendered Markdown.

## Determinism

- No `datetime.now()`. The run date is supplied by `--run-date`.
- Input hashes in `index.json` use `hashlib.sha256` over file contents
  sorted by relative path.
- File writes use `\n` line endings explicitly, regardless of OS.
- JSON output uses `json.dumps(..., sort_keys=True, indent=2)` plus a
  trailing newline.
- Ledger rows use `json.dumps(..., sort_keys=True)` (single-line) plus
  a trailing newline — append-only and diff-stable.

## Voice / format

The four Markdown files share a shape:

```
# <Kind> candidates — <week label>

> N candidates. Evidence threshold: <rule-specific>.

## <slug>

- Evidence count: <n>
- Notes: <one-line rule-derived note>

<body>
```

The renderer holds the template; rules supply `slug`, `evidence_count`,
and `body` only.

## Test plan

- `test_ingest_traces.py` — adapter dispatch + JSONL parsing.
- `test_ingest_specs.py` — `R-*-NNN` extraction across multiple specs.
- `test_ingest_decisions.py` — DEC ID parsed from filename, body kept
  verbatim.
- `test_synthesize.py` — one test per rule, hand-built fixtures.
- `test_render.py` — diff against golden Markdown.
- `test_end_to_end.py` — full pipeline against
  `tests/fixtures/portfolio_sample/`.
- `test_determinism.py` — run twice, walk trees, assert byte-equal.
