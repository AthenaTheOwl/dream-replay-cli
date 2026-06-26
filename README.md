# dream-replay-cli

Eight candidate skills, memory edits, tests, and spec amendments come out of one
week's traces. None of them ship. They sit in `dreams/2026-W25/` until a person
opens the file and says yes. The CLI proposes; the gate is a human.

## What it does

Every agent framework in 2026 ships a runtime — LangGraph, CrewAI, Bedrock Agents,
the OpenAI Agents SDK. None of them ship a replay plane: a deliberate offline pass
over the week's traces that proposes changes to the long-running system instead of
mutating it in place. An agent that learns by overwriting itself mid-flight has no
audit trail and no veto. This is the veto.

dream-replay-cli reads three things — a trace log, a spec ledger, a decision
ledger — and writes one weekly `dreams/YYYY-WNN/` directory: candidate skills,
candidate memory updates, candidate tests, candidate spec amendments, and an
`index.json` so the promotion gate can iterate. It is a CLI, not a service. It
writes files, not database rows. A reviewer reads the week in under thirty minutes.

The interesting output isn't the candidates that pass. It's the drift the traces
expose: agents acting on a requirement (`R-DRM-999`) the spec ledger never defined.
The replay pass catches the gap between what the agents did and what anyone wrote
down, and shows it to a human before anything gets promoted.

## try it

No setup, no args. Reads the committed `dreams/2026-W25/` corpus and
prints the week's candidates ranked by how much trace evidence backs
each one:

```bash
uv run python -m dream_replay_cli show
```

```
dream review -- 2026-W25  (run 2026-06-22)

8 candidate(s) await human review. Promotion is gated.

ranked by evidence (strongest first):
   #  evid  kind            candidate
   1     4  memory update   ledger-row-write
   2     4  skill           thought-then-action
   6     2  spec amendment  add-r-drm-999

headline -- spec drift (referenced but undefined):
  - add-r-drm-999: R-DRM-999 referenced in 2 trace event(s) but absent from the spec ledger
```

The headline is the point: the traces show agents acting on a
requirement (`R-DRM-999`) the spec ledger never defined, so a reviewer
sees the drift before promoting anything.

## live demo

an interactive streamlit page mirrors the `show` verb: it reads the committed
`dreams/*/index.json` and renders the week's candidates ranked by evidence, the
spec-drift headline, and per-kind totals. no network, no secrets.

<!-- live url: https://<your-app>.streamlit.app -->

run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

deploy on streamlit community cloud: new app -> repo `AthenaTheOwl/dream-replay-cli`,
branch `main`, main file `streamlit_app.py`.

## how to run a fresh week

```bash
uv sync
uv run python -m dream_replay_cli run \
    --traces ./tests/fixtures/portfolio_sample/traces \
    --spec-ledger ./tests/fixtures/portfolio_sample/specs \
    --decision-ledger ./tests/fixtures/portfolio_sample/decisions \
    --week 2026-W26 \
    --run-date 2026-06-26 \
    --out ./dreams/2026-W26
```

`run` requires `--week` and `--run-date`; `show` and `validate` take no
args and read only the committed corpus.

## How it connects

This is the replay plane pulled out of the CDCP operating model the rest of the
portfolio runs on. Two ledgers feed it and nothing it produces is automatic:

- The spec ledger (`specs/NNNN-*/requirements.md`-shaped) and the decision ledger
  (`decisions/DEC-NNN-*.md`-shaped) are the same artifact types every active repo
  carries. dream-replay-cli reads them as inputs, not as decoration.
- The trace log arrives through an adapter, so the traces live wherever you already
  keep them. This repo never becomes the store.
- Promotion is a person reading `dreams/YYYY-WNN/` and merging by hand. There is no
  confidence score standing in for the human, and no hosted plane doing it for you.

## Run / layout

```bash
uv sync
uv run python -m dream_replay_cli validate   # schema-check the committed corpus
```

```
dream_replay_cli/   cli, ledger, score, report — the working package
dreams/2026-W25/     the committed corpus show + validate read
specs/  decisions/   the two ledgers that feed run
schemas/  tests/  docs/
```

## License

MIT. See `LICENSE`.
