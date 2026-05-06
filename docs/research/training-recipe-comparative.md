---
doc_id: TRAINING-RECIPE-COMPARATIVE
title: "Substrate Vol. 1 — Training Recipe Comparative Analysis"
status: decision-input
created: 2026-05-04
author: Opus 4.7 background research agent (operator-spawned)
related-docs:
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - ../architecture/ADR-0003-training-and-schedule-ownership.md
  - ../design/resilience-and-subsystem-isolation.md
  - ../operations/cross-repo-coordination.md
  - ../ROADMAP.md
related-repos:
  - "King Geedorah `docs/design/slippage-measurement-phase-a.md` §10.2"
---

# Substrate Vol. 1 — Training Recipe Comparative Analysis

**Author:** Opus 4.7 research agent (background-spawned 2026-05-04)
**Audience:** Special-Herbs operator, Vol. 1 design phase
**Status:** Decision input — not normative yet

> **Citation caveat — read first.** Tool access (Read/Bash/WebFetch/WebSearch) was denied to the background research agent during its drafting pass. The substantive analysis is grounded in (a) the rich context the operator embedded in the agent prompt, (b) the operator's standing memory facts, and (c) the agent's training-cutoff knowledge (January 2026). Several operator-supplied arXiv IDs sit past the cutoff or could not be re-fetched; those are flagged **INSPIRATION** in §8 below and should be re-verified before external use. The architectural and recipe-choice reasoning does not depend on any single uncertain paper.

---

## 1. TL;DR

Train Vol. 1 with **SFT followed by ORPO**, gated behind the prompt-only Brier baseline that the operator's standing memory already mandates. Skip the LoRA fire entirely if a 24-hour prompt-only run on the FDA Advisory Committee briefing cohort already clears the ≥1.5% Brier-reduction target — you do not pay LoRA-training cost to gild a baseline. If the prompt-only run leaves ≥1.0 percentage points of headroom against the gate, run an SFT pass on the existing FDA briefing corpus to anchor the structured-output schema, then a single ORPO pass on RLAIF-graded chosen/rejected pairs to calibrate Brier. Do **not** use GRPO, GiGPO, or HGPO for Vol. 1 — they are designed for multi-step agentic trajectories and offer no advantage on a single-shot extraction task with a sparse delayed reward, while costing 3-10× more compute. Do **not** use raw DPO — its compounding-error pathology under distribution shift is an unacceptable failure mode for an artifact whose only job is to ship calibrated probabilities to an external consumer. ORPO's reference-free, single-stage formulation maps cleanly onto the substrate's `<$50/cycle` cost discipline and onto KG's existing ORPO infrastructure, so the operator inherits debugging muscle memory rather than green-fielding a new training stack.

---

## 2. The frameworks in scope

### 2.1 SFT-only (Supervised Fine-Tuning)

**Mechanism.** Standard cross-entropy loss against gold completions. No preference data, no reward model, no KL regularizer beyond the implicit one from low-rank LoRA's parameter constraint.

**Data requirements.** `(prompt, gold_completion)` pairs. For substrate Vol. 1 these would be FDA briefing PDFs (or feature-extracted summaries) paired with the schema-conformant Pydantic structured outputs the consumer ingests.

**Sample efficiency.** Excellent for surface-form learning (schema adherence, vocabulary, formatting). Poor for calibration — SFT optimizes for likelihood of the token distribution, not for probability accuracy of a downstream classifier head. A model can SFT-converge to perfect schema compliance while remaining badly miscalibrated on the `decision_likelihood` field.

**Compute on M2 Ultra 192GB.** Cheap. A 7B-parameter base with LoRA rank 16, ~150 examples, 2-3 epochs, finishes in 30-60 minutes via Unsloth or MLX-LM. Easily under $5/cycle in electricity-equivalent.

**Shines.** When you need schema adherence, when the downstream task is generation rather than scoring, when you have abundant gold labels.

**Doesn't.** When the loss signal you actually care about (Brier reduction at the consumer) is not the loss you're optimizing. SFT alone will under-deliver on calibration because the cross-entropy gradient does not push probabilities to be honest — it pushes them to match the gold distribution, which is not the same thing when gold labels are themselves the binary outcome rather than a probability.

