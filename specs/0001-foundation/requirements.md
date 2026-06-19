# Spec 0001 — Foundation (DreamReplay)

## R-DRM-001 — repo scaffold
Repo lives at `e:/claude_code/random-apps/dream-replay-cli`. MIT license,
copyright Vignesh Gopalakrishnan. README, AGENTS.md, .gitignore, and the
specs/0001-foundation/ directory exist before any code lands.

## R-DRM-002 — input contract
DreamReplay accepts three inputs: a trace log directory, a spec ledger
directory (`specs/*/requirements.md`-shaped Markdown), and a decision
ledger directory (`decisions/DEC-*.md`-shaped Markdown). All three are
file-system paths. No database, no API, no auth.

## R-DRM-003 — output contract
A single run writes one directory: `dreams/YYYY-WNN/`. The directory
contains `candidate_skills.md`, `candidate_memory.md`,
`candidate_tests.md`, `candidate_spec_amendments.md`, and one
machine-readable `index.json` validated by `schemas/dream.schema.json`.

## R-DRM-004 — promotion-gate rule
DreamReplay never mutates the spec ledger or the decision ledger. It
only writes to `dreams/`. Promotion (moving a candidate into the real
ledger) is a separate, manual step documented in
`decisions/DEC-001-promotion-gate-rules.md`.

## R-DRM-005 — adapter shape
Trace ingestion goes through an adapter interface. The reference
adapter targets the trace-to-eval-harness event schema. Additional
adapters (LangGraph, CrewAI, Bedrock) land in spec 0003.

## R-DRM-006 — schema-validated index
`dreams/YYYY-WNN/index.json` validates against
`schemas/dream.schema.json`. Validation runs in CI on every PR.

## R-DRM-007 — gates
Three gates run locally and in CI: `voice_lint.py`, `spec_check.py`,
`validate_schemas.py`. A PR that fails any gate does not merge.

## R-DRM-008 — dogfood requirement
Every tagged release of DreamReplay ships with at least one
`dreams/YYYY-WNN/` directory produced by running the CLI on the author's
own portfolio. This is the proof-of-discipline artifact.

## R-DRM-009 — determinism
Re-running DreamReplay on the same inputs produces byte-identical
output files. No timestamps in file bodies; no LLM-temperature drift
that's not pinned in `pyproject.toml`.

## R-DRM-010 — offline fixture
`tests/fixtures/portfolio_sample/` ships a small synthetic portfolio
(traces + specs + decisions) so the test suite runs offline with no
network and no model key.
