# AGENTS.md — dream-replay-cli

Operating contract for AI agents (Claude, Codex, Cursor) working in this
repo. Conventions match the rest of the AthenaTheOwl portfolio so an
agent already trained on trace-to-eval-harness or
procurement-negotiation-lab recognizes the shape.

## What this repo is

An open-source CLI that ingests trace logs plus spec and decision
ledgers and emits a weekly `dreams/YYYY-WNN/` directory of candidate
skills, memory updates, tests, and spec amendments. The CLI proposes;
a human promotes. The promotion gate is the entire point — the moment
you remove it, this becomes another auto-learning experiment that
quietly corrupts the long-running system.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `trace-ingester` | Reads adapter-specific trace formats into the internal event shape |
| `ledger-reader` | Parses `specs/*/requirements.md` and `decisions/DEC-*.md` |
| `candidate-synthesizer` | Drafts skills / memory / tests / spec amendments from the week's evidence |
| `dreams-renderer` | Writes `dreams/YYYY-WNN/` with deterministic file names |
| `promotion-gate-author` | Documents the rules in `decisions/DEC-001-promotion-gate-rules.md` |

These roles exist in the spec ledger; v0 does not implement them.

## Voice constraints

- No marketing words. The banlist mirrors `voice_lint.py` across the
  portfolio.
- No antithetical reversals as a structural device.
- Plain assertions. The discipline (human-gated promotion, deterministic
  output) is the moat. The voice is scaffolding.

## Gates (will land in spec 0002)

- `voice_lint.py` mirrored from athena-site
- `spec_check.py` — every `R-DRM-*` ID in `specs/` must be implemented or
  tested by the time its parent PR merges
- `validate_schemas.py` — `dream.schema.json` validates against an
  example `dreams/YYYY-WNN/index.json` fixture
- `dogfood_check.py` — every shipped release must include a `dreams/`
  output from the author's own portfolio

## Out of scope

- Auto-promotion. The CLI never mutates the spec or decision ledger
  directly.
- A hosted service. No DreamReplay cloud, no API, no auth surface.
- Trace storage. This repo reads traces; it does not store them.
- Cross-org sharing of dreams. The corpus the author publishes is opt-in
  and from a single portfolio.