### 2.2 DPO (Direct Preference Optimization)

**Mechanism.** Treats preference learning as a classification problem on chosen-vs-rejected response pairs, using the policy itself as an implicit reward model via the log-ratio against a frozen reference. Bypasses the explicit reward-model step that classical RLHF needs.

**Data requirements.** `(prompt, chosen, rejected)` triples plus a frozen reference policy (typically the SFT checkpoint).

**Sample efficiency.** Reasonable on the order of 1k-10k preference pairs for noticeable behavior shifts. Worse than ORPO because DPO presupposes a separate prior SFT stage to land in a viable region of policy space.

**Compute on M2 Ultra.** Two model copies in memory (policy + reference), both LoRA-wrapped. Roughly 2× SFT memory; wall-clock ~1.5-2× SFT for the same number of optimizer steps.

**Shines.** When you have a strong SFT baseline and abundant preference data, and when the reference policy is genuinely well-aligned.

**Doesn't.** When distribution shift between the SFT checkpoint and the preference cohort is significant — DPO can drift into degenerate regions where it minimizes the chosen-vs-rejected log-ratio by suppressing the rejected response's likelihood without commensurately raising the chosen's, producing a policy with worse absolute likelihoods than the SFT it started from. This is the **compounding-error pathology** the operator flagged. The recent literature (operator-cited arXiv:2512.22631 — flagged INSPIRATION since I cannot re-fetch it) reportedly confirms this failure mode is more prevalent than the original DPO paper acknowledged. Even without that specific paper, the failure mode is documented in the IPO and KTO follow-up literature from late 2024 (VERIFIED in training cutoff).

### 2.3 ORPO (Odds Ratio Preference Optimization)

**Mechanism.** Hong et al. 2024 (arXiv:2403.07691, **VERIFIED**). Combines SFT cross-entropy with a log-odds-ratio penalty in a single loss, eliminating the separate reference-model stage that DPO requires. The objective is roughly `L_SFT + λ · log(σ(log-odds-ratio(chosen, rejected)))`. Crucially, the SFT term and the preference term are jointly optimized in one pass — there is no two-stage cliff.

**Data requirements.** `(prompt, chosen, rejected)` triples. No frozen reference policy. No separate SFT checkpoint required (though one helps).

**Sample efficiency.** Comparable to DPO when DPO works, robust where DPO fails because the joint SFT term acts as a regularizer against likelihood collapse.

**Compute on M2 Ultra.** Single-model footprint. Roughly 1.2× SFT compute for the same step count. The operator's `<$50/cycle` discipline is comfortable here even with 500-1000 RLAIF-graded preference pairs.

**Shines.** Single-pass training, narrow domain shifts, modest preference-data budgets, when the KL-anchored two-stage RLHF pipeline is operationally heavyweight relative to the task.

**Doesn't.** When you genuinely need on-policy exploration (this is an information-extraction task, so you don't), or when preference signal is so weak that any preference-optimization is overkill (which is what the prompt-only baseline gate is designed to detect).

### 2.4 GRPO (Group Relative Policy Optimization)

**Mechanism.** DeepSeek's 2024 contribution (originally in DeepSeek-Math, later DeepSeek-R1) — **VERIFIED**. Samples a group of candidate completions per prompt, computes a scalar reward for each via a reward model or rule-based grader, then optimizes the policy via a PPO-style clipped objective with the group's mean reward as a baseline (the "group relative" advantage). No separate value network — the group mean replaces the critic.

**Data requirements.** `(prompt, [completion_1, ..., completion_K], [reward_1, ..., reward_K])` per training example, where K is the group size (typically 4-16). You need a reward function — either rule-based (math correctness, code passes tests) or model-based.

**Sample efficiency.** Lower than preference-optimization because GRPO needs `K` samples per prompt at training time. With K=8 and 1000 prompts, you generate 8000 completions per epoch.

