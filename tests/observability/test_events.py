"""Unit tests for EventLogger + capture_events + context propagation."""

from __future__ import annotations

import json

import pytest

from special_herbs.observability import EventLogger, capture_events


def test_emit_produces_required_fields() -> None:
    log = EventLogger("training")
    with capture_events() as events:
        log.emit("cycle_started", cycle_id="vol-1-cycle-3")

    assert len(events) == 1
    e = events[0]
    assert e["subsystem"] == "training"
    assert e["event"] == "training.cycle_started"
    assert e["cycle_id"] == "vol-1-cycle-3"
    ts = e.get("ts", "")
    assert ts.endswith("+00:00") or ts.endswith("Z"), ts


def test_subsystem_must_be_bare_identifier() -> None:
    with pytest.raises(ValueError, match="must be a non-empty bare identifier"):
        EventLogger("")
    with pytest.raises(ValueError, match="must be a non-empty bare identifier"):
        EventLogger("training.cycle")


def test_event_name_must_not_contain_dot() -> None:
    log = EventLogger("training")
    with pytest.raises(ValueError, match="must not contain '\\.'"):
        log.emit("cycle.started")


def test_event_name_must_not_be_empty() -> None:
    log = EventLogger("training")
    with pytest.raises(ValueError, match="must not be empty"):
        log.emit("")


def test_context_propagates_to_emitted_events() -> None:
    log = EventLogger("training")
    with capture_events() as events:
        with log.context(cycle_id="vol-1-cycle-3"):
            log.emit("cycle_started", training_data_hash="abc")
            log.emit("lora_step", step=42, loss=0.123)

    assert all(e["cycle_id"] == "vol-1-cycle-3" for e in events)
    assert events[0]["training_data_hash"] == "abc"
    assert events[1]["step"] == 42


def test_nested_context_merges_with_outer() -> None:
    log = EventLogger("release")
    with capture_events() as events:
        with log.context(cycle_id="vol-1-cycle-3"):
            with log.context(plv_step="signature_verify"):
                log.emit("plv_step_passed")

    assert events[0]["cycle_id"] == "vol-1-cycle-3"
    assert events[0]["plv_step"] == "signature_verify"


def test_emit_field_overrides_context_field() -> None:
    """Per-call fields take precedence over context — explicit beats implicit."""
    log = EventLogger("training")
    with capture_events() as events:
        with log.context(cycle_id="outer"):
            log.emit("cycle_started", cycle_id="override")

    assert events[0]["cycle_id"] == "override"


def test_context_fields_cleared_after_block() -> None:
    log = EventLogger("training")
    with capture_events() as events:
        with log.context(cycle_id="vol-1-cycle-3"):
            log.emit("cycle_started")
        log.emit("ambient")

    assert events[0]["cycle_id"] == "vol-1-cycle-3"
    assert "cycle_id" not in events[1]


def test_capture_events_isolates_separate_blocks() -> None:
    log = EventLogger("training")
    with capture_events() as events_a:
        log.emit("first")
    with capture_events() as events_b:
        log.emit("second")

    assert len(events_a) == 1
    assert events_a[0]["event"] == "training.first"
    assert len(events_b) == 1
    assert events_b[0]["event"] == "training.second"


def test_emitted_payload_is_json_serializable() -> None:
    log = EventLogger("ingest")
    with capture_events() as events:
        log.emit("pdf_downloaded", url="https://example.test/x.pdf", size_bytes=12345)

    encoded = json.dumps(events[0])
    decoded = json.loads(encoded)
    assert decoded == events[0]


def test_configure_default_handler_writes_json_lines_to_stream() -> None:
    """Production output path: handler emits one JSON line per event."""
    import io

    from special_herbs.observability import configure_default_handler

    buf = io.StringIO()
    configure_default_handler(stream=buf)
    try:
        log = EventLogger("training")
        log.emit("cycle_started", cycle_id="vol-1-cycle-3")
        log.emit("cycle_completed", final_loss=0.087)

        lines = [line for line in buf.getvalue().splitlines() if line]
        assert len(lines) == 2
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        assert first["event"] == "training.cycle_started"
        assert second["event"] == "training.cycle_completed"
        assert second["final_loss"] == 0.087
    finally:
        # Reset to avoid handler accumulation across tests
        configure_default_handler(stream=io.StringIO())


def test_configure_default_handler_is_idempotent() -> None:
    """Repeat calls replace the previous default handler, never stack them."""
    import io

    from special_herbs.observability import configure_default_handler

    first_buf = io.StringIO()
    second_buf = io.StringIO()
    configure_default_handler(stream=first_buf)
    configure_default_handler(stream=second_buf)
    try:
        log = EventLogger("training")
        log.emit("cycle_started")

        # Only the second buffer should receive output.
        assert first_buf.getvalue() == ""
        assert "training.cycle_started" in second_buf.getvalue()
    finally:
        configure_default_handler(stream=io.StringIO())
