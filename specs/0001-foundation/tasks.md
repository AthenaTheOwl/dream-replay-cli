# Spec 0001 — Tasks (DreamReplay)

First PR (the scaffold — this commit):

- [x] R-DRM-001 scaffold: README + LICENSE + AGENTS.md + .gitignore
- [x] R-DRM-001 specs/0001-foundation/ requirements + design + tasks + acceptance
- [x] R-DRM-001 docs/first-pr.md

Second PR (foundation runnable code):

- [ ] R-DRM-002 input contract: `cli/main.py` argparse stub that accepts
      `--traces`, `--spec-ledger`, `--decision-ledger`, `--out`
- [ ] R-DRM-005 adapter shape: `src/ingest/trace_loader.py` with
      `TraceAdapter` protocol + reference adapter
- [ ] R-DRM-002 `src/ingest/spec_ledger.py` parses R-*-NNN IDs
- [ ] R-DRM-002 `src/ingest/decision_ledger.py` parses DEC-NNN-* files
- [ ] R-DRM-003 `src/render/dreams_dir.py` writes the 4 .md files
- [ ] R-DRM-006 `schemas/dream.schema.json` + index.json writer
- [ ] R-DRM-010 `tests/fixtures/portfolio_sample/` synthetic fixture
- [ ] R-DRM-010 unit + integration tests, all offline
- [ ] R-DRM-004 `decisions/DEC-001-promotion-gate-rules.md`
- [ ] R-DRM-007 `scripts/voice_lint.py` + `scripts/spec_check.py` +
      `scripts/validate_schemas.py`
- [ ] R-DRM-009 determinism check in CI (run twice, diff outputs)

Third PR (dogfood + first published corpus):

- [ ] R-DRM-008 first `dreams/2026-W26/` run against the author's own
      portfolio, committed
- [ ] R-DRM-008 release notes referencing the dogfood corpus
