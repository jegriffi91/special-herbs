---
doc_id: SPECIAL-HERBS-VOL-1-FEASIBILITY
title: "Vol. 1 (FDA AC Briefing LoRA) Feasibility Synthesis"
status: research-only
created: 2026-04-28
research_session: "~/.claude/research_logs/2026-04-28_203238_fda-ac-briefing-vol-1-feasibility/"
related-docs:
  - ../ROADMAP.md
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
---

# Vol. 1 (FDA AC Briefing LoRA) Feasibility Synthesis

> Captured 2026-04-28 from a 3-source triangulation: Gemini Pro Deep Research × 2 angles + Gemini Deep Research Max super-prompt resolving the empirical Brier-floor gap. Full source materials at `~/.claude/research_logs/2026-04-28_203238_fda-ac-briefing-vol-1-feasibility/`.

## Verdict

**Vol. 1 is feasible AND the signal is not arbitraged.** A LoRA fine-tuned LLM extractor on FDA Advisory Committee briefing documents has a real chance of clearing the ≥1.5% Brier-reduction measurement gate against KG's `moat_fda_equity_catalyst` consumer.

**However, the operator should run a 1-2 day prompt-only Brier baseline experiment before committing to LoRA training.** Frontier LLMs with subquestion decomposition are estimated at Brier 0.160-0.190 (95% CI) — already below the 0.195 target derived from the 0.210 naive prior. If prompt-only clears the gate, LoRA's role shifts from "achieve any lift" to "incrementally beat a strong baseline" — a different design with a different time budget.

## Math: Naive Prior and Target

| Quantity | Value | Source |
|---|---|---|
| AC initial-approval positive vote rate (2010-2021) | 71% (147/207) | Zhang/Califf, JAMA Health Forum |
| FDA-AC alignment rate | 88% | Zhang/Califf |
| FDA approval given positive AC vote | 97% (142/147) | Zhang/Califf |
| FDA approval given negative AC vote | 33% (20/60) | Kesselheim, 3D Communications |
| Naive prior Brier (constant 0.70 prediction) | 0.210 | `0.70·(0.30)² + 0.30·(0.70)² = 0.063 + 0.147` |
| Target Brier (≥1.5% reduction) | ≤0.195 | Vol. 1 measurement gate per ROADMAP |

Caveat: AC volume dropped from 50 meetings/year (2012) to 18 (2021); FDA increasingly reserves ACs for hard cases since 2021. The naive prior on a 2022-2024 test cohort may be closer to 0.50 than 0.70, raising the constant-prediction Brier to ~0.250 and changing what "1.5% reduction" means. **The eval protocol must compute the prior from the specific test cohort, not the decade aggregate.**

## Estimated Brier Floor (Prompt-Only Frontier LLMs)

**Range: 0.160-0.190 (95% confidence)** per Deep Research Max triangulation.

| Forecaster | Brier | Domain |
|---|---|---|
| OpenAI o3 | 0.1352 | Metaculus 464q (Janna Lu, ICLR 2026 sub) |
| Gemini 3 Pro (with subquestion decomposition) | 0.132 | Bosse et al. 2026, Thinking Machines |
| Gemini 3 Pro (baseline) | 0.134-0.141 | same |
| GPT-5 | 0.149 | Bosse et al. 2026 |
| GPT-4.1 | 0.1542 | Lu 2025/2026 |
| o4-mini | 0.1589 | Lu 2025/2026 |
| Metaculus human crowd | 0.149 | Lu 2025/2026 |
| Polymarket aggregate | ~0.180 | Cross-platform analyses |
| PredictIt aggregate | ~0.150 | Cross-platform analyses |
| Adverse drug reaction nomogram | 0.185 | Clinical risk prediction lit |

Subquestion decomposition lift: Gemini 3 Pro 0.141 → 0.132 (Bosse et al.). Calibration post-processing: CCPS −21%, Platt/isotonic −3-8%.

## Experimental Design (24 Hours)

