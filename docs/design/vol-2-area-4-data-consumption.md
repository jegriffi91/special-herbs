---
doc_id: SPECIAL-HERBS-VOL-2-AREA-4-SCOPE
title: "Vol. 2 (Area 4 Cross-Venue Correlation) — Data Consumption Scope"
status: scoping-only
created: 2026-05-06
related-docs:
  - ../ROADMAP.md
  - ../operations/cross-repo-coordination.md
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - ../architecture/ADR-0003-training-and-schedule-ownership.md
  - ../design/special-herbs-formats-api.md
  - ../design/lora-and-frontier-model-distribution.md
related-repos:
  - "King Geedorah Phase 14A.1-3 pm-event-mapper (KG PRs #140-#142)"
  - "King Geedorah `data/polymarket_event_mapper_log.db` (data domain reference, NOT substrate input)"
---

# Vol. 2 (Area 4 Cross-Venue Correlation) — Data Consumption Scope

> Pre-design scope note. Vol. 2 is conditional on Vol. 1 clearing its ≥1.5% Brier-reduction gate per [ROADMAP §"Phase 2"](../ROADMAP.md). This doc captures the substrate-side ingestion shape, the artifact contract, and the Vol. 1 / KG dependencies so design work can fire fast when Vol. 1 clears. **No commitment yet — scope only.**

## 1. Why this doc exists now

KG's Phase 14A.1-3 pm-event-mapper chain went LIVE 2026-05-06 (KG PRs #140-#142, daemon registered 2026-05-06 20:34 PT). KG is now accumulating Polymarket-event → equity-ticker mappings in `data/polymarket_event_mapper_log.db`. ~30-50 resolved events expected by mid-June.

**This is the same data domain as substrate Vol. 2 Area 4 (cross-venue correlation matrix).** It is NOT, however, substrate's data source — per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4 substrate ingests Polymarket independently. This doc disambiguates what substrate does and doesn't read at training time, so Vol. 2 design (when it fires) inherits a clean boundary instead of having to re-derive it.

This doc is **not**:

- A Vol. 2 design doc. That lands when Vol. 1 clears its gate (~Q4 2026 if all goes well).
- A Vol. 2 commitment. Vol. 2 can still be killed by Vol. 1 failure or by a substrate-side decision to invest depth into Area 1 instead.
- A KG-side ask. Nothing in this doc requests KG-side work.

## 2. The artifact-only contract for Vol. 2

Vol. 2 is the substrate's first non-LoRA artifact. The Volume Design Phase Option I/II/III framing in [`../operations/cross-repo-coordination.md`](../operations/cross-repo-coordination.md) was developed for LoRA-style scorers; Vol. 2 ships a **data artifact** (correlation matrix) instead.

The artifact-only contract per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) still applies unchanged:

- Versioned, immutable, SHA-tagged signed manifest (per [`special-herbs-formats-api.md`](special-herbs-formats-api.md)).
- KG pins SHA at startup and degrades gracefully if missing.
- No runtime API between substrate and KG.

The new artifact_type literal (`correlation_matrix`) is already reserved in the formats schema ([`special-herbs-formats-api.md` §"Manifest Schema"](special-herbs-formats-api.md)). Per-type metadata extensions (e.g., venue list, time-window declaration) are flagged as a Vol. 2-time deferred decision in that doc's §"Open Questions Deferred Beyond Phase 0".

In Option-framework spirit, Vol. 2 is closest to **Option II (feature extractor)** — substrate emits structured features (correlation coefficients, lead-lag deltas, divergence scores) and the consuming KG strategy's deterministic scorer applies them. But the framing isn't a perfect fit because there's no LLM doing extraction: the substrate computes correlations from numeric inputs. Better label: **"feature publisher"** — substrate publishes a versioned features artifact, consumer reads it.

## 3. Substrate's independent ingestion stack

Per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4 ("duplicate ingestion is the accepted cost"), substrate writes its own ingestion. Three input streams Vol. 2 needs:

| Stream | Source | Why substrate-owned |
|---|---|---|
| Polymarket events (CLOB or Gamma API) | Public Polymarket Gamma API directly | KG's `PolymarketEventSource` writes to KG's Redis `leads_raw` stream — that's KG runtime state; substrate must not read it. Public Gamma API is free + rate-limited; appropriate for substrate's batch ingestion cadence. |
| Polygon equity OHLCV | Polygon REST API directly | KG also reads Polygon for the dynamic-universe screener; both projects independently consume per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4. Same upstream source, separate connections. |
| Polymarket event → equity ticker mapping | Substrate writes its own mapper | KG's pm-event-mapper LOG db is the same data domain; per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §3 substrate writes its own. May converge on a similar architecture (DSPy signature + universe-membership hallucination guard) without sharing code. Recipe sharing lands in a third package only when both projects independently want it. |

**Substrate-side ingestion footprint estimate (Phase 1-budget terms):**

