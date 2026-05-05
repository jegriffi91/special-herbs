---
doc_id: LORA-FRONTIER-DISTRIBUTION
title: "LoRA + Frontier Model Distribution Across KG, SH, and DOOMBot"
status: draft
created: 2026-05-04
related-docs:
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - ../architecture/ADR-0003-training-and-schedule-ownership.md
  - ../operations/cross-repo-coordination.md
  - ./resilience-and-subsystem-isolation.md
  - ../research/training-recipe-comparative.md
related-repos:
  - "DOOMBot Gateway: ~/dev/doombot/backend-gateway/"
  - "King Geedorah: ~/dev/king-geedorah/"
---

# LoRA + Frontier Model Distribution Across KG, SH, and DOOMBot

> Systems-architecture map for where every LoRA in the joint Special-Herbs + King-Geedorah system runs, where frontier APIs are invoked, and what each layer commits to vs leaves open. Drafted 2026-05-04 from direct reads of DOOMBot Gateway code, KG's `slippage-measurement-phase-a.md`, KG's `docs/ROADMAP.md`, and the substrate's existing ADR set.

## 1. Goal

Pin down the architectural distribution before debating training recipes for individual adapters. The training-recipe choice (ORPO vs GRPO vs GiGPO etc.) is *downstream* of this map; locking the distribution first prevents debating recipes for adapters whose role isn't pinned. Three audiences:

1. **Substrate operators (today + future)** — what role does Vol. N actually play in the consumer's runtime decision path
2. **Substrate-side reviewers at PR time** — does this PR respect the boundary the architecture defines
3. **Future Claude / future operator** — when this conversation is gone, what prevents re-litigating decisions whose answers are already embedded in code

This doc is descriptive of the architecture as it actually exists in code today, with explicit flags for the parts that are *planned* but not yet built.

## 2. The seven layers

Concrete table with component names + verifiable file paths:

| # | Layer | Component | Owner | What it does | Real today? |
|---|---|---|---|---|---|
| L0 | Routing | DOOMBot Gateway @ `localhost:3000` | DOOMBot | All LLM traffic from KG and SH MUST route through here per `~/dev/doombot/AGENTS.md` "Inference Gateway Mandate" | Yes |
| L1 | Frontier APIs | Gemini engine | DOOMBot (`backend-gateway/src/engines/gemini.engine.ts`) | Outbound calls to Google Gen AI. Used as RLAIF teacher, runtime feature extractor, debate critic | Yes — Gemini only |
| L2 | Local base models | Bodega @ `localhost:44468` (private) | DOOMBot (`backend-gateway/src/engines/bodega.engine.ts`) | OpenAI-compatible local inference. Default model is `bodega-raptor-8b-mxfp4`; `gpt-oss-120b` loads on demand for KG Commander | Yes |
| L3a | KG-internal LoRAs | Commander, Scout, future strategy-scoped adapters | KG (`mlops/`, training cycles fire weekend cron) | Trade-decision generation on already-extracted features (Commander), pre-screen / triage (Scout) | Yes |
| L3b | Substrate-produced LoRAs | SH Vol. 1 FDA briefing LoRA, future Vol. 2+ | SH (training); KG (runtime via pinning per ADR-0001 §2) | Narrow-task scoring on per-Volume domain (Vol. 1 = FDA briefings) | No — pre-Phase-1 |
| L4 | Multi-LoRA composition | KG Gateway adapter-load logic | KG (per ADR-0003 §1) | Loads SH artifacts alongside KG-internal LoRAs with declared weights / order / fallback | Yes for KG-internal adapters; SH adapters not yet pinned |
| L5 | Classical scorers | XGBoost / LSTM / rules on top of LLM outputs | KG (`feedback_loops/`, `risk_manager/`) | Apply guardrails, calibration, position sizing on top of the LLM-stage output | Yes |
| L6 | Decisions | Commander rails, Cloud CIO debate, broker routing | KG (`execution_layer/`, `openclaw_workspace/`) | Final trade decisions; lifecycle event emission per `decision_lifecycle_events` table (Phase 12.7.1) | Yes for routing; lifecycle telemetry at A.1 stage |

Two boundaries from this table that are non-obvious:

