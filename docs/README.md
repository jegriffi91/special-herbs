# Special Herbs Documentation

This directory contains the architectural records and roadmap for the Special Herbs substrate.

## Structure

- **[`ROADMAP.md`](./ROADMAP.md)** — Substrate phases (Vol. 0 through Vol. 4), kill criteria per phase, and the consumer-side dependency on King Geedorah (KG) Phase 13.1 RLAIF validation.

### `architecture/`

Architecture Decision Records (ADRs) — narrowly-scoped, dated decisions that establish architectural law for the substrate. ADRs are append-only; superseding an ADR requires writing a new ADR that explicitly references the prior one.

- **[`ADR-0001-substrate-as-artifact-contract.md`](./architecture/ADR-0001-substrate-as-artifact-contract.md)** — The foundational architectural law. Defines what the substrate is, what consumers can and cannot assume, and the binding rules that prevent runtime coupling drift.
- **[`ADR-0002-separate-repo-from-consumers.md`](./architecture/ADR-0002-separate-repo-from-consumers.md)** — Why the substrate lives in its own repo, separate from King Geedorah and any future consumers.

### Sister documents (in King Geedorah's repo for now)

- `docs/exploration/area-1-agentic-information-synthesis.md` — Area 1 detailed architecture, measurement indicators, research directions.
- `docs/exploration/area-4-cross-domain-signal-networks.md` — Area 4 detailed architecture, honest caveats on institutional competition.

These will likely migrate to this repo when Vol. 1 / Vol. 2 design begins. Until migration, they remain in KG and are referenced via path.
