# Methodology — how DreamReplay scores and calibrates

This document records the rules behind v0.1 candidate synthesis, the
thresholds those rules use, and what "calibration" means in a
release-by-release sense. The intended reader is a human reviewer
deciding whether a candidate in `dreams/YYYY-WNN/` should be promoted.

## The four rules

DreamReplay runs four independent rules against a week of trace
events. Each rule is pure (same input → same output), runs offline,
and emits a list of candidates sorted for stable rendering.

### Skills — repeated event-kind bigrams

- Group events by `actor`.
- For each actor, take the sequence of `kind` values in event order.
- Extract bigrams `(kind_i, kind_{i+1})`.
- Across the whole corpus, count occurrences of each bigram.
- Bigrams with count >= 3 become skill candidates.

Why this rule: skills are repeated micro-procedures. A bigram like
`thought` → `action` that recurs across actors is the trace-shaped
fingerprint of a routine worth naming.

### Memory — repeated long payload values

- Walk every event's payload.
- Keep string values of length >= 8.
- Count how many distinct events each unique value appears in.
- Values present in >= 3 distinct events become memory candidates.

Why this rule: a fact mentioned in three separate events, by possibly
different actors, is more likely to be durably true than noise. The
length filter screens out trivial tokens.

### Tests — one per failure event

- Every event with `kind == "failure"` becomes one test candidate.

Why this rule: a failure observed in production is the highest-value
seed for a regression test. The rule's job is to ensure none get
silently dropped; the human decides which become real tests.

### Spec amendments — referenced-but-undefined IDs

- Scan all payload string values for matches against `R-[A-Z]+-\d{3}`.
- Any ID matched in traces but absent from the spec ledger becomes one
  amendment candidate.
- Evidence count = number of events that referenced the ID.

Why this rule: trace producers cite requirement IDs. Drift between
what the running system thinks exists and what the ledger documents is
load-bearing — either the spec is missing or the producer is wrong.

## Thresholds, defaults, and the calibration loop

The thresholds (`MIN_BIGRAM_COUNT = 3`, `MIN_VALUE_LENGTH = 8`,
`MIN_EVENT_COUNT = 3`) are starting values, not science. The
calibration loop is:

1. Run the CLI weekly against the author's portfolio.
2. Read every candidate end-to-end.
3. Promote the ones that survive the read.
4. If the read rate (candidates read / candidates produced) drops
   below ~70%, raise the thresholds. If the promote rate (candidates
   promoted / candidates produced) drops below ~10%, raise them again
   or write a regret note explaining why the rule generated a bad
   candidate that nonetheless cleared the threshold.

The thresholds live in code, not config, so changing them lands in a
PR with a written rationale and a re-run of the dogfood corpus.

## What calibration means in v0.1

Calibration today is **rule-and-threshold tuning by inspection**, not
per-candidate confidence scoring. Concretely:

- Determinism is enforced by `test_determinism.py`: re-running the
  CLI on identical inputs produces byte-identical files. If a future
  change breaks that, the test fails before the PR merges.
- The committed `dreams/2026-W25/` directory is the calibration
  baseline. A regression in any rule shows up as a diff against the
  baseline in `test_end_to_end.py`. Updating the baseline is a
  deliberate act with a PR comment explaining what changed.
- Per-candidate confidence scoring is in the next-feature queue
  (`STATUS.md`). Once it lands, the calibration loop adds a fifth
  step: "if a high-confidence candidate is rejected, write a regret
  note."

## What this is not

- Not a model. There is no LLM in the v0.1 loop. Synthesis is
  arithmetic over the trace.
- Not auto-promotion. Calibration tunes the proposer, not the
  promoter. The promoter is always a human.
- Not a scoring contest. Candidates are not ranked against each other
  for "best". The rule's job is recall; the human's job is precision.

## What revisits this

This document is a living calibration record. The triggers that
should force a re-read and an edit:

- **A new dogfood corpus lands** under `dreams/YYYY-WNN/` and the
  candidate-totals shape (skill / memory / test / spec_amendment)
  diverges from the prior week's by more than 2x in either direction.
  That divergence either means the rules are mis-tuned or the trace
  population changed; either way the thresholds paragraph above
  needs a new entry.
- **A regret note is filed.** When a promoted candidate is walked
  back via `decisions/DEC-NNN-regret-*.md`, this file gets a new
  sub-bullet under the relevant rule explaining why the rule
  generated it and what (if anything) is changing in the threshold.
- **A new rule is added** to `src/dreamreplay/synthesize/`. The new
  rule gets its own "Why this rule" subsection here before merge.
- **The determinism contract changes.** Any edit to
  `test_determinism.py`, to the JSON serialisation, or to the
  candidate sort order updates the "What calibration means" section
  with the new contract and the date of the change.
- **A new release cuts.** The release PR includes a re-read of this
  document. If nothing has changed, the PR description says so
  explicitly — silence is not assent.
- **Quarterly cadence by default.** If none of the triggers above
  fire for a full quarter, the author re-reads this file anyway at
  quarter-end as part of the portfolio review and either updates it
  or commits a single-line confirmation that it still matches
  reality.

The intent of this section is that "the methodology is still right"
is a claim someone has actively re-validated within the last quarter,
not a default assumption that decays silently.

## References

- `specs/0002-runnable-cli/requirements.md` — the R-DRM-011 through
  R-DRM-021 contract.
- `specs/0002-design/` — contract-named copy of the same spec.
- `decisions/DEC-001-promotion-gate-rules.md` — what promotion looks
  like once the human is in the loop.
- `STATUS.md` — what is shipped, what is missing, what is queued.
- `data/ledger/run-*.jsonl` — the append-only record of every
  scoring / calibration run.
