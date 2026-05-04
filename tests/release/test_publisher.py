"""Unit tests for the publisher."""

from __future__ import annotations

from pathlib import Path

import pytest

from special_herbs.formats.manifest import Manifest
from special_herbs.observability import assert_event_sequence, capture_events
from special_herbs.release.publisher import (
    PublishedRelease,
    ReleaseAlreadyExistsError,
    publish,
)
from special_herbs.release.signer import sign_with_stub
from tests.release._fixtures import sample_manifest


def _signed_manifest() -> Manifest:
    return sign_with_stub(sample_manifest())


def test_publish_writes_manifest_and_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"weights")
    release_root = tmp_path / "releases"

    result = publish(
        manifest=_signed_manifest(),
        artifact_path=artifact,
        release_root=release_root,
    )

    assert isinstance(result, PublishedRelease)
    assert result.artifact_path.exists()
    assert result.manifest_path.exists()
    assert result.artifact_path.name == "adapter.safetensors"
    assert result.manifest_path.name == "manifest.json"
    assert result.artifact_path.read_bytes() == b"weights"
    # Manifest content round-trips
    Manifest.from_json(result.manifest_path.read_text())


def test_publish_layout_is_artifact_id_then_version(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"weights")
    release_root = tmp_path / "releases"

    result = publish(
        manifest=_signed_manifest(),
        artifact_path=artifact,
        release_root=release_root,
    )
    expected = release_root / "vol-1-fda-briefing" / "v1.0.0"
    assert result.artifact_path.parent == expected


def test_publish_refuses_unsigned_manifest(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"weights")
    with pytest.raises(ValueError, match="unsigned manifest"):
        publish(
            manifest=sample_manifest(),  # unsigned
            artifact_path=artifact,
            release_root=tmp_path / "releases",
        )


def test_publish_refuses_to_overwrite(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"weights")
    release_root = tmp_path / "releases"

    publish(
        manifest=_signed_manifest(),
        artifact_path=artifact,
        release_root=release_root,
    )
    with pytest.raises(ReleaseAlreadyExistsError, match="immutable"):
        publish(
            manifest=_signed_manifest(),
            artifact_path=artifact,
            release_root=release_root,
        )


def test_publish_emits_event(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter.safetensors"
    artifact.write_bytes(b"weights")
    release_root = tmp_path / "releases"

    with capture_events() as events:
        publish(
            manifest=_signed_manifest(),
            artifact_path=artifact,
            release_root=release_root,
        )

    assert_event_sequence(events, ["release.published"])
    payload = events[-1]
    assert payload["artifact_id"] == "vol-1-fda-briefing"
    assert payload["version"] == "v1.0.0"
