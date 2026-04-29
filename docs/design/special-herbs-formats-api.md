---
doc_id: SPECIAL-HERBS-FORMATS-API
title: "special-herbs-formats — API Design Sketch"
status: design-only
created: 2026-04-29
related-docs:
  - ../research/special-herbs-formats-design.md
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - ../architecture/ADR-0002-separate-repo-from-consumers.md
  - ../ROADMAP.md
phase-0-deliverable: C
---

# `special-herbs-formats` — API Design Sketch

> Phase 0 deliverable C. The design rationale and literature triangulation lives in [`../research/special-herbs-formats-design.md`](../research/special-herbs-formats-design.md). This document specifies WHAT the package is, not WHY.

## Mission

`special-herbs-formats` is the **only** piece of substrate code that consumers ever import. Per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §8 and [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md). It contains:

- The manifest schema (Pydantic v2).
- Artifact load + verification utilities (signature check + per-file SHA-256).
- Consumer-side pin verification helpers.

It does **not** contain training pipelines, eval harnesses, ingestion code, knowledge-graph logic, or any other substrate research code.

## Package Boundary

| In scope | Out of scope |
|---|---|
| Manifest Pydantic models | Training pipeline, eval harness, ingestion |
| Detached-signature verification (PyNaCl) | Signing CLI for the substrate (lives in main `special-herbs` repo, can shell to `minisign`) |
| Per-file SHA-256 verification helper | Network-fetch logic (consumers handle their own download pipeline) |
| Pinned-version helpers (consumer asserts artifact_id + version + sha256 + pubkey) | Consumer-specific business logic |
| `Manifest` parsing + schema-version handling | Inference-time model loading (consumers compose with `peft` / `transformers` / `vLLM` themselves) |

Out of scope means: the package does not depend on `transformers`, `torch`, `huggingface_hub`, `peft`, `safetensors`, or anything else heavy. Consumers compose `special-herbs-formats` with whatever inference stack they use.

## Dependencies

Hard requirements (production):

| Package | Reason | Transitive footprint |
|---|---|---|
| `pydantic` (>=2.0,<3) | Manifest schema validation | ~3 packages (annotated-types, pydantic-core, typing-extensions) |
| `pynacl` (>=1.5) | Ed25519 signature verification via libsodium | ~1 package (cffi) |

Total transitive footprint: ≈ 5 packages. Compare: `sigstore-python` ≈ 30+ transitive packages.

Test-time only: `pytest`, `pytest-cov`. No runtime `requests`, no `cryptography`, no `tuf`, no `huggingface_hub`.

## Manifest Schema

The wire format is JSON validated by these Pydantic v2 models. Schema is versioned via the `schema_version` field; future schema changes either bump it or extend additively.

```python
# special_herbs_formats/manifest.py
from pydantic import BaseModel, Field
from typing import Literal

ArtifactType = Literal["lora_adapter", "kg_snapshot", "correlation_matrix"]
SignatureAlgorithm = Literal["ed25519"]

class BaseModelRef(BaseModel):
    """Pinned base-model reference. Required for lora_adapter; null otherwise."""
    name: str       # canonical identifier, e.g. "meta-llama/Llama-3.1-8B-Instruct"
    sha256: str     # hex digest of the base model weights file (defends against HF Hub silent mutation)

class ArtifactFile(BaseModel):
    """One heavy file in the release bundle."""
    path: str       # release-relative path, e.g. "adapter_model.safetensors"
    sha256: str     # hex digest of file bytes
    size_bytes: int # for budgeting on consumer side

class Manifest(BaseModel):
    """The signed substrate-side manifest. ADR-0001 §1 source of truth."""
    schema_version: Literal["1"] = "1"
    artifact_id: str                          # e.g. "vol-1-fda-briefing"
    artifact_type: ArtifactType
    version: str                              # semver, e.g. "1.0.0"
    released_at: str                          # UTC ISO 8601, e.g. "2026-09-01T14:23:00Z"
    base_model: BaseModelRef | None           # required for lora_adapter
    training_data_hash: str                   # hex digest of training corpus snapshot
    compatible_consumer_contracts: list[str]  # set membership; see "Compatible Consumer Contracts" below
    files: list[ArtifactFile]                 # all heavy artifact files in this release
    signature_algorithm: SignatureAlgorithm = "ed25519"
```

Notes:

- `schema_version` allows non-breaking schema evolution. Consumer libraries pin to a major schema version; new fields are additive.
- `released_at` is operator-provided and not authoritative for ordering; the canonical ordering is `(artifact_id, version)`.
- `signature_algorithm` is in-band so post-quantum migration is a per-release attribute, not a library upgrade.

