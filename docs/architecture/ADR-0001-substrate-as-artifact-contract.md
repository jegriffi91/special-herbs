---
adr: 0001
title: "Substrate-as-Artifact Consumer Contract"
status: accepted
date: 2026-04-28
deciders: jegriffi91
supersedes: none
superseded_by: none
---

# ADR-0001 — Substrate-as-Artifact Consumer Contract

## Status

**Accepted, 2026-04-28.** Foundational. Any future ADR that modifies these rules must explicitly reference and supersede this one.

## Context

The Special Herbs substrate produces artifacts (LoRA adapters, knowledge graph snapshots, correlation matrices) that consumer systems use to enhance their decisions. The initial consumer is King Geedorah; future consumers (a sister trading system, research tooling, external collaborators) may emerge.

Two failure modes are anticipated and must be prevented architecturally, not just by convention:

1. **Runtime coupling drift.** It is tempting to add a "quick" runtime API between substrate and consumer ("just one query," "just a webhook," "just a shared Redis"). Each such addition compounds: the substrate becomes a service that consumers depend on at runtime, the consumer becomes brittle to substrate availability, and the two systems' lifecycles fuse. This destroys the substrate's most valuable property — that its artifacts are durable, replayable, and consumer-agnostic.

2. **Semantic drift.** If consumer code expects a specific artifact behavior and the substrate silently changes the artifact (a new LoRA weight, an updated KG schema), the consumer's deterministic scorer suddenly receives different feature vectors and trade outcomes drift. Versioning and consumer-side pinning are the only architectural defense.

This ADR codifies the rules that prevent both failure modes.

## Decision

### 1. Artifacts are versioned and immutable

Every artifact released by the substrate carries a SHA-tagged, signed manifest. Once published, an artifact version is **immutable** — corrections produce a new version, never a retroactive edit.

Manifest must include:

- **`artifact_id`** — unique within the substrate (e.g., `vol-1-fda-briefing`).
- **`version`** — semantic version (`v1.0.0`, `v1.1.0`, etc.).
- **`sha256`** — cryptographic hash of the artifact contents.
- **`released_at`** — UTC ISO timestamp.
- **`base_model`** — for LoRA adapters: the base model SHA the adapter is trained against.
- **`training_data_hash`** — hash of the training dataset (for reproducibility audits).
- **`compatible_consumer_contracts`** — list of consumer-API contract versions this artifact is compatible with.
- **`signature`** — release-key-signed manifest signature.

### 2. Consumers pin specific versions

Consumer code reads the artifact version pin at startup (from a config file, environment variable, or strategy YAML manifest). The pin is explicit and version-specific:

```yaml
# In a consumer's strategy YAML
substrate_artifacts:
  - artifact_id: vol-1-fda-briefing
    version: v1.2.3
    sha256: abc123...
```

Consumers MUST verify the SHA on load. Mismatched SHA → load fails fast.

Consumers MUST NOT use floating version selectors (`latest`, `>=1.0`, etc.) in production. Pinning is explicit.

### 3. No runtime API between substrate and consumers

The substrate emits artifacts to a release location (local filesystem, blob storage, model registry). Consumers read those artifacts at startup or on a controlled refresh cadence. **Nothing else is exchanged at runtime.**

Specifically prohibited:

- HTTP / gRPC / IPC calls from consumer to substrate during inference.
- Webhook callbacks from substrate to consumer.
- Shared Redis / message bus / pub-sub channels.
- Live database connections that span substrate and consumer.
- "Helper services" that wrap substrate logic for runtime consumer use.

If a use case appears to require runtime API coupling, the architecturally correct answer is one of:

- Bake the required logic into the artifact itself (e.g., a richer LoRA, a more complete KG snapshot).
- Bake it into the consumer (the consumer can run its own model alongside substrate features).
- Defer the use case until the substrate's artifact format can absorb it.

### 4. No shared databases

The substrate and any consumer MUST NOT share a database, even read-only. Each system maintains its own data layer.

If the same upstream source (e.g., FDA briefing PDFs) is needed by both, **each system independently ingests it.** Duplicate ingestion cost is acceptable; coupling cost is not.

