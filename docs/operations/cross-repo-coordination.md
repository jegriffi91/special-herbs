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

| KG event | Unblocks substrate | Earliest expected |
|---|---|---|
| Phase 10 settle gate clears | Phase 0 → can start design work | ~2026-05-05 |
| Phase 11.2 Strategy-Scoped Signal Routing landed | Phase 0 exit precondition | ~2026-06 |
| Phase 12.1 Golden Dataset Regression Suite operational | Phase 0 deliverable B (Vol. 1 MVA design) can start | ~2026-07 |
| Phase 13.1 RLAIF Pipeline Validation passes | Phase 1 (Vol. 1 build) can start | ~late 2026-08 |
| Phase 14A `moat_fda_equity_catalyst.yaml` deployed | Vol. 1 has a live consumer | post-Vol. 1 release |

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

## Why No Automated Trigger

[ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §3 forbids runtime APIs between substrate and consumer. [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2 extends this to schedulers. The operator-as-integration-point is a deliberate consequence: it forces a human-readable handoff that lives in `git` history and the ROADMAP, rather than in webhook logs or a shared queue. Slow, intentional, auditable.

A future automation candidate is a scripted release-notification (substrate writes a release manifest path; consumer's CI lints `strategy_manifest.yaml` against published manifests). Even then, the trigger to pin a new version remains operator-driven — automation only catches mismatches, never picks versions.
