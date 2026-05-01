---
doc_id: SPECIAL-HERBS-ROADMAP
title: "Special Herbs — Substrate Roadmap"
status: active
created: 2026-04-28
related-docs:
  - architecture/ADR-0001-substrate-as-artifact-contract.md
  - architecture/ADR-0002-separate-repo-from-consumers.md
  - architecture/ADR-0003-training-and-schedule-ownership.md
  - operations/cross-repo-coordination.md
  - operations/kg-migration-plan.md
  - design/special-herbs-formats-api.md
  - design/resilience-and-subsystem-isolation.md
  - research/special-herbs-formats-design.md
  - research/vol-1-fda-ac-feasibility.md
  - research/paper-queue.md
related-repos:
  - https://github.com/jegriffi91/King-Geedorah (initial consumer)
---

# Special Herbs — Substrate Roadmap

> Each phase produces a versioned artifact ("Volume"). Each volume drops only when the prior volume clears its measurement gate. Stagnation in either area kills that area's investment.

## Naming Convention

| Phase | "Volume" Naming | What Drops |
|---|---|---|
| Phase 0 | Vol. 0 (Preconditions) | Read-the-room phase; no public artifact |
| Phase 1 | Vol. 1 (Area 1 MVA) | First LoRA adapter (FDA briefing docs domain) |
| Phase 2 | Vol. 2 (Area 4 first artifact) | First cross-venue correlation matrix |
| Phase 3+ | Vol. 3, Vol. 4, ... | Depth investments in surviving areas |
| Phase 4 | (no volume — meta) | Second consumer integration |

Volume numbers are append-only. A failed Vol. 1 still consumes the "Vol. 1" slot; the next attempt is Vol. 2.

---

## Phase 0 — Preconditions (no code work)

All four required before any substrate code work begins:

