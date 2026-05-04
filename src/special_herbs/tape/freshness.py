"""Tape freshness check — fail loud when tapes age out.

Tapes capture a real upstream contract at the moment of recording. When
that contract changes — frontier API ships a new model, a source
publishes a new template, a consumer changes its feature schema — the
tape no longer reflects reality and tests pass against stale fixtures
that hide regressions.

The 90-day window is the conservative default from
``docs/design/resilience-and-subsystem-isolation.md`` §10 ("tape
freshness").

Freshness is measured from ``recorded_at`` inside the tape JSON, NOT
filesystem mtime — git operations rewrite mtimes, which would silently
bypass the check.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from special_herbs.tape.metadata import TapeMetadata

DEFAULT_MAX_AGE = timedelta(days=90)


@dataclass(frozen=True)
class StaleTape:
    """A tape that has aged past the freshness window."""

    path: Path
    recorded_at: datetime
    age: timedelta


def discover_tapes(root: Path) -> list[Path]:
    """Return all tape JSON files under ``root``, sorted for determinism."""
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.json") if p.is_file())


def check_freshness(
    root: Path,
    *,
    max_age: timedelta = DEFAULT_MAX_AGE,
    now: datetime | None = None,
) -> list[StaleTape]:
    """Identify tapes whose ``recorded_at`` is older than ``max_age``.

    Returns an empty list if all tapes are fresh (or if no tapes exist
    yet — vacuously fresh). Raises ``ValueError`` only if a tape file
    is malformed; in that case the caller should treat it as a hard
    failure separate from staleness.

    ``now`` is injectable for deterministic testing.
    """
    if now is None:
        now = datetime.now(UTC)

    stale: list[StaleTape] = []
    for tape_path in discover_tapes(root):
        tape = TapeMetadata.from_path(tape_path)
        age = now - tape.recorded_at
        if age > max_age:
            stale.append(StaleTape(path=tape_path, recorded_at=tape.recorded_at, age=age))
    return stale
