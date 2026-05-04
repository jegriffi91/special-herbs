"""Test-time assertions over captured event streams.

Used by integration tests to verify that subsystems emit the expected
sequence of events. The substrate's hardest bug — "release pipeline
silently skipped PLV" — is caught by ``assert_event_sequence`` the way
a unit test alone never could (resilience doc §9.6).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def assert_event_sequence(
    captured: Sequence[dict[str, Any]],
    expected: Sequence[str],
) -> None:
    """Assert that ``expected`` event names appear in order within ``captured``.

    Other events may appear between the expected ones — this checks
    *order*, not adjacency. A strict-adjacency check is intentionally
    not provided: real pipelines emit additional events for
    instrumentation (heartbeats, progress) that callers should not
    have to enumerate.

    Raises ``AssertionError`` if the expected sequence is not satisfied.
    """
    expected_idx = 0
    for event in captured:
        if expected_idx >= len(expected):
            break
        if event.get("event") == expected[expected_idx]:
            expected_idx += 1

    if expected_idx < len(expected):
        actual = [e.get("event") for e in captured]
        missing = list(expected[expected_idx:])
        raise AssertionError(
            f"Event sequence not satisfied.\n"
            f"  Expected: {list(expected)}\n"
            f"  Stopped at expected[{expected_idx}] = {expected[expected_idx]!r}\n"
            f"  Missing: {missing}\n"
            f"  Actual events: {actual}"
        )
