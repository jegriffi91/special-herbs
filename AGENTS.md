# Special Herbs — Agent Directives

> Mandatory for all AI contributors working on this codebase.

## The ADR Set — Foundational Law

Three architectural decision records collectively establish the substrate's binding contract; all are co-equal foundational law. Future ADRs that modify these rules must explicitly reference and supersede the relevant prior ADR.

| ADR | Scope |
|---|---|
| [ADR-0001](docs/architecture/ADR-0001-substrate-as-artifact-contract.md) | Substrate-as-artifact contract — eight rules governing the manifest, version pinning, runtime decoupling, and consumer agnosticism. Restated as enforceable mandates below. |
| [ADR-0002](docs/architecture/ADR-0002-separate-repo-from-consumers.md) | Filesystem-level separation. The substrate lives in its own repository; cross-repo imports are forbidden by construction. |
| [ADR-0003](docs/architecture/ADR-0003-training-and-schedule-ownership.md) | Training pipeline + schedule ownership boundaries. Substrate and consumer schedulers are sovereign; recipe sharing goes through third packages; an anti-temptation list enumerates forbidden patterns. |

ADR-0001 is restated below as the eight mandatory rules. ADR-0002 and ADR-0003 are not duplicated here — refer to them directly. Anything any of the three ADRs forbid, this AGENTS.md implicitly forbids.

---

## ADR-0001 Mandates — The Eight Rules of the Substrate-as-Artifact Contract

Special Herbs is a research substrate, not a trading system. It produces versioned artifacts at rest (LoRA adapters, knowledge graph snapshots, correlation matrices) consumed by independent trading systems. The rules below prevent the two failure modes that destroy substrate value over time: runtime coupling drift and semantic drift.

### 1. Artifacts Are Versioned and Immutable

Every artifact released by the substrate carries a SHA-tagged, signed manifest. Once published, an artifact version is immutable — corrections produce a new version, never a retroactive edit.

Required manifest fields: `artifact_id`, `version` (semver), `sha256`, `released_at` (UTC ISO), `base_model`, `training_data_hash`, `compatible_consumer_contracts`, `signature`.

**Why this matters:** Reproducibility is non-negotiable. Consumer outcomes (trade PnL, eval metrics) must be traceable to the exact substrate state that produced them. Retroactive edits destroy the audit trail.

### 2. Consumers Pin Specific Versions

Consumer code reads the artifact version pin at startup. Pins are version-specific (`v1.2.3` + `sha256:abc...`); floating selectors (`latest`, `>=1.0`) are forbidden in production.

Consumers must verify the SHA on load. Mismatched SHA → load fails fast.

**Why this matters:** Floating selectors silently change consumer behavior when the substrate releases. A trading strategy that worked on `vol-1-fda-briefing-v1.2.3` may not work on `v1.3.0`. The consumer must opt in explicitly.

### 3. No Runtime API Between Substrate and Consumers

The substrate emits artifacts to a release location. Consumers read those artifacts at startup or on a controlled refresh cadence. Nothing else is exchanged at runtime.

Forbidden:

- HTTP / gRPC / IPC calls from consumer to substrate during inference.
- Webhook callbacks from substrate to consumer.
- Shared Redis / message bus / pub-sub channels.
- Live database connections that span substrate and consumer.
- "Helper services" that wrap substrate logic for runtime consumer use.

If a use case appears to require runtime coupling, the correct answer is one of: bake it into the artifact, bake it into the consumer, or defer until the artifact format can absorb it.

**Why this matters:** Each "quick" runtime API compounds. The substrate becomes a service consumers depend on at runtime; the consumer becomes brittle to substrate availability; the two systems' lifecycles fuse. This destroys the substrate's most valuable property — that artifacts are durable, replayable, and consumer-agnostic.

### 4. No Shared Databases

The substrate and consumers MUST NOT share a database, even read-only. If the same upstream source (e.g., FDA briefing PDFs) is needed by both, each system independently ingests it.

**Why this matters:** Duplicate ingestion cost is acceptable; coupling cost is not. Shared databases create implicit schema dependencies and runtime availability constraints between systems whose lifecycles are explicitly decoupled.

### 5. Graceful Consumer Degradation

Consumers MUST function (with reduced capability) when substrate artifacts are unavailable, corrupted, or fail SHA verification. The fallback path:

- Log the failure.
- Disable the substrate-augmented feature path.
- Continue operating on the consumer's own logic.

A consumer that crashes when a substrate artifact is missing is in violation.

**Why this matters:** Substrate and consumer have independent release cadences and failure domains. A bad LoRA training cycle, a corrupted KG snapshot, or a complete substrate outage must not take down the consumer's trading path.

### 6. Substrate Has No Knowledge of Consumers

The substrate codebase MUST NOT contain:

- Lists of consumer system names.
- Conditional logic keyed on consumer identity.
- API endpoints that serve specific consumers.
- Tests that depend on consumer behavior.

The substrate is consumer-agnostic by construction. Any consumer-aware logic belongs on the consumer side.

**Why this matters:** Consumer-specific code in the substrate inverts the dependency: the substrate becomes a service-mesh of consumer-specific code paths. New consumers force substrate changes; deprecated consumers leave dead code. Consumer-agnostic substrate accepts new consumers freely.

### 7. LLM as Feature Extractor Only, Never Decision-Maker

The substrate may use LLMs internally during artifact production (synthesis, classification, extraction). The substrate MUST NOT produce artifacts that are themselves decision-makers.

