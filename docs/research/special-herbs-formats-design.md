---
doc_id: SPECIAL-HERBS-FORMATS-RESEARCH
title: "special-herbs-formats — Manifest Format + Signing Research Synthesis"
status: research-only
created: 2026-04-29
research_session: "~/.claude/research_logs/2026-04-28_221649_manifest-format-and-signing-vol-1/"
related-docs:
  - ../design/special-herbs-formats-api.md
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - ../architecture/ADR-0002-separate-repo-from-consumers.md
  - ../ROADMAP.md
---

# `special-herbs-formats` — Manifest Format + Signing Research Synthesis

> Captured 2026-04-29 from a 2-angle Gemini Pro Deep Research session covering manifest landscape and artifact signing. Full source materials at `~/.claude/research_logs/2026-04-28_221649_manifest-format-and-signing-vol-1/`. The companion design doc lives at [`../design/special-herbs-formats-api.md`](../design/special-herbs-formats-api.md).

## Verdict

Both angles converged on the same architecture: **plain Pydantic-validated JSON manifest co-located with a standard `peft` directory (`adapter_config.json` + `adapter_model.safetensors`) plus a detached Ed25519 signature over the manifest.**

The angles diverged on which signing tool — Angle 1 reached for Sigstore Cosign by default; Angle 2 made a rigorous case AGAINST Sigstore for this specific use case. **Angle 2 wins** because the substrate ships direct-to-consumer (KG via local FS, not via a public registry like PyPI / npm) — Sigstore's value prop (shifting trust to a federated registry) doesn't apply. Recommended tool: `minisign` for the operator side and PyNaCl (libsodium binding) for the consumer side.

