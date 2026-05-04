"""Observability — structured JSON event logging.

The substrate's logs are not just operator-facing telemetry. Per
``docs/design/resilience-and-subsystem-isolation.md`` §9 they are also:

1. **Audit trail** — every release, sign event, PLV run produces log
   entries that volume postmortems link to.
2. **Test fixtures** — tests assert specific events fired in specific
   order via :func:`capture_events` + :func:`assert_event_sequence`.
3. **Provenance ground truth** — manifest fields like
   ``training_data_hash`` and ``hyperparams_hash`` are derived from
   logged events (binding implemented in ``release/`` per E.5).

Leaf package — no internal substrate dependencies. Subsystems import
:class:`EventLogger` for emitting; tests import :func:`capture_events`
and :func:`assert_event_sequence` for verification.
"""

from special_herbs.observability.assertions import assert_event_sequence
from special_herbs.observability.events import (
    EventLogger,
    capture_events,
    configure_default_handler,
)

__all__ = [
    "EventLogger",
    "assert_event_sequence",
    "capture_events",
    "configure_default_handler",
]