- **L0 is mandatory for both projects.** KG's existing `cloud.controller.ts` and SH's future RLAIF-teacher path both terminate at the same gateway. Direct-to-Bodega calls and direct-to-frontier-API calls are forbidden by DOOMBot's AGENTS.md.
- **L3b is what the substrate is for.** Everything else exists today on the KG side or DOOMBot side. The substrate's only artifact in this stack is the Vol. N LoRA released to L4.

## 3. LoRA inventory

| LoRA | Owner | Training method | Runtime base | Role | Status |
|---|---|---|---|---|---|
| **KG Commander** | KG | Currently ORPO (`mlops/pipelines/orpo_pipeline.py`); migration to GRPO/GiGPO under consideration per slippage-doc §10.2 | gpt-oss-120b (local via Bodega) | Trade-decision generation on already-extracted features | Operational |
| **KG Scout** | KG | (KG-side detail; per slippage-doc §10.2 / KG ROADMAP) | 21B-class (local) | Pre-screen / triage of catalysts | Operational |
| **KG strategy-scoped adapters** | KG | Per-strategy ORPO with `strategy_id` filter (Phase 11+); `WEIGHT_UPDATE` strategies only | (per-strategy) | Per-strategy specialization | Phase 11+ rollout in progress |
| **SH Vol. 1 FDA briefing LoRA** | SH | TBD pending §7 resolution; `training-recipe-comparative.md` recommends SFT+ORPO if scorer | 7B-class (Llama / Qwen / Mistral — TBD) | **Open.** See §7 — scorer, extractor, or calibrator | Pre-design (Phase 1, ~Aug 2026) |
| **SH Vol. 2+** | SH | Per-Volume | Per-Volume | Per-Volume | Conditional on Vol. 1 clearing measurement gate |

## 4. Frontier-model role inventory

Four distinct uses; **the cost discipline applies differently to each.**

| Use | Where | Provider today | Cost-discipline rule | Owner of the call |
|---|---|---|---|---|
| **(a) RLAIF teacher** at training time | KG-side training cycles + (future) SH-side training cycles | Gemini via Gateway | KG: KG-side budget. SH: `<$50/cycle` per AGENTS.md "Cost Discipline" | The training pipeline that's being graded |
| **(b) Feature extractor** at consumer runtime | KG-side only (per Volume Design Phase handshake) | Gemini via Gateway — **but see §7: this layer doesn't exist yet for FDA** | KG-side budget; explicitly out of scope for substrate's cost rule | KG runtime |
| **(c) Adversarial debate critic** (Cloud CIO) | KG-side runtime | Gemini via Gateway (per slippage-doc §12.7.5 Cloud CIO debate loop) | KG-side budget | KG runtime |
| **(d) Bounded research / DR sweeps** | Operator-side, manual | Gemini Deep Research | Per-sweep approval, separately tracked, audited in `cost-log.md` | Operator |

The non-obvious point: **(a) and (b) are *both* substrate-relevant but only (a) counts against substrate's cost discipline.** The substrate's AGENTS.md cost rule was scoped in PR #11 to substrate-runtime only; consumer-side runtime frontier use is explicitly out of scope per ADR-0003 §1. (b) is a consumer cost line that lives entirely outside the substrate's books.

## 5. The DOOMBot Gateway boundary

Concrete state from `~/dev/doombot/backend-gateway/`:

**Engines available:**
- `bodega.engine.ts` — local Bodega at `localhost:44468`
- `gemini.engine.ts` — Google Gen AI SDK (`@google/genai`)
- **No Anthropic engine. No OpenAI engine.** The pricing table in `cloud-budget.service.ts` lines 8–19 enumerates only Gemini variants (`gemini-3.1-pro`, `gemini-3.1-flash`, `gemini-3.1-flash-lite`, `gemini-deep-research-pro-preview`, `gemini-2.5-flash`, `gemini-2.5-pro`, plus a `default` fallback).

**Routing:**
- `inference.controller.ts` — local-inference path
- `cloud.controller.ts` — frontier path (Gemini today). Has structured error mapping (`RESOURCE_EXHAUSTED → 429`, `UNAVAILABLE → 503`, `UNAUTHENTICATED → 401`, etc.) so callers can branch on backoff vs auth-failure cleanly.

