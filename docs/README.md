# Special Herbs Documentation

This directory contains the architectural records, design docs, operational protocols, and research synthesis for the Special Herbs substrate.

## Structure

- **[`ROADMAP.md`](./ROADMAP.md)** — Substrate phases (Vol. 0 through Vol. 4), kill criteria per phase, and the consumer-side dependency on King Geedorah (KG) Phase 13.1 RLAIF validation.

### `architecture/`

Architecture Decision Records (ADRs) — narrowly-scoped, dated decisions that establish architectural law for the substrate. ADRs are append-only; superseding an ADR requires writing a new ADR that explicitly references the prior one.

- **[`ADR-0001-substrate-as-artifact-contract.md`](./architecture/ADR-0001-substrate-as-artifact-contract.md)** — The foundational architectural law. Defines what the substrate is, what consumers can and cannot assume, and the binding rules that prevent runtime coupling drift.
- **[`ADR-0002-separate-repo-from-consumers.md`](./architecture/ADR-0002-separate-repo-from-consumers.md)** — Why the substrate lives in its own repo, separate from King Geedorah and any future consumers.
- **[`ADR-0003-training-and-schedule-ownership.md`](./architecture/ADR-0003-training-and-schedule-ownership.md)** — Training pipeline + schedule ownership boundaries; topology matrix, schedule isolation, recipe-promotion via third packages, anti-temptation list.
- **[`_template.md`](./architecture/_template.md)** — ADR scaffold for new decisions.

### `design/`

Substrate-internal design documents. One per major feature; companion-package design lives here too.

- **[`special-herbs-formats-api.md`](./design/special-herbs-formats-api.md)** — `special-herbs-formats` companion package's API + manifest schema (Phase 0 deliverable C).
- **[`resilience-and-subsystem-isolation.md`](./design/resilience-and-subsystem-isolation.md)** — Subsystem decomposition + import directionality + Pre-Launch Validation gate + testing / backtest / tape / logging design.

### `operations/`

Cross-repo coordination, runbooks, migration protocols.

- **[`cross-repo-coordination.md`](./operations/cross-repo-coordination.md)** — KG ↔ substrate handoff protocol; release sequence; postmortem flow; documentation-drift resolution.
- **[`kg-migration-plan.md`](./operations/kg-migration-plan.md)** — Per-document migration verdict for KG `docs/exploration/` Area 1 / Area 4 material plus ADR-0003 topology + schedule boundary audit (Phase 0 deliverable D). Migration itself executes post-KG-Phase-13.1 (~late August 2026).

### `research/`

Literature triangulations, feasibility studies, reading queues. Substrate-internal; consumer-agnostic.

- **[`paper-queue.md`](./research/paper-queue.md)** — Phase 0 reading queue, 71 verified entries across Areas 1 & 4 (Phase 0 deliverable A). Cleared by ≥30 entries marked `read` plus a synthesis tying each Area to Vol. 1 / Vol. 2 design decisions.
- **[`vol-1-fda-ac-feasibility.md`](./research/vol-1-fda-ac-feasibility.md)** — Vol. 1 (FDA AC briefing LoRA) feasibility synthesis from a 3-source Gemini Deep Research triangulation; canonical experimental design for the prompt-only baseline.
- **[`special-herbs-formats-design.md`](./research/special-herbs-formats-design.md)** — Manifest format + signing literature triangulation backing the Phase 0 deliverable C design.

### Sister documents (in King Geedorah's repo until migration)

- `docs/exploration/area-1-agentic-information-synthesis.md` — Area 1 detailed architecture, measurement indicators, research directions.
- `docs/exploration/area-4-cross-domain-signal-networks.md` — Area 4 detailed architecture, honest caveats on institutional competition.

The migration plan for these documents lives at [`operations/kg-migration-plan.md`](./operations/kg-migration-plan.md). Migration executes post-KG-Phase-13.1 (~late August 2026); until then the docs are read-only references at the cited paths.