- Polymarket Gamma API: free; rate-limited to a manageable QPS; pure-batch ingestion runs on weekends per [`cross-repo-coordination.md` §"Hardware Coexistence"](../operations/cross-repo-coordination.md).
- Polygon API: paid (substrate would need its own subscription, or share KG's subscription via operator-tier billing — clarification needed at design time).
- Mapper LLM calls: routed through DOOMBot Gateway with a substrate `workflowId` per [`lora-and-frontier-model-distribution.md` §6](lora-and-frontier-model-distribution.md). Gateway-budget reservation at the substrate Vol. N level (currently `sh-vol-N-rlaif-teacher: $5/month` placeholder; Vol. 2 may need its own line item).

**What substrate ingestion DOES NOT touch:**

- KG's `data/polymarket_event_mapper_log.db` (KG runtime state).
- KG's Redis `leads_raw` / `pm_event_mapper:<event_id>` cache (KG runtime state).
- KG's `data/signal_log.db` / `decision_log.db` (KG runtime state).
- KG's `data/universe_overlays/<strategy>.json` (KG runtime state; substrate uses its own universe definition).

The substrate's ingestion stack is wholly independent. The KG LOG db is at most an operator-driven cross-validation reference at design time — compare substrate's mapper hallucination-rejection rate against KG's, sanity-check mapper-confidence distribution alignment, etc.

## 4. The Vol. 2 artifact shape (sketch)

Vol. 2's first release is conjectured to be a **monthly correlation matrix** keyed on `(polymarket_event_id, equity_ticker, time_window)` with cells holding correlation / lead-lag / divergence scores. The matrix is the artifact bundle:

```
release/vol-2-pm-equity-correlations-v1.0.0/
├── manifest.json              # Pydantic-validated; only this is signed
├── manifest.json.minisig      # Detached Ed25519 signature
├── correlation_matrix.parquet # the matrix itself (sparse, columnar)
├── event_index.parquet        # event_id ↔ event metadata
├── ticker_index.parquet       # ticker ↔ Polygon canonical metadata
└── methodology.md             # how correlations were computed; pinned at this version
```

The matrix is read-once at consumer startup (per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §3 — no runtime API). Subsequent matrix updates are released as new artifact versions; consumers re-pin via strategy-YAML edit.

**Open at Vol. 2 design time:**

1. **Time-window granularity.** Daily, weekly, or per-resolved-event windows? Each has different sample-size + signal-decay tradeoffs. Decide empirically once substrate has its own ingested dataset.
2. **Correlation method.** Pearson on log-returns, Spearman rank, Kendall tau, or a probit copula? Domain-dependent; defer to Vol. 2 design.
3. **Lead-lag dimensions.** Polymarket → equity (does PM resolve before/after equity moves?), or symmetric? KG's `prediction_market_arb` strategy will dictate which direction matters at consumer-side.
4. **Sparse encoding.** Most (event, ticker) pairs are uninformative; matrix is naturally sparse. Parquet with row-group pruning is the obvious encoding but COO/CSR variants may win at scale.

## 5. Decision gate (Vol. 2-specific)

Same `≥1.5% Brier reduction or equivalent IC delta` floor as Vol. 1, applied to the consuming KG strategy. Per [ROADMAP §"Phase 2"](../ROADMAP.md), the initial consumer is `prediction_market_arb` (Phase 14.0 — activated 2026-05-05 with the 22-day observation window); `moat_kalshi_tail_risk_maker` deferred to Vol. 3+.

Vol. 2 is on the same kill/escalate criterion as Vol. 1: ≥3% Brier reduction by the third release in the area or the area is killed.

**Pre-Vol-2 ablation question:** what is the Brier baseline for `prediction_market_arb` *without* substrate features? KG's settle-gate metrics on the strategy provide this once the 22-day observation window closes (2026-05-28 for the initial pass; longer for stable ground truth). Vol. 2 design therefore can't fire any earlier than ~late June 2026 even if Vol. 1 cleared its gate before then.

## 6. First-data milestone (substrate side, NOT KG side)

The brief from KG says ~30-50 resolved Polymarket events accumulated in the KG LOG db by mid-June. **That is a KG-side milestone**, not substrate's. Substrate has no ingestion pipeline yet and will not reach a comparable milestone until:

1. Substrate writes its own Polymarket Gamma API ingestion (~1-2 weeks Phase 1-pre-Vol-2 work).
2. Substrate writes its own equity ingestion + alignment (~1-2 weeks).
3. Substrate writes its own event→ticker mapper (~2-4 weeks; KG's PR #140-#142 is a useful architectural reference, not a code source per ADR-0003 §3).
4. Substrate accumulates enough Polymarket→equity resolved events to compute correlations on (~30+ events minimum; depends on event-resolution cadence).

End-to-end first-data realistic estimate: **2-3 months from "Vol. 2 design fires" to first labeled correlation dataset.** Vol. 2 design fires only after Vol. 1 clears its gate. So substrate's first Vol. 2 data is ~3-6 months after Vol. 1 lands.

This is consistent with the ROADMAP's "Phase 2 — Vol. 2: ~3 months, conditional on Vol. 1" line. The mid-June KG-side milestone is irrelevant to substrate's clock; it's surfaced here because the operator may use it as a cross-validation reference at substrate-side mapper-design time.

## 7. Cross-repo independence reminders

Restating because the data-domain overlap with KG's pm-event-mapper makes coupling temptations easy to fall into:

| Tempting pattern | Why forbidden | Correct alternative |
|---|---|---|
| "Substrate just SELECTs from KG's `polymarket_event_mapper_log.db` to bootstrap Vol. 2 training data" | Shared DB forbidden per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4; substrate runtime read of KG's runtime state forbidden per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2 | Substrate writes own Polymarket Gamma ingestion + own mapper. KG LOG db remains operator-readable for design-time cross-validation only. |
| "Substrate imports KG's `PolymarketEventMapperSignature` to avoid re-deriving the prompt + guard" | Cross-repo import forbidden per [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md) §"What Stays Out" + [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §3 anti-temptation list | Substrate independently writes its own DSPy signature. If both projects converge on a pattern AND both already independently want a shared pattern, it goes through `special-herbs-mapper-recipes` (hypothetical third package) per ADR-0003 §3. |
| "Substrate triggers a re-train when KG's pm-event-mapper hallucination-rejection rate spikes above 5%" | Schedule isolation violated per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2; substrate reading KG runtime state forbidden | Operator notes drift, opens a substrate-side issue, substrate's per-Volume gate decides. |
| "Substrate's correlation matrix uses KG's `data/universe_overlays/prediction_market_arb.json` to constrain ticker scope" | Substrate runtime read of KG runtime state | Substrate maintains its own universe definition (e.g., S&P 500 + Russell 2000 baseline) and trusts KG to apply consumer-side overlay filtering at trade time. |

## 8. Open questions

These are real and need operator decisions before Vol. 2 design fires. Not blocking this scope doc landing.

1. **Polymarket Gamma API rate-limit headroom.** Free tier is rate-limited; substrate's batch ingestion needs to fit within those limits without escalating to paid. Verify at Vol. 2-design start.
2. **Polygon subscription model.** Substrate buys its own subscription, or operator-tier-billed shared subscription? KG already pays for Polygon; clarification needed on whether the same subscription covers substrate's separate consumption per Polygon's Terms of Service.
3. **Mapper LLM cost line.** Substrate's own pm-event-mapper-equivalent will burn DOOMBot Gateway tokens via a `sh-vol-2-mapper` workflowId. Need to add this to Gateway's per-workflow registry alongside `sh-vol-N-rlaif-teacher`. Likely $3-5/month placeholder, refine after first ingestion cycle.
4. **Whether Vol. 2 ships as a single matrix or as a streaming-update artifact.** Per ADR-0001 §1 artifacts are immutable, so streaming updates means new artifact versions every time. Acceptable cadence: monthly, weekly, daily? Probably monthly for Vol. 2; revisit at Vol. 3.
5. **Backtest harness for Vol. 2.** [Resilience design §6](../design/resilience-and-subsystem-isolation.md) mandates a read-only backtest harness for every Volume. Backtest cohorts for correlation matrices look different from LoRA-eval cohorts (time-windowed slices vs single-shot extraction); design when Vol. 2 fires.
6. **Forecasting vs descriptive.** Is Vol. 2 a *descriptive* artifact (here are correlations as observed) or a *forecasting* artifact (here are correlations expected next period)? Forecasting introduces eval-leakage concerns similar to Vol. 1's chronological-split mandate. Default descriptive for v1.0.0; revisit.

## 9. What this doc is NOT

- A commitment to Vol. 2. Vol. 2 only fires if Vol. 1 clears its gate.
- A KG-side ask. Nothing here requests KG work.
- An ingestion design. The actual ingestion code design lives in the Vol. 2 design doc when Vol. 2 fires.
- A correlation-method choice. §4 lists candidates; Vol. 2 design picks empirically.

## 10. See Also

- [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4 — duplicate ingestion is the accepted cost; no shared databases.
- [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §1 topology matrix; §2 schedule isolation; §3 third-package recipe pattern; §5 anti-temptation list.
- [`../ROADMAP.md`](../ROADMAP.md) §"Phase 2 — Vol. 2: Area 4 First Artifact" — Vol. 2 framing, decision gate, cross-repo dependency table.
- [`../operations/cross-repo-coordination.md`](../operations/cross-repo-coordination.md) §"Dynamic-Universe Overlay + Polymarket Mapper Pathway" — the KG-side data structures Vol. 2 design must reason about.
- [`special-herbs-formats-api.md`](special-herbs-formats-api.md) §"Manifest Schema" — `correlation_matrix` is a reserved `ArtifactType`; per-type metadata extensions deferred to Vol. 2 design.
- [`lora-and-frontier-model-distribution.md`](lora-and-frontier-model-distribution.md) §6 — DOOMBot Gateway per-workflow cap reconciliation; Vol. 2 mapper LLM call routing.
- KG `docs/ROADMAP.md` §14A.1-3 — KG-side pm-event-mapper architecture (informational, not a substrate dependency).
- KG `openclaw_workspace/signatures/polymarket_event_mapper.py` — KG's mapper DSPy signature (informational reference for substrate's own design; not a code import per ADR-0002 §"What Stays Out").