Forbidden:

- An artifact that is a "buy/sell signal generator."
- An artifact that emits trade orders.
- An artifact whose output is consumed directly without a deterministic scorer in the consumer's path.

Consumers may use substrate artifacts as features for their own deterministic scorers, gradient-boosted ensembles, or rule-based logic. The substrate provides features; the consumer decides.

**Why this matters:** LLMs are powerful feature extractors and unreliable decision-makers. A substrate artifact that emits trade orders couples consumer PnL to substrate hallucinations. A substrate artifact that emits features lets the consumer's deterministic scorer apply guardrails, calibration, and risk limits.

### 8. Cross-Repo Separation Enforced at the File System

The substrate codebase MUST NOT import from any consumer codebase, and vice versa.

- Substrate's `pyproject.toml` MUST NOT list any consumer repo as a dependency.
- Consumer's dependency list MAY list `special-herbs-formats` (the small, separately-published format library containing manifest schemas + load utilities) — but never the substrate's training, evaluation, or research code.

`grep` checks at PR time:

- Substrate codebase: `import king_geedorah` or any consumer import → fail.
- Substrate codebase: HTTP / gRPC calls to consumer hostnames → review.

**Why this matters:** [ADR-0002](docs/architecture/ADR-0002-separate-repo-from-consumers.md) makes this filesystem-enforced. ADR-0001's architectural law becomes mechanically checkable, not just convention.

---

## Cost Discipline — Frontier APIs Are RLAIF Teachers Only

**Frontier APIs (Anthropic / OpenAI / Google) MUST NOT appear in the substrate's artifact-runtime path.** They are used only as RLAIF teachers during weekend training cycles, or for bounded upfront research.

**Scope.** This rule binds the substrate. A consumer's runtime use of frontier APIs — for example, KG calling Claude at runtime to extract structured features that feed into a substrate-produced LoRA — is a consumer-owned cost and design decision per [ADR-0003](docs/architecture/ADR-0003-training-and-schedule-ownership.md) §1. The substrate has no opinion on consumer inference topology and does not budget for consumer-side frontier spend.

### Rules

1. **Substrate-produced artifacts are runtime-local.** A LoRA loaded by any consumer makes no frontier API calls — runtime is fully self-contained on the local M2 Ultra Qwen / Llama base + the LoRA weights. Substrate-side training cycles may invoke frontier APIs only as RLAIF teachers, never as the inference model being graded.
2. **RLAIF teacher use is bounded.** Frontier API spend per LoRA training cycle (including teacher grading) targets <$50.
3. **Track every cycle.** Each training cycle's API spend is logged in `docs/research/cost-log.md` with the volume / artifact ID it produced.

### Why This Matters

Solo retail capital ($2k starting, $5-10k ceiling by month 24 conditional on audited results). If substrate-produced LoRAs made frontier API calls at runtime during consumer trade decisions, that spend would exceed the consumer's own trade size on any meaningful signal volume — and would also re-couple substrate availability to consumer execution, violating [ADR-0001](docs/architecture/ADR-0001-substrate-as-artifact-contract.md) §3. The substrate's value comes from local-model fine-tuning + the architectural moat, not from frontier-API magic at substrate runtime. Cost-log tracking creates pressure to keep training cycles efficient and prevents silent runaway spend during the substrate's own training and research work.

---

## Citation Hygiene — Do Not Cite

Six items were corrected during the strategic synthesis that produced this repo (research log: `~/.claude/research_logs/2026-04-28_112632_kg-moat-substrate-selection/`). They MUST NOT be cited as evidence in design docs, ADRs, research notes, or commit messages:

| Claim | Reality |
|---|---|
| "SAHF-PD" framework as quant-trading evidence | Phishing-detection paper, misattributed to trading. |
| "A Sober Look at LLMs" (ICML 2024) | Unverifiable in ICML 2024 proceedings. |
| QuantAgent Sharpe 2.63 | Economically meaningless per ICLR review. |
| PrimoRL 1.70 Sharpe | 7-month / 5 mega-cap sample; not generalizable. |
| Form 4 insider buying "+2.41% / 10d" | Hallucinated t-statistic. Real per Cohen-Malloy-Pomorski: +1.55% / 10d, 0.4-0.6 net Sharpe. |
| Kalshi MAE improvement vs. Bloomberg "40-60%" | Diercks-Katz-Wright 2026 (NBER WP 34702) reports ~22%. |

Confirmed and citable:

- Susquehanna IS Kalshi's primary market maker since 2024-04-03.
- Diercks-Katz-Wright 2026 (NBER WP 34702 / FEDS WP 2026-010) is real; cite the actual ~22% MAE improvement number.

### Why This Matters

Citation drift erodes design credibility. A design doc that references a hallucinated statistic propagates the error into downstream decisions; a future operator (or future Claude) treating the citation as evidence makes worse choices than one that knows the evidence is missing.

---

## What This Repo MUST NOT Contain

Per [ADR-0002](docs/architecture/ADR-0002-separate-repo-from-consumers.md) §"What Stays Out of This Repo":

- Live trading strategy YAML manifests (those live in king-geedorah).
- Brokerage API code or trade execution logic.
- KG's golden dataset, settle gate metrics, or `pipeline_quality_gate.py`.
- KG's signal listener, orchestrator, scout, commander code.
- Any code that touches a brokerage API or executes trades.

If anything in this repo starts to look like a trading system, it is in the wrong repo.
