"""Unit tests for assert_event_sequence."""

from __future__ import annotations

import pytest

from special_herbs.observability import assert_event_sequence


def _evt(name: str) -> dict[str, str]:
    return {"event": name}


def test_exact_sequence_passes() -> None:
    captured = [_evt("a"), _evt("b"), _evt("c")]
    assert_event_sequence(captured, ["a", "b", "c"])


def test_extra_events_between_expected_ones_pass() -> None:
    captured = [_evt("a"), _evt("noise"), _evt("b"), _evt("noise"), _evt("c")]
    assert_event_sequence(captured, ["a", "b", "c"])


def test_missing_event_fails() -> None:
    captured = [_evt("a"), _evt("c")]
    # Once we fail to find 'b', everything after 'b' in expected is
    # reported as missing too — the assertion can't tell whether 'c'
    # was meant to follow the missing 'b' or stand alone.
    with pytest.raises(AssertionError, match=r"Missing: \['b', 'c'\]"):
        assert_event_sequence(captured, ["a", "b", "c"])


def test_out_of_order_fails() -> None:
    captured = [_evt("b"), _evt("a"), _evt("c")]
    with pytest.raises(AssertionError, match="Missing"):
        assert_event_sequence(captured, ["a", "b", "c"])


def test_empty_expected_passes_against_anything() -> None:
    assert_event_sequence([_evt("anything")], [])
    assert_event_sequence([], [])


def test_empty_captured_with_nonempty_expected_fails() -> None:
    with pytest.raises(AssertionError, match="Missing: \\['a'\\]"):
        assert_event_sequence([], ["a"])
