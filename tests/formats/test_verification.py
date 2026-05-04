"""Unit tests for manifest verification (SHA + signature)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from special_herbs.formats.hashing import sha256_file
from special_herbs.formats.manifest import Manifest, ProvenanceTrace
from special_herbs.formats.verification import (
    ShaMismatch,
    verify_artifact_sha,
    verify_signature,
)


def _build_manifest_for(artifact_path: Path) -> Manifest:
    return Manifest(
        artifact_id="vol-1-fda-briefing",
        version="v1.0.0",
        sha256=sha256_file(artifact_path),
        released_at=datetime(2026, 5, 3, tzinfo=UTC),
        base_model="b" * 64,
        training_data_hash="t" * 64,
        compatible_consumer_contracts=("kg-strategy-v1",),
        provenance=ProvenanceTrace(
            cycle_id="vol-1-cycle-3",
            training_data_hash="t" * 64,
            hyperparams_hash="h" * 64,
            base_model_sha="b" * 64,
        ),
    )


def test_verify_artifact_sha_match(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"trained-weights-pretend")
    manifest = _build_manifest_for(artifact)
    assert verify_artifact_sha(manifest, artifact) is None


def test_verify_artifact_sha_mismatch(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"trained-weights-pretend")
    manifest = _build_manifest_for(artifact)

    # Corrupt the artifact post-hoc — SHA must now mismatch.
    artifact.write_bytes(b"corrupted")
    result = verify_artifact_sha(manifest, artifact)
    assert isinstance(result, ShaMismatch)
    assert result.expected != result.actual
    assert result.file == artifact


def test_verify_signature_raises_pre_phase_1(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"x")
    manifest = _build_manifest_for(artifact).with_signature("placeholder")
    with pytest.raises(NotImplementedError, match="PyNaCl"):
        verify_signature(manifest, "fake-public-key")
