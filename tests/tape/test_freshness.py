"""Unit tests for the tape freshness checker."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from special_herbs.tape.freshness import check_freshness, discover_tapes
from special_herbs.tape.metadata import TapeInteraction, TapeMetadata, TapeSource


def _write_tape(path: Path, recorded_at: datetime) -> None:
    tape = TapeMetadata(
        category="teacher",
        recorded_at=recorded_at,
        recorded_by="operator",
        source=TapeSource(kind="anthropic", version="claude-4.7-sonnet"),
        interactions=(
            TapeInteraction(request={"model": "claude-4.7-sonnet"}, response={"ok": True}),
        ),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tape.to_json(), encoding="utf-8")


def test_empty_directory_is_vacuously_fresh(tmp_path: Path) -> None:
    assert check_freshness(tmp_path) == []


def test_missing_directory_is_vacuously_fresh(tmp_path: Path) -> None:
    assert check_freshness(tmp_path / "does-not-exist") == []


def test_fresh_tape_passes(tmp_path: Path) -> None:
    now = datetime(2026, 5, 3, tzinfo=UTC)
    _write_tape(tmp_path / "teacher" / "fresh.json", now - timedelta(days=10))
    assert check_freshness(tmp_path, now=now) == []


def test_stale_tape_detected(tmp_path: Path) -> None:
    now = datetime(2026, 5, 3, tzinfo=UTC)
    _write_tape(tmp_path / "teacher" / "stale.json", now - timedelta(days=120))
    stale = check_freshness(tmp_path, now=now)
    assert len(stale) == 1
    assert stale[0].path.name == "stale.json"
    assert stale[0].age.days == 120


def test_only_stale_tapes_returned(tmp_path: Path) -> None:
    now = datetime(2026, 5, 3, tzinfo=UTC)
    _write_tape(tmp_path / "teacher" / "fresh.json", now - timedelta(days=30))
    _write_tape(tmp_path / "teacher" / "stale.json", now - timedelta(days=120))
    _write_tape(tmp_path / "ingest" / "stale_too.json", now - timedelta(days=200))
    stale_paths = {s.path.name for s in check_freshness(tmp_path, now=now)}
    assert stale_paths == {"stale.json", "stale_too.json"}


def test_discover_tapes_sorted(tmp_path: Path) -> None:
    """discover_tapes returns paths in deterministic full-path order."""
    now = datetime(2026, 5, 3, tzinfo=UTC)
    _write_tape(tmp_path / "teacher" / "b.json", now)
    _write_tape(tmp_path / "teacher" / "a.json", now)
    _write_tape(tmp_path / "ingest" / "c.json", now)
    paths = discover_tapes(tmp_path)
    # Sort key is the full path (lexicographic), not the basename.
    # ingest/c.json sorts before teacher/a.json because "i" < "t".
    assert paths == sorted(paths)
    assert [p.relative_to(tmp_path).as_posix() for p in paths] == [
        "ingest/c.json",
        "teacher/a.json",
        "teacher/b.json",
    ]
