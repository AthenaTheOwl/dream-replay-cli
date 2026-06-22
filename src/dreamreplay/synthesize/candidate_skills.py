from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

from dreamreplay.models import Candidate, InternalEvent

MIN_BIGRAM_COUNT = 3


def synthesize_skills(events: Iterable[InternalEvent]) -> list[Candidate]:
    """Group events by actor, look at bigrams of `kind`, propose any bigram
    that occurs MIN_BIGRAM_COUNT or more times across the full corpus.
    """
    sequences_by_actor: dict[str, list[str]] = defaultdict(list)
    for ev in events:
        sequences_by_actor[ev.actor].append(ev.kind)

    bigram_counts: Counter[tuple[str, str]] = Counter()
    actors_per_bigram: dict[tuple[str, str], set[str]] = defaultdict(set)
    for actor, kinds in sequences_by_actor.items():
        for a, b in zip(kinds, kinds[1:]):
            bigram_counts[(a, b)] += 1
            actors_per_bigram[(a, b)].add(actor)

    candidates: list[Candidate] = []
    for (a, b), count in bigram_counts.items():
        if count < MIN_BIGRAM_COUNT:
            continue
        slug = f"{a}-then-{b}"
        n_actors = len(actors_per_bigram[(a, b)])
        notes = f"kind sequence repeated by {n_actors} distinct actor(s)"
        body = (
            f"Bigram observed: `{a}` then `{b}`.\n\n"
            "Promote into a named skill if the underlying sequence is "
            "the same behavior every time. Otherwise discard.\n"
        )
        candidates.append(
            Candidate(
                kind="skill",
                slug=slug,
                evidence_count=count,
                notes=notes,
                body=body,
            )
        )
    candidates.sort(key=lambda c: (-c.evidence_count, c.slug))
    return candidates
