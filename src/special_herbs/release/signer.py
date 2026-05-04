"""Ed25519 signer — interface only; implementation is a Phase-1 task.

The signing call itself requires PyNaCl, which is a Phase-1 dependency
not yet authorized. Until then this module defines the API surface so
the release pipeline can be wired end-to-end and integration-tested
against the stub. Phase 1 fills in the real crypto.

Pre-Phase-1 callers can use :func:`sign_with_stub` to produce a
syntactically-valid placeholder signature for testing the publisher
pipeline. Verifiers MUST refuse stub signatures
(``"STUB::<reason>::<sha-prefix>"``) — the format is intentionally
unparseable as base64 to make accidental acceptance impossible.
"""

from __future__ import annotations

from special_herbs.formats.manifest import Manifest
from special_herbs.observability import EventLogger
from special_herbs.observability.event_names import RELEASE_SIGNATURE_GENERATED

_log = EventLogger("release")


def sign(manifest: Manifest, private_key_b64: str) -> Manifest:  # noqa: ARG001
    """Sign ``manifest`` with the given Ed25519 private key.

    Returns a new manifest with ``signature_b64`` populated.

    NOT YET IMPLEMENTED — see module docstring. Phase 1 task: replace
    the stub by importing ``nacl.signing`` and computing
    ``SigningKey(pk).sign(manifest.to_canonical_bytes()).signature``.
    """
    raise NotImplementedError(
        "Ed25519 signing requires PyNaCl (Phase-1 dependency). Until then, "
        "use sign_with_stub() for end-to-end pipeline testing — verifiers "
        "will reject stub signatures so accidental release is impossible."
    )


def sign_with_stub(manifest: Manifest, *, reason: str = "pre-phase-1") -> Manifest:
    """Produce a syntactically-invalid placeholder signature.

    Intended for plumbing tests of the release pipeline before Phase 1
    crypto lands. The placeholder format is
    ``STUB::<reason>::<artifact-sha-prefix>``, which:

    * Is NOT valid base64 (contains ``::``), so any verifier that
      attempts ``base64.b64decode`` raises and refuses the manifest.
    * Carries enough context (reason, sha prefix) to make accidental
      release attempts visible in postmortems.

    Real Ed25519 signing replaces this in Phase 1.
    """
    sha_prefix = manifest.sha256[:8]
    placeholder = f"STUB::{reason}::{sha_prefix}"
    signed = manifest.with_signature(placeholder)

    _log.emit(
        RELEASE_SIGNATURE_GENERATED,
        artifact_id=manifest.artifact_id,
        version=manifest.version,
        signature_kind="stub",
        signature_reason=reason,
    )
    return signed
