"""R-DRM-015 — rule-based synthesis."""

from __future__ import annotations

from pathlib import Path

from dreamreplay.ingest.spec_ledger import parse_spec_ledger
from dreamreplay.ingest.trace_loader import load_events
from dreamreplay.models import InternalEvent
from dreamreplay.synthesize.candidate_memory import synthesize_memory
from dreamreplay.synthesize.candidate_skills import synthesize_skills
from dreamreplay.synthesize.candidate_spec_amendments import (
    synthesize_amendments,
)
from dreamreplay.synthesize.candidate_tests import synthesize_tests


def test_skills_finds_repeated_bigrams(traces_dir: Path) -> None:
    events = load_events(traces_dir)
    skills = synthesize_skills(events)
    slugs = [s.slug for s in skills]
    assert slugs == ["thought-then-action", "action-then-observation"]
    # the first candidate has the higher count, confirming
    # (-evidence_count, slug) sorting
    assert skills[0].evidence_count >= skills[1].evidence_count


def test_skills_bigram_count_threshold_boundary() -> None:
    # actor-hi emits x,y three times -> ("x","y") count 3 (at threshold).
    # actor-lo emits p,q twice -> ("p","q") count 2 (below threshold).
    # Pins MIN_BIGRAM_COUNT == 3: dropping it to 2 would emit p-then-q.
    def ev(actor: str, kind: str) -> InternalEvent:
        return InternalEvent(timestamp="t", kind=kind, actor=actor)

    events = [
        ev("actor-hi", "x"),
        ev("actor-hi", "y"),
        ev("actor-hi", "x"),
        ev("actor-hi", "y"),
        ev("actor-hi", "x"),
        ev("actor-hi", "y"),
        ev("actor-lo", "p"),
        ev("actor-lo", "q"),
        ev("actor-lo", "p"),
        ev("actor-lo", "q"),
    ]
    skills = synthesize_skills(events)
    assert [s.slug for s in skills] == ["x-then-y"]
    assert skills[0].evidence_count == 3


def test_memory_finds_repeated_values(traces_dir: Path) -> None:
    events = load_events(traces_dir)
    mem = synthesize_memory(events)
    slugs = {m.slug for m in mem}
    assert any("calibration-pass" in s for s in slugs)
    assert any("audit-log-write" in s for s in slugs)


def test_tests_one_per_failure_event(traces_dir: Path) -> None:
    events = load_events(traces_dir)
    tests = synthesize_tests(events)
    assert len(tests) == 2
    actors = {t.slug.split("-")[1] + "-" + t.slug.split("-")[2] for t in tests}
    assert actors == {"agent-gamma", "agent-delta"}


def test_amendments_flags_missing_ids(traces_dir: Path, spec_dir: Path) -> None:
    events = load_events(traces_dir)
    specs = parse_spec_ledger(spec_dir)
    amend = synthesize_amendments(events, specs)
    slugs = [a.slug for a in amend]
    assert slugs == ["add-r-drm-999"]
    assert amend[0].evidence_count == 2


def test_rules_are_pure(traces_dir: Path) -> None:
    events = load_events(traces_dir)
    a = synthesize_skills(events)
    b = synthesize_skills(events)
    assert a == b
