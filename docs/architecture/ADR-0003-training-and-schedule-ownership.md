---
adr: 0003
title: "Training Pipeline & Schedule Ownership Boundaries"
status: accepted
date: 2026-04-29
deciders: jegriffi91
supersedes: none
superseded_by: none
related:
  - ADR-0001-substrate-as-artifact-contract.md
  - ADR-0002-separate-repo-from-consumers.md
---

# ADR-0003 — Training Pipeline & Schedule Ownership Boundaries

## Status

**Accepted, 2026-04-29.** Companion to [ADR-0001](ADR-0001-substrate-as-artifact-contract.md) (artifact contract) and [ADR-0002](ADR-0002-separate-repo-from-consumers.md) (filesystem separation). Locks in additional boundary rules that ADR-0001 + ADR-0002 do not explicitly cover.

## Context

ADR-0001 establishes the *artifact* contract between substrate and consumers. ADR-0002 makes that contract filesystem-enforced. Neither explicitly addresses three operationally important boundaries that will compound coupling drift if left undocumented:

1. **Training-pipeline ownership.** Both substrate and King Geedorah (KG) run LoRA fine-tuning, RLAIF teacher grading, and ORPO/GRPO training cycles. Without an explicit boundary, the temptation is to share training code, training schedules, eval harnesses, or even shared GPU resources at runtime.

2. **Schedule ownership.** KG runs a weekend training cron gated by Phase 13 settle metrics. Substrate runs per-volume training cycles gated by ROADMAP volume gates. Without an explicit rule, "just trigger substrate retraining when KG drift fires" or "just have substrate read KG's settle-gate DB to decide when to release Vol. N+1" look tempting and would silently fuse the two projects' lifecycles.

3. **Recipe / pattern sharing.** Both projects will independently arrive at similar ORPO recipes, eval-harness patterns, and DSPy signature conventions. Without an explicit rule, "just import the substrate's recipe into KG" or vice versa looks tempting and would re-introduce the cross-repo imports that ADR-0002 forbids.

This ADR makes the boundaries explicit and forbidden patterns enumerable.

## Decision

### 1. Topology Ownership Matrix

The substrate owns the topology of substrate's *training* pipeline. The consumer owns the topology of its *inference* stack and its own continuous-learning loop. The matrix:

| Asset | Substrate owns | Consumer owns |
|---|---|---|
| Substrate training pipeline (Unsloth / PEFT config, training data assembly, RLAIF teacher prompts, eval harness shape) | ✓ | |
| Substrate base-model selection (which Llama / Qwen for which volume) | ✓ | |
| LoRA adapter file-format compliance (peft `adapter_config.json` + `adapter_model.safetensors`) | ✓ | |
| Manifest schema (`special-herbs-formats` package per [ADR-0001](ADR-0001-substrate-as-artifact-contract.md) §8) | ✓ | |
| Substrate's own continuous-learning loop (per-volume gates, postmortems, next-volume design) | ✓ | |
| Substrate's own ground-truth dataset accumulation | ✓ | |
| Consumer Gateway multi-LoRA composition (load order, weight scaling, fallback chain) | | ✓ |
| Consumer Scout / Commander / Cloud CIO pipeline (or equivalent inference stack) | | ✓ |
| Consumer's own RLAIF / ORPO / GRPO training (on consumer-internal adapters) | | ✓ |
| Consumer's strategy YAML manifests (which substrate volume to pin) | | ✓ |
| Consumer-side counterfactual scoring + settle gate | | ✓ |
| Consumer-side feature engineering on top of substrate-emitted features | | ✓ |

Specifically: substrate has **no opinion** on what the consumer does with a published artifact at inference time, and the consumer has **no opinion** on how the substrate trained the artifact. The contract surface is the manifest + the binary files only.

### 2. Schedule Isolation

Each project's scheduler is sovereign. Cron, PM2, weekend training, settle gates — none cross repo boundaries.

Specifically forbidden:

- Substrate code triggering KG's PM2 jobs (or any other consumer scheduler).
- KG code triggering substrate training cycles.
- Shared cron files defined in either repo that fire jobs in the other.
- "Just call this script in the other repo" cross-repo invocations from any scheduled job.
- Substrate reading KG's settle-gate database, breach log, or any other live runtime state to decide when to train.
- KG reading substrate's training-progress state to decide when to allocate trust to a substrate-augmented strategy.

The **only** cross-repo handoff is the artifact release per [ADR-0001](ADR-0001-substrate-as-artifact-contract.md) §1 and [docs/operations/cross-repo-coordination.md](../operations/cross-repo-coordination.md). That handoff is operator-driven, not scheduler-driven. KG decides whether to pin a new substrate volume by editing its strategy YAML; substrate decides when to release a volume by completing its own internal volume gates.

