"""Unit tests for the tape metadata model."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from special_herbs.tape.metadata import (
    TAPE_VERSION,
    TapeInteraction,
    TapeMetadata,
    TapeSource,
)


def _sample_metadata() -> TapeMetadata:
    return TapeMetadata(
        category="teacher",
        recorded_at=datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC),
        recorded_by="operator",
        source=TapeSource(kind="anthropic", version="claude-4.7-sonnet"),
        interactions=(
            TapeInteraction(
                request={"model": "claude-4.7-sonnet", "messages": []},
                response={"id": "msg_test", "content": "ok"},
            ),
        ),
    )


def test_round_trip_through_json() -> None:
    original = _sample_metadata()
    parsed = TapeMetadata.from_json(original.to_json())
    assert parsed == original


def test_default_tape_version() -> None:
    assert _sample_metadata().tape_version == TAPE_VERSION


def test_missing_required_field_raises() -> None:
    with pytest.raises(ValueError, match="missing required fields"):
        TapeMetadata.from_json('{"category": "teacher"}')


def test_naive_datetime_normalized_to_utc() -> None:
    raw = (
        '{"category": "teacher", "recorded_at": "2026-05-01T12:00:00", '
        '"recorded_by": "operator", '
        '"source": {"kind": "anthropic", "version": "claude-4.7-sonnet"}, '
        '"interactions": []}'
    )
    parsed = TapeMetadata.from_json(raw)
    assert parsed.recorded_at.tzinfo is UTC