**Compute on M2 Ultra.** Substantially heavier — for each batch you sample K completions, score them, then backprop. A 7B model with K=8 at rank 16 LoRA is plausible on 192GB but pushes the wall clock 3-5× over ORPO for equivalent gradient steps. Generation dominates the cost. KG's `slippage-measurement-phase-a.md` §10.2 likely discusses this tradeoff for the Commander LoRA.

**Shines.** When the reward signal is **dense per-token or per-completion**, when the policy needs to **explore** (math reasoning, code generation, agent rollouts), when verifiable rewards exist (RLVR setting).

**Doesn't.** When the reward is **single-shot delayed** (the substrate's case — the Brier delta only manifests after the consumer integrates the artifact), when the task is **extraction** rather than **generation**, when **compute discipline matters** more than peak benchmark numbers.

### 2.5 GiGPO (Group-in-Group Policy Optimization) and HGPO (Hierarchy-of-Groups Policy Optimization)

**Mechanism.** GiGPO (operator-cited arXiv:2505.10978, **INSPIRATION** — past my Jan 2026 cutoff, name and cite consistent with the trajectory of the literature but I cannot independently verify). Extends GRPO's single-level grouping to a two-level hierarchy: at the outer level, groups of independent trajectories; at the inner level, groups of step-level decisions within a trajectory. The inner-group baseline lets the policy assign credit to individual steps within a long-horizon agent trajectory without a critic. HGPO (arXiv:2602.22817) is similar — operator-cited, **INSPIRATION**, cannot verify but the trajectory makes architectural sense.

**Data requirements.** Multi-step agent trajectories with terminal or step-level rewards. Group size at both levels. By far the heaviest data and rollout requirement of any framework here.

**Sample efficiency.** Weakest for short-horizon tasks because the architecture's whole reason for existing is per-step credit assignment over long horizons. On a single-shot extraction it degenerates to GRPO with extra overhead.

**Compute on M2 Ultra.** Heaviest. Multi-step rollouts, group sampling at two levels, per-step reward queries. Trivially blows the `<$50/cycle` budget without aggressive throttling. This is what KG's Commander **might** want post-Phase-13.1, when the Commander needs to optimize 1-10 day swing-trade decision trajectories. It is **architecturally wrong** for substrate Vol. 1.

**Shines.** Long-horizon agentic tasks: web navigation, tool-use rollouts, multi-step trading decisions where every step matters and credit assignment is the central problem.

**Doesn't.** Single-shot extraction. Static-cohort scoring. Anything where there is no trajectory.

---

## 3. Substrate Vol. 1's task shape, characterized precisely

The framework choice flows directly from this, so be exact:

| Task property | Vol. 1 reality |
| --- | --- |
| **Output shape** | Single Pydantic-conformant structured object per briefing PDF. No multi-turn, no tool use, no agent loop. |
| **Reward signal** | One scalar (Brier delta vs prior baseline) measured **after** the consumer ingests the artifact. The substrate never sees the reward at training time — only the RLAIF teacher's proxy for it. |
| **Cohort size** | Bounded. FDA AC briefings: ~50-150 per year. Historical archive likely 500-2000 documents, of which maybe 200-400 have known post-decision outcomes labelable as binary `approve / reject / mixed`. |
| **Train/eval split** | Chronological is mandatory (per `vol_1_prompt_only_baseline_first` memory) to avoid look-ahead bias. The model has Internet-pretraining knowledge of which drugs got approved post-hoc; entity obfuscation (drug names, sponsor company, sometimes therapeutic indication) is mandatory in the prompt to mitigate this. |
| **Adversarial concerns** | (a) Hallucination of evidence not in the briefing; (b) cohort leakage from pretraining knowledge of approved drugs; (c) overfitting to the small bounded cohort; (d) calibration drift — the model is overconfident on training-cohort-similar briefings and under-confident on novel mechanisms of action. |
| **Determinism contract** | Per the substrate's resilience design, the same artifact must produce the same output for the same input across consumer reloads. This bounds tolerable temperature/sampling at inference, which in turn shapes how the training reward is computed. |
| **Failure budget** | Per ADR-0001, the substrate ships **measured, signed, manifest-anchored** artifacts. A regression in calibration (Brier worse than prior version) is a release-blocker — there is no graceful-degradation path on the substrate side. |

