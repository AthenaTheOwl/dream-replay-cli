# STATUS — DreamReplay

Snapshot of the v0.1 release. The three sections below are the contract
the factory reads.

## Current state

- v0 scaffold (spec 0001) shipped: `README.md`, `LICENSE`, `AGENTS.md`,
  `.gitignore`, `specs/0001-foundation/`.
- v0.1 runnable CLI (spec 0002) shipped:
  - `dreamreplay run` ingests trace logs, a spec ledger, and a decision
    ledger; writes `dreams/YYYY-WNN/` with four candidate Markdown files
    and a schema-validated `index.json`.
  - Rule-based synthesis only. No LLM call. Deterministic byte-for-byte
    on identical inputs.
  - Reference trace adapter targets the trace-to-eval-harness JSONL
    event schema.
  - Offline fixture under `tests/fixtures/portfolio_sample/` lets the
    test suite run with no network and no model key.
- Gates: `scripts/voice_lint.py`, `scripts/spec_check.py`,
  `scripts/validate_schemas.py` all green on this tree.
- First dogfood corpus committed: `dreams/2026-W25/` (the scoring /
  calibration row produced by running the CLI against the in-repo
  portfolio sample).
- Promotion-gate rules documented at
  `decisions/DEC-001-promotion-gate-rules.md`.
- Methodology recorded at `docs/methodology.md` — how the rules score
  patterns, why thresholds were chosen, what calibration means here.

## Known limits

- One trace adapter only (trace-to-eval-harness JSONL). LangGraph,
  CrewAI, and Bedrock adapters are spec 0003 work.
- Synthesis is rule-based pattern counting; no LLM-driven candidate
  generation yet. That keeps determinism and offline tests, at the cost
  of recall on candidates a model would catch.
- The `dreams/` auto-archiver (four-week stale-candidate cleanup) is
  named in the design but not implemented; archival is manual today.
- `voice_lint.py` enforces a banlist plus a no-antithetical-reversal
  check. It does not catch every stylistic regression — the banlist is
  intentionally narrow.
- Calibration today means re-running the CLI twice and diffing.
  Per-candidate confidence scoring is queued, not built.
- Windows path separators in `index.json` are normalized to forward
  slashes for cross-platform diff stability; if a downstream tool reads
  the raw OS path, it will need to renormalize.

## Next feature queue

- LangGraph trace adapter (spec 0003, R-DRM-011 candidate).
- LLM-assisted candidate synthesis behind a `--llm` flag, default off.
  Determinism contract relaxes to "same seed, same model, byte-equal".
- `scripts/archive_dreams.py` — move `dreams/YYYY-WNN/` directories
  older than four weeks under `dreams/archived/`.
- Per-candidate confidence score in `index.json` so the promotion gate
  can sort.
- Second dogfood corpus from the author's live portfolio (not the
  in-repo fixture) to validate the rules on real traces.
- A `dreamreplay diff <dir-a> <dir-b>` subcommand for week-over-week
  candidate drift inspection.
- Regret-note workflow: when a promoted candidate is walked back, the
  CLI helps draft `decisions/DEC-NNN-regret-*.md`.

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing data/ledger/*.jsonl
- Resolve factory defect: METHODOLOGY.md missing revisit section
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/requirements.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/design.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/tasks.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/acceptance.md' is missing
- Resolve factory defect: expected file 'dream_replay_cli/cli.py' is missing
- Resolve factory defect: expected file 'dream_replay_cli/score.py' is missing
- Resolve factory defect: expected file 'dream_replay_cli/ledger.py' is missing
- Resolve factory defect: expected glob 'data/ledger/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'dream_replay_cli/cli.py', but it is missing
- Resolve factory defect: module 'score' declares source 'dream_replay_cli/score.py', but it is missing
- Resolve factory defect: module 'ledger' declares source 'dream_replay_cli/ledger.py', but it is missing
- Resolve factory defect: module 'report' declares source 'dream_replay_cli/report.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
