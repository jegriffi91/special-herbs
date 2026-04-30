---
adr: NNNN
title: "<Title — title-cased noun phrase>"
status: proposed   # one of: proposed, accepted, deprecated, superseded
date: YYYY-MM-DD
deciders: jegriffi91
supersedes: none   # or the ADR ID(s) this supersedes
superseded_by: none
related:           # optional; remove section if N/A
  - ADR-NNNN-<slug>.md
---

# ADR-NNNN — <Title>

## Status

*One line: Proposed / Accepted / Deprecated / Superseded, date, and any supersession pointer.*

Example: **Accepted, YYYY-MM-DD.** Companion to [ADR-0001](ADR-0001-substrate-as-artifact-contract.md).

## Context

*What problem motivates this decision? Two paragraphs max.*

*Explain the forces at play: what failure modes are you preventing, what competing concerns exist, what prior ADRs does this extend or refine. Reference concrete examples where possible.*

## Decision

*The rules / mandates being established. Use numbered subsections (### 1. ...) for multi-part decisions, matching the style of ADR-0001 and ADR-0003.*

*Each subsection should state the rule first, then give a brief "Why this matters" rationale. Tables and "Specifically forbidden / allowed" lists help reviewers apply rules mechanically at PR time.*

### 1. <Rule Name>

*State the rule here.*

**Why this matters:** *One-to-two sentence rationale.*

## Consequences

### Positive

*Bullet list: what becomes easier, safer, or more reliable as a result of this decision.*

### Negative

*Bullet list: what becomes harder or more expensive. Be honest — every architectural constraint has a cost. Name it.*

### Neutral

*Bullet list: changes that are neither clearly better nor worse, or that merely formalize existing reality.*

## Alternatives Considered

*At least two alternatives with a one-line rejection rationale each.*

| Alternative | Why rejected |
|---|---|
| *Alternative A* | *One-line rejection rationale.* |
| *Alternative B* | *One-line rejection rationale.* |

## Compliance Verification

*Tests / lints / grep checks that should fail loudly if this ADR is violated. Mark as "aspirational" if tooling does not yet exist.*

- *Example: `grep` for `<pattern>` in substrate codebase → fail.*

## See Also

*Pointers to related ADRs, design docs, or operations docs.*

- [ADR-0001](ADR-0001-substrate-as-artifact-contract.md) — Substrate-as-Artifact Consumer Contract.
- [ADR-0002](ADR-0002-separate-repo-from-consumers.md) — Special Herbs Lives in a Separate Repository.
- [ADR-0003](ADR-0003-training-and-schedule-ownership.md) — Training Pipeline and Schedule Ownership Boundaries.
- *Add links to docs/design/ or docs/operations/ docs that informed or are affected by this decision.*