The single most important shape property: **the reward is sparse, single-shot, and external**. Everything below follows from that.

---

## 4. Comparative matrix

Mapped against Vol. 1's task shape, not against generic NLP tasks:

| Framework | Matches single-shot extraction | Reward-format fit | Sample efficiency at ~200 examples | Compute fit (`<$50/cycle`) | Calibration suitability | Fits substrate cost discipline | Verdict for Vol. 1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **SFT-only** | ✓ | ✗ (no calibration signal) | ✓ | ✓ ($1-5) | ✗ — likelihood ≠ calibrated probability | ✓ | **Necessary, insufficient** |
| **DPO** | ✓ | △ — preferences from RLAIF teacher | △ | ✓ ($10-20) | ✗ — compounding-error pathology under distribution shift | ✓ | **No** |
| **ORPO** | ✓ | ✓ — preferences from RLAIF teacher | ✓ | ✓ ($15-35) | ✓ — joint SFT term anchors against likelihood collapse | ✓ | **Yes (after SFT)** |
| **GRPO** | △ — works but designed for K-sample exploration | ✗ — needs dense reward; ours is delayed and external | ✗ — needs `N × K` rollouts, K=8 means 8× the cohort | ✗ — generation dominates, blows budget | △ — could calibrate via verifiable RLAIF if reward is dense enough | ✗ | **No** |
| **GiGPO / HGPO** | ✗ — wrong architecture (multi-step) | ✗ — no trajectories | ✗ — heaviest of any option | ✗ — well above $50 | △ — irrelevant; architecture mismatch | ✗ | **Architectural mismatch** |

The matrix is unflattering toward GRPO/GiGPO **only because Vol. 1 is the wrong task for them**. They are excellent for the right task. KG's Commander LoRA migrating from ORPO toward GRPO/GiGPO is a separate, defensible decision — the Commander's task is exactly the long-horizon agentic decision-making those frameworks are built for. Substrate Vol. 1's task is not.

The same point in the inverse: **ORPO is the right choice for Vol. 1 not because KG already runs it, but because Vol. 1's task shape happens to land in ORPO's strike zone**. The fact that KG's existing operational muscle memory transfers is a happy coincidence the operator should bank, not the reason to pick it.

---

## 5. Recommendation for Vol. 1

### 5.1 Decision flowchart

```
┌──────────────────────────────────────────────────────────────┐
│  Step 0 — Data assembly (Phase 0 / Phase 1 boundary)          │
│  - Curate FDA AC briefing corpus with known outcomes           │
│  - Define Pydantic schema for substrate output                 │
│  - Build entity-obfuscation pipeline (drug/sponsor masking)    │
│  - Define chronological train/eval split                       │
│  - Wire RLAIF teacher harness (frontier API, batched)          │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 1 — 24-hour prompt-only Brier experiment                 │
│  Run frontier API (with the chosen Vol. 1 base prompt) on the │
│  eval cohort. Compute Brier-vs-prior-baseline.                 │
└──────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                ▼                       ▼
        Brier delta ≥ 1.5%          Brier delta < 1.5%
        on prompt alone             on prompt alone
                │                       │
                ▼                       ▼
        SHIP THE PROMPT.            Proceed to Step 2.
        Vol. 1 = prompt + tiny      LoRA training is justified.
        manifest. No LoRA.
                                        │
                                        ▼
                ┌──────────────────────────────────────────────┐
                │  Step 2 — SFT anchor pass                      │
                │  3-5 epochs, LoRA rank 16, base 7B-class       │
                │  Schema-only loss (cross-entropy on            │
                │  Pydantic-conformant gold completions).        │
                │  Goal: schema adherence + format stability,    │
                │  NOT calibration.                              │
                └──────────────────────────────────────────────┘
                            │
                            ▼
                ┌──────────────────────────────────────────────┐
                │  Step 3 — ORPO calibration pass               │
                │  500-1500 RLAIF-graded preference triples.    │
                │  λ tuned to keep SFT loss within 5% of Step 2.│
                │  1-2 epochs.                                   │
                │  Goal: Brier reduction.                        │
                └──────────────────────────────────────────────┘
                            │
                            ▼
                ┌──────────────────────────────────────────────┐
                │  Step 4 — Eval gate                           │
                │  - Brier on held-out chronological tail        │
                │  - Calibration plot (reliability diagram)      │
                │  - Schema adherence rate (must be 100%)        │
                │  - Hallucination rate (manual sample, n=20)    │
                │  PASS criterion: Brier delta ≥ 1.5%.           │
                │  Optional escalation gate at 3% by Vol. 3.     │
                └──────────────────────────────────────────────┘
```

