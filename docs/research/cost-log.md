---
doc_id: COST-LOG
title: "Frontier-API Spend Log"
status: active
created: 2026-04-30
related-docs:
  - ../../AGENTS.md
  - ../ROADMAP.md
  - ../design/special-herbs-formats-api.md
---

# Frontier-API Spend Log

> Per [AGENTS.md](../../AGENTS.md) §"Cost Discipline — Frontier APIs Are RLAIF Teachers Only": frontier APIs (Anthropic / OpenAI / Google) MUST NOT appear in the substrate's artifact-runtime path. They are used only as RLAIF teachers during training cycles or for bounded upfront research. Consumer-side runtime frontier use (e.g., KG calling frontier APIs at runtime to extract structured features feeding into a substrate-produced LoRA) is out of scope for this log — see [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §1 and [`../operations/cross-repo-coordination.md`](../operations/cross-repo-coordination.md) §"Volume Design Phase". Each cycle's API spend is logged here with the volume / artifact ID it produced, so total cost is auditable per release and stays within the per-cycle target.

## Targets

- **Per-cycle target**: <$50 USD for any single LoRA training cycle (including teacher grading).
- **Substrate artifact-runtime path**: $0 — frontier APIs MUST NOT appear in the substrate-produced LoRA's runtime hot path. (Consumer-side runtime frontier spend is a consumer-owned cost line, tracked separately by the consumer.)
- **Research / DR sweeps**: separately tracked; bounded by per-sweep approval per AGENTS.md.

## Spend log

| Date | Volume / Artifact ID | Provider | Purpose | Spend (USD) | Notes |
|------|---------------------|----------|---------|-------------|-------|
| _no spend yet (pre-Phase-0)_ | — | — | — | $0.00 | Repo is in Phase 0; no training cycles or research sweeps have fired yet. |

## Schema

- **Date** — ISO date (`YYYY-MM-DD`) of the cycle / sweep.
- **Volume / Artifact ID** — e.g., `vol-1-fda-briefing-v0.1.0`, `pre-vol-1-research`, or `unattached` for spend not tied to a specific volume.
- **Provider** — `anthropic` / `openai` / `google` / `other`.
- **Purpose** — `rlaif-teacher` / `gemini-dr` / `verification-search` / `other`.
- **Spend (USD)** — total cost; if estimated, prefix with `~`.
- **Notes** — anything material (over budget; teacher disagreed with substrate output X% of the time; sweep produced N papers added to queue; etc.).

## Audit

When a Volume releases, append a line to its release manifest summary linking back to the cost-log rows that produced it. The substrate's `special-herbs-formats` package may at some future point absorb this as a sidecar manifest field; until then, the link is manual (this file <-> release manifest's `release_notes` field).

## See Also

- [AGENTS.md](../../AGENTS.md) §"Cost Discipline — Frontier APIs Are RLAIF Teachers Only".
- [`docs/ROADMAP.md`](../ROADMAP.md) — per-volume gates that bound when cycles fire.
- [`docs/design/special-herbs-formats-api.md`](../design/special-herbs-formats-api.md) — release manifest format (potential future home of an audit sidecar).
