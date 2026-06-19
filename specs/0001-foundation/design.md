# Spec 0001 — Design (DreamReplay)

## Pipeline shape

```
trace dir ──┐
spec dir  ──┼──► ingest ──► synthesize ──► render ──► dreams/YYYY-WNN/
decision dir ┘                                 │
                                               └──► index.json (validated)
```

Each box is a Python module under `src/`. The pipeline runs end-to-end
from the CLI in `cli/main.py`. There is no daemon, no scheduler. A cron
job (or a human) invokes the CLI weekly.

## Module map

```
cli/
  main.py                   # argparse, command dispatch
src/
  ingest/
    trace_loader.py         # adapter dispatch, returns InternalEvent stream
    spec_ledger.py          # parses R-*-NNN IDs out of requirements.md
    decision_ledger.py      # parses DEC-NNN-* files
  synthesize/
    candidate_skills.py     # patterns repeated 3+ times in traces -> skill draft
    candidate_memory.py     # facts referenced 3+ times that aren't in CLAUDE.md
    candidate_tests.py      # failed traces with deterministic shape -> eval case
    candidate_spec_amendments.py  # decision-evidence mismatch -> amend draft
  render/
    dreams_dir.py           # writes the 4 .md files + index.json
schemas/
  dream.schema.json
```

## The trace adapter contract

```python
class TraceAdapter(Protocol):
    def can_handle(self, path: Path) -> bool: ...
    def load(self, path: Path) -> Iterator[InternalEvent]: ...
```

`InternalEvent` is a frozen dataclass with `timestamp`, `kind`,
`actor`, `payload`. v0 ships one adapter — the trace-to-eval-harness
adapter — and an explicit error message when no adapter claims the
input.

## Promotion gate

Promotion is a manual `git mv` from `dreams/YYYY-WNN/` into the real
ledger, plus a human-authored `decisions/DEC-NNN-*.md` explaining the
choice. The CLI never does this. `decisions/DEC-001-promotion-gate-rules.md`
documents the discipline:

- A candidate may only be promoted if a human has read it end-to-end.
- A candidate that's been in `dreams/` for four weeks without promotion
  is auto-archived under `dreams/archived/` (a separate script, not the
  main CLI).
- A skill that was promoted then walked back must produce a regret
  note in the decision ledger.

## Determinism

- All synthesis steps run with `temperature=0` if an LLM is in the loop.
- The version of every model and prompt template is pinned in
  `pyproject.toml` and emitted into `index.json` for the run.
- No `datetime.now()` calls in file bodies. Run timestamp lives in
  `index.json` only.

## Test discipline

- One unit test per `R-DRM-*` requirement, named to match.
- One integration test that runs the full pipeline on
  `tests/fixtures/portfolio_sample/` and diffs the output against
  `tests/fixtures/expected_dreams/`.
- No test hits the network.