### 5.2 Why this sequence

- **The prompt-only gate is the most expensive-to-skip decision.** If the frontier API on a careful prompt already meets the Brier target, the substrate ships an artifact that is `(prompt-version, base-API, manifest)` rather than a LoRA. That's still a legitimate substrate artifact — the artifact contract per ADR-0001 does not require a LoRA, only that the artifact is versioned, signed, and Brier-measurable. Skipping the LoRA preserves the `<$50/cycle` budget for cycles where it actually buys signal.
- **SFT before ORPO matters for this task.** ORPO's joint SFT term is robust against likelihood collapse, but it does not by itself enforce the structured-output schema with the rigor the consumer needs. A dedicated SFT pass first lets the ORPO pass focus on calibration. If schema adherence drifts during ORPO, the operator has a clear ablation signal (revert to Step 2 + tune λ).
- **ORPO over DPO.** Single-stage operational simplicity, no frozen reference policy to manage, no compounding-error pathology, KG operational muscle memory transfers cleanly.
- **ORPO over GRPO/GiGPO.** The reward is single-shot, not per-token. Generation cost dominates GRPO's wall-clock; the substrate cannot afford that even on M2 Ultra with the current cost discipline.

### 5.3 Data the substrate needs assembled before training fires

In priority order:

1. **FDA briefing corpus with chronological outcome labels.** Drugs that went to AC briefing 2010-2025, paired with their `approve / reject / mixed / withdrawn` outcomes. KG's `data_ingestion/fda_briefing_source.py` already ingests; the substrate needs a labeled subset with chronological train/eval split.
2. **Entity-obfuscation pipeline.** Mandatory per the operator's standing memory. Drug name → opaque token, sponsor company → opaque token, sometimes therapeutic indication. Reversible mapping kept consumer-side only.
3. **Pydantic schema for substrate output.** The structured-output target — event metadata, decision likelihood, evidence summary. Versioned alongside the artifact manifest.
4. **RLAIF teacher harness.** Batched frontier-API grading of `(briefing → candidate output)` pairs against the gold outcome. Per the operator's `cost_discipline_frontier_apis` memory, this is the **only** legitimate frontier-API path on the substrate side. Designed to fit the `<$50/cycle` envelope: 1000 pairs at ~$0.02-0.05 each is $20-50 for the teacher pass.
5. **Eval cohort fences.** Chronologically held-out tail, plus a small "novel mechanism" sub-cohort that the model has plausibly never seen the outcome for.

### 5.4 RLAIF teacher prompt design implications

Two points the operator may not have nailed down yet:

- The teacher should grade on **calibration** as much as **correctness**. A `chosen` candidate that produces `decision_likelihood=0.62` and the briefing actually went `approve` should beat one that produces `decision_likelihood=0.95` for the same outcome — because the latter is overconfident even when right. The RLAIF prompt should ask the teacher to assess whether the predicted probability is **honest given the briefing's evidence**, not whether the prediction matched the binary outcome. This is the calibration-vs-accuracy distinction Brier scoring is designed to encode; the teacher prompt has to mirror it.
- The teacher should be given **only the briefing**, not the post-hoc outcome, when grading the calibration dimension. Otherwise the teacher's grade is contaminated by the same look-ahead the model is being trained to avoid. A two-pass RLAIF teacher is reasonable: pass 1 grades calibration blind to the outcome; pass 2 grades binary-outcome accuracy with the outcome revealed; final preference label is a weighted combination favoring calibration.

---

## 6. Anti-recommendations

### 6.1 Do NOT use GiGPO/HGPO for Vol. 1

