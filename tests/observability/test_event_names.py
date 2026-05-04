"""Verify the event-name registry follows the namespace convention."""

from __future__ import annotations

from special_herbs.observability import event_names


def _public_constants() -> list[tuple[str, str]]:
    return [
        (name, value)
        for name in dir(event_names)
        if not name.startswith("_") and isinstance((value := getattr(event_names, name)), str)
    ]


def test_no_dots_in_event_constants() -> None:
    """Constants are bare event names; the subsystem prefix is added by EventLogger."""
    offenders = [(name, value) for name, value in _public_constants() if "." in value]
    assert not offenders, (
        f"Event constants must not contain '.': {offenders}. "
        "The subsystem prefix is added by EventLogger.emit()."
    )


def test_constants_are_snake_case() -> None:
    offenders = [
        (name, value)
        for name, value in _public_constants()
        if not value.replace("_", "").isalnum() or not value.islower()
    ]
    assert not offenders, f"Event constants must be lowercase snake_case: {offenders}"


def test_constants_grouped_by_subsystem_prefix() -> None:
    """Each constant's name prefix indicates its target subsystem.

    Convention: the constant ``TRAINING_CYCLE_STARTED`` is for the
    ``training`` subsystem; ``RELEASE_PUBLISHED`` for ``release``;
    etc. This test enforces the naming so future contributors can
    see at a glance which subsystem owns an event.
    """
    expected_prefixes = {"INGEST", "TRAINING", "EVAL", "RELEASE"}
    for name, _value in _public_constants():
        prefix = name.split("_")[0]
        assert prefix in expected_prefixes, (
            f"Constant {name!r} doesn't start with a known subsystem prefix "
            f"(expected one of {sorted(expected_prefixes)})"
        )
