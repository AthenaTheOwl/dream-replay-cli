# Spec 0001 — Acceptance (DreamReplay)

v0 (this scaffold PR) is done when:

- `README.md`, `LICENSE`, `AGENTS.md`, `.gitignore` exist
- `specs/0001-foundation/{requirements,design,tasks,acceptance}.md` exist
- `docs/first-pr.md` describes the second PR
- The top of `README.md` shows status checkboxes with the scaffold rows
  checked and the implementation rows unchecked
- No code beyond what spec 0001 names lives in this repo

Spec 0002 (the next PR) is done when:

```bash
uv sync
uv run pytest                                            # all green
uv run dreamreplay run \
    --traces tests/fixtures/portfolio_sample/traces \
    --spec-ledger tests/fixtures/portfolio_sample/specs \
    --decision-ledger tests/fixtures/portfolio_sample/decisions \
    --out dreams/test-run
uv run python scripts/voice_lint.py                      # clean
uv run python scripts/spec_check.py                      # every R-DRM-* satisfied
uv run python scripts/validate_schemas.py dreams/test-run/index.json
```

And:

- `dreams/test-run/` contains 4 .md files + index.json
- Running the same command twice produces byte-identical output
- The integration test passes offline with no network and no model key
- `decisions/DEC-001-promotion-gate-rules.md` exists and is referenced
  from README + AGENTS.md

Gates that must pass before merge: `voice_lint`, `spec_check`,
`validate_schemas`. A PR that fails any gate is not merged.
