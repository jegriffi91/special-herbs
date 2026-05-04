"""Tape metadata model — stdlib dataclass-based.

Captures the JSON schema documented in ``tests/fixtures/tape/README.md``.
Stdlib-only by design: ``tape`` is a leaf package per
``docs/design/resilience-and-subsystem-isolation.md`` §2 (no internal
deps; no third-party deps until Pydantic adoption in Phase 1+).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

TapeCategory = Literal["teacher", "ingest", "consumer"]
TAPE_VERSION = "1"


@dataclass(frozen=True)
class TapeSource:
    """Identifies what was recorded — provider, version, plus arbitrary extras."""

    kind: str
    version: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TapeInteraction:
    """One (request, response) pair captured during recording."""

    request: dict[str, Any]
    response: dict[str, Any]


@dataclass(frozen=True)
class TapeMetadata:
    """Top-level tape document — one per JSON file under ``tests/fixtures/tape/``."""

    category: TapeCategory
    recorded_at: datetime
    recorded_by: str
    source: TapeSource
    interactions: tuple[TapeInteraction, ...]
    tape_version: str = TAPE_VERSION

    def to_json(self) -> str:
        """Serialize to a JSON string suitable for committing to ``tests/fixtures/tape/``."""
        payload = asdict(self)
        payload["recorded_at"] = self.recorded_at.astimezone(UTC).isoformat()
        return json.dumps(payload, indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> TapeMetadata:
        """Parse a tape JSON string back into a TapeMetadata instance.

        Raises ``ValueError`` if required fields are missing or
        ``recorded_at`` is not a valid ISO-8601 timestamp.
        """
        data = json.loads(raw)
        required = {"category", "recorded_at", "recorded_by", "source", "interactions"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Tape JSON missing required fields: {sorted(missing)}")

        recorded_at = datetime.fromisoformat(data["recorded_at"].replace("Z", "+00:00"))
        if recorded_at.tzinfo is None:
            recorded_at = recorded_at.replace(tzinfo=UTC)

        source_data = data["source"]
        source = TapeSource(
            kind=source_data["kind"],
            version=source_data["version"],
            extra=source_data.get("extra", {}),
        )
        interactions = tuple(
            TapeInteraction(request=i["request"], response=i["response"])
            for i in data["interactions"]
        )
        return cls(
            tape_version=data.get("tape_version", TAPE_VERSION),
            category=data["category"],
            recorded_at=recorded_at,
            recorded_by=data["recorded_by"],
            source=source,
            interactions=interactions,
        )

    @classmethod
    def from_path(cls, path: Path) -> TapeMetadata:
        """Load a tape from its JSON file on disk."""
        return cls.from_json(path.read_text(encoding="utf-8"))
