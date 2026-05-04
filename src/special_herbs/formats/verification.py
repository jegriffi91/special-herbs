"""Manifest verification — SHA + signature checks.

SHA-256 verification is fully implemented (stdlib hashlib).

Signature verification is a stubbed interface — the actual Ed25519
verify call requires PyNaCl, which is a Phase-1 dependency
authorization. Until then, :func:`verify_signature` raises
``NotImplementedError`` so a Vol. 0.x release can never be
silently accepted by a consumer running stub verification.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from special_herbs.formats.hashing import sha256_file
from special_herbs.formats.manifest import Manifest


@dataclass(frozen=True)
class ShaMismatch:
    """Reported when a file's actual SHA does not match the manifest."""

    file: Path
    expected: str
    actual: str


def verify_artifact_sha(manifest: Manifest, artifact_path: Path) -> ShaMismatch | None:
    """Verify that ``artifact_path`` matches ``manifest.sha256``.

    Returns ``None`` on match, a :class:`ShaMismatch` describing the
    drift on mismatch. Callers should refuse to load any artifact for
    which a non-None mismatch is returned.
    """
    actual = sha256_file(artifact_path)
    if actual != manifest.sha256:
        return ShaMismatch(file=artifact_path, expected=manifest.sha256, actual=actual)
    return None


def verify_signature(manifest: Manifest, public_key_b64: str) -> None:
    """Verify the manifest's Ed25519 signature against ``public_key_b64``.

    NOT YET IMPLEMENTED. Signing requires PyNaCl, which is a Phase-1
    dependency. Calling this raises so consumers cannot silently
    accept unverified artifacts during the pre-Phase-1 window.

    Phase 1 implementation will:

    1. Compute ``manifest.to_canonical_bytes()``.
    2. Decode ``manifest.signature_b64`` (base64).
    3. Decode ``public_key_b64`` (base64).
    4. ``nacl.signing.VerifyKey(pk).verify(canonical_bytes, sig)``.
    5. Raise on verify failure; return on success.
    """
    raise NotImplementedError(
        "Ed25519 signature verification requires PyNaCl (Phase-1 dependency). "
        "Substrate is currently in pre-Phase-1; no signed releases yet exist. "
        "See docs/design/special-herbs-formats-api.md for the verification design."
    )
