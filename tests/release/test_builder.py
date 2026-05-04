"""Unit tests for the manifest builder."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from special_herbs.formats.hashing import sha256_file
from special_herbs.formats.manifest import ProvenanceTrace
from special_herbs.observability import assert_event_sequence, capture_events
from special_herbs.release.builder import build_manifest


def _provenance() -> ProvenanceTrace:
    return ProvenanceTrace(
        cycle_id="vol-1-cycle-3",
        training_data_hash="t" * 64,
        hyperparams_hash="h" * 64,
        base_model_sha="b" * 64,
        teacher_model="anthropic",
        teacher_model_version="claude-4.7-sonnet",
    )


def test_build_manifest_populates_required_fields(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"pretend-weights")

    manifest = build_manifest(
        artifact_id="vol-1-fda-briefing",
        version="v1.0.0",
        artifact_path=artifact,
        provenance=_provenance(),
        compatible_consumer_contracts=("kg-strategy-v1",),
    )

    assert manifest.artifact_id == "vol-1-fda-briefing"
    assert manifest.version == "v1.0.0"
    assert manifest.sha256 == sha256_file(artifact)
    assert manifest.base_model == "b" * 64
    assert manifest.training_data_hash == "t" * 64
    assert manifest.compatible_consumer_contracts == ("kg-strategy-v1",)
    assert manifest.signature_b64 == ""  # builder leaves unsigned


def test_build_manifest_uses_explicit_timestamp(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"pretend-weights")
    fixed = datetime(2026, 5, 3, 14, 30, 0, tzinfo=UTC)

    manifest = build_manifest(
        artifact_id="vol-1-fda-briefing",
        version="v1.0.0",
        artifact_path=artifact,
        provenance=_provenance(),
        compatible_consumer_contracts=(),
        released_at=fixed,
    )

    assert manifest.released_at == fixed


def test_build_manifest_emits_event(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"pretend-weights")

    with capture_events() as events:
        build_manifest(
            artifact_id="vol-1-fda-briefing",
            version="v1.0.0",
            artifact_path=artifact,
            provenance=_provenance(),
            compatible_consumer_contracts=(),
        )

    assert_event_sequence(events, ["release.manifest_built"])
    payload = events[0]
    assert payload["artifact_id"] == "vol-1-fda-briefing"
    assert payload["cycle_id"] == "vol-1-cycle-3"
    assert payload["artifact_sha256"] == sha256_file(artifact)


def test_build_manifest_missing_artifact_fails(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="artifact not found"):
        build_manifest(
            artifact_id="vol-1-fda-briefing",
            version="v1.0.0",
            artifact_path=tmp_path / "missing.bin",
            provenance=_provenance(),
            compatible_consumer_contracts=(),
        )
