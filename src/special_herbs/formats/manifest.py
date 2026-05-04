"""Release manifest schema — substrate's artifact contract surface.

Encodes the eight required fields from ADR-0001 §1 plus the
provenance-trace fields derived from the observability event stream
per E.4. Stdlib-only (no Pydantic until Phase 1 dependency
authorization); see ``docs/design/special-herbs-formats-api.md`` for
the full design rationale.

Serialization is canonical JSON:

* keys sorted alphabetically;
* timestamps as RFC-3339 UTC strings ending in ``+00:00`` or ``Z``;
* no insignificant whitespace.

Canonical encoding matters because the signature in
``signature_b64`` is taken over this exact byte sequence — any
formatting drift between sign-time and verify-time is a SHA-divergence
that consumers will reject.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

MANIFEST_VERSION = "1"


@dataclass(frozen=True)
class ProvenanceTrace:
    """Provenance fields derived from the training-cycle event stream.

    Each value originates as a logged event payload field per §9 of the
    resilience doc. The release pipeline aggregates events from one
    cycle into a single :class:`ProvenanceTrace` before building the
    manifest.
    """

    cycle_id: str
    training_data_hash: str
    hyperparams_hash: str
    base_model_sha: str
    teacher_model: str | None = None
    teacher_model_version: str | None = None


@dataclass(frozen=True)
class Manifest:
    """Substrate release manifest.

    Required fields (ADR-0001 §1): ``artifact_id``, ``version``,
    ``sha256``, ``released_at``, ``base_model``, ``training_data_hash``,
    ``compatible_consumer_contracts``, ``signature_b64``.

    Convention beyond ADR-0001: ``provenance`` carries the
    cycle-tracing fields so a postmortem can resolve a manifest back to
    the exact training cycle that produced it.
    """

    artifact_id: str
    version: str
    sha256: str
    released_at: datetime
    base_model: str
    training_data_hash: str
    compatible_consumer_contracts: tuple[str, ...]
    provenance: ProvenanceTrace
    # Filled in by the signer step. Empty string when the manifest is
    # still being built; verifiers MUST refuse manifests with empty
    # signatures.
    signature_b64: str = ""
    manifest_version: str = MANIFEST_VERSION

    def to_json(self) -> str:
        """Serialize canonically — sorted keys, RFC-3339 UTC timestamp."""
        payload = asdict(self)
        payload["released_at"] = self.released_at.astimezone(UTC).isoformat()
        # tuple → list for JSON
        payload["compatible_consumer_contracts"] = list(self.compatible_consumer_contracts)
        return json.dumps(payload, indent=2, sort_keys=True)

    def to_canonical_bytes(self) -> bytes:
        """Canonical byte form used as the signing input.

        Crucially, the signature itself is excluded — signing computes
        the signature over the bytes of the *unsigned* manifest, then
        the signature is added to produce the final signed manifest.
        Verifiers strip the signature before re-hashing.
        """
        payload = asdict(self)
        payload["released_at"] = self.released_at.astimezone(UTC).isoformat()
        payload["compatible_consumer_contracts"] = list(self.compatible_consumer_contracts)
        payload.pop("signature_b64", None)
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def with_signature(self, signature_b64: str) -> Manifest:
        """Return a new manifest with the signature set."""
        return Manifest(
            artifact_id=self.artifact_id,
            version=self.version,
            sha256=self.sha256,
            released_at=self.released_at,
            base_model=self.base_model,
            training_data_hash=self.training_data_hash,
            compatible_consumer_contracts=self.compatible_consumer_contracts,
            provenance=self.provenance,
            signature_b64=signature_b64,
            manifest_version=self.manifest_version,
        )

    @classmethod
    def from_json(cls, raw: str) -> Manifest:
        """Parse a manifest JSON string back into a Manifest instance."""
        data = json.loads(raw)
        required = {
            "artifact_id",
            "version",
            "sha256",
            "released_at",
            "base_model",
            "training_data_hash",
            "compatible_consumer_contracts",
            "provenance",
        }
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Manifest JSON missing required fields: {sorted(missing)}")

        released_at = datetime.fromisoformat(data["released_at"].replace("Z", "+00:00"))
        if released_at.tzinfo is None:
            released_at = released_at.replace(tzinfo=UTC)

        provenance = ProvenanceTrace(**data["provenance"])

        return cls(
            artifact_id=data["artifact_id"],
            version=data["version"],
            sha256=data["sha256"],
            released_at=released_at,
            base_model=data["base_model"],
            training_data_hash=data["training_data_hash"],
            compatible_consumer_contracts=tuple(data["compatible_consumer_contracts"]),
            provenance=provenance,
            signature_b64=data.get("signature_b64", ""),
            manifest_version=data.get("manifest_version", MANIFEST_VERSION),
        )


def manifest_to_dict(manifest: Manifest) -> dict[str, Any]:
    """Helper for callers that need the manifest as a plain dict."""
    payload = asdict(manifest)
    payload["released_at"] = manifest.released_at.astimezone(UTC).isoformat()
    payload["compatible_consumer_contracts"] = list(manifest.compatible_consumer_contracts)
    return payload


__all__ = ["MANIFEST_VERSION", "Manifest", "ProvenanceTrace", "manifest_to_dict"]