### 3. Recipe / Pattern Sharing Goes Through a Third Package

Each project develops its own training recipe. If a pattern matures and both projects want it, it goes into a **new** separately-versioned package, never into either repo's main codebase.

Naming convention: `special-herbs-<scope>` for packages owned by the substrate and consumed by others. Examples:

- `special-herbs-formats` (already designed in [docs/design/special-herbs-formats-api.md](../design/special-herbs-formats-api.md)) — manifest schema + verification utilities.
- `special-herbs-training-recipes` (hypothetical future) — if a clean ORPO-on-regulatory-corpora recipe matures and KG wants to adopt it for KG's own internal training, this is where it goes.

The third-package promotion mechanism is identical to [ADR-0002](ADR-0002-separate-repo-from-consumers.md)'s existing `special-herbs-formats` allowance, generalized. The rules are:

- The third package contains **only** the shared pattern itself — no business logic, no integration glue.
- The third package is published separately and pinned independently by both consumers.
- Promotion to a third package requires both projects to **already independently want it**, not speculative future need.
- Substrate and KG remain free to diverge from the third-package pattern at any time by reverting to project-local implementations.

Specifically forbidden:

- `import king_geedorah.training` from substrate code.
- `import special_herbs.training` from KG code.
- Symlinks across repos.
- Shared git submodules pointing into either project's main tree.
- Sibling-directory monorepo experiments where both projects coexist under one root.

### 4. Migration Triggers

Code currently in KG that "feels substrate-like" (e.g., `data_ingestion/fda_briefing_source.py`, the FOMC ingestion pipeline, etc.) does NOT automatically migrate to substrate. Default: **stays in KG** if KG uses it for KG's own purposes — even if substrate also needs the same source. Substrate writes its own version per [ADR-0001](ADR-0001-substrate-as-artifact-contract.md) §4 (duplicate ingestion is the accepted cost).

Exceptions — rare, and only by amendment to this ADR:

1. **Pure-research artifacts with no operational consumer in KG.** Example: the Area 1 and Area 4 architecture exploration docs currently at `~/dev/king-geedorah/docs/exploration/`. These migrate to substrate when substrate's design work for the corresponding volume begins (per [ADR-0002](ADR-0002-separate-repo-from-consumers.md) §"Migration Path for Existing Substrate Documentation").

2. **Code that becomes operationally orphaned in KG** because KG drops the related strategy. Then either substrate adopts a fork (independent code, history-attribution preserved by attribution comment, no git-level lineage) OR the code is deleted in KG and the knowledge is captured in a substrate design doc instead.

Cut-over migrations require all of: (a) explicit operator decision, (b) ADR amendment that names the specific code unit being moved, (c) KG-side cleanup PR, (d) substrate-side intake PR. The default is "no migration" — friction is intentional.

### 5. Anti-Temptation List

Patterns specifically forbidden because they look tempting and each one re-introduces coupling that ADR-0001 + ADR-0002 + this ADR are designed to prevent:

| Tempting pattern | Why it's forbidden | Correct alternative |
|---|---|---|
| "Just import the substrate's eval harness into KG to debug." | Cross-repo import; couples release cadence; defeats §6 of ADR-0001. | Reproduce the eval steps independently in KG, or operator-driven artifact-only handoff. |
| "Just have KG's PM trigger substrate retraining when it sees drift." | Runtime coupling per ADR-0001 §3, extended to schedulers per this ADR §2. | Operator notes the drift, opens a substrate-side issue, substrate decides next volume. |
| "Just share the ORPO library across repos via a sibling directory." | Sibling-directory monorepo violates ADR-0002 §"Decision". | Third package per this ADR §3, when both projects independently want it. |
| "Just have substrate read KG's settle-gate DB to know when to release a volume." | Shared database forbidden per ADR-0001 §4 and runtime read forbidden per §3. | Operator-driven release decision per cross-repo-coordination.md. |
| "Just share GPU memory across processes that span both projects." | Process-level coupling; if substrate training crashes the GPU context, KG inference dies with it. | Each project gets its own process tree; coexistence is operator-scheduled. |
| "Just have KG's signal listener push freshly resolved trades to substrate's training queue." | Pub-sub channel forbidden per ADR-0001 §3. | Substrate accumulates its own ground-truth independently; resolved trades may be one input among many, sourced via substrate's own ingestion. |
| "Just let KG and substrate share a venv." | Implicit dependency coupling; one project's pin upgrade silently breaks the other. | Each project has its own `pyproject.toml`. Hardware-shared base-model files (e.g., a single Llama-3.1-8B safetensors blob on disk) are fine — file-level sharing is not API-level sharing. |
| "Just have substrate import KG's manifest types to verify consumer compatibility." | Substrate must not know what consumers exist (ADR-0001 §6). | `compatible_consumer_contracts` is opaque strings; the substrate publishes them, the consumer asserts membership. Substrate does not validate against consumer-side schemas. |

