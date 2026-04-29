---
adr: 0002
title: "Special Herbs Lives in a Separate Repository from Consumer Systems"
status: accepted
date: 2026-04-28
deciders: jegriffi91
supersedes: none
superseded_by: none
related:
  - ADR-0001-substrate-as-artifact-contract.md
---

# ADR-0002 — Special Herbs Lives in a Separate Repository from Consumer Systems

## Status

**Accepted, 2026-04-28.** Repository organization decision. Companion to ADR-0001 (the architectural law); this ADR records why the architectural law is also a filesystem-level law.

## Context

When the substrate concept first surfaced (King Geedorah `docs/exploration/research-substrate-roadmap.md`, 2026-04-26, now consolidated into KG's `docs/ROADMAP.md`), one open question was whether substrate code should live inside the King Geedorah monorepo or in a separate repository.

Arguments in each direction:

**Arguments for monorepo (single repo):**
- Faster early iteration — no cross-repo PR coordination.
- Shared CI / tooling / dependency management.
- Easy refactoring across substrate-and-consumer boundaries during prototyping.
- Single source of truth for "the system."

**Arguments for separate repo:**
- Different release cadences (substrate: weeks-to-months training cycles; KG: PM2 deploy cycles).
- Different success metrics (substrate: artifact quality; KG: trade PnL).
- Different lifecycle ownership (substrate: knowledge-accumulation depth; KG: trading-strategy phases).
- Multiple consumers eventually possible — a monorepo locks substrate to one consumer.
- Architectural separation (ADR-0001) is harder to enforce when files are in the same tree; cross-imports become easy and tempting.

## Decision

**Special Herbs lives in its own repository, separate from King Geedorah and any future consumer.**

Operator instruction (2026-04-28): "Clear lines of separation between the substrate and the client(s) (KG) help isolate bug origins and prevent runtime coupling drift."

Implications:

1. **Independent CI.** Special Herbs has its own test suite, lint config, pre-commit hooks. CI does not depend on King Geedorah's CI passing.
2. **Independent dependency management.** `pyproject.toml` is separate. Substrate may use different library versions than KG.
3. **Independent release cadence.** Substrate releases when an artifact (a "Volume") is ready; KG releases on its PM2 deploy cycle. Neither blocks the other.
4. **Independent issue tracker / PR review.** Each repo has its own GitHub issues and PRs.
5. **Cross-repo communication is artifact-only.** Per ADR-0001 §3-§4, substrate and KG do not share runtime services or databases. The artifact release is the only "interface."
6. **Shared base model dependency only.** Both repos may load the same Qwen / Llama base model from local disk independently. No shared model-serving infrastructure.

## What Stays Out of This Repo

The following live in King Geedorah, not here:

- Live trading strategy YAML manifests (`moat_fda_equity_catalyst.yaml`, etc.).
- KG's RLAIF training pipeline (`mlops/pipelines/orpo_pipeline.py`, `mlops/pipelines/grpo_pipeline.py`).
- KG's golden dataset, settle gate metrics, and `pipeline_quality_gate.py`.
- KG's signal listener, orchestrator, scout, commander code.
- Any code that touches a brokerage API or executes trades.

If anything in this repo starts to look like a trading system, it is in the wrong repo.

## What Lives in This Repo

- Source-data ingestion adapters (FDA briefing PDFs, NOAA forecasts, Polymarket Gamma read-only, governance forums) — substrate-specific, distinct from KG's signal-listener ingestion.
- LoRA training pipeline for substrate adapters.
- Knowledge graph build / snapshot tooling.
- Correlation computation engine (Area 4).
- Artifact release pipeline (manifest builder, signer, version bumper).
- Substrate eval harness — measures artifact quality, not consumer trade outcomes.
- ADRs and design documents.

## What Goes In a Separate Companion Package

The artifact format library (`special-herbs-formats`) is published as its own small Python package, separately versioned. It contains:

- Manifest schema (Pydantic models or similar).
- Artifact load utilities (read manifest, verify SHA, load LoRA into a base model).
- Consumer-side pin verification.

Consumers depend on `special-herbs-formats` (small, stable). Consumers do NOT depend on the main `special-herbs` repo (large, fast-moving research code).

The format library may live as a `packages/special-herbs-formats/` subdirectory of this repo (monorepo-internal split) or as its own repo. Defer until the format stabilizes; for Vol. 1 it can be inline in this repo.

## Migration Path for Existing Substrate Documentation

The Area 1 and Area 4 architecture docs currently live in King Geedorah at `docs/exploration/area-1-agentic-information-synthesis.md` and `docs/exploration/area-4-cross-domain-signal-networks.md`. These will migrate to this repo when substrate Vol. 1 / Vol. 2 design begins (likely August 2026 once KG Phase 13.1 lands). Until migration, they remain in KG and are referenced via path in this repo's `docs/ROADMAP.md`.

## Consequences

### Positive

- ADR-0001's architectural law becomes filesystem-enforced, not just convention.
- Each system can be refactored, restarted, or even abandoned independently.
- Multiple consumers (KG today, sister systems in years 3-5) integrate against a clean external API.
- Bug origins are unambiguous: a failure in `special-herbs/` is substrate; a failure in `king-geedorah/` is consumer.
- Each repo's commit history is focused and reviewable.

### Negative

- Cross-repo PR coordination required when an artifact format change requires consumer-side updates. Mitigation: ADR-0001 §1 makes artifact format versions backward-compatible by default; breaking changes require a major version bump and explicit consumer migration.
- Slightly higher overhead to set up CI, pre-commit, and tooling in two places. One-time cost, paid back over many cycles.
- Operator must context-switch between two repos. Mitigated by the substrate's slow release cadence — most operator time is in one repo at a time.

### Neutral

- The choice of `git submodule` / `git subtree` / `pip install` for cross-repo dependencies is deferred to whenever that integration is actually needed (likely Vol. 1 release).

## References

- ADR-0001 — the architectural law this ADR makes filesystem-enforced.
- King Geedorah `docs/ROADMAP.md` — consumer-side roadmap; references this repo for the substrate side.
- Source synthesis: `~/.claude/research_logs/2026-04-28_112632_kg-moat-substrate-selection/CONSOLIDATED_ROADMAP_DRAFT.md` — Decision #3 resolution.