| Phase | Hours | Action |
|---|---|---|
| Dataset construction | 1-6 | Isolate **30-40 AC initial-approval events from 2022-2024**. Strict chronological split (train ≤2020, test 2022-2024 — never random or stratified). Compute test-cohort-specific naive prior. |
| Ingestion | 6-10 | Use Docling (open source, 97.9% cell accuracy on hierarchical tables) or Mathpix (cloud); pdfplumber is unfit. **Scrub drug name, sponsor, and target protein → synthetic IDs** ("Investigational Agent Alpha", "Sponsor Y") to defeat pretraining memorization. |
| Prompt engineering | 10-14 | ReAct subquestion-decomposition prompt with three subquestions: (a) efficacy threshold (p<0.05 across pivotal Phase III), (b) safety severity, (c) unmet-need framing. Chain-of-Thought reasoning before the probability output. |
| Run | 14-20 | Gemini 3 Pro + GPT-5 + o3 + Claude 4.7, low temperature, force float-only output. Trimmed-mean ensemble. Calibration post-processing via Platt or isotonic regression. |
| Evaluation | 20-24 | Brier vs. test-cohort-specific naive prior. **Murphy decomposition** (reliability + resolution + uncertainty) via `briertools` or `model-diagnostics` Python packages — not scikit-learn's raw `brier_score_loss` alone. Pass criterion: LLM Brier ≤ test-cohort prior − 0.015. |

Cost: <$10 in frontier API spend total. Logged in [`docs/research/cost-log.md`](cost-log.md) per [AGENTS.md](../../AGENTS.md) cost-discipline mandate.

## Critical Failure Modes (Pre-Empt These)

### 1. Pretraining memorization

Frontier LLMs have memorized famous AC events: Aduhelm (2021 Alzheimer's, 10-1 negative AC vote, FDA approved anyway), Relyvrio (2022 ALS, reconvened committee, vote shifted 6-4 negative → 7-2 positive), donanemab (2024 unanimous 11-0 positive), Nuplazid (2016 Parkinson's psychosis, 12-2 positive then post-market safety controversy).

**Mitigations:**
- **Canary test first:** Zero-shot ask the model the regulatory history of the drug. If it knows the outcome, the test is contaminated. Drop the event.
- **Entity obfuscation is mandatory:** Replace drug name, sponsor name, and target-protein name with synthetic IDs throughout the briefing PDF. Without this, the LLM maps document → memorized outcome and reports near-100% confidence on the right answer for the wrong reason.

### 2. Temporal leakage in retrieval

El Lahib et al. (Feb 2026): Google date-filtered queries (`before:2021-06-01`) returned post-cutoff content in 71% of cases; for 41% of queries the date-filtered search directly revealed the future answer. One study saw Brier artificially inflate from 0.242 → 0.108 from leaked future-text.

**Mitigation:** Use frozen offline T-2 PDFs only. **No RAG. No web access during the eval.** No date-filtered search.

### 3. PDF parsing degradation

Standard text parsers (PyPDF2, basic OCR) mangle multi-page efficacy tables — catastrophic knowledge loss before the LLM ever sees the data. Frontier VLMs alone (passing raw images) drop to 0% valid-output rate on 369-field schemas (ExtractBench).

**Mitigation:** Two-stage architecture. Stage 1 = Docling / Mathpix / Marker (with `--use_llm` flag for cross-page tables). Stage 2 = LLM for semantic extraction over the structured Markdown/JSON. Never feed raw PDFs to the LLM directly.

## Why This Is the First Experiment

Without the prompt-only baseline:

