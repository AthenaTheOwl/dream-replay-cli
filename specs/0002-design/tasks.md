# Spec 0002 — Tasks (DreamReplay v0.1, design ledger)

Mirror of `specs/0002-runnable-cli/tasks.md` under the contract-named
`specs/0002-design/` path. Both files should be edited together.

- [x] R-DRM-011 `src/dreamreplay/cli.py` — click group with `run`
      command (plus `dream_replay_cli/cli.py` shim).
- [x] R-DRM-012 `src/dreamreplay/ingest/trace_loader.py` — adapter
      protocol + JSONL reference adapter.
- [x] R-DRM-013 `src/dreamreplay/ingest/spec_ledger.py`.
- [x] R-DRM-014 `src/dreamreplay/ingest/decision_ledger.py`.
- [x] R-DRM-015 four synthesis rules under
      `src/dreamreplay/synthesize/`.
- [x] R-DRM-016 `src/dreamreplay/render/dreams_dir.py`.
- [x] R-DRM-017 `schemas/dream.schema.json`.
- [x] R-DRM-018 `scripts/voice_lint.py`, `scripts/spec_check.py`,
      `scripts/validate_schemas.py`.
- [x] R-DRM-019 `tests/fixtures/portfolio_sample/` and the seven test
      modules.
- [x] R-DRM-020 `tests/test_determinism.py`.
- [x] R-DRM-021 `dreams/2026-W25/` committed (dogfood corpus) plus the
      first-run row at `data/ledger/run-2026-W25.jsonl`.
- [x] `decisions/DEC-001-promotion-gate-rules.md`.
- [x] `docs/METHODOLOGY.md` — explains the rules, the calibration
      meaning, the determinism contract, and "what revisits this".
- [x] `STATUS.md` — current state, known limits, next feature queue.
- [x] `PRODUCT_BRIEF.md`, `SYSTEM_MAP.md` — top-level orientation.
- [x] `dream_replay_cli/` shim package with `cli.py`, `score.py`,
      `ledger.py`, `report.py`.
