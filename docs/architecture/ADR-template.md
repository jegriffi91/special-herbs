---
adr: NNNN
title: "<Short imperative noun phrase>"
status: proposed
date: YYYY-MM-DD
deciders: jegriffi91
supersedes: none
superseded_by: none
related:
  - ADR-XXXX-related-adr.md
---

# ADR-NNNN — <Short imperative noun phrase>

## Status

**<Proposed | Accepted | Superseded by ADR-XXXX | Deprecated>**, YYYY-MM-DD.

If this ADR modifies rules established by a foundational ADR (0001 / 0002 / 0003), state that explicitly here and link the prior ADR.

## Context

What problem are we solving? Why now? What constraints, prior incidents, or external pressures shape the decision space?

Be specific about failure modes that motivate this ADR. The reader six months from now needs enough context to judge whether the decision still applies — abstractions without grounding rot.

## Decision

The decision itself, stated as enforceable rules. Numbered subsections for clarity:

### 1. <First rule>

What's required. What's forbidden. How a reviewer or lint check identifies a violation.

### 2. <Second rule>

…

## Consequences

### Positive

- What this enables.
- What it makes easier or safer.

### Negative

- What it costs (developer time, runtime overhead, coordination friction).
- What use cases it forecloses.

### Neutral

- Side effects that are neither wins nor losses but are worth surfacing.

## Compliance Verification

Tests, lints, or review checks that should fail-loudly if this ADR is violated:

- `grep` patterns for forbidden imports / strings.
- `import-linter` contracts.
- Custom CI scripts.
- PR-time review checks (when no automated check is feasible).

If tooling does not yet exist, mark verification as "aspirational; reviewer-enforced" and link the deliverable that will land the tooling.

## See Also

- Related ADRs.
- Foundational design docs.
- Research logs / synthesis sources.
- External references (papers, vendor docs).
