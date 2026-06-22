from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable

from dreamreplay.models import Candidate, InternalEvent

MIN_VALUE_LENGTH = 8
MIN_EVENT_COUNT = 3
SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def _slugify(value: str, *, max_length: int = 40) -> str:
    slug = SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return slug[:max_length].rstrip("-") or "value"


def synthesize_memory(events: Iterable[InternalEvent]) -> list[Candidate]:
    """Collect payload string values of length >= MIN_VALUE_LENGTH that
    appear in MIN_EVENT_COUNT or more distinct events.
    """
    events_list = list(events)
    events_by_value: dict[str, set[int]] = defaultdict(set)
    for idx, ev in enumerate(events_list):
        for v in ev.payload_dict().values():
            if len(v) >= MIN_VALUE_LENGTH:
                events_by_value[v].add(idx)

    candidates: list[Candidate] = []
    for value, indices in events_by_value.items():
        count = len(indices)
        if count < MIN_EVENT_COUNT:
            continue
        slug = _slugify(value)
        notes = f"value appears in {count} distinct events"
        body = (
            f"Value referenced repeatedly: `{value}`.\n\n"
            "Promote into the long-running memory store if the fact is "
            "durably true across runs.\n"
        )
        candidates.append(
            Candidate(
                kind="memory",
                slug=slug,
                evidence_count=count,
                notes=notes,
                body=body,
            )
        )
    candidates.sort(key=lambda c: (-c.evidence_count, c.slug))
    return candidates