## Release Directory Layout

```
release/<artifact_id>-v<version>/
├── manifest.json              # Pydantic-validated; only this is signed
├── manifest.json.minisig      # Detached Ed25519 signature
├── adapter_config.json        # Standard peft schema (lora_adapter only)
├── adapter_model.safetensors  # Standard peft weights (lora_adapter only)
└── ...                        # Per artifact_type: kg_snapshot.db, correlation_matrix.parquet, etc.
```

Concrete example for Vol. 1:

```
release/vol-1-fda-briefing-v1.0.0/
├── manifest.json
├── manifest.json.minisig
├── adapter_config.json
└── adapter_model.safetensors
```

## Signing Pipeline (Substrate Side)

Lives in main `special-herbs` repo (`src/special_herbs/release/`), not in `special-herbs-formats`. Shells out to `minisign` CLI:

1. Substrate generates the heavy artifact files (`adapter_model.safetensors` etc.).
2. Substrate computes per-file SHA-256 + size.
3. Substrate writes `manifest.json` with all fields populated, validated against `Manifest`.
4. Substrate runs `minisign -S -s <release-key-path> -m manifest.json` — produces `manifest.json.minisig`.
5. Substrate publishes the directory to the release location.

Release-key storage: outside any git tree (recommended: `~/.special-herbs/release-key.minisign`, mode 0600, with a separate encrypted backup on external storage and a macOS Keychain copy). The substrate's [AGENTS.md](../../AGENTS.md) will document this path so future operators / Claude sessions don't grep for the key inside the repo.

## Verification Pipeline (Consumer Side)

Public API surface:

```python
# special_herbs_formats/__init__.py
from .manifest import Manifest, BaseModelRef, ArtifactFile, ArtifactType
from .verify import (
    verify_release,
    VerifiedRelease,
    SubstrateKeyRing,
    IntegrityError,
    SignatureError,
    SchemaVersionError,
    ContractError,
)

__all__ = [
    "Manifest", "BaseModelRef", "ArtifactFile", "ArtifactType",
    "verify_release", "VerifiedRelease", "SubstrateKeyRing",
    "IntegrityError", "SignatureError", "SchemaVersionError", "ContractError",
]
```

The single entry point consumers call:

```python
# special_herbs_formats/verify.py
from pathlib import Path
from dataclasses import dataclass
from .manifest import Manifest

@dataclass
class VerifiedRelease:
    """Result of a successful verify_release() call. Files are paths, not bytes —
    consumers stream them at their own pace into their inference layer."""
    manifest: Manifest
    release_dir: Path
    file_paths: dict[str, Path]   # path-relative-to-release → absolute Path

class IntegrityError(Exception):
    """Raised when a file's SHA-256 mismatches the signed manifest."""

class SignatureError(Exception):
    """Raised when the detached Ed25519 signature fails verification."""

class SchemaVersionError(Exception):
    """Raised when manifest schema_version is unknown to this library version."""

class ContractError(Exception):
    """Raised when manifest.compatible_consumer_contracts does not include any of the
    contracts the consumer claims to satisfy."""

class SubstrateKeyRing:
    """Append-only set of trusted Ed25519 public keys for a substrate.
    Old keys remain valid for previously-released artifacts; rotated keys verify new ones."""

    def __init__(self, public_keys_b64: list[str]) -> None: ...
    def verify(self, manifest_bytes: bytes, signature: bytes) -> None: ...

def verify_release(
    release_dir: Path,
    keyring: SubstrateKeyRing,
    consumer_contracts: list[str],
    expected_artifact_id: str | None = None,
    expected_version: str | None = None,
) -> VerifiedRelease:
    """Verify a release directory end-to-end.

    Steps (any failure raises and short-circuits):
      1. Read manifest.json + manifest.json.minisig (raw bytes).
      2. keyring.verify(manifest_bytes, signature)  →  SignatureError on mismatch.
      3. Manifest.model_validate_json(manifest_bytes)  →  SchemaVersionError if schema_version unknown.
      4. If expected_artifact_id / expected_version provided, assert match.
      5. Assert set(consumer_contracts) & set(manifest.compatible_consumer_contracts) is non-empty.
         Else  →  ContractError.
      6. For each f in manifest.files:
           - Stream-hash release_dir / f.path → compute SHA-256.
           - Compare to f.sha256.  →  IntegrityError on mismatch.
      7. Return VerifiedRelease(manifest, release_dir, {f.path: release_dir/f.path}).
    """
```

