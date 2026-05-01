---
doc_id: SPECIAL-HERBS-KG-MIGRATION-PLAN
title: "KG Migration Plan + ADR-0003 Boundary Audit"
status: design-only
created: 2026-04-30
phase-0-deliverable: D
related-docs:
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - ../architecture/ADR-0002-separate-repo-from-consumers.md
  - ../architecture/ADR-0003-training-and-schedule-ownership.md
  - cross-repo-coordination.md
  - ../ROADMAP.md
related-repos:
  - https://github.com/jegriffi91/King-Geedorah (initial consumer)
---

# KG Migration Plan + ADR-0003 Boundary Audit

> Phase 0 deliverable D. Per-document migration verdict for King Geedorah's `docs/exploration/` Area 1 / Area 4 material, plus topology and schedule boundary audit against [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md). Read-only audit on the KG side; no KG-side edits proposed here are authorised — the operator decides what (if anything) to act on.

## Scope and timing

[ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md) §"Migration Path for Existing Substrate Documentation" sets the migration trigger: "These will migrate to this repo when substrate Vol. 1 / Vol. 2 design begins (likely August 2026 once KG Phase 13.1 lands). Until migration, they remain in KG and are referenced via path in this repo's `docs/ROADMAP.md`." [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §4 confirms this is a permitted exception (pure-research artifacts with no operational consumer in KG).

Today is 2026-04-30; KG Phase 13.1 RLAIF Pipeline Validation is targeted for 2026-08-30. This plan is therefore preparatory: the ordering and section-level rewrites it specifies are intended to land in the same window as Vol. 1 design kickoff, not now.

## Audit method

Cross-repo state was inspected read-only via `git -C /Users/jamesgriffin/dev/king-geedorah grep` and absolute-path `Read`. No KG files were modified or staged. Every leakage / gap / drift finding cites a specific path and line number from KG's checkout at audit time (commit visible to the operator).

---

## 1. Per-document migration verdict

The KG `docs/exploration/` directory contains exactly three files (verified via `git -C ... ls-files docs/exploration/`):

| KG path | Verdict | Rationale | Target substrate path (if migrating) | Sequence |
|---|---|---|---|---|
| [`docs/exploration/research-substrate-roadmap.md`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/research-substrate-roadmap.md) (222 lines) | **split** | Strategic framing ("depth in substrate, breadth in consumers"; areas-1+4 complementarity) is substrate-internal and migrates. KG-internal phasing (the §"Roadmap sketch" subsections) has been superseded by [substrate `docs/ROADMAP.md`](../ROADMAP.md) and should not move — the substrate ROADMAP is now authoritative. | `docs/ROADMAP.md` (distilled into a new §"Strategic framing" subsection — see §2.1) | 1 |
| [`docs/exploration/area-1-agentic-information-synthesis.md`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md) (147 lines) | **migrates-to-substrate** | Content is substrate-internal architecture (multi-agent synthesis, KG snapshot schema patterns, Vol. 1 LoRA corpus framing). KG has no operational consumer of this content; it lives in `docs/exploration/` precisely because it was never wired into KG production code. Per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §4 exception 1, this is the canonical "pure-research artifact with no operational consumer in KG" case. | `docs/research/area-1-architecture.md` | 2 |
| [`docs/exploration/area-4-cross-domain-signal-networks.md`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-4-cross-domain-signal-networks.md) (150 lines) | **migrates-to-substrate** | Same rationale as area-1: substrate-internal architecture (correlation matrices, divergence detection, lead-lag analysis). area-4 is the cleaner of the two — area-4:135 already states the substrate "is mostly self-justifying through pure data ingestion and statistical analysis," which makes the consumer-agnosticism rewrite lighter. | `docs/research/area-4-architecture.md` | 3 |

**Verdict counts:** 0 stays-in-kg / 2 migrates-to-substrate / 0 duplicates / 1 split.

### Out-of-scope adjacents (noted, not migrated)

| KG path | Disposition | Note |
|---|---|---|
| [`docs/research/archetype-2-volume-shape-system-vision.md`](file:///Users/jamesgriffin/dev/king-geedorah/docs/research/archetype-2-volume-shape-system-vision.md) | **stays-in-kg** | KG-side vision for a hypothetical sister-system to KG; uses "substrate" language but the substrate it describes is KG's *own* multi-strategy framework (KG-internal LoRA-per-strategy plumbing), not Special Herbs. Stays in KG per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §"Decision" §4. The substrate's [ROADMAP `docs/ROADMAP.md` §"Related repos"](../ROADMAP.md) does not currently list this doc; correct outcome — substrate stays consumer-agnostic. |
| [`strategies/fit_functions/base.py:8`](file:///Users/jamesgriffin/dev/king-geedorah/strategies/fit_functions/base.py) — comment "the mature substrate" | **stays-in-kg** | KG-internal language about FitFunction graduation, unrelated to Special Herbs. False-positive on the `substrate` grep. No action. |

---

## 2. Section-level breakdown for split / migrating docs

### Governing principle: consumer-name policy

The migration rewrites below follow this asymmetry, formalized to resolve Phase 0 deliverable D's policy question:

- **Substrate code (`src/special_herbs/...`) MUST be consumer-agnostic.** No consumer names, no consumer-keyed conditionals, no consumer-specific tests. Per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6, mechanically enforceable at PR time via grep.
- **Substrate architecture / research / design docs (`docs/architecture/`, `docs/research/`, `docs/design/`) MUST be consumer-agnostic.** These document the substrate's own structure, its artifact contracts, and its design rationale. They survive consumer churn unchanged. Migrated `area-1` and `area-4` content lands here and must therefore strip every King Geedorah / KG / archetype-2 / Gateway / Commander / Scout / RawSignal / settle-gate / RLAIF-cycle / `kg_lookup` / circuit-breaker reference.
- **Substrate operations / coordination docs (`docs/operations/`, `docs/ROADMAP.md`) MAY name the initial consumer.** These coordinate concrete cross-repo handoffs (Vol. 1 release ↔ KG strategy YAML pin, KG phase gates ↔ substrate phase preconditions). Naming KG explicitly is the only way to make the handoff legible. The `related-repos:` frontmatter, the cross-repo dependency tables, and the ROADMAP §"Phase 1 — Vol. 1" consumer-contract bullets are correct as-is.
- **Substrate AGENTS.md / CLAUDE.md MAY name the initial consumer** in operator-facing contexts (commit conventions, ops commands, memory conventions). These are operator-instruction docs, not architectural law.

Concrete consequence: every "King Geedorah", "KG", "Gateway", "Commander", "Scout", "RawSignal", "settle gate", "RLAIF cycle", "kg_lookup", "circuit-breaker", "Phase 14", "Phase 1.2", or "Archetype-2" string in the migrated content goes through this filter. Destination is `docs/research/...` or `docs/architecture/...` → strip. Destination is `docs/operations/...` or `docs/ROADMAP.md` → keep only where the reference identifies a specific cross-repo coordination touchpoint (e.g., a KG-side phase number that gates a substrate phase, or a KG strategy YAML name that pins a substrate volume).

### 2.1 `research-substrate-roadmap.md` — split

**Resolution (migration-vs-distillation):** Distill into substrate `docs/ROADMAP.md` §"Strategic framing", a new ~15-line subsection inserted before §"Naming Convention". Rationale: the doc is 222 lines but ~70% overlaps content already in substrate `docs/ROADMAP.md` (Phase 0 / Phase 1 / Phase 2 framing, "Honest Caveats") or [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §3-§6 (coupling rules). A standalone `docs/research/area-1-and-4-strategic-framing.md` would mostly restate. Distillation captures the unique residue: the "depth concentrates in the substrate; breadth happens in consumers" framing + the area-1-and-4 complementarity table.

| KG section / lines | Disposition | Notes |
|---|---|---|
| Lines 1-22 (frontmatter + §"Status") | drop | Status reads "Exploration. Not a commitment." That tense is consumed by the substrate's existing [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) acceptance and the substrate ROADMAP's Phase 0 framing. No equivalent needed substrate-side. **Severs the line-20 back-pointer to KG `docs/research/archetype-2-volume-shape-system-vision.md`** — substrate has no opinion on consumer sister-systems per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6, and the archetype-2 doc itself stays in KG per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §4. |
| Lines 24-37 (§"The strategic frame") | **migrate verbatim, light rewrite** | Move to the new "Strategic framing" subsection of substrate `docs/ROADMAP.md` (per the §2.1 Resolution above). Strip "KG today" → replace with "the initial consumer" per the consumer-name policy at the top of §2: research/architecture-class destinations strip consumer names; operations/ROADMAP-class destinations may keep them at coordination touchpoints. The strategic-framing residue lands in ROADMAP, so it leans toward stripping consumer names except where ROADMAP already names KG (the cross-repo dependency table, the related-repos frontmatter). |
| Lines 39-50 (§"Why Areas 1 and 4 specifically") | **migrate, rewrite** | This is the area-prioritization rationale and is substrate-internal. Rewrite the table column header "Justification by KG alone" → "Justification by the initial consumer alone" and strip the "Archetype-2" column entirely (substrate has no opinion on KG sister-systems). |
| Lines 52-66 (§"How the two areas relate") | **migrate verbatim** | Pure substrate-internal architecture comparison; no consumer-aware language. |
| Lines 67-83 (§"Shared substrate components", §"Where they remain separate") | **migrate verbatim** | Substrate-internal infrastructure decomposition. Already aligned with substrate `docs/design/resilience-and-subsystem-isolation.md` §2 subsystem layout. |
| Lines 86-124 (§"Consumer model" + diagram) | **migrate, rewrite** | The diagram explicitly names "KG (initial)", "Archetype-2 (if built)", "Research tooling", "Dashboards". Per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6 ("Substrate has no knowledge of consumers"), the substrate-side migrated diagram must replace consumer names with abstract slots: "Consumer A (initial)", "Consumer B (future)", etc. The subordinate "Coupling rules" bullet list is already canonicalized in [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §3-§6 — drop the duplicate. |
| Lines 134-176 (§"Roadmap sketch" Phase 0/1/2/3/4) | **DROP** | Superseded by substrate's own [`docs/ROADMAP.md`](../ROADMAP.md). The phasing in this section uses an old numbering ("Phase 1.2 RLAIF") that KG itself has renumbered to Phase 13.1; preserving it would propagate stale state. KG's copy can keep the section temporarily; substrate's migrated copy must drop it cleanly. |
| Lines 179-186 (§"Long-term moat compounding") | **migrate verbatim** | Three-axis moat-compounding framing is substrate-internal architecture; no consumer-aware language. |
| Lines 188-194 (§"Honest caveats applying to both areas") | duplicate (already in substrate ROADMAP) | Substrate's [`docs/ROADMAP.md` §"Honest Caveats"](../ROADMAP.md) already covers four of the five bullets verbatim. Drop the duplicate. |
| Lines 197-204 (§"What this enables strategically") | **migrate, rewrite** | Replace "KG benefits from substrate investment immediately" → "the initial consumer benefits…". Strip the "archetype-2 (or other consumers) become free upside" phrasing — substrate has no opinion on what consumers exist. |
| Lines 207-214 (§"Open strategic questions") | **migrate, rewrite** | Questions 1-4 are mostly resolved: Q1 (single vs separate repo) → resolved by [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md). Q2 (Area 1 first) → resolved by substrate ROADMAP Phase 1. Q3 (single substrate codebase covering both areas) → still open, migrate. Q4 (minimum first artifact) → resolved by Vol. 1 design. Q5 (catastrophic-forgetting policy) and Q6 (external publication) → still open, migrate. |
| Lines 216-221 (§"Summary") | drop | Restates content covered above. No equivalent needed. |

**Content that must be REMOVED from any migrated copy** (per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6):

- "KG today; archetype-2 if ever built" — replace consumer names with abstract slots.
- The entire "Archetype-2" column in the area-prioritization table.
- "swisstony's $6-7M PnL" reference (line 186) — operator-internal context that has no place in a substrate doc.
- Any phrase implying substrate trains on KG's settle-gate-resolved trades (covered in §2.2 below).

### 2.2 `area-1-agentic-information-synthesis.md` — migrates-to-substrate

| KG section / lines | Disposition | Notes |
|---|---|---|
| Lines 1-9 (frontmatter) | rewrite | Substrate-side `doc_id`, status `design-only` → migrate to substrate frontmatter conventions (see substrate `docs/design/special-herbs-formats-api.md` for the pattern). |
| Lines 11-37 (§"What this is", §"What this is NOT", §"Why structure it as a separate entity") | **migrate verbatim** | Pure substrate-internal architecture statement. The line "Not a child process of KG" should be rewritten to "Not a child process of any consumer" — same rule as `research-substrate-roadmap.md` consumer-name stripping. |
| Lines 48-58 (§"Initial consumer: King Geedorah") | **REMOVE entirely from migrated copy** | Per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6, the substrate codebase MUST NOT contain consumer-aware enumerations. This entire section names KG, lists KG's Gateway, KG's Commander/Scout DSPy signatures, KG's `kg_lookup` tool, KG's `RawSignal` type, KG's circuit-breaker. Migrated content cannot retain any of it. The information is consumer-internal — KG decides for itself how to consume substrate artifacts. **This is the single largest rewrite cost in the migration.** |
| Lines 60-67 (§"Future consumers") | **REMOVE entirely** | Same reason: enumerates speculative consumers ("Archetype-2", "Discrete research tooling", "Operator dashboards", "External publication"). [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6 forbids consumer enumeration in substrate code. |
| Lines 69-98 (§"Architecture overview" + diagram) | **migrate verbatim** | Substrate-internal architecture sketch. No consumer language. |
| Lines 100-110 (§"Measurement" table) | **migrate, rewrite** | Row "KG-side adoption of substrate features | At least 1 KG strategy using substrate adapters within 6 months of first release" — replace "KG-side adoption" → "downstream consumer adoption", strip "1 KG strategy" → "≥1 consuming strategy". |
| Lines 112-118 (§"Honest caveats") | **migrate verbatim** | All five caveats are substrate-internal observations. |
| Lines 120-128 (§"Research directions to dive deeper") | **migrate verbatim** | Already aligned with substrate's reading-30-papers Phase 0 precondition. |
| Lines 130-138 (§"Dependencies on KG") | **REWRITE substantially — most subordinate to ADR-0003** | Subsection bullets 1, 2 ("Outcome ground truth" and "Reward signal" from KG settle gate / RLAIF cycle) describe coupling that [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2 explicitly forbids ("Substrate reading KG's settle-gate database… is forbidden"; "Recipe / pattern sharing goes through a third package"). The migrated form must say: substrate ingests its own ground-truth from upstream sources independently, per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4 ("duplicate ingestion is the accepted cost"). Bullet 3 ("Initial domain prioritization") is fine — it describes a prioritization heuristic, not a runtime coupling. |
| Lines 140-146 (§"Open questions") | **migrate, rewrite** | Question 1 (single repo vs separate) → resolved by [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md). Question 3 (artifact-version pinning model) → resolved by [`special-herbs-formats-api.md`](../design/special-herbs-formats-api.md). Q4 (substrate as direct trading authority) → resolved by [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §7. Q5 (minimum viable first artifact) → resolved by Vol. 1 design. Migrate only Q2 ("How tightly should substrate domain prioritization track KG's?") — and even that needs rewriting to drop the explicit "KG" reference. |

### 2.3 `area-4-cross-domain-signal-networks.md` — migrates-to-substrate

Same shape as area-1 but with lighter consumer-aware content. Specific section actions:

| KG section / lines | Disposition | Notes |
|---|---|---|
| Lines 1-9 (frontmatter) | rewrite | Substrate-side conventions. |
| Lines 11-46 (§"What this is", §"What this is NOT", §"Why structure it as a separate entity") | **migrate verbatim** | Pure architecture statement. |
| Lines 48-57 (§"Initial consumer: King Geedorah") | **REMOVE entirely** | Same [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6 violation as area-1's equivalent section. Cross-venue confidence signals, lead-lag features, divergence-flag inputs to universe screening, cross-asset position-sizing — all consumer-internal opinions. |
| Lines 59-65 (§"Future consumers") | **REMOVE entirely** | Same reason. |
| Lines 66-100 (§"Architecture overview" + diagram) | **migrate verbatim** | Substrate-internal. |
| Lines 102-113 (§"Measurement" table) | **migrate, rewrite** | Row "KG-side feature adoption" → "consumer-side feature adoption". |
| Lines 114-121 (§"Honest caveats") | **migrate verbatim** | All five are substrate-internal. |
| Lines 123-132 (§"Research directions to dive deeper") | **migrate verbatim** | |
| Lines 134-141 (§"Dependencies on KG") | **rewrite substantially** | Bullet 1 (domain prioritization following KG) → rewrite to "domain prioritization initially follows the initial consumer's needs". Bullet 2 (validation through KG's resolved trades) → rewrite to "validation through resolved-event labels ingested independently by the substrate per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4". Bullet 3 (computational infrastructure overlap with KG Phase 14.0.2) → DROP entirely; per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §4, substrate writes its own ingestion; this bullet implies code-sharing that is forbidden. |
| Lines 143-150 (§"Open questions") | **migrate verbatim** | All five are open and substrate-internal — keep as Vol. 2 design open questions. |

---

## 3. ADR-0003 topology matrix audit (row-by-row)

Walking [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §1 row by row. Substrate has no code yet (Phase 0), so leakage findings are all in documentation. Status legend: **clean** = no cross-repo leakage observed; **leakage** = cross-repo reference found that violates the row; **gap** = substrate-side equivalent needed but not yet present.

| Row | Status | Evidence | Action |
|---|---|---|---|
| Substrate training pipeline (Unsloth/PEFT, RLAIF teacher prompts, eval harness shape) | **clean** | No substrate code. Substrate-side references in `vol-1-fda-ac-feasibility.md` are correctly self-contained. KG `mlops/pipelines/orpo_pipeline.py` and equivalents stay KG-side per [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md) §"What Stays Out". | None. |
| Substrate base-model selection | **clean** | Substrate ROADMAP Open Decision #1 owns this; KG's own base-model choice (120B Commander, 32B Scout) is decoupled. | None. |
| LoRA adapter file-format compliance | **clean** | Substrate `docs/design/special-herbs-formats-api.md` §"Manifest Schema" owns the adapter `peft` `adapter_config.json` + `adapter_model.safetensors` contract. KG does not specify an adapter format. | None. |
| Manifest schema (`special-herbs-formats`) | **clean** | Substrate-side at [`docs/design/special-herbs-formats-api.md`](../design/special-herbs-formats-api.md). KG has zero references to `compatible_consumer_contracts`, `verify_release`, `SubstrateKeyRing`, or `special-herbs-formats` (verified via `git -C ... grep`; binary match on `data/code_graph.db` is KG's own GraphRAG store, unrelated). | None. |
| Substrate's own continuous-learning loop | **clean** | Substrate ROADMAP §"Phase 1 — Vol. 1" Decision Gate owns the per-volume pass/fail. | None. |
| **Substrate's own ground-truth dataset accumulation** | **leakage (doc-only)** | KG `docs/exploration/area-1-agentic-information-synthesis.md:134` — "KG's settle gate produces resolved-trade outcomes that train substrate agents on whether their syntheses correlated with profitable decisions." This implies substrate reads or otherwise consumes KG's settle-gate state, which [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2 forbids ("Substrate reading KG's settle-gate database, breach log, or any other live runtime state to decide when to train") and [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4 forbids (no shared databases). | Rewrite during migration per §2.2 above (substrate ingests upstream sources independently). Until migration: do NOT propagate this language into substrate-side docs. |
| Consumer Gateway multi-LoRA composition | **clean** | KG `docs/exploration/area-1-agentic-information-synthesis.md:52` references "KG's Gateway alongside KG's own RLAIF-trained adapters. Multi-LoRA serving (already in Phase 1.2 design)" — but this is a description of consumer-side infrastructure, which [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §1 correctly assigns to the consumer. The line is consumer-internal opinion, which violates [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6 only if migrated to substrate verbatim. | Strip during migration per §2.2 (entire §"Initial consumer: King Geedorah" section is removed). |
| Consumer Scout/Commander/Cloud CIO pipeline | **clean** | No substrate-side reference to these names. KG owns. | None. |
| **Consumer's own RLAIF/ORPO/GRPO training (on consumer-internal adapters)** | **leakage (doc-only)** | KG `docs/exploration/area-1-agentic-information-synthesis.md:135` — "KG's RLAIF cycle feeds reward signals back into substrate LoRA training (with the per-system-independent attribution chains discussed in the archetype-2 vision doc)." This proposes a runtime/training-time coupling between KG's RLAIF and substrate's LoRA training. [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §3 anti-temptation table row 1 ("Just import the substrate's eval harness into KG to debug.") generalizes: the analogous reverse-direction coupling is equally forbidden. | Rewrite during migration per §2.2 (drop this bullet entirely). Substrate gets its own reward signal from independently ingested ground truth. |
| Consumer's strategy YAML manifests | **clean** | Substrate ROADMAP Phase 1 line 67 references `moat_fda_equity_catalyst.yaml` — known drift, see Open Question #1 below. The substrate is naming the consumer's strategy YAML for cross-repo coordination clarity (permitted by [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md), which itself names KG paths). Not a leakage; not a code-level enumeration. | None mechanical; see Open Question #1. |
| Consumer-side counterfactual scoring + settle gate | **clean** | No substrate-side references to KG's `pipeline_quality_gate.py`, `quality_gate_breaches.db`, settle gate metrics, or breach severity tiers. (The CLAUDE.md ops command at substrate `CLAUDE.md` §"KG settle-gate quick check" references KG's DB via absolute path — operator-driven, not in substrate runtime, allowed by [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §6 file-level sharing allowance.) | None. |
| Consumer-side feature engineering on top of substrate-emitted features | **clean** | No substrate references. | None. |

**Topology matrix summary:** 12 rows audited, 10 clean, 2 doc-only leakages (both in `area-1` lines 134-136), 0 gaps. The most concerning leakage is `area-1:135` ("KG's RLAIF cycle feeds reward signals back into substrate LoRA training") — it implies a forbidden cross-repo training-time coupling. Both leakages are confined to the migration source material and are addressed by §2.2's mandatory rewrite. Neither has propagated into substrate-side docs.

---

## 4. ADR-0003 schedule isolation audit

Per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2 forbidden patterns. Findings:

### 4.1 KG-side schedulers (`ecosystem.config.js`)

KG's `ecosystem.config.js` defines four PM2 entries: `geedorah-listener`, `geedorah-weekend-train`, `geedorah-pm-scout`, `geedorah-plv-review`. Direct grep:

```
grep -ni "substrate\|special.herbs\|special_herbs\|vol-1\|vol_1" /Users/jamesgriffin/dev/king-geedorah/ecosystem.config.js
# (zero matches)
```

**Finding:** No KG cron / PM2 entry references substrate paths or commands. **Clean.** [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2 sub-rule "Shared cron files defined in either repo that fire jobs in the other" — not violated.

### 4.2 KG-side runtime code reading substrate state

```
git -C /Users/jamesgriffin/dev/king-geedorah grep -li 'substrate\|special.herbs\|special_herbs' -- '*.py' '*.js' '*.yaml' '*.yml' '*.json' '*.toml' '*.sh'
# strategies/fit_functions/base.py  (false-positive — KG-internal "the mature substrate" language about FitFunction graduation; unrelated to Special Herbs)
```

**Finding:** No KG runtime code reads substrate paths, files, or table names. **Clean.** [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2 sub-rule "KG reading substrate's training-progress state to decide when to allocate trust" — not violated.

### 4.3 KG-side documentation claiming substrate triggers KG behaviour (or vice versa)

KG `docs/exploration/area-1-agentic-information-synthesis.md:134-135` describes a hypothetical training-signal flow from KG's settle gate to substrate's LoRA training (see §3 row "Substrate's own ground-truth dataset accumulation" above). This is documentation, not scheduler config — but if migrated verbatim it would justify someone wiring substrate to read KG's settle-gate DB later. **Soft leakage** (documentation-level only).

KG `docs/exploration/area-4-cross-domain-signal-networks.md:139` — "Polymarket CLOB ingest could initially share data-pipeline tooling with KG's Phase 14.0.2 prediction market provider, then fork as the substrate's needs diverge." This implies code-sharing that [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §3 forbids ("symlinks across repos", "shared git submodules pointing into either project's main tree"). **Soft leakage** (documentation-level only).

### 4.4 Substrate-side schedulers

Substrate has no code yet (Phase 0). No cron, no PM2, no scheduler. Nothing to audit. **Clean by absence.**

### 4.5 Substrate-side documentation referencing KG runtime state

Substrate `CLAUDE.md` §"KG settle-gate quick check" provides an operator-run `sqlite3` query against KG's `quality_gate_breaches.db`. This is an *operator-driven, ad-hoc* read, executed manually from a shell — not substrate runtime, not a scheduler trigger. [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §6 explicitly allows file-level sharing under operator scheduling: "coordination is operator-driven (manual scheduling decisions written into the operator's calendar or runbook), not automated cross-process IPC." **Clean.**

**Schedule-isolation summary:** 0 hard violations (no cron/scheduler/runtime-state coupling). 2 soft leakages, both confined to KG-side documentation that is itself the migration source material. Both are addressed by §2.2 / §2.3 rewrite specifications.

---

## 5. KG-side references needing substrate-side equivalents

Each row identifies a KG-side reference that implies a substrate-side artifact, manifest, or process exists or will exist. Status vocabulary used below:

- **Already designed** — a substrate-side doc covers it.
- **Pending design** — a future deliverable (Phase 0 or Vol. 1) will produce it.
- **Decision: defer to Vol. 1 design** — flagged here, deliberately not designed in Phase 0; resolves at Vol. 1 design (deliverable B).
- **Forbidden** — the implied coupling is forbidden by an ADR; no equivalent should exist.
- **Drift** — substrate and KG references diverge; recoverable, see Open Question #1.
- **N/A (consumer-internal)** — substrate need not provide an equivalent; consumer owns.

| KG reference | What substrate-side equivalent must exist | Status |
|---|---|---|
| [`docs/exploration/area-1...md:52`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md) — "LoRA adapters loaded into KG's Gateway alongside KG's own RLAIF-trained adapters" | Substrate must publish a LoRA adapter format the consumer's loader can consume. | **Already designed** — [`docs/design/special-herbs-formats-api.md` §"Release Directory Layout"](../design/special-herbs-formats-api.md) standardizes `adapter_config.json` + `adapter_model.safetensors` + signed manifest. |
| [`docs/exploration/area-1...md:53`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md) — "Knowledge graph snapshots are queried at decision time as a static read-only resource" | Substrate must define a `kg_snapshot` artifact format with a stable schema for consumer-side `kg_lookup` style integrations. | **Pending design** — [`docs/design/special-herbs-formats-api.md` §"Open Questions Deferred Beyond Phase 0"](../design/special-herbs-formats-api.md) item 4 acknowledges this. Resolves at Vol. 2 design. |
| [`docs/exploration/area-1...md:54`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md) — "Synthesis notes surfaced as DSPy context for catalyst events the substrate has analyzed in depth" | Substrate must define a synthesis-note artifact format (likely a JSON document with structured citations + per-event metadata). | **Decision: defer to Vol. 1 design (deliverable B).** Format library should not absorb synthesis-note schema pre-emptively. Vol. 1 deliverable B will decide whether Vol. 1's release bundle includes synthesis notes; if yes, the schema lands in [`special-herbs-formats-api.md` §"Open Questions Deferred Beyond Phase 0"](../design/special-herbs-formats-api.md) as a 5th bullet (alongside KG snapshot + correlation matrix). If Vol. 1 ships LoRA-only, the synthesis-note format slips to Vol. 2+. Either way the substrate's `ArtifactType` literal stays unchanged through Vol. 1. |
| [`docs/exploration/area-1...md:55`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md) — "Mispricing flags become an additional `RawSignal` type" | Consumer-internal — substrate need not provide an equivalent. The substrate emits flags; consumers wrap them in their own signal types. | N/A (consumer-internal). |
| [`docs/exploration/area-1...md:56`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md) — "Source coverage manifests inform KG's circuit-breaker / fallback logic" | Substrate must publish a source-coverage manifest format (separate from the artifact manifest — describes what was ingested when, not what was released). | **Decision: defer to Vol. 1 design (deliverable B).** Distinct from `manifest.json.training_data_hash` (which is a single hash; source-coverage is a structured map). Vol. 1 deliverable B will decide whether to attach source-coverage as an additional file inside the release directory, as a sibling sidecar published alongside the release, or as an opaque per-event field inside the existing manifest. The format library does not absorb this until Vol. 1 design picks one of the three. |
| [`docs/exploration/area-1...md:134`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md) — "Outcome ground truth from KG's settle gate" | Substrate needs an independent ground-truth ingestion pipeline (per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2, substrate cannot read KG's settle-gate DB). | **Pending design** — Vol. 1 deliverable B will design substrate's own ground-truth ingestion (FDA decisions resolved against AC briefing predictions, ingested independently of KG's `decision_log.db`). The KG-coupled phrasing in this line must be rewritten during migration. |
| [`docs/exploration/area-1...md:135`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md) — "KG's RLAIF cycle feeds reward signals back into substrate LoRA training" | **No equivalent should exist.** This describes a forbidden cross-repo training-time coupling. The substrate must NOT design a path that consumes consumer-side RLAIF outputs. | **Forbidden by [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2.** Rewrite during migration; do not provide an equivalent. |
| [`docs/exploration/area-4...md:139`](file:///Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-4-cross-domain-signal-networks.md) — "Polymarket CLOB ingest could initially share data-pipeline tooling with KG's Phase 14.0.2 prediction market provider" | Substrate must have its own Polymarket ingest (per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §4 "duplicate ingestion is the accepted cost"). | **Pending design** — Vol. 2 design. The KG-coupled phrasing must be rewritten during migration. |
| Substrate `docs/ROADMAP.md` line 67 + cross-repo-coordination references `moat_fda_equity_catalyst.yaml` | KG must have a strategy YAML by that name for the substrate's Vol. 1 release to have a consumer. | **Drift** — KG `docs/ROADMAP.md` §14A.4 names this YAML `regulatory_event_contracts.yaml`, not `moat_fda_equity_catalyst.yaml`. Already flagged in substrate [`docs/operations/cross-repo-coordination.md` §"When KG-Side Documentation Drifts From Substrate Plans"](cross-repo-coordination.md). See Open Question #1 below. |
| KG ROADMAP Phase 14A.4 — `BAYESIAN_BELIEF` learning mode, `event_triggered` scheduling, `hard_abort` Cloud CIO overlay | Consumer-internal mechanisms — substrate need not provide equivalents. | N/A (consumer-internal). Substrate correctly does not reference these. |

**Substrate-side equivalents summary:** 4 already designed, 3 pending design, 2 deferred to Vol. 1 design (synthesis-note + source-coverage formats — both opt-in, will only land in `special-herbs-formats` if Vol. 1 design includes them in the release bundle), 1 forbidden, 1 known drift (YAML name — see Open Question #1).

---

## 6. Recommended migration sequence

Migration is post-KG-Phase-13.1 (~late August 2026) per [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md) §"Migration Path". When the trigger fires, ordering preference is: reduce documentation coupling first, then content migrations, then substrate-side cleanups.

1. **Pre-stage substrate-side stub paths.** Add empty (or frontmatter-only) stubs at `docs/research/area-1-architecture.md` and `docs/research/area-4-architecture.md`. Substrate-side docs may now reference the future paths. Rationale: lets substrate `docs/ROADMAP.md` §"Related repos" stop linking back into KG `docs/exploration/...` ahead of content migration. Lowest risk; fully reversible.

2. **Re-write substrate `docs/ROADMAP.md` §"Related repos"** to point at the substrate-side stubs instead of KG `docs/exploration/...`. Removes the cross-repo `..` paths that are the only structural reason substrate currently knows the KG `docs/exploration/` filenames. Once this lands, KG is free to relocate or rename its copies without substrate-side breakage.

3. **Migrate `area-4-cross-domain-signal-networks.md` first.** Cleanest of the three (area-4:135 already states substrate "is mostly self-justifying"). Section-level rewrites per §2.3 above. This validates the migration shape without touching the highest-coupled doc. Substrate-side stub at `docs/research/area-4-architecture.md` becomes the canonical content.

4. **Migrate `area-1-agentic-information-synthesis.md` second.** Largest rewrite (entire §"Initial consumer: King Geedorah" + §"Future consumers" + §"Dependencies on KG" must be removed or rewritten). Substrate-side stub at `docs/research/area-1-architecture.md` becomes canonical. Cross-checks against [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6 must pass before merge.

5. **Distill `research-substrate-roadmap.md` into substrate `docs/ROADMAP.md` §"Strategic framing"** (single subsection, ~15 lines, capturing the depth-vs-breadth framing plus the area-1-and-4 complementarity rationale from §2.1's "migrate, rewrite" rows). Drop the KG-internal phasing entirely (already superseded by substrate ROADMAP). No standalone research doc materialized — the residue is small enough that a ROADMAP subsection is the right home.

6. **Mark KG-side originals as superseded.** Each of the three KG `docs/exploration/` files becomes a 1-line redirect pointing to the substrate path. Operator decides whether to leave them in place or delete; both are valid. Recommend leaving them so KG's GraphRAG (`data/code_graph.db`) doesn't lose the doc_id reference.

7. **Run grep checks** on the migrated `docs/research/area-1-architecture.md` and `docs/research/area-4-architecture.md` to confirm zero residual occurrences of the consumer-name-policy strings: `King Geedorah`, `\bKG\b`, `archetype-2`, `Gateway`, `Commander`, `Scout`, `RawSignal`, `settle gate`, `RLAIF cycle`, `kg_lookup`, `circuit-breaker`, `Phase 14`, `Phase 1\.2`. Per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6 + the governing principle in §2. (Substrate `docs/ROADMAP.md`, `docs/operations/`, `AGENTS.md`, `CLAUDE.md` are exempt — those destinations may name the initial consumer per the policy.)

8. **Update [`docs/operations/cross-repo-coordination.md`](cross-repo-coordination.md) if anything changed** in the consumer-contract pinning model post-migration. Likely no-op; included for completeness.

---

## 7. Open questions

The four nice-to-have questions surfaced in the initial draft have been resolved in-line:

| Resolved question | Resolution | Where |
|---|---|---|
| Migration vs. distillation for `research-substrate-roadmap.md` | Distill into substrate `docs/ROADMAP.md` §"Strategic framing"; no standalone research doc | §1 table row + §2.1 Resolution + §6 step 5 |
| Consumer-name policy in cross-repo coordination contexts | Asymmetry formalized: code + architecture/research/design docs are consumer-agnostic; operations/ROADMAP/AGENTS may name initial consumer for cross-repo touchpoints | §2 "Governing principle" |
| Synthesis-note + source-coverage manifest format placement | Defer both to Vol. 1 design (deliverable B); format library does not absorb pre-emptively | §5 rows |
| `archetype-2-volume-shape-system-vision.md` cross-link | Sever in migrated copy; back-pointer dropped per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §6 | §2.1 lines 1-22 disposition |

One question genuinely requires operator decision before it can be closed:

1. **YAML name drift.** Substrate `docs/ROADMAP.md` line 67 + [`cross-repo-coordination.md`](cross-repo-coordination.md) reference `moat_fda_equity_catalyst.yaml` as Vol. 1's consumer. KG `docs/ROADMAP.md` §14A.4 names the strategy `regulatory_event_contracts.yaml`. Should the substrate side rename references to match KG's actual naming, OR wait for KG to confirm the final filename when Phase 14A is implemented?

   **Blocks Vol. 1 design (deliverable B), not Phase 0 deliverable D landing.** The eval harness will need to bind to a concrete filename, but Vol. 1 design itself is gated on KG Phase 12.1 (Golden Dataset Regression Suite) per substrate `docs/ROADMAP.md` §"Cross-Repo Dependencies".

   **Recommendation:** keep substrate references at `moat_fda_equity_catalyst.yaml` until KG ships Phase 14A.4 with a final filename, then update both sides in a coordinated PR pair (KG-side YAML rename or new file + substrate-side reference update). Rationale: KG Phase 14A.4 is a future-phase plan, not landed code; filenames in pre-implementation roadmap rows can change cheaply on either side. The current drift is documented in [`cross-repo-coordination.md` §"When KG-Side Documentation Drifts From Substrate Plans"](cross-repo-coordination.md) and is recoverable. Pre-emptively renaming on the substrate side risks a second rename if KG settles on a third name during implementation.

---

## See Also

- [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) — eight rules, especially §6 (no consumer enumeration in substrate code).
- [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md) — §"Migration Path for Existing Substrate Documentation" (the trigger).
- [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) — §1 topology matrix, §2 schedule isolation, §3 third-package recipe pattern, §4 migration triggers, §5 anti-temptation list.
- [`docs/ROADMAP.md`](../ROADMAP.md) — Phase 0 deliverable D entry; Phase 1 KG-side dependency on Phase 13.1 RLAIF Pipeline Validation.
- [`docs/operations/cross-repo-coordination.md`](cross-repo-coordination.md) — operator-driven handoff; documentation-drift resolution protocol.
- [`docs/design/special-herbs-formats-api.md`](../design/special-herbs-formats-api.md) — manifest schema; companion-package allowance.
- KG `docs/exploration/area-1-agentic-information-synthesis.md`, `area-4-cross-domain-signal-networks.md`, `research-substrate-roadmap.md` — migration sources.