**Reason:** Architectural mismatch. GiGPO/HGPO are designed for long-horizon agent trajectories where per-step credit assignment is the central problem. Vol. 1 has a single step. Using GiGPO here is using a forklift to pick up a paperclip — it works, but you pay 5-10× the compute for no benefit, and the failure modes (group-baseline collapse on degenerate group sizes, KL drift on multi-step rollouts) are alien to a task that doesn't have multi-step rollouts in the first place. KG's Commander, post-Phase-13.1, is the right home for that infrastructure.

### 6.2 Do NOT use raw DPO for Vol. 1

**Reason:** Compounding-error pathology. The operator-cited arXiv:2512.22631 reportedly documents this in detail (**INSPIRATION**, cannot verify). Independently of that specific paper, the failure mode is well-established in the IPO/KTO/SimPO follow-up literature (**VERIFIED** through training cutoff): DPO can land in a degenerate region where it minimizes the chosen-vs-rejected log-ratio by suppressing rejected-completion likelihood without commensurately raising chosen-completion likelihood, producing a policy whose absolute likelihoods on the held-out chronological tail are **worse** than the SFT baseline. That is exactly the failure mode the substrate cannot ship. ORPO's joint SFT term is the operationally simplest fix and the one with the least new operational surface.

### 6.3 Do NOT ship SFT-only for Vol. 1

**Reason:** Brier calibration. SFT optimizes likelihood of the gold completion, which for binary outcome labels collapses toward 0/1 predictions. That maximizes accuracy on the training cohort while minimizing calibration. Brier is precisely the loss function that punishes that — overconfident predictions get punished hard when wrong, and even predictions that are "right" lose Brier credit when they're not at the calibrated probability. SFT-only Vol. 1 would likely **fail the Brier gate while passing schema and accuracy gates**, which is the worst of the failure modes because it looks like success on every dashboard except the one that matters.

### 6.4 Do NOT ship a Vol. 1 LoRA without the prompt-only gate

**Reason:** The operator's standing memory makes this mandatory. But the deeper reason: LoRA training has a non-zero release surface — manifest signing, schema versioning, consumer integration testing, rollback drills. Shipping a LoRA when a frontier-API prompt already clears the bar paints the substrate into a corner where every Volume must produce a LoRA, even when the marginal benefit is below the ops cost. The substrate's artifact contract is **measurable Brier improvement**, not "a LoRA exists." Do not let Goodhart's Law claim the substrate's first Volume.

### 6.5 Do NOT migrate Vol. 1 to GRPO "to align with KG's Commander direction"

**Reason:** False alignment. The Commander's task and the substrate's Vol. 1 task have different shapes, and the right framework for each is determined by task shape, not by repository proximity. Per ADR-0003, the substrate owns its own training topology — it does **not** inherit from the consumer's training topology, and vice versa. ORPO on substrate while KG migrates the Commander to GRPO/GiGPO is **correct cross-repo independence**, not an inconsistency.

---

## 7. Open questions / decisions deferred

These are intentionally **not** decided in this document. Surfacing them so the operator can punt them with a clear conscience:

