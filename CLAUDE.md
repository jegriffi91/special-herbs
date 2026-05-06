# Special Herbs — Claude Code Rules

> All rules in [AGENTS.md](./AGENTS.md) are **mandatory** and take full precedence. Read that file first before doing any work.

## Quick Reference

- **Project:** Research substrate that produces versioned artifacts (LoRA adapters, KG snapshots, correlation matrices) consumed by trading systems.
- **Initial consumer:** King Geedorah at `~/dev/king-geedorah`.
- **Naming:** MF Doom (Metal Fingers) "Special Herbs" beat-tape series, 2003-2007. Substrate produces instrumentals; consumers rap. Each release is a Volume; volume numbers are append-only (a failed Vol. 1 still consumes the slot).
- **Status:** Phase 0 exited 2026-05-05. Repo holds ADRs, design documents, and Phase 0E scaffolding code (formats / observability / release / tape modules + tests + import-linter contracts + 80% coverage gate). Phase 1 (Vol. 1 design) gated on KG Phase 12.1 (~July 2026) and KG Phase 13.1 (~late August 2026); no Vol. 1 production code lands until both clear.
- **Hardware:** Apple M2 Ultra 192GB, no co-location.
- **Operator:** Solo software architect. Learning quant trading; not a quant. Capital lives on consumer side ($2k starting, $5-10k ceiling by month 24).

## Cross-Repo Boundary

This repo MUST NOT import King Geedorah code, and vice versa. Per [ADR-0001](docs/architecture/ADR-0001-substrate-as-artifact-contract.md) §8 and [ADR-0002](docs/architecture/ADR-0002-separate-repo-from-consumers.md). The only future cross-repo dependency is the small `special-herbs-formats` companion package (manifest schemas + load utilities), and only consumers depend on it — never vice versa.

## Status & Phase Gates

Phase 0 exited 2026-05-05. All three precondition boxes ticked: KG Phase 10 settle gate (operator override; full rationale in KG `docs/ROADMAP.md` §"Phase 10"), KG Phase 11.2 Strategy-Scoped Signal Routing (shipped 2026-04-21), KG Phase 14.0 non-schema infra dry-run (KG PRs #18/#19/#21 merged 2026-04-26/27).

**Phase 1 (Vol. 1 design + build) gated on:**

1. KG Phase 12.1 Golden Dataset Regression Suite operational (~July 2026) — Vol. 1 measurement harness binds to it.
2. KG Phase 13.1 RLAIF Pipeline Validation lands (~late August 2026) — substrate Vol. 1 build cannot start until then.

The 30+ papers milestone moved to Phase 1 (decided 2026-05-03); reading concurrent with Phase 1 design rather than gating Phase 0 exit. Vol. 1 task shape locked as Option I (alternative Commander on FDA briefings) per [Special-Herbs#14 §13](https://github.com/jegriffi91/Special-Herbs/pull/14). See [docs/ROADMAP.md](docs/ROADMAP.md) for Volume-by-Volume phasing and decision gates.

## Phase 0 Deliverable Menu (closed 2026-05-05)

Phase 0 deliverables — historical record. Phase 1 deliverables tracked in [docs/ROADMAP.md](docs/ROADMAP.md).

- **A.** ✅ Paper queue ([`docs/research/paper-queue.md`](docs/research/paper-queue.md)) — 71 verified entries (38 Area 1 / 33 Area 4); reading-30+ milestone moved to Phase 1 (decided 2026-05-03). The synthesis tying Areas to Vol. 1 / Vol. 2 design decisions becomes a Phase 1 prerequisite.
- **B.** Vol. 1 FDA briefing MVA design doc — **Phase 1 deliverable, not Phase 0**. Gated on KG Phase 12.1 Golden Dataset Regression Suite (~July 2026). Task shape locked as Option I per [Special-Herbs#14 §13](https://github.com/jegriffi91/Special-Herbs/pull/14).
- **C.** ✅ `special-herbs-formats` API ([docs/design/special-herbs-formats-api.md](docs/design/special-herbs-formats-api.md)) — design + literature triangulation ([docs/research/special-herbs-formats-design.md](docs/research/special-herbs-formats-design.md)) both complete.
- **D.** ✅ KG migration plan + ADR-0003 boundary audit ([docs/operations/kg-migration-plan.md](docs/operations/kg-migration-plan.md)) — verdicts locked; migration executes post-KG-Phase-13.1.
- **E.** ✅ Phase 0E scaffolding shipped ([Special-Herbs#10](https://github.com/jegriffi91/Special-Herbs/pull/10)): `src/special_herbs/{formats,release,observability,tape,plv,training,eval/{harness,backtest},ingest}/` package tree with real implementations in formats / release / observability / tape; 7 import-linter contracts encoding subsystem boundaries from [resilience design §2](docs/design/resilience-and-subsystem-isolation.md); ruff + bandit + pytest with 80% coverage gate; `--disable-socket` default; self-hosted CI runner (`[self-hosted, special-herbs]`); release workflow.
- **F.** ✅ CLAUDE.md + [AGENTS.md](./AGENTS.md) + [docs/operations/cross-repo-coordination.md](docs/operations/cross-repo-coordination.md).

## Code Structure

Phase 0E shipped the package skeleton. `src/special_herbs/` already contains formats / observability / release / tape / ingest / training / eval / plv subdirectories, with real implementations in formats / release / observability / tape and stubs in the rest. Phase 1 fills out the remaining pipelines:

```
src/special_herbs/
  ingest/        # substrate-side data ingestion (FDA PDFs, NOAA, etc.)        — stub (Phase 1)
  training/      # LoRA training pipeline (likely Unsloth-based)               — stub (Phase 1)
  eval/          # measurement harness (binds to KG Golden Dataset)            — stub (Phase 1)
  release/       # artifact release pipeline (manifest builder, signer)        — implemented
  formats/       # manifest schema + verification utilities                    — implemented
                 #   (companion-package precursor; published separately as
                 #    special-herbs-formats once Vol. 1 ships)
  observability/ # structured event emission + assertions                      — implemented
  tape/          # frontier-API call recording + freshness checks              — implemented
  plv/           # Pre-Launch Validation gate orchestration                    — stub (Phase 1)
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
