# Spec 0002 — Design (DreamReplay v0.1)

## Module map

```
src/dreamreplay/
  __init__.py
  __main__.py          # python -m dreamreplay
  cli.py               # click group; one command, `run`
  models.py            # InternalEvent, SpecRequirement, DecisionRecord,
                       # Candidate dataclasses
  ingest/
    trace_loader.py    # TraceAdapter protocol + reference adapter
    spec_ledger.py     # R-*-NNN parser
    decision_ledger.py # DEC-NNN-* parser
  synthesize/
    candidate_skills.py
    candidate_memory.py
    candidate_tests.py
    candidate_spec_amendments.py
  render/
    dreams_dir.py      # 4 .md files + index.json writer
schemas/
  dream.schema.json
scripts/
  voice_lint.py
  spec_check.py
  validate_schemas.py
```

## Data model

```python
@dataclass(frozen=True)
class InternalEvent:
    timestamp: str   # ISO-8601, kept as string (no parsing in v0.1)
    kind: str        # "thought" | "action" | "observation" | "failure"
    actor: str
    payload: dict[str, str]  # flat string→string for stable hashing

@dataclass(frozen=True)
class SpecRequirement:
    id: str          # e.g. "R-DRM-011"
    spec_dir: str    # relative path like "0002-runnable-cli"
    title: str       # the heading text after the ID

@dataclass(frozen=True)
class DecisionRecord:
    id: str          # e.g. "DEC-001"
    title: str
    body: str

@dataclass(frozen=True)
class Candidate:
    kind: str        # "skill" | "memory" | "test" | "spec_amendment"
    slug: str        # kebab-case, used in Markdown headings
    evidence_count: int
    body: str        # the Markdown block to render
```

## Pipeline

```
load events  ──┐
load specs   ──┼──► run 4 synthesis rules ──► render(out_dir)
load dec     ──┘                                  │
                                                  └──► index.json
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

## Determinism

- No `datetime.now()`. The run date is supplied by `index.json` via a
  `--run-date` flag (default: read from the latest trace file's
  modification time, but only after `floor`-ing to the date in UTC).
- Input hashes in `index.json` use `hashlib.sha256` over file contents
  sorted by relative path.
- File writes use `\n` line endings explicitly, regardless of OS.
- JSON output uses `json.dumps(..., sort_keys=True, indent=2)` plus a
  trailing newline.

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
  `tests/fixtures/portfolio_sample/`, diffed against
  `tests/fixtures/expected_dreams/test-run/`.
- `test_determinism.py` — run twice, walk trees, assert byte-equal.
