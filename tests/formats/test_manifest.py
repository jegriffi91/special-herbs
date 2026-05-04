"""Unit tests for the release manifest schema."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from special_herbs.formats.manifest import (
    MANIFEST_VERSION,
    Manifest,
    ProvenanceTrace,
    manifest_to_dict,
)


def _sample_provenance() -> ProvenanceTrace:
    return ProvenanceTrace(
        cycle_id="vol-1-cycle-3",
        training_data_hash="t" * 64,
        hyperparams_hash="h" * 64,
        base_model_sha="b" * 64,
        teacher_model="anthropic",
        teacher_model_version="claude-4.7-sonnet",
    )


def _sample_manifest() -> Manifest:
    return Manifest(
        artifact_id="vol-1-fda-briefing",
        version="v1.0.0",
        sha256="a" * 64,
        released_at=datetime(2026, 5, 3, 12, 0, 0, tzinfo=UTC),
        base_model="b" * 64,
        training_data_hash="t" * 64,
        compatible_consumer_contracts=("kg-strategy-v1",),
        provenance=_sample_provenance(),
    )


def test_round_trip_through_json() -> None:
    original = _sample_manifest()
    parsed = Manifest.from_json(original.to_json())
    assert parsed == original


def test_unsigned_manifest_has_empty_signature() -> None:
    assert _sample_manifest().signature_b64 == ""


def test_with_signature_returns_new_manifest() -> None:
    original = _sample_manifest()
    signed = original.with_signature("abc-signature")
    assert original.signature_b64 == ""
    assert signed.signature_b64 == "abc-signature"
    # All other fields preserved
    assert signed.artifact_id == original.artifact_id
    assert signed.sha256 == original.sha256


def test_canonical_bytes_excludes_signature() -> None:
    """Signing input must be signature-free so verify can recompute it."""
    unsigned = _sample_manifest()
    signed = unsigned.with_signature("some-sig")
    assert unsigned.to_canonical_bytes() == signed.to_canonical_bytes()


def test_canonical_bytes_is_stable() -> None:
    a = _sample_manifest()
    b = _sample_manifest()
    assert a.to_canonical_bytes() == b.to_canonical_bytes()


def test_canonical_bytes_keys_are_sorted() -> None:
    """Decode the canonical bytes and verify the JSON keys are sorted."""
    raw = _sample_manifest().to_canonical_bytes()
    # We cannot directly assert key order from json.loads (dicts re-sort),
    # but we can confirm the byte form is what json.dumps(sort_keys=True) produces.
    payload = json.loads(raw)
    expected = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    assert raw == expected


def test_missing_required_field_raises() -> None:
    with pytest.raises(ValueError, match="missing required fields"):
        Manifest.from_json('{"artifact_id": "x"}')


def test_default_manifest_version() -> None:
    assert _sample_manifest().manifest_version == MANIFEST_VERSION


def test_manifest_to_dict_helper() -> None:
    manifest = _sample_manifest()
    d = manifest_to_dict(manifest)
    assert d["artifact_id"] == "vol-1-fda-briefing"
    assert d["compatible_consumer_contracts"] == ["kg-strategy-v1"]
    assert isinstance(d["released_at"], str)