Verification is a single function call. Consumers wrap it in their startup logic and degrade gracefully on any exception per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §5.

Example consumer integration (in King Geedorah, hypothetical):

```python
# In KG: strategies/moat_fda_equity_catalyst.py (illustrative)
from special_herbs_formats import verify_release, SubstrateKeyRing

SUBSTRATE_KEYRING = SubstrateKeyRing(public_keys_b64=[
    "RWQX3hxJlmA9...",   # special-herbs release-key v1
])

def load_substrate_adapter(release_dir: Path) -> dict | None:
    try:
        rel = verify_release(
            release_dir=release_dir,
            keyring=SUBSTRATE_KEYRING,
            consumer_contracts=["king-geedorah-gateway-v1"],
            expected_artifact_id="vol-1-fda-briefing",
            expected_version="1.0.0",
        )
    except Exception as e:
        logger.warning("substrate adapter unavailable: %s", e)
        return None  # ADR-0001 §5 graceful degradation
    return {
        "manifest": rel.manifest,
        "adapter_config": rel.file_paths["adapter_config.json"],
        "adapter_weights": rel.file_paths["adapter_model.safetensors"],
    }
```

## Compatible Consumer Contracts (Resolution of Open Question #1)

`compatible_consumer_contracts` is an opaque list of named contract identifiers. Each consumer publishes the contracts it satisfies as a constant in its own code. Pin-time check is set membership.

Naming convention: `<consumer-name>-<surface>-v<major>`. Examples:

- `king-geedorah-gateway-v1` — KG's Gateway adapter slot, contract version 1.
- `king-geedorah-gateway-v2` — same surface, schema-incompatible v2 (e.g., adapter API rename).
- `king-geedorah-eval-v1` — KG's eval harness consuming the manifest's `training_data_hash` for golden-set version pinning.

A substrate release that targets KG Vol. 1 would publish:

```json
"compatible_consumer_contracts": ["king-geedorah-gateway-v1"]
```

When KG Gateway evolves to a v2 surface that the existing Vol. 1 release still satisfies (no breaking change), the substrate publishes a new minor release with both contracts:

```json
"compatible_consumer_contracts": ["king-geedorah-gateway-v1", "king-geedorah-gateway-v2"]
```

Set-membership keeps the check simple, explicit, and consumer-agnostic — substrate doesn't import consumer code, doesn't know what the contracts mean, just publishes the strings the operator declares.

Rejected alternatives:
- **Coupling-via-feature-schema** (e.g., hash of expected adapter-config keys): brittle when consumer schema evolves additively.
- **Semver ranges**: implicit; harder to audit in `git diff`.

## Public-Key Distribution (Resolution of Open Question #2)

The substrate's release public key (32-byte Ed25519, base64 string) ships **inside `special-herbs-formats` source code** as a constant. Consumer code constructs `SubstrateKeyRing` with that constant.

```python
# special_herbs_formats/keys.py
SPECIAL_HERBS_RELEASE_KEYS_V1 = [
    "RWQX3hxJlmA9bM7P9...",  # special-herbs release-key generated 2026-09-01
]
```

Key rotation = library version bump = consumer-side `pip` lockfile update + redeploy. No network fetch, no CRL, no transparency log.

This makes the format library version itself a privileged piece of consumer dependency — a `special-herbs-formats==1.0.0` consumer trusts whatever keys ship in 1.0.0. Future rotations append new keys without removing old ones (so historical artifacts remain verifiable):

```python
# In special_herbs_formats v1.1.0
SPECIAL_HERBS_RELEASE_KEYS_V1 = [
    "RWQX3hxJlmA9bM7P9...",  # release-key generated 2026-09-01
    "RWQpd2jnLkM3aZxB8...",  # release-key generated 2027-03-15 (rotation)
]
```

Compromised key removal: explicit major-version bump that drops a key, plus a deprecation note pinning the version range during which that key was active. Consumers force-pin to a `special-herbs-formats>=X` version that excludes the compromised key.

## Release-Key Storage (Resolution of Open Question #3)

Operator side (`~/dev/special-herbs/AGENTS.md` will document this canonical path):

```
~/.special-herbs/release-key.minisign       (mode 0600, primary)
+ encrypted backup on external storage      (rotated quarterly)
+ macOS Keychain "special-herbs-release"    (recovery copy)
```

The key file is **never** in any git tree. The substrate repo's `.gitignore` will explicitly exclude `release-key*` and `*.minisign`. The release pipeline (in main `special-herbs` repo) reads the key path from an env var (`SPECIAL_HERBS_RELEASE_KEY_PATH`) so it can never accidentally commit a path inside the repo.

