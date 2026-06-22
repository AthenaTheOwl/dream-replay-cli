from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InternalEvent:
    timestamp: str
    kind: str
    actor: str
    payload: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, d: dict) -> "InternalEvent":
        raw_payload = d.get("payload", {}) or {}
        items = tuple(
            sorted((str(k), str(v)) for k, v in raw_payload.items())
        )
        return cls(
            timestamp=str(d.get("timestamp", "")),
            kind=str(d.get("kind", "")),
            actor=str(d.get("actor", "")),
            payload=items,
        )

    def payload_dict(self) -> dict[str, str]:
        return dict(self.payload)


@dataclass(frozen=True)
class SpecRequirement:
    id: str
    spec_dir: str
    title: str


@dataclass(frozen=True)
class DecisionRecord:
    id: str
    title: str
    body: str


@dataclass(frozen=True)
class Candidate:
    kind: str
    slug: str
    evidence_count: int
    notes: str
    body: str
