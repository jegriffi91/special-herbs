"""Unit tests for the signer (stub + real-API contract)."""

from __future__ import annotations

import base64

import pytest
from hypothesis import given
from hypothesis import strategies as st

from special_herbs.formats.verification import verify_signature
from special_herbs.observability import assert_event_sequence, capture_events
from special_herbs.release.signer import sign, sign_with_stub
from tests.release._fixtures import sample_manifest


def test_sign_with_stub_populates_signature() -> None:
    manifest = sample_manifest()
    signed = sign_with_stub(manifest, reason="pre-phase-1")
    assert signed.signature_b64.startswith("STUB::pre-phase-1::")
    assert manifest.signature_b64 == ""  # original unchanged


def test_stub_signature_is_not_valid_base64() -> None:
    """Verifiers using b64decode will reject stub signatures — by design."""
    manifest = sample_manifest()
    signed = sign_with_stub(manifest)
    with pytest.raises(ValueError):  # binascii.Error is a ValueError subclass
        base64.b64decode(signed.signature_b64, validate=True)


@given(reason=st.text(min_size=0, max_size=200))
def test_stub_signature_never_parses_as_base64(reason: str) -> None:
    """Property: sign_with_stub() output is unparseable as base64 for ANY reason.

    The ``::`` separator in ``STUB::<reason>::<sha-prefix>`` keeps the
    string outside the base64 alphabet. This property test makes sure
    a future format change doesn't accidentally produce a valid-base64
    placeholder that real verifiers would silently accept.
    """
    manifest = sample_manifest()
    signed = sign_with_stub(manifest, reason=reason)
    with pytest.raises(ValueError):
        base64.b64decode(signed.signature_b64, validate=True)


def test_sign_with_stub_carries_sha_prefix() -> None:
    manifest = sample_manifest()
    signed = sign_with_stub(manifest)
    sha_prefix = manifest.sha256[:8]
    assert sha_prefix in signed.signature_b64


def test_sign_with_stub_emits_event() -> None:
    manifest = sample_manifest()
    with capture_events() as events:
        sign_with_stub(manifest, reason="custom-reason")
    assert_event_sequence(events, ["release.signature_generated"])
    assert events[0]["signature_kind"] == "stub"
    assert events[0]["signature_reason"] == "custom-reason"


def test_real_sign_raises_until_pyna_cl_lands() -> None:
    manifest = sample_manifest()
    with pytest.raises(NotImplementedError, match="PyNaCl"):
        sign(manifest, "fake-private-key")


def test_verify_signature_does_not_accept_stub_signed_manifest() -> None:
    """Contract: stub signatures must be rejected by the verification path.

    Pre-Phase-1: passes because verify_signature itself raises
    NotImplementedError (so any input fails the verify gate, including
    a stub-signed manifest — fail-loud-by-default).

    Phase-1 task: when real Ed25519 verification lands, this test
    should continue to pass because the ``STUB::reason::sha-prefix``
    format is invalid base64 — any Ed25519 verifier will reject it
    before signature math can succeed. If this test starts FAILING in
    Phase 1, the implementer forgot to handle the stub case and the
    central pre-Phase-1 safety guarantee has regressed.
    """
    manifest = sign_with_stub(sample_manifest())
    with pytest.raises(NotImplementedError):
        # Phase-1: replace this raises clause to match the new exception
        # type (likely binascii.Error or nacl.exceptions.BadSignatureError).
        verify_signature(manifest, "fake-public-key")
