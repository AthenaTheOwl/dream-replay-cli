from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from dreamreplay.models import Candidate, InternalEvent, SpecRequirement

REQ_ID = re.compile(r"R-[A-Z]+-\d{3}")


def synthesize_amendments(
    events: Iterable[InternalEvent],
    spec_requirements: Iterable[SpecRequirement],
) -> list[Candidate]:
    """Scan payload values for R-*-NNN references; flag any ID present in
    traces but absent from the spec ledger.
    """
    known_ids = {r.id for r in spec_requirements}
    counts: Counter[str] = Counter()
    for ev in events:
        seen_in_event: set[str] = set()
        for v in ev.payload_dict().values():
            for match in REQ_ID.findall(v):
                seen_in_event.add(match)
        for ref_id in seen_in_event:
            if ref_id not in known_ids:
                counts[ref_id] += 1

    candidates: list[Candidate] = []
    for ref_id, count in counts.items():
        slug = f"add-{ref_id.lower()}"
        notes = f"ID referenced in {count} event(s); absent from spec ledger"
        body = (
            f"Trace payloads reference `{ref_id}` but the spec ledger "
            "does not define it. Either add the requirement to the "
            "appropriate spec or remove the reference from the trace "
            "producer.\n"
        )
        candidates.append(
            Candidate(
                kind="spec_amendment",
                slug=slug,
                evidence_count=count,
                notes=notes,
                body=body,
            )
        )
    candidates.sort(key=lambda c: (-c.evidence_count, c.slug))
    return candidates
