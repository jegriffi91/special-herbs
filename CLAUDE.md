# Special Herbs — Claude Code Rules

> All rules in [AGENTS.md](./AGENTS.md) are **mandatory** and take full precedence. Read that file first before doing any work.

## Quick Reference

- **Project:** Research substrate that produces versioned artifacts (LoRA adapters, KG snapshots, correlation matrices) consumed by trading systems.
- **Initial consumer:** King Geedorah at `~/dev/king-geedorah`.
- **Naming:** MF Doom (Metal Fingers) "Special Herbs" beat-tape series, 2003-2007. Substrate produces instrumentals; consumers rap. Each release is a Volume; volume numbers are append-only (a failed Vol. 1 still consumes the slot).
- **Status:** Pre-Phase-0. Repo holds design documents and ADRs only — no production code.
- **Hardware:** Apple M2 Ultra 192GB, no co-location.
- **Operator:** Solo software architect. Learning quant trading; not a quant. Capital lives on consumer side ($2k starting, $5-10k ceiling by month 24).

## Cross-Repo Boundary

This repo MUST NOT import King Geedorah code, and vice versa. Per [ADR-0001](docs/architecture/ADR-0001-substrate-as-artifact-contract.md) §8 and [ADR-0002](docs/architecture/ADR-0002-separate-repo-from-consumers.md). The only future cross-repo dependency is the small `special-herbs-formats` companion package (manifest schemas + load utilities), and only consumers depend on it — never vice versa.

## Status & Phase Gates

Pre-Phase-0. **No code work** until both:

1. KG Phase 10 settle gate clears (~2026-05-05).
2. KG Phase 13.1 RLAIF Pipeline Validation lands (~late August 2026).

Phase 0 *exit* (kicks off Vol. 1 design) additionally requires KG Phase 11.2 Strategy-Scoped Signal Routing landed and 30+ papers read across Areas 1 + 4. See [docs/ROADMAP.md](docs/ROADMAP.md) for Volume-by-Volume phasing and decision gates.

## Phase 0 Deliverable Menu

All design / research only:

- **A.** Paper queue (`docs/research/paper-queue.md`) — 30+ papers across Areas 1 + 4 research directions.
- **B.** Vol. 1 FDA briefing MVA design doc (`docs/design/vol-1-fda-briefing-mva.md`). Cannot start until KG Phase 12.1 Golden Dataset Regression Suite is operational so the measurement harness has something to bind to.
- **C.** `special-herbs-formats` API sketch ([docs/design/special-herbs-formats-api.md](docs/design/special-herbs-formats-api.md)). ✅ Initial design complete (2026-04-29) — see also [docs/research/special-herbs-formats-design.md](docs/research/special-herbs-formats-design.md) for the literature triangulation.
- **D.** KG migration plan for Area 1 / Area 4 docs currently at `~/dev/king-geedorah/docs/exploration/`, plus topology / schedule boundary audit per [ADR-0003](docs/architecture/ADR-0003-training-and-schedule-ownership.md) — what stays in KG, what migrates here, what gets duplicated, and which KG-side training/scheduling references need substrate-side equivalents.
- **E.** CI / pre-commit / tooling skeleton (no test code yet — ruff config, pre-commit config, ADR template).
- **F.** This file + [AGENTS.md](./AGENTS.md) + [docs/operations/cross-repo-coordination.md](docs/operations/cross-repo-coordination.md). ✅ Initial draft complete (2026-04-28).

## Projected Code Structure

When Vol. 1 begins (post-Phase-0):

```
src/special_herbs/
  ingest/        # substrate-side data ingestion (FDA PDFs, NOAA, etc.)
  training/      # LoRA training pipeline (likely Unsloth-based)
  eval/          # measurement harness (binds to KG Golden Dataset)
  release/       # artifact release pipeline (manifest builder, signer)
  formats/       # manifest schema + load utilities (companion-package
                 #   precursor; published separately as
                 #   special-herbs-formats once Vol. 1 ships)
tests/           # repo-root test directory
docs/
  architecture/  # ADRs (append-only; supersede via new ADR)
  design/        # design docs per volume + per major feature
  operations/    # cross-repo coordination, runbooks
  research/      # paper notes, comparative analyses, cost-log.md
```

Substrate code MUST NOT have any subdirectory named after a consumer (no `src/special_herbs/king_geedorah/`). The substrate is consumer-agnostic by construction (ADR-0001 §6).

## Ops Commands

### KG settle-gate quick check (7-day window)

```bash
cd ~/dev/king-geedorah && \
  sqlite3 data/quality_gate_breaches.db \
  "SELECT metric, severity, COUNT(*) FROM quality_gate_breaches \
   WHERE evaluated_at >= datetime('now', '-7 days') \
   AND settle_gate_suppressed = 0 \
   GROUP BY metric, severity ORDER BY 3 DESC;"
```

Empty result = no breaches in the last 7 days = clean settle. KG mirrors the same pattern at [`~/dev/king-geedorah/CLAUDE.md`](../king-geedorah/CLAUDE.md) "Breach history".

### KG Phase 13.1 status

Read `~/dev/king-geedorah/docs/ROADMAP.md` Phase 13.1 — RLAIF Pipeline Validation. Look for the `✅` marker or settle-gate checkbox state.

## Cross-Repo Coordination

See [docs/operations/cross-repo-coordination.md](docs/operations/cross-repo-coordination.md) for the full protocol covering:

- KG → substrate phase unblocking handoffs.
- Substrate → KG Volume release procedure.
- Measurement-gate-failure response.

The operator is the integration point; there is no automated cross-repo trigger.

## Commit Rules

- All commits MUST include `[Conversation-ID: <uuid>]` in the message body. See [AGENTS.md](./AGENTS.md) §"Conversation-ID Commit Mandate".
- Never commit without explicit operator permission.
- Never skip pre-commit hooks (no `--no-verify`).
- Never push to `main` directly. PR flow only — match KG's worktree → PR → squash-merge convention.
- No floating version selectors (`latest`, `>=1.0`) anywhere in consumer-facing examples. Pinning is explicit per ADR-0001 §2.

## Communication Style

- Concise + structured. Lead with the answer, follow with reasoning.
- Use tables / bullet lists for enumerable content.
- No emojis unless explicitly requested.
- No filler ("Great question!", "I'd be happy to..."). When uncertain, surface the uncertainty as a question rather than padding with hedges.

## Memory State

This is a new project. Project memory at `~/.claude/projects/-Users-jamesgriffin-dev-special-herbs/memory/` accrues over time. The global memory at `~/.claude/CLAUDE.md` always loads (worktree-isolation rules, gemini-research pipeline, etc.).

KG's project memory at `~/.claude/projects/-Users-jamesgriffin-dev-king-geedorah/memory/` does **NOT** auto-load when working in this project. Do not assume cross-project memory transfer; if you need a KG memory, read it explicitly from disk.

## Worktree Isolation

When invoked as a worktree-isolated subagent, you are operating in `<parent-repo>/.claude/worktrees/<name>-<hash>/`. Never `cd` outside the worktree. Use `git -C <parent-path>` or absolute-path `Read` for read-only access to the parent. Full convention in `~/.claude/CLAUDE.md` "Worktree-isolated subagents".