### 5. Graceful consumer degradation

Consumers MUST function (with reduced capability) when substrate artifacts are unavailable, corrupted, or fail SHA verification. The fallback path is:

- Log the failure.
- Disable the substrate-augmented feature path.
- Continue operating on the consumer's own logic.

A consumer that crashes when a substrate artifact is missing is in violation of this ADR.

### 6. Substrate has no knowledge of consumers

The substrate codebase MUST NOT contain:

- Lists of consumer system names.
- Conditional logic keyed on consumer identity.
- API endpoints that serve specific consumers.
- Tests that depend on consumer behavior.

The substrate is consumer-agnostic by construction. Any consumer-aware logic belongs on the consumer side.

### 7. LLM as feature extractor only, never decision-maker

The substrate may use LLMs internally during artifact production (for synthesis, classification, extraction). The substrate MUST NOT produce artifacts that are themselves decision-makers. Specifically prohibited:

- An artifact that is a "buy/sell signal generator."
- An artifact that emits trade orders.
- An artifact whose output is consumed directly without a deterministic scorer in the consumer's path.

Consumers may use substrate artifacts as features for their own deterministic scorers, gradient-boosted ensembles, or rule-based logic. The substrate provides features; the consumer makes decisions.

### 8. Cross-repo separation enforced at the file system

The substrate codebase MUST NOT import from any consumer codebase, and vice versa. Cross-repo imports are detected as follows:

- Substrate's `pyproject.toml` / `Cargo.toml` MUST NOT list any consumer repo as a dependency.
- Consumer's dependency list MAY list the substrate's released-artifact format library (a small, separately-published package containing only manifest schemas and load utilities) — but never the substrate's training, evaluation, or research code.

Released-artifact format library proposed name: `special-herbs-formats` (separately versioned and published; depends on nothing from this repo's training pipeline).

## Consequences

### Positive

- **Substrate failure does not break consumers.** A bad LoRA training cycle, a corrupted KG snapshot, or even a complete substrate outage degrades consumer features but does not crash consumer execution.
- **Consumers can be refactored freely.** No coordination overhead with the substrate.
- **Substrate can be refactored freely.** No risk of breaking consumers as long as the artifact format contract is preserved.
- **Multiple consumers can integrate over time** without the substrate fanning out into a service-mesh of consumer-specific code paths.
- **Artifact releases are auditable.** Every artifact has a manifest with hash, training data hash, and signature. Reproducibility is built in.

### Negative

- **Higher artifact-format bar.** The substrate cannot fix consumer issues by adding a quick runtime endpoint; it must release a corrected artifact. Slower turnaround on edge cases.
- **Some duplicate ingestion cost.** Both substrate and consumers may ingest the same upstream source. Acceptable cost for the architectural separation.
- **Consumer-side pin maintenance.** Consumers must explicitly pin and update artifact versions; floating selectors aren't allowed.

### Neutral

- The substrate may eventually publish a separate, small format library (`special-herbs-formats`) for consumer integration. This is the only piece of substrate code that may be imported by consumers, and it contains zero business logic.

## Compliance Verification

Tests / lints that should fail-loudly if this ADR is violated:

- Substrate codebase: grep for `import king_geedorah` or any consumer import → fail.
- Substrate codebase: grep for `requests.post`, `urllib`, `httpx` calls to consumer hostnames → review at PR time.
- Consumer codebase: artifact load helpers must verify SHA before use; missing verification → CI failure.
- Substrate release pipeline: artifact manifest must include all required fields → CI failure if missing.

These are aspirational; tooling will be added as the substrate codebase grows. For now, this ADR is the convention; reviewers enforce it.

## See Also

- King Geedorah `docs/ROADMAP.md` — the consumer side; see Architectural Principles section.
- Source synthesis: `~/.claude/research_logs/2026-04-28_112632_kg-moat-substrate-selection/CONSOLIDATED_ROADMAP_DRAFT.md` — Decision #3 resolution rationale.
- Operator emphasis (2026-04-28): "Clear lines of separation between the substrate and the client(s) (KG)."