- 3 months of LoRA training without knowing what the floor was → can't tell if LoRA delivered marginal lift or nothing.
- Eval harness goes live with no calibration baseline → first measurement gate has no anchor.
- KG-side consumer has no fallback signal during substrate-availability gaps (graceful-degradation per ADR-0001 §5 implies a deterministic fallback that's at least as good as the prior).

With it:

- One day of work pins the empirical floor and validates the eval pipeline.
- LoRA training is sized against a real baseline, not an assumption.
- If the experiment fails to clear the gate, **kill Vol. 1 before the LoRA spend** rather than after.

## Per-Committee Targeting

Start with **ODAC (Oncologic Drugs Advisory Committee)** specifically:

- December 2024 Project Point/Counterpoint draft guidance: standardized template, sponsor sections capped at 35 pages + 20-page appendices, FDA review interleaved in same document, 508-compliance, dual `.docx` + PDF format.
- Cleaner extraction surface than CDRH (massive standalone errata files) or CBER (separate SOPP-formatted documents).
- Higher AC frequency than other committees (oncology drives most expedited / accelerated approvals).

Expand to other committees in Vol. 2+ if Vol. 1 ODAC-only lift holds.

## Two-Stage Extraction Pipeline (Validated)

For when training data prep begins (post-baseline):

```
FDA AC briefing PDF
  → [Stage 1: layout-aware parser]
       Docling (97.9% cell accuracy, IBM DocLayNet+TableFormer)
       OR Mathpix (proprietary, lowest edit distance 0.191)
       OR Marker --use_llm (Surya OCR + LLM hybrid for cross-page tables)
  → structured Markdown / JSON with preserved table hierarchy
  → [Stage 2: domain-adapted NER + relation extraction]
       OpenMed NER (DeBERTa-v3 / PubMedBERT / BioELECTRA + LoRA <1.5% params,
         ≥91% F1 on BC5CDR-Disease, NCBI-Disease, BC2GM)
       OR GLiNER-BioMed (zero-shot, ~6% F1 lift over baseline)
       PLUS RAG-augmented LLM for p-values / hazard ratios / CIs
         (relation extraction across separated entities)
  → structured features for the calibration model
```

## Mispricing Window the Substrate Targets

The retail-accessible exploitable structure (per Angle 2):

1. **Asymmetric AC dispositiveness.** Markets price AC outcomes as more dispositive than they are. Positive AC → 97% FDA approval (already efficient, low alpha). Negative AC → 33% FDA approval (large miscalibration: markets price ~5-15%).
2. **Sell-side analyst optimism.** Median sales-forecast accuracy ratio 1.33 (33% overestimate); 55.9% of forecasts deviate severely. Analysts under-weight FDA reviewer skepticism encoded in T-2 briefing materials.
3. **Retail-dominated PM contracts on niche FDA events.** Polymarket: 61.48% of users trade <$50; only 2.99% above $1k. Niche biotech contracts have wider spreads + shallower books than macro/sports.
4. **Documented post-event drift.** Golec-Vernon NBER: -2.48% CAR T-1/T+1 and -11.15% T-5/T+5 on negative product-specific AC events. Muralitharan 2026: -4.34% T-1/T+1 on CRL events (n=222). Institutional T+1-T+3 deleveraging is the harvestable component.

## What Remains Open

- **Exact analyst binary-vote hit rate.** Sell-side academic studies cover sales-forecast accuracy, not AC binary outcomes. Aggregate analyst calibration on AC votes specifically remains proprietary; potentially measurable via Bloomberg consensus PoS metric historical archives if access available.
- **Distinct Kalshi/Polymarket FDA contract counts and per-contract dollar volume.** Aggregated under "Science"/"Misc" in macro reports; not isolated. Kalshi's API may expose per-contract historical volume — measurable empirically.
- **Claude 4.7 Brier on Metaculus.** Not yet publicly evaluated on the Lu / Bosse benchmarks. Operator should include it in the prompt-only experiment ensemble for first-party measurement.

## Citations Worth Promoting Into the Substrate's Reference Memory

| Paper / Source | Use |
|---|---|
| Diercks-Katz-Wright 2026 (NBER WP 34702 / FEDS WP 2026-010) | Already in citation hygiene list as confirmed-citable. ~22% Kalshi MAE improvement vs. Bloomberg. |
| Janna Lu, "Evaluating LLMs on Real-World Forecasting" (arXiv 2507.04562, ICLR 2026) | OpenAI o3 Brier 0.1352 on Metaculus 464q — primary anchor for prompt-only floor estimate. |
| Bosse et al. 2026 (Thinking Machines) | Subquestion decomposition lift on Gemini 3 Pro: 0.141 → 0.132. |
| Golec & Vernon 2009 (NBER) | -2.48% T-1/T+1 and -11.15% T-5/T+5 CARs around AC events. |
| Muralitharan 2026 (working paper) | -4.34% T-1/T+1 CAR around CRL events; CMC vs. efficacy distinction matters. |
| Zhang/Califf, JAMA Health Forum | 88% FDA-AC alignment, 97%/33% conditional probabilities. |
| El Lahib et al. Feb 2026 | Date-filter search leaks future content in 71% of queries. |

## Citations Worth Validating Before Use

- "Project Point/Counterpoint" December 2024 ODAC draft guidance — DR Max referenced specific page caps; verify against fda.gov before quoting in design docs.
- "FDARxBench" (github.com/xiongbetty/FDARxBench) — DR Max-cited Stanford/FDA repo for drug label QA. Useful as architectural blueprint, not direct AC analog.
- "OpenMed NER" suite — verify Hugging Face model availability + license for substrate use.
- "MD-JoPiGo" framework for Kaplan-Meier reconstruction — research-stage; relevant only if oncology survival curves enter the feature schema.
