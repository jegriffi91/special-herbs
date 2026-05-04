"""Shared test fixtures for release-pipeline unit tests.

Underscore-prefixed so pytest doesn't try to collect it as a test module.
"""

from __future__ import annotations

from datetime import UTC, datetime

from special_herbs.formats.manifest import Manifest, ProvenanceTrace


def sample_provenance() -> ProvenanceTrace:
    return ProvenanceTrace(
        cycle_id="vol-1-cycle-3",
        training_data_hash="t" * 64,
        hyperparams_hash="h" * 64,
        base_model_sha="b" * 64,
        teacher_model="anthropic",
        teacher_model_version="claude-4.7-sonnet",
    )


def sample_manifest() -> Manifest:
    return Manifest(
        artifact_id="vol-1-fda-briefing",
        version="v1.0.0",
        sha256="a" * 64,
        released_at=datetime(2026, 5, 3, 12, 0, 0, tzinfo=UTC),
        base_model="b" * 64,
        training_data_hash="t" * 64,
        compatible_consumer_contracts=("kg-strategy-v1",),
        provenance=sample_provenance(),
    )
