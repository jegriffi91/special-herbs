"""Shared pytest configuration.

Subsystem-specific fixtures live in ``tests/<subsystem>/conftest.py``.
This file holds only the globally applicable hooks.
"""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-mark unmarked tests as ``unit``.

    Default behavior: any test without an explicit ``integration`` /
    ``tape`` / ``live`` / ``slow`` marker is treated as a unit test.
    Keeps the marker convention enforceable without forcing every test
    to declare ``@pytest.mark.unit``.
    """
    explicit_markers = {"integration", "tape", "live", "slow"}
    unit_marker = pytest.mark.unit
    for item in items:
        if not explicit_markers.intersection(m.name for m in item.iter_markers()):
            item.add_marker(unit_marker)