This satisfies [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §1 manifest schema verbatim and gives the lightest possible consumer dependency footprint with five-year offline survivability.

## Where the Two Angles Converged

| Topic | Both angles agree | Confidence |
|---|---|---|
| **Reject** MLflow / BentoML / ZenML / Mozilla MLEM / W&B / OCI Modelpack | All require running infrastructure (DB / registry / SaaS) or pull massive transitive deps for trivial parsing | High |
| **Reject** Python pickle (legacy `.bin`) for weights | Arbitrary code execution risk; HF + PyTorch ecosystem aggressively migrating to safetensors | High |
| **Adopt** standard `peft` artifact directory for the inference-layer files | `adapter_config.json` + `adapter_model.safetensors` is the inference-time wire format that vLLM, NIM, Transformers, and Apple MLX all expect | High |
| **Reject** floating tags on HF Hub | Tags are mutable pointers; pin by 40-char commit SHA | High |
| **Reject** SBOM-as-runtime-manifest (CycloneDX/SPDX) | SBOMs are for offline auditors and security scanners, not runtime load gates; way too heavy | High |
| **Layered architecture** | Custom signed Pydantic manifest WRAPS the standard peft files; the manifest is the substrate's provenance layer, the peft files are the inference layer | High |
| **Detached signature, not embedded envelope** | DSSE/JWS expose the parser to attack before crypto verifies; detached files (`.minisig`, `.sig`) verify bytes before parsing — Linux RPM/Debian convention | High |

## Where They Diverged — and Resolution

| Question | Angle 1 said | Angle 2 said | Resolution |
|---|---|---|---|
| Which signing tool? | Sigstore Cosign blob signatures | **Detached Ed25519 via minisign / PyNaCl** | **Angle 2** |

Angle 2's reasoning, validated:

1. `sigstore-python` pulls heavy transitive deps (`cryptography`, `pydantic`, `tuf`, `rfc3161-client`) — exposed to CVE-2026-39892 in `cryptography`.
2. Sigstore's offline-verification path requires keeping a TUF trust-root JSON synced with Fulcio / Rekor key rotations — fragile over a 5-year horizon.
3. The substrate ships direct-to-consumer; Sigstore's value prop is shifting trust to a federated registry, which doesn't apply when there is no registry intermediary.
4. Real solo OSS maintainers (Simon Willison, llama.cpp release pipeline) don't use Sigstore for direct-to-consumer artifact distribution.
5. Minisign signing is sub-second local computation with no network, no OIDC redirect, no CI dependency — well-aligned to the cost-discipline mandate.

## Why "Sign the Manifest, Not the Artifact Bytes"

Both angles independently reached the same conclusion (also validated by OpenSSF model-signing v1.0, April 2025):

The manifest contains the SHA-256 of every artifact file. Signing the manifest cryptographically locks those hashes to the operator's intent. If the substrate operator accidentally attaches a wrong-version model file at release time, the consumer's load-time hash check will mismatch the signed manifest and fail fast.

Signing gigabyte-scale model bytes directly:
- is computationally expensive (multi-GB Ed25519 signature throughput is unnecessary I/O),
- duplicates the SHA-256 binding already in the manifest,
- gains nothing in security (the manifest signature already authenticates the hash chain).

## Why Detached, Not Embedded (DSSE / JWS)

The Linux distro world (Debian's `Release.gpg`, RPM detached signatures) settled this decades ago: parser exploits land **before** cryptographic verification when the signature is embedded in a structured envelope. The consumer must parse the envelope to extract the signature — and any parser flaw becomes a pre-validation attack surface.

Concrete 2026 anchor: `llama.cpp` CVE-2026-33298 + CVE-2026-27940. Maliciously crafted GGUF files triggered heap corruption during embedded-metadata parsing **before** integrity checking ran.

Detached `.minisig` flips the order: the consumer hands the raw manifest bytes + the detached signature to PyNaCl, gets a yes/no, and only then parses the JSON. Cryptographic perimeter precedes JSON parser perimeter.

## Why Ed25519 (Not RSA, Not PQC Yet)

| Property | Status |
|---|---|
| Algorithm | Ed25519 — well-audited libsodium primitive |
| Key size | 32 bytes private / 32 bytes public — fits in a config constant |
| Sign / verify speed | Sub-second on M2 Ultra, microseconds for verify |
| 5-10 year quantum risk | Negligible; nation-state actors out of stated threat model; CRQC for Ed25519 estimated >2035 |
| Migration path | Schema's `signature_algorithm` field switches to `ml-dsa` when PyNaCl gets ML-DSA bindings (NIST CRYSTALS-Dilithium) |

Post-quantum migration is a future concern, not a present one. The schema accommodates it without architectural rework.

## Why Not Hugging Face Hub Native Signing

HF Hub's "signature" model is GPG-signed git commits at the repo level + SHA-256 checksums fetched from the Hub API. Both fail offline:

- GPG commit signature verifies authorship of the commit, not byte integrity of the downloaded file.
- SHA-256 checksum API requires Hub connectivity at consumer load time — violates [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §3 (no runtime API to substrate or its services).

The substrate may publish artifacts to HF Hub later as a distribution convenience, but the signing chain must travel inside the release package itself.

## Architecture Convergence — Concrete

Release directory layout per volume / version:

```
release/vol-1-fda-briefing-v1.0.0/
├── manifest.json              # Pydantic-validated; only this is signed
├── manifest.json.minisig      # Detached Ed25519 signature (zero-trust)
├── adapter_config.json        # Standard peft schema (vLLM / Transformers compatible)
└── adapter_model.safetensors  # Standard peft weights (memory-mappable)
```

Optional future siblings (Vol. 2+): `kg_snapshot.db`, `correlation_matrix.parquet` — same manifest pattern.

Verification flow:

1. Consumer reads `manifest.json` and `manifest.json.minisig`.
2. PyNaCl verifies the Ed25519 detached signature over the raw manifest bytes against the pinned public key. Mismatch → fail fast.
3. Pydantic parses the manifest into the `Manifest` model. Schema mismatch → fail fast.
4. Consumer streams each file in `manifest.files`, computing SHA-256. Mismatch → fail fast.
5. Consumer hands `adapter_config.json` + `adapter_model.safetensors` to its inference layer.

Consumer transitive dependency footprint: **PyNaCl + Pydantic** (≈ 4 transitive packages total) vs. ≈ 30+ for sigstore-python.

## Threat Model Alignment

| Threat | Defense | Why it works |
|---|---|---|
| Accidental corruption in transfer | Per-file SHA-256 in signed manifest | Manifest signature locks the expected hash; consumer recomputes and compares |
| Substrate operator drift (wrong artifact + right manifest) | SHA-256 binding + signature over manifest | Operator can't tamper post-signing without invalidating the `.minisig` |
| Future-collaborator verification (5+ years out) | Pinned Ed25519 public key, zero network deps | PyNaCl + libsodium will outlive Sigstore hosted services; no TUF root sync required |
| Key rotation | Append-only `trusted_keys: list[str]` on consumer side | Old releases stay verifiable; rotated key signs new releases. No CRL / network needed |
| Post-quantum (5-10 yr) | Ed25519 fine through ~2035 (CRQC out of threat model) | Migration path: schema's `signature_algorithm` field allows ML-DSA when PyNaCl gets bindings |
| CI/CD compromise / credential harvesting | Air-gapped local signing key on M2 Ultra | Per Apr 2026 npm/PyPI/Docker Hub supply-chain wave + CanisterSprawl — keys that never touch the internet can't be exfiltrated by a compromised dependency |

## Citations Worth Promoting Into Reference Memory

| Source | Use |
|---|---|
| OpenSSF model-signing v1.0 (April 2025) | Validates the "sign-the-manifest, not-the-bytes" pattern — file:hash pairs in DSSE envelope. We use the same idea with detached Ed25519 instead of DSSE/Sigstore for footprint reasons. |
| llama.cpp CVE-2026-33298 + CVE-2026-27940 | Concrete evidence that parsing-before-verification (embedded envelopes) is a real exploit class — anchors the "detached signature" choice. |
| `cryptography` library CVE-2026-39892 | Anchors why minimal-dependency PyNaCl beats sigstore-python on attack surface. |
| April 2026 npm / PyPI / Docker Hub supply chain wave + CanisterSprawl | Anchors the air-gapped-key argument over CI/CD-signed flows. |
| EleutherAI Pythia, AllenAI OLMo 3 release pipelines | Peer ML research substrates; both rely on HF Hub + Git-LFS, neither uses formal artifact signing — confirms there's no de facto signing standard to copy in this niche. |

## Citations Worth Validating Before Use

- "Modelpack" (CNCF) — DR mentions; verify status against the CNCF landscape page before quoting in design docs.
- IETF `draft-cui-dns-native-agent-naming-resolution-01` — sparse anchoring; treat as forward-looking signal, not load-bearing for the design.
- "MD-JoPiGo" / "Marin 32B" — referenced in passing; not relevant to this design.

## Implementation Gaps (Resolved in the Design Doc)

These are not literature gaps — they're design choices for the `special-herbs-formats` package itself. None warrant another DR Max session. They are addressed in [`../design/special-herbs-formats-api.md`](../design/special-herbs-formats-api.md):

1. **`compatible_consumer_contracts` semantics.** [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) mandates the field but doesn't define its shape.
2. **Public-key distribution.** Where the consumer gets the substrate's release public key.
3. **Release-key storage on the M2 Ultra.** Filesystem location + backup strategy.
4. **Format library packaging.** PyPI vs. monorepo-internal subdirectory until Vol. 1 release.

## What This Synthesis Does NOT Cover

- **Distribution of the artifact bundle itself.** Where do consumers download from? Local FS for Vol. 1; later candidates: S3, R2, GitHub Releases, HF Hub. Out of scope; design doc covers this.
- **Versioning of the format library.** When the schema evolves, how do old consumers handle new releases? Out of scope; design doc covers this.
- **Quantization-specific concerns.** GGUF integration is a 2027+ question; the format library can adopt GGUF as an additional artifact_type later without changing the manifest schema.
