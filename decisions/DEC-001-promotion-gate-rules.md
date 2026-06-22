# DEC-001 — Promotion gate rules

## Status
Accepted, 2026-06-22.

## Context
DreamReplay writes weekly `dreams/YYYY-WNN/` directories of candidate
skills, memory updates, tests, and spec amendments. The CLI proposes;
a human promotes. This decision records what "promote" means, so the
rule is the same across the portfolio and across weeks.

## Rules

1. **Read end-to-end before promoting.** A candidate may only be
   promoted into the real ledger (`specs/`, `decisions/`, `CLAUDE.md`,
   the test suite) if a human has read the full candidate body, not
   just the slug.
2. **Promotion is a git move.** `git mv dreams/2026-W25/<file> <target>`
   into the real ledger. The dream candidate is rewritten in the
   destination location with whatever edits the human chose. The
   original dreams/ row stays in git history.
3. **Every promotion gets a decision record.** Each promoted candidate
   produces a new `decisions/DEC-NNN-<slug>.md` describing what was
   promoted and why. No silent promotions.
4. **Four-week stale window.** A candidate that sits in `dreams/`
   unread for four full weeks is auto-archived under `dreams/archived/`
   by a separate script (named in STATUS.md next-feature-queue). The
   main CLI does not touch already-written dreams.
5. **Regret notes are mandatory.** If a promoted candidate is later
   walked back, the human writes `decisions/DEC-NNN-regret-<slug>.md`
   recording what was wrong and what evidence was missed. This is the
   feedback path back into the synthesis rules.
6. **The CLI is read-only against the real ledger.** DreamReplay reads
   `specs/` and `decisions/`. It never writes there. Any code that
   appears to write outside `dreams/` is a bug.

## Consequences

- The promotion bottleneck is a human. That is the entire moat.
- Candidate volume is a metric to watch: if a weekly run proposes
  hundreds of candidates, the rules need tighter thresholds, not the
  human needs to read faster.
- Regret notes form a small, slow-growing dataset that informs the
  next generation of synthesis rules.

## References
- `STATUS.md` — current state and feature queue.
- `specs/0001-foundation/requirements.md` — R-DRM-004, R-DRM-008.
- `specs/0002-runnable-cli/requirements.md` — R-DRM-011 through
  R-DRM-021.