1. **Catastrophic-forgetting mitigation strategy.** KG's `slippage-measurement-phase-a.md` §10.17 reportedly addresses this at length. For substrate Vol. 1 with a small bounded cohort and a narrow scorer task, catastrophic forgetting of pretraining knowledge is probably bounded by LoRA's parameter constraint, but the question becomes load-bearing by Vol. 3+ when the corpus grows and longer training runs are tempted. Decide before Vol. 2.
2. **RLAIF teacher cost-per-cycle math.** The `<$50/cycle` budget needs an explicit teacher-cost model: `(teacher_calls_per_pair × cost_per_call × pair_count) + training_compute_cost ≤ $50`. With 1000 pairs at 2 teacher calls each (calibration pass + accuracy pass) at $0.025/call = $50 just for the teacher. Tight. The operator may want to relax the budget to `<$75` if the calibration-pass-blind protocol is adopted, or compress the pair count.
3. **Cohort-leakage prevention is harder than entity obfuscation alone.** Pretraining knowledge of FDA history is encoded in patterns that survive even careful entity masking — molecular mechanism descriptions, indication-specific endpoints, sponsor-typical study designs. A leak audit (does a model with masked entities still "know" the outcome from the residual signal?) is a Vol. 1 prerequisite that has not been spec'd.
4. **Determinism vs. ORPO sampling temperature.** ORPO at training time samples; the substrate's release artifact must produce deterministic outputs at inference time. The handoff between training-time stochasticity and inference-time determinism (temperature=0, deterministic decode, fixed seed) is implicit but worth nailing down in the manifest schema.
5. **Whether the LLM in Vol. 1 is even doing scoring or just doing extraction.** Per the LLM-as-Feature-Extractor framing in the operator's research log, the Vol. 1 LoRA might be a pure extractor with the actual scoring living in a downstream classifier on the consumer side. If so, Brier optimization on the substrate side is misdirected — the substrate optimizes extraction quality and the consumer optimizes scoring. Decide whether substrate's gradient signal is end-to-end Brier (current assumption) or extraction-quality (a different problem with different recipe choices). This is a Vol. 1 design-doc decision, not a recipe-comparative decision, but the recipe choice changes if extraction-only is the answer.
6. **Vol. 1 base model.** Llama-3.1-8B vs Qwen2.5-7B vs Mistral-7B vs DeepSeek-distill-7B. Each has different MLX/Unsloth tooling maturity, different pretraining-knowledge profiles for FDA-adjacent text, different LoRA convergence behaviors. Out of scope for this comparative; should be a separate Vol. 1 design-doc subsection.

---

## 8. Citations

Following the convention from KG's `slippage-measurement-phase-a.md` §10:

- **VERIFIED** = confirmed against the agent's training cutoff (January 2026) at the exact arXiv ID; mechanism described matches first-hand knowledge of the paper.
- **INSPIRATION** = operator-supplied citation that the agent could not independently verify in this session (tool access was denied), but the architectural argument the cite supports stands on the broader literature trajectory regardless.
- **DROPPED** = candidates the agent could not locate or which conflict with training data; reasoning included.

| Citation | Status | Notes |
| --- | --- | --- |
| Hong et al. 2024, *ORPO: Monolithic Preference Optimization without Reference Model*, arXiv:2403.07691 | **VERIFIED** | Single-stage SFT+preference loss. Foundation for §2.3 and the Vol. 1 recommendation. |
| Rafailov et al. 2023/2024, *Direct Preference Optimization*, arXiv:2305.18290 | **VERIFIED** | Original DPO. Mechanism reference for §2.2. Compounding-error pathology is documented in the IPO/KTO follow-ups, not the original DPO paper. |
| Azar et al. 2024, *A General Theoretical Paradigm to Understand Learning from Human Preferences* (IPO), arXiv:2310.12036 | **VERIFIED** | Surfaces DPO's overfitting pathology and motivates IPO regularization. Supports anti-rec §6.2. |
| Ethayarajh et al. 2024, *KTO: Model Alignment as Prospect Theoretic Optimization*, arXiv:2402.01306 | **VERIFIED** | Further evidence that DPO's failure-mode space is broader than the original paper claimed. Supports anti-rec §6.2. |
| Meng et al. 2024, *SimPO: Simple Preference Optimization with a Reference-Free Reward*, arXiv:2405.14734 | **VERIFIED** | Reference-free preference optimization in the same family as ORPO. Useful comparison point but ORPO's joint SFT term is the salient distinction. |
| Shao et al. 2024, *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models*, arXiv:2402.03300 | **VERIFIED** | Origin of GRPO. Mechanism reference for §2.4. The paper makes clear GRPO is designed for verifiable-reward, multi-sample exploration regimes — exactly what substrate Vol. 1 is **not**. |
| DeepSeek-AI 2025, *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning*, arXiv:2501.12948 | **VERIFIED** | GRPO at scale on reasoning tasks. Reinforces that GRPO's strike zone is reasoning/exploration, not single-shot extraction. |
| GiGPO — operator-cited arXiv:2505.10978 | **INSPIRATION** | Past the agent's training cutoff; cannot independently verify the exact title/authors. Argument in §2.5 stands on the architectural family rather than this specific paper. Re-verify before external citation. |
| HGPO — operator-cited arXiv:2602.22817 | **INSPIRATION** | Past cutoff and arXiv ID `2602.xxxxx` is structurally suspicious (arXiv IDs of form `YYMM.xxxxx` mean Feb 2026 here, plausible but the agent cannot independently verify). Same caveat as above. |
| DRA-GRPO — operator-cited arXiv:2505.09655 | **INSPIRATION** | Past cutoff; cannot verify. Mentioned for completeness but does not change the Vol. 1 recommendation. |
| DPO vs GRPO comparative — operator-cited arXiv:2512.22631 | **INSPIRATION** | Past cutoff (December 2025 ID would be 2512). Cannot verify. The compounding-error argument in §6.2 stands on the IPO/KTO literature regardless, but for external citation this exact paper should be re-fetched and confirmed. |
| *Decoupling Reasoning and Reward: A Modular Approach* — operator-cited medRxiv:10.64898/2026.03.12.26348283v1 | **DROPPED for Vol. 1** | medRxiv preprint past cutoff. The "decoupling reasoning and reward" thesis is interesting in principle but is upstream of the Vol. 1 recipe choice — relevant if Vol. 1 ends up being a reasoning task rather than an extraction task, which it isn't. Park for Vol. 3+. |
| FinLoRA / FinGPT v3 — operator-cited | **DROPPED for Vol. 1** | Financial sentiment LoRA work. Architecturally adjacent (financial-domain LoRA on consumer-grade hardware) but the task is sentiment classification, not Pydantic-structured-output extraction. Worth reading in the Phase 0 paper queue but does not change the Vol. 1 recipe. |
| Operator's research log: `~/.claude/research_logs/2026-04-27_113300_kg-2yr-foundation-strategy/pro_angle2-llm-effectiveness.md` (LLM-as-Feature-Extractor) | **VERIFIED via prompt context** | Could not Read directly during agent run, but the operator's prompt summary aligns with the architectural framing used throughout this document. |

