"""Manifest builder — assembles release manifests from training-cycle outputs.

Inputs:

* The trained artifact file (e.g., a LoRA safetensors blob).
* The provenance trace derived from the cycle's event log.
* Static metadata (artifact_id, version, compatible_consumer_contracts).

Outputs:

* An unsigned :class:`~special_herbs.formats.manifest.Manifest`.

The signing step is a separate stage handled by ``release.signer``;
the builder produces a manifest with empty ``signature_b64`` and
trusts the signer to populate it.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from special_herbs.formats.hashing import sha256_file
from special_herbs.formats.manifest import Manifest, ProvenanceTrace
from special_herbs.observability import EventLogger
from special_herbs.observability.event_names import RELEASE_MANIFEST_BUILT

_log = EventLogger("release")


def build_manifest(
    *,
    artifact_id: str,
    version: str,
    artifact_path: Path,
    provenance: ProvenanceTrace,
    compatible_consumer_contracts: tuple[str, ...],
    released_at: datetime | None = None,
) -> Manifest:
    """Assemble an unsigned manifest from training-cycle outputs.

    Emits ``release.manifest_built`` carrying the artifact SHA so
    postmortems can trace any consumer-side load failure back to the
    exact cycle that produced it.
    """
    if not artifact_path.is_file():
        raise FileNotFoundError(f"artifact not found at {artifact_path}")

    artifact_sha = sha256_file(artifact_path)
    timestamp = (released_at or datetime.now(UTC)).astimezone(UTC)

    manifest = Manifest(
        artifact_id=artifact_id,
        version=version,
        sha256=artifact_sha,
        released_at=timestamp,
        base_model=provenance.base_model_sha,
        training_data_hash=provenance.training_data_hash,
        compatible_consumer_contracts=compatible_consumer_contracts,
        provenance=provenance,
    )

    _log.emit(
        RELEASE_MANIFEST_BUILT,
        artifact_id=artifact_id,
        version=version,
        artifact_sha256=artifact_sha,
        cycle_id=provenance.cycle_id,
    )
    return manifest
