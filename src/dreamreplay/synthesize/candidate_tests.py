from __future__ import annotations

import re
from typing import Iterable

from dreamreplay.models import Candidate, InternalEvent

SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def _slugify(value: str, *, max_length: int = 40) -> str:
    slug = SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return slug[:max_length].rstrip("-") or "unknown"


def synthesize_tests(events: Iterable[InternalEvent]) -> list[Candidate]:
    """Every `kind == "failure"` event becomes one test candidate.

    Slug is derived from actor plus a slug of the payload values so it
    is human-readable and re-creatable by inspection.
    """
    candidates: list[Candidate] = []
    for ev in events:
        if ev.kind != "failure":
            continue
        payload = ev.payload_dict()
        payload_blob = " ".join(payload[k] for k in sorted(payload))
        payload_tail = _slugify(payload_blob, max_length=32) or "no-payload"
        slug = f"failure-{ev.actor}-{payload_tail}"
        notes = f"failure event from actor `{ev.actor}`"
        rendered_payload = ", ".join(
            f"`{k}` = `{v}`" for k, v in sorted(payload.items())
        ) or "(no payload)"
        body = (
            f"Failure observed for actor `{ev.actor}` with "
            f"payload: {rendered_payload}.\n\n"
            "Promote into the eval suite as a regression test if the "
            "failure shape is reproducible.\n"
        )
        candidates.append(
            Candidate(
                kind="test",
                slug=slug,
                evidence_count=1,
                notes=notes,
                body=body,
            )
        )
    candidates.sort(key=lambda c: c.slug)
    return candidates
