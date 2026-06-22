# Spec 0002 — Acceptance (DreamReplay v0.1, design ledger)

Mirror of `specs/0002-runnable-cli/acceptance.md` under the
contract-named `specs/0002-design/` path.

v0.1 is done when, in a clean checkout:

```bash
python -m uv sync
python -m uv run pytest                                  # all green
python -m uv run dreamreplay run \
    --traces tests/fixtures/portfolio_sample/traces \
    --spec-ledger tests/fixtures/portfolio_sample/specs \
    --decision-ledger tests/fixtures/portfolio_sample/decisions \
    --out dreams/test-run \
    --run-date 2026-06-22 \
    --week 2026-W25
python -m uv run python scripts/voice_lint.py
python -m uv run python scripts/spec_check.py
python -m uv run python scripts/validate_schemas.py
```

All commands exit 0.

And:

- `dreams/test-run/` contains four `.md` files plus `index.json`.
- Running the same command twice into two different `--out` paths
  produces byte-identical files (verified by `test_determinism.py`).
- `dreams/2026-W25/` is committed.
- `data/ledger/run-2026-W25.jsonl` is committed and contains one
  JSON-line row matching the rendered `index.json` totals.
- `decisions/DEC-001-promotion-gate-rules.md` exists and is referenced
  from `STATUS.md`.
- `PRODUCT_BRIEF.md`, `SYSTEM_MAP.md`, `STATUS.md`, and
  `docs/METHODOLOGY.md` are all present at their canonical paths.
- Every `R-DRM-0NN` ID from spec 0001 and spec 0002 is either
  implemented in `src/dreamreplay/` or named in a test under `tests/`.

Gates that must pass before merge: `voice_lint`, `spec_check`,
`validate_schemas`. A PR failing any gate does not merge.
