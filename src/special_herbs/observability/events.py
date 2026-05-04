"""Structured JSON event emission and capture.

Wire-format and field semantics are documented in §9 of
``docs/design/resilience-and-subsystem-isolation.md``. Every emitted
event is a single-line JSON object with required fields ``ts``,
``subsystem``, and ``event`` (full ``<subsystem>.<event>`` form).

Why stdlib ``logging`` underneath:

* Free integration with pytest's ``caplog`` if needed.
* :func:`capture_events` works by attaching a handler — same mechanism
  pytest already provides for stdlib loggers.
* Production deployments wire output via :func:`configure_default_handler`
  at startup; subsystem code never touches handler configuration.
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import IO, Any

LOGGER_NAME = "special_herbs.observability"

# Substrate-internal logger. Subsystems never call ``logging.getLogger``
# directly for event emission — they go through :class:`EventLogger`.
_logger = logging.getLogger(LOGGER_NAME)
_logger.propagate = False

# Per-task / per-thread event context. Values added via
# ``EventLogger.context()`` propagate to every event emitted inside the
# block. Typical use: bind ``cycle_id`` once and let it flow through
# all events from that training cycle.
_event_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "_event_context",
    default={},
)


class _JsonEventFormatter(logging.Formatter):
    """Serializes the structured payload attached to each event record."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] | None = getattr(record, "event_payload", None)
        if payload is None:
            return super().format(record)
        return json.dumps(payload, separators=(",", ":"))


class EventLogger:
    """Subsystem-scoped structured event logger.

    Each subsystem instantiates one ``EventLogger`` and calls
    :meth:`emit` to log events. The subsystem name becomes the prefix
    for every event's full name (``<subsystem>.<event>``).

    Example::

        log = EventLogger("training")
        with log.context(cycle_id="vol-1-cycle-3"):
            log.emit("cycle_started", training_data_hash="abc")
            log.emit("cycle_completed", final_loss=0.087)

    Both events get ``cycle_id="vol-1-cycle-3"`` automatically.
    """

    def __init__(self, subsystem: str) -> None:
        if not subsystem or "." in subsystem:
            raise ValueError(
                f"subsystem name {subsystem!r} must be a non-empty bare identifier " f"(no '.')"
            )
        self.subsystem = subsystem

    def emit(self, event: str, **fields: Any) -> None:
        """Emit a structured event under this logger's subsystem namespace."""
        if "." in event:
            raise ValueError(
                f"event name {event!r} must not contain '.'; "
                f"the subsystem prefix '{self.subsystem}' is added automatically"
            )
        if not event:
            raise ValueError("event name must not be empty")

        # Order matters: timestamp first, then required fields, then
        # context (auto-propagated), then call-site fields. Call-site
        # fields override context on key collision so a per-event
        # override (e.g., ``cycle_id`` for a cleanup hook) wins.
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "subsystem": self.subsystem,
            "event": f"{self.subsystem}.{event}",
            **_event_context.get(),
            **fields,
        }

        record = _logger.makeRecord(
            name=LOGGER_NAME,
            level=logging.INFO,
            fn="",
            lno=0,
            msg="",
            args=(),
            exc_info=None,
        )
        record.event_payload = payload  # type: ignore[attr-defined]
        _logger.handle(record)

    @contextmanager
    def context(self, **fields: Any) -> Iterator[None]:
        """Bind context fields that auto-propagate to events in the block.

        Nested ``context()`` blocks merge — inner fields override outer
        ones on key collision. ContextVar-based, so it's safe across
        threads and asyncio tasks.
        """
        prev = _event_context.get()
        token = _event_context.set({**prev, **fields})
        try:
            yield
        finally:
            _event_context.reset(token)


@contextmanager
def capture_events() -> Iterator[list[dict[str, Any]]]:
    """Capture structured events emitted during the block.

    Returns a mutable list that the caller can inspect after the block
    exits. Captures everything emitted via any :class:`EventLogger` —
    no need to know which subsystems produced events.

    Example::

        with capture_events() as events:
            run_release_pipeline(config)
        assert_event_sequence(events, [
            "release.manifest_built",
            "release.signature_generated",
            "release.published",
        ])
    """
    captured: list[dict[str, Any]] = []

    class _Handler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            payload = getattr(record, "event_payload", None)
            if payload is not None:
                captured.append(payload)

    handler = _Handler()
    _logger.addHandler(handler)
    try:
        yield captured
    finally:
        _logger.removeHandler(handler)


def configure_default_handler(stream: IO[str] | None = None) -> None:
    """Install a JSON-line StreamHandler on the observability logger.

    Idempotent — calling multiple times does not stack handlers; the
    previously-installed default handler is replaced.

    Production typically calls this once at startup with a file stream
    (``open("logs/training-cycle-X.jsonl", "a")``); CLI tools may pass
    ``sys.stderr`` (the default) for terminal output.
    """
    target = stream if stream is not None else sys.stderr

    # Remove any handler we previously installed so repeat calls don't
    # double-emit. Other handlers (e.g., pytest's caplog) are left
    # alone.
    for existing in list(_logger.handlers):
        if getattr(existing, "_special_herbs_default", False):
            _logger.removeHandler(existing)

    handler = logging.StreamHandler(target)
    handler.setFormatter(_JsonEventFormatter())
    handler._special_herbs_default = True  # type: ignore[attr-defined]
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)