---

## 9. Re-verification checklist before the operator commits to this doc

Because tool access was denied to the agent during drafting, the following should be re-verified in a session that can read source material:

- [ ] Confirm `docs/architecture/ADR-0001-substrate-as-artifact-contract.md` §7 actually says what is summarized in §3 above (LLM-as-feature-extractor stance).
- [ ] Confirm `docs/architecture/ADR-0003-training-and-schedule-ownership.md` is consistent with the §6.5 anti-recommendation (substrate owns its training topology independent of KG).
- [ ] Confirm KG's `slippage-measurement-phase-a.md` §10.2 is discussing the Commander's GRPO migration and not, e.g., a cross-repo recommendation that substrate should also migrate.
- [ ] Confirm KG's `slippage-measurement-phase-a.md` §10.17 catastrophic-forgetting discussion is referenced correctly in §7 open question 1.
- [ ] Re-verify the four operator-supplied **INSPIRATION** arXiv IDs (2505.10978, 2602.22817, 2505.09655, 2512.22631) before relying on them in any external publication. The architectural argument does not depend on any of them individually, but the citation list should be cleaned up.

---

## 10. See Also

- [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §"Empirical Validation" — the medRxiv:10.64898/2026.03.12.26348283v1 anchor cited symmetrically from KG `slippage-measurement-phase-a.md` §10.1.
- [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §1 — substrate owns its training topology; consumer owns its inference topology. Justifies §6.5 anti-recommendation.
- [docs/operations/cross-repo-coordination.md](../operations/cross-repo-coordination.md) §"Volume Design Phase" — handshake that pins the LoRA input contract to the consumer's runtime feature-extraction schema. The training-recipe choice is downstream of this contract.
- [Operator memory: `vol_1_prompt_only_baseline_first`](file:~/.claude/projects/-Users-jamesgriffin-dev-special-herbs/memory/vol_1_prompt_only_baseline_first.md) — the standing rule that gates LoRA training behind a 24-hour prompt-only Brier experiment.
- KG `docs/design/slippage-measurement-phase-a.md` §10.2 — Commander-side GRPO/GiGPO migration discussion. Substrate's recipe choice is independent (§6.5).
