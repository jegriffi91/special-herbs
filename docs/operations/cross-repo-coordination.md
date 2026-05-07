---
doc_id: SPECIAL-HERBS-CROSS-REPO-COORDINATION
title: "Cross-Repo Coordination Protocol"
status: active
created: 2026-04-28
related-docs:
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - ../architecture/ADR-0002-separate-repo-from-consumers.md
  - ../ROADMAP.md
related-repos:
  - https://github.com/jegriffi91/King-Geedorah (initial consumer)
---

# Cross-Repo Coordination Protocol

> When King Geedorah ships a phase that unblocks substrate work, or when Special Herbs releases a Volume that KG consumes, the protocol below is the convention. There is no automated cross-repo trigger — the operator is the integration point.

## When KG Ships a Phase That Unblocks Substrate Work

1. **KG side** opens a PR / merges a phase. Operator updates KG's `docs/ROADMAP.md` with the phase's settle status.
2. **Operator** references the new state in this repo's [`docs/ROADMAP.md`](../ROADMAP.md) (e.g., "Phase 13.1 ✅ shipped 2026-08-30, Vol. 1 design unblocked").
3. **Substrate side** then begins the corresponding Phase 0 / Phase 1 deliverable.

Specific KG → Substrate unblocking events:

| KG event | Unblocks substrate | Status |
|---|---|---|
| Phase 10 settle gate clears | Phase 0 exit (precondition) | ✅ operator override 2026-05-05 (full rationale mirrored in [`../ROADMAP.md`](../ROADMAP.md) §"Phase 0 — Preconditions") |
| Phase 11.2 Strategy-Scoped Signal Routing landed | Phase 0 exit (precondition) | ✅ shipped 2026-04-21 (KG commit `6f8906f`) |
| Phase 14.0 non-schema infra in dry-run | Phase 0 exit (precondition) | ✅ KG PRs #18/#19/#21 merged 2026-04-26/27 |
| Phase 11.4 + 14.0 strategy activation (22-day observation window) | Operational base for Vol. 2 (Area 4) | ✅ activated 2026-05-05; window D+0=2026-05-06 → D+22=2026-05-28 |
| Phase 14A.1-3 pm-event-mapper chain LIVE (KG PRs #140-#142) | First labeled Polymarket→equity dataset starts accumulating in `data/polymarket_event_mapper_log.db` | ✅ daemon registered 2026-05-06 20:34 PT, first cron 20:45 PT; ~30-50 resolved events expected by mid-June. **Substrate Area 4 (Vol. 2) data domain — not data source** — see [Dynamic-Universe Overlay + Polymarket Mapper Pathway](#dynamic-universe-overlay--polymarket-mapper-pathway) below for the ADR-0001 §4 ingestion split. |
| Dynamic-universe overlay cron live | Substrate Vol. N+ catalyst-class scoping must reason about overlay shape | ✅ overlays at `data/universe_overlays/<strategy>.json` are now a live contract (was preview-only); see pathway section below |
| Phase 12.1 Golden Dataset Regression Suite operational (per-strategy curator, ≥50 examples) | Vol. 1 MVA design (deliverable B) can start; substrate's Brier-baseline measurement harness binds to curator output | ~July 2026 |
| Phase 13.1 RLAIF Pipeline Validation passes | Phase 1 (Vol. 1 build) can start | ~late August 2026 |
| Phase 14A `moat_fda_equity_catalyst.yaml` deployed | Vol. 1 has a live consumer | post-Vol. 1 release |

## Volume Design Phase: Lock the LoRA's Input + Output Contracts to the Consuming KG Strategy

Substrate Volumes producing LoRA adapters must lock both the LoRA's **input shape** and **output schema** to the consuming KG strategy's actual runtime pipeline. Three architectural options for any given Volume, mapped against KG's existing infrastructure:

- **Option I — Alternative Commander.** Substrate's LoRA replaces or augments KG's Commander for the catalyst class the Volume targets. Input = same raw text chunks KG's Commander already consumes (e.g., pdfplumber output for FDA briefings, per KG Phase 14A.1). Output = same Commander-signature schema KG's downstream stack already consumes. Head-to-head Brier comparison is direct; no KG-side architectural change required.
- **Option II — Feature extractor.** Substrate's LoRA inserts a NEW layer between KG's raw-text source and KG's Commander, emitting a Pydantic structured-feature schema that Commander then consumes. Cleaner separation of concerns but requires a KG-side architectural change (Commander rewired to consume structured features instead of raw text).
- **Option III — Output calibrator.** Substrate's LoRA takes Commander's output as input and recalibrates the probability outputs against historical outcomes. Smallest blast radius but hardest to clear a meaningful Brier-reduction gate when Commander is already calibrated.

Vol. 1 picked **Option I** ([Special-Herbs#14 §13](https://github.com/jegriffi91/Special-Herbs/pull/14), 2026-05-05). Subsequent Volumes pick per-Volume; the Option choice belongs in each Volume's design doc.

Per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §7 the substrate is a feature extractor / scorer, never a decision-maker — Options I, II, III all satisfy that constraint at different layers of the pipeline. Empirical basis for the LLM-as-a-Feature-Extractor framing: `~/.claude/research_logs/2026-04-27_113300_kg-2yr-foundation-strategy/pro_angle2-llm-effectiveness.md` (Gemini Pro Deep Research, 2026-04-27).

Operator-driven handshake at the start of any Volume that ships a LoRA:

1. **Identify the consuming KG strategy** (Vol. 1 → `moat_fda_equity_catalyst.yaml`, etc.).
2. **Pick Option I / II / III** based on KG's actual runtime architecture for that strategy. Default Option I unless KG's existing pipeline already has a structured-feature schema layer (then Option II is natural) or unless the Volume's role is post-Commander recalibration (then Option III).
3. **Pin substrate training-data input shape to whatever Option implies.** Option I → raw text chunks (the same shape KG's Commander consumes); Option II → KG's structured-feature schema; Option III → `(briefing context, Commander output)` pairs. The no-synthetic-data rule still holds across all options — training data comes from real historical raw text, not substrate-fabricated examples.
4. **Pin substrate output schema to the consuming KG strategy's expectation.** For Option I this is the Commander-signature schema; for Option II it's the structured-feature schema; for Option III it's the recalibrated probability shape.
5. **Document any drift** (KG's pipeline shape changed; substrate's training data was assembled against an older shape) in the Volume's design doc and reconcile before training fires.

This is **not** a runtime API per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §3. The shape is copied (not imported) into substrate's training pipeline; substrate does not query KG at training time, and KG's runtime does not depend on substrate. The handshake is operator-driven, design-time only.

If the chosen Option requires KG-side infrastructure that doesn't yet exist (e.g., Option II against a catalyst class KG hasn't built a feature-extraction layer for), the Volume cannot enter training. The operator either (a) waits for KG to build it, (b) defers the Volume, (c) rescopes the Volume, or (d) picks a different Option that fits KG's actual current architecture.

## Dynamic-Universe Overlay + Polymarket Mapper Pathway

Two KG-side runtime data structures became live contracts on 2026-05-05/06 that any future Volume scoping a catalyst class against KG strategies must reason about. **Both are KG-internal runtime state. Substrate does NOT read either at training time** — that would violate [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §3 (no runtime API) and [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4 (no shared databases). They are documented here so substrate-side Volume design accurately reflects KG's pipeline shape.

### Universe overlays — `data/universe_overlays/<strategy>.json`

KG's per-strategy dynamic-universe screener writes a daily overlay JSON file per strategy under `data/universe_overlays/`. Each file lists the tickers that strategy is permitted to trade on a given date, derived from the screener cron's output. The overlay shape is what the consuming strategy's listener actually sees at runtime — strategies declare a wide static `target_universe` in their YAML and narrow it via the live overlay.

**Substrate-side implication for Volume design:**

- A Volume targeting catalyst class X for strategy Y must check Y's overlay file shape at design time to confirm the catalyst-class universe Y actually trades on. A Volume that scopes its training corpus to tickers Y will never see in production is a wasted training cycle.
- Overlay-shape changes are KG's call. Substrate-side Volume design does NOT pin against a specific overlay snapshot; the substrate trains on a universe-of-interest definition (sourced independently — see [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4) and trusts KG to apply the overlay at consumer-side ticker filtering.
- The overlay JSON is operator-readable for sanity-check at design time. **It is not substrate runtime input** — substrate's training pipeline must not import a path to a KG overlay file.

### Polymarket event-mapper LOG db — `data/polymarket_event_mapper_log.db`

KG's Phase 14A.1-3 chain (PRs #140-#142, daemon `geedorah-pm-event-mapper` first cron 2026-05-06 20:45 PT) maps Polymarket events to equity ticker candidates via a Bodega-routed DSPy signature, gated by a cross-source evidence score (Polygon-universe-membership hallucination guard + non-HOLD decision_log activity + signal_log volume + source diversity in a 72-hour lookback). Every emission appends to `data/polymarket_event_mapper_log.db`.

**This is the same data domain as substrate's Vol. 2 Area 4 cross-venue correlation matrix.** It is NOT, however, substrate's data source. Per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4, "duplicate ingestion is the accepted cost; coupling cost is not." For Vol. 2 design:

- Substrate writes its own Polymarket ingestion against the public Gamma API (or an equivalent public endpoint), independent of KG's ingest stack.
- Substrate writes its own event→equity mapping pipeline. The pipeline may converge on a similar architecture to KG's pm-event-mapper (a DSPy-style signature with a hallucination guard, etc.) without sharing code; per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §3, recipe sharing goes through a third package only when both projects already independently want it.
- KG's LOG db is operator-readable as a cross-validation reference at design time (compare substrate's mapper outputs against KG's, sanity-check rejection-rate parity). **It is not substrate runtime or training-time input.**

The mid-June ~30-50 resolved-event milestone in KG's LOG db is therefore a *KG-side* milestone. Substrate's own Vol. 2 first-data milestone is downstream of substrate's own ingestion pipeline, which has not yet been written.

Vol. 2 design (the formal scoping doc) lives at `docs/design/vol-2-area-4-data-consumption.md` once that file lands. That doc captures the substrate-side ingestion shape, the Option I/II/III choice for Area 4, and the conditional gating on Vol. 1 clearing its Brier gate.

## When the Substrate Releases a Volume

1. **PLV (Pre-Launch Validation) must pass.** Run the full PLV gate sequence per [`../design/resilience-and-subsystem-isolation.md` §8](../design/resilience-and-subsystem-isolation.md). All steps PASS, signed PLV report stored alongside the release. PLV failure halts the release; operator decides whether to fix and re-run, abort the volume, or amend the cycle config. **No exceptions** — there is no path from training output to published volume that bypasses PLV.
2. **Tag the release** in this repo: `git tag vol-1-fda-briefing-v1.0.0`.
3. **Publish the artifact + manifest** to the release location. Vol. 1 ships with local FS + manifests; revisit registry choice for Vol. 2+.
4. **Update KG's `moat_*.yaml` strategy manifest** with the SHA-pinned version (per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §2 — pins are explicit, never floating). Operator opens a KG-side PR.
5. **KG's deploy fires**; operator monitors KG-side metrics for the measurement gate (Brier reduction).

## When a Measurement Gate Fails

1. **Substrate side does NOT auto-rollback the release.** The artifact stays published; KG's strategy YAML simply doesn't pin it (or pins the prior known-good version, or unpins entirely and falls back to KG's own logic per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §5).
2. **Substrate side opens a postmortem** in `docs/research/postmortems/<vol>-<date>.md` capturing:
   - What was the measurement gate (target Brier reduction, actual Brier reduction).
   - What hypothesis the artifact embodied.
   - What the failure mode was (training data, eval-set distribution shift, base-model drift, integration error).
   - What the next cycle should change.
3. **Vol. N+1** either retries the same area with corrections or kills the area per the [ROADMAP](../ROADMAP.md) decision gates: ≥1.5% Brier reduction floor, ≥3% escalation gate by the third release.

Real outcomes from the consumer's settle gate become substrate-side training signal for the next cycle. Postmortems are how that signal converts to a documented trail for future operators / future Claude sessions.

## When KG-Side Documentation Drifts From Substrate Plans

Periodically the substrate's design documents reference KG state (phase numbers, strategy YAML names, ROADMAP sections) that has not yet been propagated to KG's repo. This is a known drift mode.

Resolution:

1. **Substrate side flags the drift** in the relevant deliverable's review (e.g., "Vol. 1 design references `moat_fda_equity_catalyst.yaml` which doesn't exist in KG yet").
2. **Operator decides** whether to push a KG-side ROADMAP update or to revise the substrate-side reference.
3. **Document the resolution** in the substrate's deliverable so future readers see the alignment.

Active drift items are tracked in [`kg-migration-plan.md`](kg-migration-plan.md) §7 — at present the only operator-blocking item is the YAML name drift (`moat_fda_equity_catalyst.yaml` vs `regulatory_event_contracts.yaml`), recommended for resolution when KG ships Phase 14A.4.

## Schedule Isolation

Each project's scheduler is sovereign per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md). KG runs its weekend training cron + settle-gate watchdog on its own PM2 stack. Substrate runs its per-volume training cycles on its own cadence. Neither schedule fires jobs in the other repo, reads the other repo's runtime state, or gates on the other repo's metrics.

Specifically:

- KG drift in a settle-gate metric does **not** auto-trigger a substrate retraining cycle. The operator notes the drift, opens a substrate-side issue if a new volume is warranted, and substrate's per-volume gate decides.
- A substrate volume release does **not** auto-trigger a KG redeploy. The operator opens a KG-side PR pinning the new version in the relevant `strategy_*.yaml` manifest. KG's own deploy hook fires from that PR.
- Substrate's training-progress state is invisible to KG. KG cannot read it, and substrate would not expose it even on request — runtime opacity is the point.

When workloads coexist on the same M2 Ultra (today's reality), coordination is operator-driven (manual scheduling, calendar-level decisions), not automated cross-process IPC. See [ADR-0003 §6](../architecture/ADR-0003-training-and-schedule-ownership.md) for process-isolation details.

## Hardware Coexistence: LoRA Training and Live MLX Inference

**Empirical constraint** (KG conversation `2264751e-42dc-43d9-a6ce-43cb5356a502`, 2026-04-30 — Gemini Deep Research Max on Apple Silicon concurrent inference):

> Apple's MLX framework is **not thread-safe** for concurrent generation. All MLX operations run on a single scheduler thread protected by `mlx_io_lock`. If a LoRA training script invokes its own `mlx.eval()` / generation loops while the KG inference server is decoding tokens, the Metal driver's `tryCoalescingPreviousComputeCommandEncoder` race condition triggers `SIGSEGV` and crashes both processes.
>
> Memory bandwidth is **not** the binding constraint (KG's `gpt-oss-120b` MoE uses ~25% of the M2 Ultra's 800 GB/s ceiling at 40 tok/s). The contention is in **Metal command queue management**, not in memory bandwidth or compute capacity.

**Implication for substrate Vol. 1 LoRA training schedule:**

1. **LoRA training cycles MUST run market-closed-only.** Specifically: weekends and overnight US-equity-market-closed windows. This is non-negotiable; any concurrency with live KG inference will crash both pipelines.
2. **The KG inference server must be quiesced or paused** during substrate training cycles that exercise MLX generation paths (e.g., evaluation runs over the LoRA-adapted model). Weight-loading and gradient-only steps are safer but still subject to the same Metal command-queue contention if MLX is involved.
3. **Operator coordination point**: substrate's training cron must check KG's market-state file (or equivalent calendar-aware gate) before launching cycles. KG side does not auto-yield; the substrate cycle must defer.
4. **Hardware refresh (M5 Ultra, 2026)** does not resolve this. The MLX threading constraint is software-level, not silicon-level. Workload separation remains mandatory regardless of generation.

**Specific scheduling rules:**

| Window | KG state | Substrate training? |
|---|---|---|
| Weekday 06:00–13:30 PT (pre-market + RTH) | Live inference, high event rate | ❌ Forbidden |
| Weekday 13:30–17:00 PT (post-market + after-hours) | Live inference, lower event rate | ❌ Forbidden (KG still active) |
| Weekday 17:00–06:00 PT (overnight) | Reduced inference (counterfactual backfill, EOD reports) | ⚠️ Permitted only if substrate cycle does not invoke MLX generation; weight-loading + gradient-only OK |
| Weekend (Friday 17:00 PT → Monday 06:00 PT) | Minimal inference (weekend training disabled per KG ROADMAP Phase 10) | ✅ Preferred window |

The substrate's per-volume training cycle should default to **weekend-only** unless a specific cycle is gradient-only and tightly latency-bounded (in which case overnight weekday is acceptable, but the operator must verify KG inference is idle before launch).

**Cross-link:** KG `docs/ROADMAP.md` Phase 10.9 documents the embedding-sidecar architecture (`fastembed` on E-cores) that introduces a third concurrent workload alongside the LLM. Substrate Vol. 1 therefore competes against TWO live workloads, not one. Schedule conservatively.

## Why No Automated Trigger

[ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §3 forbids runtime APIs between substrate and consumer. [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2 extends this to schedulers. The operator-as-integration-point is a deliberate consequence: it forces a human-readable handoff that lives in `git` history and the ROADMAP, rather than in webhook logs or a shared queue. Slow, intentional, auditable.

A future automation candidate is a scripted release-notification (substrate writes a release manifest path; consumer's CI lints `strategy_manifest.yaml` against published manifests). Even then, the trigger to pin a new version remains operator-driven — automation only catches mismatches, never picks versions.