### 6. Process Isolation

When substrate and consumer run on the same machine (M2 Ultra hosts both today), each runs in its own process. Substrate training is one process tree (or batch process); KG inference + KG training are separate process trees. No shared memory, no shared sockets, no shared in-process state across the boundary.

Workload coexistence is allowed — substrate training can run on weekends while KG is in low-volume mode — but coordination is operator-driven (manual scheduling decisions written into the operator's calendar or runbook), not automated cross-process IPC.

Specifically allowed (file-level sharing, not API-level):

- Both projects loading the same base-model safetensors file from disk into their own respective process spaces.
- Both projects reading the same FDA AC briefing PDF off the local filesystem (each ingests independently per [ADR-0001](ADR-0001-substrate-as-artifact-contract.md) §4).

Specifically forbidden (process-level coupling):

- Shared MLX / PyTorch model objects across processes.
- Shared CUDA / Metal contexts.
- Cross-process locks, semaphores, or queues coordinating training cadence.
- One project monitoring the other's process tree to gate its own work.

## Consequences

### Positive

- The next 18 months of substrate-and-KG development can proceed in parallel without growing implicit coupling.
- New consumers (a sister system, external collaborator) integrate against the same boundaries — no special-cased KG-only patterns.
- Bug origins remain unambiguous: a training failure in substrate is substrate's; a training failure in KG is KG's.
- Refactor freedom is preserved on both sides indefinitely.
- The anti-temptation list gives reviewers concrete patterns to reject at PR time, instead of having to re-derive the principle each time.

### Negative

- **Code duplication.** Substrate and KG will have two FDA briefing ingestion implementations, two ORPO training pipelines, two eval harness skeletons. Per [ADR-0001](ADR-0001-substrate-as-artifact-contract.md) §4, this is the accepted cost.
- **Coordination overhead when patterns ripen.** Promoting a recipe to a third package is more work than just `import`. Mitigation: only promote when both projects already independently want it; until then, parallel implementations are fine even if they look similar.
- **Operator must mentally maintain the boundary.** Mitigation: this ADR + the anti-temptation list + grep checks during PR review.

### Neutral

- The third-package promotion mechanism is identical to [ADR-0002](ADR-0002-separate-repo-from-consumers.md)'s existing `special-herbs-formats` allowance. No new conceptual surface.
- Schedule isolation aligns with how the operator already operates the two projects today (substrate is pre-Phase-0; KG runs its own PM2 cron). The rule formalizes the existing reality rather than imposing a new constraint.
- Process isolation is the macOS / Apple Silicon default. The rule formalizes "don't try to be clever about shared state" rather than restricting an existing pattern.

## Compliance Verification

Tests / lints to add as code lands:

- Substrate codebase: `grep` for `import king_geedorah` or any path under `/king-geedorah/` → fail.
- Substrate codebase: `grep` for `pm2`, `crontab`, or path references to KG's `ecosystem.config.js` → fail.
- Substrate codebase: `grep` for paths into KG's `data/` directory (settle-gate DB, breach log, etc.) → fail.
- KG codebase: `grep` for `import special_herbs` or path references into `~/dev/special-herbs/` → fail (allow `special_herbs_formats` and any future `special-herbs-<scope>` third packages once published).
- Substrate `pyproject.toml`: `grep` for any consumer repo as a dependency → fail.
- Both repos: PR-time review check against the anti-temptation list.

These are aspirational; tooling will be added as code lands (Phase 0 deliverable E covers the lint scaffolding). For now, this ADR is the convention; reviewers enforce it.

## References

- [ADR-0001](ADR-0001-substrate-as-artifact-contract.md) — Substrate-as-Artifact Consumer Contract (the artifact-side boundary).
- [ADR-0002](ADR-0002-separate-repo-from-consumers.md) — Special Herbs Lives in a Separate Repository from Consumer Systems (the filesystem boundary).
- [docs/operations/cross-repo-coordination.md](../operations/cross-repo-coordination.md) — operator-driven handoff protocol.
- [docs/design/special-herbs-formats-api.md](../design/special-herbs-formats-api.md) — concrete realization of the third-package pattern.
- King Geedorah `docs/ROADMAP.md` Phase 13 — the consumer-side training schedule that this ADR explicitly does not couple to.
- King Geedorah `AGENTS.md` "No Synthetic Data Mandate" and "DSPy Algorithmic Prompting Mandate" — consumer-side training mandates that this ADR explicitly does not extend across the boundary.