**Cost enforcement (`services/cloud-budget.service.ts`):**
- Default monthly budget: **$50.00 USD** (`DEFAULT_MONTHLY_BUDGET_USD`)
- Storage: `~/.local/share/openclaw/cloud_cio_spend.json` (single file, machine-readable)
- SEV1 alert at 80% (`SEV1_ALERT_THRESHOLD_PCT`)
- Hard kill at 100% — `isBudgetExceeded()` returns true and `recordUsage()` logs `🚨 CLOUD CIO BUDGET EXCEEDED ... All subsequent cloud calls will be blocked.`
- Workflow attribution: caller passes `workflowId` to `recordUsage()`; spend split per workflow in the JSON. **No per-workflow enforcement** — only per-month total.
- Pricing inputs are token-counts; pricing is hardcoded per model.

**Implications:**
1. **Architecture A (gateway enforces, repos log) is confirmed** by direct read. SH's `docs/research/cost-log.md` is currently a redundant human-readable audit on top of the Gateway's machine-readable JSON.
2. **All cost discipline ultimately bottoms out at the Gateway's per-month cap.** Substrate's `<$50/cycle` is self-enforced at the call site; Gateway only sees "is this caller over the global $50/month yet."
3. **If SH's RLAIF teacher needs Claude or GPT, that's blocked on Gateway adding a new engine first.** No fall-back path; direct API calls are forbidden by DOOMBot AGENTS.md.

## 6. Cost-budgeting reconciliation

Substrate AGENTS.md says `<$50/cycle`. Gateway says `$50/month` total. These don't trivially reconcile:

| Scenario | Substrate spend | Gateway state | Outcome |
|---|---|---|---|
| 1 substrate cycle/month at $50 | $50 | $50 | At cap; KG / Cloud CIO / any other gateway caller gets blocked for the rest of the month |
| 4 substrate cycles/month at $50 each | $200 | Blocked at $50 after first cycle | 3 of 4 cycles can't even fire |
| 1 substrate cycle at $30 + Cloud CIO at $30 | $30 | $60 | Cloud CIO blocks at $50 ($20 of CIO's call is rejected) |

Three reconciliation options. Pick one:

**Option A — Raise Gateway's monthly cap.** Set `DEFAULT_MONTHLY_BUDGET_USD` to a number that covers the worst-case combined spend (substrate cycles + Cloud CIO + KG RLAIF + DR sweeps). Probably $200–$300/month. Simple but loses the protective property of a tight cap.

**Option B — Per-workflow caps inside Gateway.** Extend `cloud-budget.service.ts` to enforce per-`workflowId` caps (e.g., `sh-vol-N-rlaif-teacher` capped at $50, `kg-cloud-cio` capped at $40, etc.), with the global $50/month as a hard ceiling. Tighter but requires Gateway-side code change.

**Option C — Substrate adopts per-month not per-cycle.** Rewrite AGENTS.md cost rule from `<$50/cycle` to `<$50/month`. Aligns with Gateway's existing model. Operationally tighter on substrate (one cycle/month max) but no Gateway-side change needed.

**Recommendation: B.** Per-workflow caps preserve the substrate's per-cycle discipline AND the Gateway's per-month protection. Requires DOOMBot work; not blocking until SH actually starts firing RLAIF cycles (~Phase 1, late August 2026). Until then, treat substrate cost-log as authoritative for substrate spend and Gateway cost-log as authoritative for total.

## 7. KG's actual FDA pipeline architecture vs substrate's assumed handshake

This is the load-bearing finding from this drafting pass. **The Volume Design Phase handshake we landed in PR #10 assumed KG would have a runtime frontier-driven feature-extraction layer for FDA briefings. KG's actual design does not.**

**KG's planned FDA briefing pipeline (Phase 14A.1 per `docs/ROADMAP.md` lines 625–631):**

```
FDA AC briefing PDF
       │
       ▼  pdfplumber (deterministic PDF parsing)
Raw text chunks (~4K tokens each, Commander-digestible)
       │
       ▼  CatalystType.REGULATORY_ACTION queue
Direct-to-Commander pipeline (KG Phase 14.0.7)
       │
       ▼  Commander (gpt-oss-120b + Commander LoRA)
Trade decision
```

**No frontier-API extraction. No Pydantic-typed `FDABriefingFeatures` schema. No structured-feature intermediate layer.** Commander processes raw pdfplumber text chunks directly.

The Volume Design Phase handshake (`cross-repo-coordination.md` §"Volume Design Phase") says substrate's LoRA's input contract is the structured-feature schema KG's runtime extraction emits. If that schema doesn't exist, the handshake is binding against vapor.

**Three possible substrate-side responses:**

### 7.1 Substrate Vol. 1 = alternative Commander on FDA briefings (Option I)

Substrate's LoRA replaces or augments KG's Commander specifically for FDA-briefing catalysts. Input = same pdfplumber chunks. Output = same trade-decision-relevant schema Commander emits.

- **Pro:** No new layer needed in KG. Direct head-to-head measurable Brier improvement.
- **Pro:** Aligns with the Opus 4.7 research doc's recommendation (SFT+ORPO on the structured-output extraction task).
- **Con:** Couples substrate to KG's specific Commander signature (input/output schema). Couples substrate's release cadence to KG's Commander schema versioning.
- **Con:** "Multi-LoRA composition" at L4 is harder when one of the LoRAs is an alternative for the same base function as another.

### 7.2 Substrate Vol. 1 = feature extractor (Option II)

Substrate's LoRA inserts a NEW layer between pdfplumber and Commander: structured-feature extraction. Input = pdfplumber chunks. Output = Pydantic `FDABriefingFeatures` schema. Commander then processes the structured features instead of raw text.

- **Pro:** Cleanest separation of concerns. Substrate does extraction; Commander does decision.
- **Pro:** Matches the original Volume Design Phase handshake assumption.
- **Pro:** Reusable across multiple KG strategies that consume FDA briefings.
- **Con:** Requires KG-side architectural change — Commander has to consume structured features instead of raw text.
- **Con:** Schema design becomes a cross-repo dependency.

### 7.3 Substrate Vol. 1 = output calibrator on top of Commander (Option III)

Substrate's LoRA takes Commander's output as input and rescales/recalibrates the probability outputs to match historical FDA-briefing outcomes. Input = `(briefing context, Commander output)`. Output = recalibrated probability.

- **Pro:** Minimal KG-side change. Bolt-on at L4.
- **Pro:** Brier reduction is measurable directly (compare Commander vs Commander+SH-calibrator).
- **Con:** Substrate becomes parasitic on Commander; failure modes inherit Commander's.
- **Con:** Hard to argue this clears a meaningful 1.5% Brier-reduction gate when Commander is already calibrated.

**Recommendation: Option I** unless KG team is independently planning to add a feature-extraction layer (in which case Option II becomes the natural fit). Option III is the default fallback if Vol. 1 design wants to stay narrow.

This decision needs to be made *before* the training-recipe choice is finalized. The training-recipe doc (`docs/research/training-recipe-comparative.md` PR #12) should be re-read after this decision lands; some of its open questions resolve once Option I/II/III is picked.

## 8. The four load-bearing open questions, reframed

1. **Is SH Vol. 1 a scorer (Option I), an extractor (Option II), or a calibrator (Option III)?** Decided in §7 above; default recommendation is Option I. This subsumes Open Question #5 from `training-recipe-comparative.md`.

2. **Does KG plan to add a feature-extraction layer between pdfplumber and Commander for FDA briefings?** If yes, substrate should target Option II and align with the new schema. If no, substrate should target Option I or III. Needs KG team confirmation.

3. **How are RLAIF-teacher tapes shared and regenerated across the KG/SH boundary?** Both projects' RLAIF teachers route through the same Gateway, but tapes live in each repo's `tests/fixtures/tape/teacher/`. Need disjoint `workflowId` namespaces (`sh-vol-1-teacher` vs `kg-commander-teacher`), AND tape regeneration cadence per project. Substrate's freshness check is at 90 days; KG's may differ.

4. **Does DOOMBot Gateway need an Anthropic or OpenAI engine before substrate Phase 1 fires?** If Vol. 1's RLAIF teacher needs Claude or GPT specifically (e.g., for FDA-domain reasoning), Gateway needs a new engine. Currently Gemini-only. Open question for Phase 1 timeline.

## 9. Substrate Phase 1 design implications

**What this architecture forces SH to commit to:**

- Vol. 1 deployment = release artifact (signed manifest + safetensors) + KG-side pin update (per ADR-0001 §2). No auto-deploy.
- Vol. 1 RLAIF teacher path = DOOMBot Gateway only (no direct API calls).
- Vol. 1 cost path = Gateway-enforced (via §6 reconciliation).
- Vol. 1 input contract = whatever §7's resolution dictates (pdfplumber chunks for I or III, structured features for II).

**What it leaves open:**

- Vol. 1 training recipe (per §7 resolution; the existing PR #12 research doc is decision input but assumes Option II's task shape; needs re-read after §7 decision).
- Vol. 1 base model choice (Llama / Qwen / Mistral / etc. — depends partly on which Bodega-loadable models exist via Gateway).
- Whether Vol. 1 even fires LoRA training, or ships as a prompt + manifest if the prompt-only Brier baseline already clears the gate.

## 10. Recommended next moves (in order)

1. **Decide Option I/II/III** (§7) — this is a design decision, not a research question. Substrate operator + KG operator align. Probably one short doc + one design discussion.
2. **Confirm KG's Phase 14A.1 timeline** — when does `data_ingestion/fda_briefing_source.py` actually land in KG? That's the gating event for substrate Vol. 1 to have a real consumer to measure against.
3. **Decide §6 cost reconciliation** — Option A / B / C. If B, file an issue against DOOMBot for per-workflow caps.
4. **Audit Gateway engine roster against Vol. 1 needs** — does substrate's RLAIF teacher need Anthropic/OpenAI, or is Gemini sufficient? If the former, file an issue against DOOMBot.
5. **Re-read `docs/research/training-recipe-comparative.md` (PR #12)** with §7's decision applied. Some recommendations sharpen, some open questions resolve. Then decide PR #12 disposition.

## 11. Cross-repo independence reminders

These don't change with this map but are worth restating since they govern what this doc can and can't dictate:

- Substrate has no opinion on KG's Commander training-recipe choice (ORPO → GRPO/GiGPO migration). Per ADR-0003 §1, KG owns its inference and training topology. This doc maps where each adapter lives but doesn't recommend that one project's choices constrain the other's.
- Substrate has no knowledge of consumers other than via the artifact contract. The KG-specific routes / strategies / Cloud-CIO behavior described in §3, §4, §6 are documented for the operator's mental model, not as substrate-side dependencies.
- DOOMBot Gateway is shared infrastructure. Issues filed against DOOMBot from substrate-side need to flag the substrate use case but should expect DOOMBot to optimize for the union of KG, SH, and iOS-client requirements.

## 12. See Also

- [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) — substrate-as-artifact contract, particularly §1 (versioned/immutable artifacts), §3 (no runtime API), §6 (substrate has no knowledge of consumers), §7 (LLM as feature extractor only)
- [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) — substrate vs consumer training/schedule ownership; particularly §1 topology matrix
- [docs/operations/cross-repo-coordination.md](../operations/cross-repo-coordination.md) §"Volume Design Phase" — input-contract handshake (NEEDS REVISIT after §7 resolution)
- [docs/design/resilience-and-subsystem-isolation.md](./resilience-and-subsystem-isolation.md) §2 (subsystem boundaries), §7 (tape playback), §9 (logging architecture)
- [docs/research/training-recipe-comparative.md](../research/training-recipe-comparative.md) (PR #12) — Vol. 1 training-recipe comparative; assumes Option II task shape; needs re-read after §7 resolution
- KG `docs/design/slippage-measurement-phase-a.md` §10.1, §10.2, §12.7.5 — KG-side architecture references
- KG `docs/ROADMAP.md` §14A.1 — FDA Briefing Document Source; the actual KG-side pipeline this doc maps against
- DOOMBot `~/dev/doombot/backend-gateway/AGENTS.md` — Gateway routing mandate
- DOOMBot `~/dev/doombot/backend-gateway/src/services/cloud-budget.service.ts` — Gateway cost enforcement
