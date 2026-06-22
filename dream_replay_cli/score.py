"""Candidate scoring helpers.

v0.1 scoring is intentionally arithmetic: a candidate's score is its
``evidence_count``, rule-namespaced so cross-rule comparison is not
implied. Per-candidate confidence scoring (probabilistic) is queued in
``STATUS.md`` and not implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from dreamreplay.models import Candidate


@dataclass(frozen=True)
class ScoredCandidate:
    kind: str
    slug: str
    evidence_count: int
    score: int

    @property
    def namespaced_score(self) -> str:
        return f"{self.kind}:{self.score}"


def score_candidate(candidate: Candidate) -> ScoredCandidate:
    """Return the candidate paired with its v0.1 evidence-count score."""
    return ScoredCandidate(
        kind=candidate.kind,
        slug=candidate.slug,
        evidence_count=candidate.evidence_count,
        score=candidate.evidence_count,
    )


def score_all(candidates: Iterable[Candidate]) -> list[ScoredCandidate]:
    """Score every candidate, preserving the input ordering."""
    return [score_candidate(c) for c in candidates]


def totals_by_kind(scored: Iterable[ScoredCandidate]) -> dict[str, int]:
    """Sum scores per candidate kind. Used by the ledger row writer."""
    totals: dict[str, int] = {}
    for s in scored:
        totals[s.kind] = totals.get(s.kind, 0) + s.score
    return totals