- [ ] King Geedorah Phase 10 settle gate closed (target ~2026-05-05)
- [ ] King Geedorah Phase 11.2 Strategy-Scoped Signal Routing landed
- [ ] King Geedorah Phase 14.0 non-schema infra in dry-run on Polymarket / Kalshi (already shipped via PR #18, #19, #21)
- [ ] Operator has read 30+ papers across Areas 1 and 4 research directions

### Action — 2026-05-05 settle-gate check

On 2026-05-05 (or the first business day on/after):

**1. Pre-flight — confirm the KG breach DB exists.** `sqlite3` silently creates an empty file at a missing path, so an empty result from a missing DB is indistinguishable from a clean settle:

```bash
ls -la /Users/jamesgriffin/dev/king-geedorah/data/quality_gate_breaches.db
```

If the file is absent, do NOT tick any box; diagnose KG-side first.

**2. Run the canonical query** documented in [`CLAUDE.md`](../CLAUDE.md) §"KG settle-gate quick check (7-day window)".

**3. Empty result** → before ticking the Phase 10 box, also:

  - **(a) Suppressed-breach sanity check.** Confirm the suppressed count is in line with the 2026-04-30 baseline of 45 rather than spiking — a sudden suppression jump with a clean unsuppressed result means someone may have suppressed their way to clean:

    ```bash
    sqlite3 /Users/jamesgriffin/dev/king-geedorah/data/quality_gate_breaches.db \
      "SELECT COUNT(*) FROM quality_gate_breaches \
       WHERE evaluated_at >= datetime('now', '-7 days') \
       AND settle_gate_suppressed = 1;"
    ```

  - **(b) KG ROADMAP secondary verification.** Read KG `docs/ROADMAP.md` §"Phase 10 — Settle gate" and confirm the four `[ ]` boxes are now `[x]`. If they aren't, do NOT tick the substrate box until KG's own Phase 10 reflects completion.

  If both (a) and (b) pass, tick the Phase 10 box above and commit with a message of the form `docs: tick Phase 10 settle-gate precondition (clean 7-day window 2026-04-29..2026-05-05)`.

**4. Non-empty result** → leave the Phase 10 box unchecked. Add a dated note directly below the Phase 10 checkbox line, format `  - 2026-05-05 check: N unsuppressed breaches; dominant: <metric>/<severity>; re-evaluate 2026-MM-DD`. Commit that note alone with a message of the form `docs: record Phase 10 settle-gate check result (N breaches, re-evaluate 2026-MM-DD)`. The settle gate is a *trailing* signal — a single fresh breach within the window pushes the precondition out at least 7 days.

**Either way** — the Phase 11.2, Phase 14.0, and 30+ papers boxes are independent of this query; do not touch them in the same commit.

**Baseline established 2026-04-30:** trailing 7-day query returned 22 unsuppressed breaches (3 SEV-1, dominated by `scout_parse_rate` SEV-1 ×23). 30-day weekly trend 561 → 1,655 → 60. Settle clock restarted 2026-04-21; gate appears on track but not yet clean as of the baseline date.

**During Phase 0:** design documents, ADRs, repo scaffold, and reading. No production code.

**Phase 0 exit criterion:** all four boxes checked. Kick off Vol. 1 design work.

---

## Phase 1 — Vol. 1: Area 1 Minimum Viable Artifact (~3 months post-preconditions)

**Estimated start:** post-KG-Phase-13.1 validation (~late August 2026).

**Domain:** FDA briefing documents. Selected because (a) lowest cold-start cost (one ingestion source, no multi-venue infrastructure), (b) clean first consumer in KG's `moat_fda_equity_catalyst` strategy, (c) aligns with operator's agentic-architecture interest.

**Deliverable:** one fine-tuned LoRA adapter on FDA Advisory Committee briefing documents. Loaded into KG's Gateway alongside KG's own RLAIF-trained adapters via multi-LoRA serving.

**Architecture:**
- Source: FDA Advisory Committee briefing PDFs (already ingested by KG via `data_ingestion/fda_briefing_source.py`).
- Training: structured-output extraction task (event metadata, decision likelihood, evidence summary).
- Format: LoRA adapter (Qwen / Llama base, ~3.6% of base model parameters trained).
- Release: SHA-tagged, signed manifest, semantic version (`special-herbs-vol-1-fda-briefing-vN`).

**Consumer contract** (per [ADR-0001](architecture/ADR-0001-substrate-as-artifact-contract.md)):
- Consumer (KG `moat_fda_equity_catalyst`) pins `vol-1-fda-briefing-vN` at startup.
- Consumer falls back to KG's own Commander reasoning if the adapter is unavailable.
- No runtime queries from consumer to substrate. Consumer reads from local disk only.

**Decision gate:** does Vol. 1 measurably improve KG's catalyst-decision quality on backtested data?
- **Pass:** Brier reduction ≥1.5% on KG's existing settle-gate metrics for the consuming strategy.
- **Phase 2 escalation gate:** ≥3% Brier reduction. If Vol. 1 only clears 1.5%, the area lives but is on probation; if Vol. 2+ doesn't escalate to ≥3% by the third release, kill the area.
- **Fail:** below 1.5% Brier reduction → kill Area 1, attempt Area 4 instead, or stop substrate investment entirely.

---

## Phase 2 — Vol. 2: Area 4 First Artifact (~3 months, conditional on Vol. 1)

**Domain:** TBD — likely Polymarket weather contracts × NOAA forecasts (Polymarket read-only access approved per KG roadmap Decision #5; Polymarket trading remains banned). Or Kalshi macro contracts × CME futures lead-lag.

**Deliverable:** pairwise correlation matrix between two venues. Surfaced as confidence-adjustment features for KG's `moat_kalshi_tail_risk_maker` strategy.

**Decision gate:** same lift threshold (≥1.5% Brier reduction or equivalent IC delta on the consuming strategy). If only one of Areas 1 / 4 produces consumer value, the other is killed and the surviving area gets all further depth investment.

---

## Phase 3 — Vol. 3+: Depth in Surviving Areas (~6-12 months, conditional)

For whichever area(s) cleared Vol. 1 / Vol. 2:

- More domains covered (Vol. 3, Vol. 4, ...)
- More LoRA adapters trained per domain
- Knowledge graph / correlation matrix coverage broadens
- Artifact release cadence stabilizes (target: monthly minor versions, quarterly major versions)
- KG consumption deepens; multiple KG strategies pin substrate volumes
- Substrate begins accumulating its own ground-truth dataset independent of any single consumer

**Decision gate (per cycle):** does substrate quality continue improving cycle-over-cycle, with measurable downstream consumer impact? Stagnation across 2+ consecutive volumes → kill that area or pause substrate entirely.

---

## Phase 4 — Second Consumer (conditional, far future)

Only if substrate has demonstrated durable value to KG over 12+ months. A second consumer (a sister system, research tooling, or external collaborator) integrates against the same artifact contract.

The substrate is self-justified by KG at this point; second-consumer investment is incremental upside, not load-bearing. The consumer contract has been proven across a single consumer over time.

---

## Cross-Repo Dependencies

| Substrate Phase | Requires KG State |
|---|---|
| Phase 0 preconditions | KG Phase 10 settle + KG Phase 11.2 Strategy-Scoped Signal Routing landed |
| Phase 1 (Vol. 1) | KG Phase 13.1 RLAIF Pipeline Validation passed |
| Phase 1 measurement | KG Phase 12.1 Golden Dataset Regression Suite operational |
| Phase 1 consumer integration | KG `moat_fda_equity_catalyst.yaml` deployed |
| Phase 2 (Vol. 2) | KG Phase 14.0 prediction-market provider live (Kalshi-only for execution; Polymarket read-only for correlation research) |

---

## Open Decisions

1. **Base model.** Qwen vs. Llama vs. mixed. Defer until Phase 1 design begins; the choice may differ per area.
2. **LoRA training framework.** Unsloth (already used by KG) vs. native PyTorch + PEFT vs. MLX. Likely Unsloth for cross-repo consistency with KG's training pipeline.
3. **Artifact distribution.** The manifest *format* is locked: Pydantic JSON + safetensors + detached Ed25519 signature, packaged as `special-herbs-formats` (see [`design/special-herbs-formats-api.md`](design/special-herbs-formats-api.md) for the design and [`research/special-herbs-formats-design.md`](research/special-herbs-formats-design.md) for the literature triangulation). What remains open is the *distribution* mechanism: local filesystem (Vol. 1 default) vs. GitHub Releases vs. S3 / R2 vs. Hugging Face Hub. Defer until Vol. 2; Vol. 1 ships local FS + manifests.
4. **External publication of artifacts.** Probably not — features are alpha. Re-evaluate if a research-collaboration opportunity surfaces.
5. **Catastrophic-forgetting policy.** Inherit KG's RLAIF guardrails; adapt for substrate's different reward signal shape (information value vs. trade outcome).

---

## Honest Caveats

- **The substrate may not produce alpha.** Research systems can be intellectually impressive without producing PnL improvements. The decision gates exist specifically to kill areas that fail this test.
- **18 months is short.** Even with the substrate framing, swisstony-class outcomes are 30-48+ months out. Substrate accelerates accumulation but doesn't transform it.
- **Consumer discipline is required.** It's tempting to live-couple consumers to substrate. The artifact-only contract has to be enforced by ADR-0001.
- **Domain selection still matters.** Even with the substrate framing, scattering across 6 domains dilutes the moat. Phase 1 picks one (FDA briefing docs); Phase 3 expands carefully.

---

## See Also

### Architecture (binding)

- [`architecture/ADR-0001-substrate-as-artifact-contract.md`](architecture/ADR-0001-substrate-as-artifact-contract.md) — substrate-as-artifact contract; the eight foundational rules
- [`architecture/ADR-0002-separate-repo-from-consumers.md`](architecture/ADR-0002-separate-repo-from-consumers.md) — filesystem-level separation from consumer repos
- [`architecture/ADR-0003-training-and-schedule-ownership.md`](architecture/ADR-0003-training-and-schedule-ownership.md) — training pipeline + schedule ownership boundaries

### Operations

- [`operations/cross-repo-coordination.md`](operations/cross-repo-coordination.md) — KG ↔ substrate handoff protocol; release sequence; postmortem flow
- [`operations/kg-migration-plan.md`](operations/kg-migration-plan.md) — per-doc migration verdict for KG `docs/exploration/` Area 1 / Area 4 material + ADR-0003 boundary audit (Phase 0 deliverable D)

### Design (substrate-internal)

- [`design/special-herbs-formats-api.md`](design/special-herbs-formats-api.md) — companion package's API + manifest schema (Phase 0 deliverable C)
- [`design/resilience-and-subsystem-isolation.md`](design/resilience-and-subsystem-isolation.md) — testing / backtest / tape / logging / PLV design

### Research synthesis

- [`research/paper-queue.md`](research/paper-queue.md) — Phase 0 reading queue, 71 verified entries across Areas 1 & 4 (Phase 0 deliverable A)
- [`research/vol-1-fda-ac-feasibility.md`](research/vol-1-fda-ac-feasibility.md) — Vol. 1 prompt-only baseline + LoRA feasibility from a 3-source Gemini DR triangulation
- [`research/special-herbs-formats-design.md`](research/special-herbs-formats-design.md) — manifest format + signing literature triangulation
- Source synthesis: `~/.claude/research_logs/2026-04-28_112632_kg-moat-substrate-selection/`

### Related repos

- King Geedorah `docs/ROADMAP.md` — consumer-side phases, including the Phase 13.1 dependency
- King Geedorah `docs/exploration/area-1-agentic-information-synthesis.md` — Area 1 architecture detail; migration plan in [`operations/kg-migration-plan.md`](operations/kg-migration-plan.md) §1, executes post-KG-Phase-13.1
- King Geedorah `docs/exploration/area-4-cross-domain-signal-networks.md` — Area 4 architecture detail; migration plan in [`operations/kg-migration-plan.md`](operations/kg-migration-plan.md) §1, executes post-KG-Phase-13.1