## Format Library Packaging (Resolution of Open Question #4)

Ship `special-herbs-formats` as a separately-versioned PyPI package once Vol. 1 is public.

Until Vol. 1 release: live as `packages/special-herbs-formats/` inside the main `special-herbs` repo (per [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md) §"What Goes In a Separate Companion Package" allowance for monorepo-internal split).

Repo-internal layout:

```
packages/special-herbs-formats/
├── pyproject.toml                  # Independent versioning; depends only on pydantic + pynacl
├── README.md                       # Consumer-facing docs
├── special_herbs_formats/
│   ├── __init__.py                 # Public API surface
│   ├── manifest.py                 # Pydantic models
│   ├── verify.py                   # verify_release(), SubstrateKeyRing, exceptions
│   └── keys.py                     # SPECIAL_HERBS_RELEASE_KEYS_V1 constant
└── tests/
    ├── test_manifest_schema.py
    ├── test_verify_signature.py
    ├── test_verify_hashes.py
    └── fixtures/                    # canned manifest + signature pairs
```

When publishing to PyPI:
- Move `packages/special-herbs-formats/` to its own git repo (or use `git subtree`).
- The main `special-herbs` repo continues to depend on `special-herbs-formats==<exact-version>` for its own release pipeline (the substrate uses its own format library to build manifests).
- Consumer repos (KG and future) depend on `special-herbs-formats==<exact-version>` for verification.

## Versioning Policy

| Versioning axis | Mechanism |
|---|---|
| Manifest schema | `schema_version` field. Library knows the version range it supports; unknown version → `SchemaVersionError`. |
| Artifact (e.g., Vol. 1 v1.0.0 → v1.1.0) | Per-release semver in manifest. Consumer pins exact `(artifact_id, version, sha256)`. |
| Format library | Library-level semver. Consumer pins exact version in `pyproject.toml` lockfile. |
| Release public key | Append-only `SPECIAL_HERBS_RELEASE_KEYS_V1` list inside the format library. New rotations = new library minor version. |

The format library itself never depends on a specific artifact version. The artifact's `schema_version` declares which library versions can parse it.

## CI / Lint Hooks (Phase 0 Deliverable E will pick this up)

These belong in the substrate's CI when first code lands:

- Schema-evolution gate: any change to `manifest.py` requires bumping `schema_version` if the change is not strictly additive.
- Forbid-import gate: `special_herbs_formats` source must not import anything outside `pydantic`, `pynacl`, and stdlib. CI runs `grep` to enforce.
- Manifest-snapshot test: a canned `manifest.json` + `manifest.json.minisig` pair lives in `tests/fixtures/`; verify against a fixed test-only public key. Catches silent breaking changes to the verification logic.
- No-network test guard: tests run with network disabled (or asserted) to confirm the library never reaches out.

## Open Questions Deferred Beyond Phase 0

These are real but not blocking the C deliverable:

1. **Distribution mechanism for the release bundles.** Vol. 1 ships local FS + manifests; revisit at Vol. 2. Candidates: GitHub Releases (free, signed-tag friendly), S3 / R2 (cheap, no signing intelligence), HF Hub (best discoverability, mutable-tag risk per [research](../research/special-herbs-formats-design.md)). Decision: defer.
2. **Whether to publish the release public key out-of-band as well.** A second copy on the operator's GitHub or personal site adds minor redundancy for the future-collaborator threat-model leg. Low-cost; defer until Vol. 1 ships.
3. **GGUF as an additional `artifact_type`.** Useful for `llama.cpp` / Ollama distribution; not Vol. 1 scope. Add to the `ArtifactType` literal when the first GGUF release happens.
4. **Manifest extensions for KG snapshot + correlation matrix artifacts.** Each artifact_type may need type-specific metadata blocks (e.g., `kg_snapshot` schema version, `correlation_matrix` venue list). Either add nested per-type fields (`kg_metadata: KGMetadata | None`) or version the `Manifest` itself per artifact_type. Resolve at Vol. 2 design time.

## References

- Research synthesis: [`../research/special-herbs-formats-design.md`](../research/special-herbs-formats-design.md)
- [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) — required manifest fields, no-runtime-API rule, graceful degradation
- [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md) — companion-package allowance
- [ROADMAP.md](../ROADMAP.md) — Phase 0 deliverable C, Open Decision #3 (artifact registry)
- [AGENTS.md](../../AGENTS.md) — cost discipline, Conversation-ID commit mandate, citation hygiene
- Full Gemini DR session: `~/.claude/research_logs/2026-04-28_221649_manifest-format-and-signing-vol-1/`
