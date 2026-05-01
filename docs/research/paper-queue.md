---
doc_id: PAPER-QUEUE
title: "Phase 0 Reading Queue — Areas 1 & 4"
status: active
created: 2026-04-30
related-docs:
  - ../ROADMAP.md
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - vol-1-fda-ac-feasibility.md
  - special-herbs-formats-design.md
related-cross-repo:
  - /Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-1-agentic-information-synthesis.md
  - /Users/jamesgriffin/dev/king-geedorah/docs/exploration/area-4-cross-domain-signal-networks.md
---

# Phase 0 Reading Queue — Areas 1 & 4

## Purpose

Curated reading list to clear the Phase 0 reading precondition (per [ROADMAP.md](../ROADMAP.md) §"Phase 0 — Preconditions": *"Operator has read 30+ papers across Areas 1 and 4 research directions"*). The four Phase 0 boxes must all be checked before any substrate code work begins; this file is the operator's working list for the reading box.

## Distribution

| Area | Verified entries | High | Medium | Low |
|---|---:|---:|---:|---:|
| Area 1 — Agentic Information Synthesis | 38 | 22 | 16 | 0 |
| Area 4 — Cross-Domain Signal Networks | 33 | 20 | 10 | 3 |
| **Total** | **71** | **42** | **26** | **3** |

The queue exceeds the 30-paper minimum so the operator has slack to skip entries that turn out to be redundant or off-target during reading. The "Phase 0 reading complete" milestone is reached when the operator has marked at least 30 entries `read` (any priority, any area) AND can produce a brief summary tying each Area 1 and Area 4 to a specific Vol. 1 / Vol. 2 design decision.

Twenty-two entries were added 2026-04-30 from three local subagent sweeps:

- **Polymarket non-election empirical** (gap #1 from the original topical-gaps list): A1-027 + A4-023 through A4-032. See [§"Vol. 2 operational notes from local sweep"](#vol-2-operational-notes-from-local-sweep) for incident evidence and data-quality findings.
- **LLM forecast calibration** (gap #3, Vol. 1-critical): A1-028 through A1-032. Five Vol. 1-relevant additions covering the invert-softmax trick, verbalized-confidence baselines, and the AIA Forecaster operational recipe.
- **Multi-LoRA adapter merging** (gap #2, Vol. 2-relevant): A1-033 through A1-038. Six adds covering TIES, DARE, MergeBench, LoRA-LEGO, Task Arithmetic, and Model Soups.

Local subagent sweeps were preferred over Gemini Deep Research per the cost-discipline mandate; both 2026-04-30 sweeps surfaced sufficient material to skip DR escalation.

## How to use this file

- **Status field** per entry tracks operator progress: `queued` → `reading` → `read` → `skipped` (with a one-line reason for any `skipped`).
- **Estimated read time**: `skim` (15-30 min, abstract + figures + selected sections), `careful` (60-90 min, full paper + replication of one figure or equation if possible), `deep` (multi-session, possibly with code or follow-on citations).
- **Why it matters for substrate**: each entry ties to a specific Vol. 1 / Vol. 2 design question. If the rationale doesn't hold up after reading the paper, prefer to `skipped` it with a note explaining what the paper turned out to actually be about.
- Read order within an area should follow priority (High → Medium → Low) but operator is free to reorder.

## Citation hygiene — six forbidden items

These six items MUST NOT be cited as evidence in design docs, ADRs, research notes, or commit messages (per [AGENTS.md](../../AGENTS.md) §"Citation Hygiene"). They are excluded from this queue and should not be added later:

1. "SAHF-PD" framework as quant-trading evidence (real paper is phishing-detection)
2. "A Sober Look at LLMs" (ICML 2024) — unverifiable in proceedings
3. QuantAgent Sharpe 2.63 claim
4. PrimoRL 1.70 Sharpe claim
5. Form 4 insider buying "+2.41% / 10d" (real per Cohen-Malloy-Pomorski: +1.55% / 10d)
6. Kalshi MAE improvement vs Bloomberg "40-60%" (real per Diercks-Katz-Wright 2026: ~22%)

If any of these are encountered while reading the queue (e.g., as a citation in another paper), exclude silently — do not propagate.

## Verification gaps

Two entries carry partial-verification caveats and are explicitly marked `[unverified ...]` in their titles:

- **A1-005** — Janna Lu's *Evaluating LLMs on Real-World Forecasting* — arXiv abs page confirmed; ICLR 2026 submission/acceptance status not independently confirmed. Does not affect the citability of the Brier numbers themselves.
- **A4-011** — Golec & Vernon 2009 (NBER WP 14932) — the working paper exists at the cited link, but the specific CAR figures used in [vol-1-fda-ac-feasibility.md](vol-1-fda-ac-feasibility.md) (−2.48% T-1/T+1, −11.15% T-5/T+5) may be subset-specific. The abstract characterizes effects as "weak or statistically insignificant" overall. Operator should verify exact figures before quoting in design docs.

Additionally, the following 2025-2026 vintage entries were verified against arXiv / SSRN abstract pages but post-date the prior research-synthesis cycle. None are load-bearing for *citable evidence* yet — they are queued for the operator to read and judge. If any becomes load-bearing for a Vol. 1 or Vol. 2 design decision, treat them like the "Citations Worth Validating Before Use" tier in [vol-1-fda-ac-feasibility.md](vol-1-fda-ac-feasibility.md) and re-verify against venue / DOI before propagating:

- A1-006 (Bosse et al.), A1-007 (El Lahib et al.), A1-014 (ExtractBench)
- A1-027 (Wen et al. — LLM-UMA dispute arbitration)
- A1-028 (Wang et al. — invert-softmax), A1-030 (AIA Forecaster — Bridgewater technical report, no peer-review venue)
- A1-035 (MergeBench — NeurIPS 2025), A1-036 (LoRA-LEGO — ICLR 2025)
- A4-007 (Ng et al.), A4-008 (Yang & Tsang), A4-010 (Muralitharan & Banerjee)
- A4-023 (Dubach), A4-024 (Akey et al.), A4-025 (Sirolly et al.), A4-026 (Mohanty & Krishnamachari), A4-027 (Gomez-Cram et al.), A4-028 (Gebele & Matthes), A4-029 (Bartlett & O'Hara), A4-030 (Yang/Cheng/Zou)
- A4-031 (Reichenbach & Walther) — flagged Medium confidence by the local sweep due to SSRN abstract page returning 403; abstract content was reconstructed from secondary sources
- A4-032 (Packin & Rabinovitz, *Science* 2024) — peer-reviewed but full text behind paywall during verification; qualitative claims confirmed via EurekAlert and Gambling Insider summaries

---

## Area 1 — Agentic Information Synthesis

### Priority: High

#### A1-001 — LoRA: Low-Rank Adaptation of Large Language Models

- **Authors**: Hu, E.J.; Shen, Y.; Wallis, P.; et al.
- **Venue / Year**: ICLR 2022
- **Link**: <https://arxiv.org/abs/2106.09685>
- **Why it matters for substrate**: The foundational method for every LoRA adapter the substrate will produce. Vol. 1's entire training pipeline is LoRA fine-tuning on FDA briefing PDFs; understanding rank selection, adapter merge semantics, and the original benchmark methodology is prerequisite to any credible Brier-gate claim.
- **Estimated read time**: careful
- **Status**: queued

#### A1-002 — QLoRA: Efficient Finetuning of Quantized LLMs

- **Authors**: Dettmers, T.; Pagnoni, A.; Holtzman, A.; et al.
- **Venue / Year**: NeurIPS 2023
- **Link**: <https://arxiv.org/abs/2305.14314>
- **Why it matters for substrate**: Vol. 1 inference runs locally on an M2 Ultra 192 GB. QLoRA's 4-bit NF4 quantization + paged optimizers is the practical path to fitting a 70B+ base model during training. Read before choosing base model and memory budget.
- **Estimated read time**: careful
- **Status**: queued

#### A1-003 — LoRA Land: 310 Fine-tuned LLMs that Rival GPT-4

- **Authors**: Zhao, J.; Wang, T.; Abid, W.; et al.
- **Venue / Year**: arXiv 2024 (Predibase technical report)
- **Link**: <https://arxiv.org/abs/2405.00732>
- **Why it matters for substrate**: Benchmarks LoRAX multi-LoRA serving — the inference architecture for running many domain-specific adapters on one GPU. Directly informs the Vol. 1 release pipeline design where a single M2 Ultra must serve both the substrate adapter and the KG query path simultaneously.
- **Estimated read time**: skim
- **Status**: queued

#### A1-004 — Approaching Human-Level Forecasting with Language Models

- **Authors**: Halawi, D.; Zhang, F.; Yueh-Han, C.; et al.
- **Venue / Year**: arXiv 2024
- **Link**: <https://arxiv.org/abs/2402.18563>
- **Why it matters for substrate**: The closest existing system to the Vol. 1 prompt-only Brier baseline experiment. Details the retrieval-augmented LLM forecasting recipe (search → generate → aggregate) and reports Brier scores against human forecasters — sets the comparison bar before any LoRA is trained.
- **Estimated read time**: deep
- **Status**: queued

#### A1-005 — Evaluating LLMs on Real-World Forecasting Against Expert Forecasters [unverified — ICLR 2026 submission status]

- **Authors**: Lu, J.
- **Venue / Year**: arXiv 2025 (v3 August 2025; ICLR 2026 submission status unconfirmed)
- **Link**: <https://arxiv.org/abs/2507.04562>
- **Why it matters for substrate**: Evaluates frontier models on 464 Metaculus questions with verified Brier scores — frontier models surpass the human crowd but underperform experts. Provides the prompt-only ceiling estimate that the 24-hour baseline experiment must beat or match before triggering LoRA training. Brier numbers are citable; only the venue label is the verification gap.
- **Estimated read time**: careful
- **Status**: queued

#### A1-006 — Automating Forecasting Question Generation and Resolution for AI Evaluation

- **Authors**: Bosse, N.I.; Mühlbacher, P.; Wildman, J.; Phillips, L.; Schwarz, D.
- **Venue / Year**: arXiv 2026
- **Link**: <https://arxiv.org/abs/2601.22444>
- **Why it matters for substrate**: Directly validates subquestion decomposition as a Brier-improving technique (0.141 → 0.132 on Gemini 3 Pro), which is a named component of the Vol. 1 ReAct + decomposition pipeline. Also demonstrates automated question generation for evaluation, relevant to constructing the held-out FDA test set.
- **Estimated read time**: careful
- **Status**: queued

#### A1-007 — Temporal Leakage in Search-Engine Date-Filtered Web Retrieval

- **Authors**: El Lahib, A.; Xia, Y.-J.; Li, Z.; et al.
- **Venue / Year**: arXiv / ACL 2026
- **Link**: <https://arxiv.org/abs/2602.00758>
- **Why it matters for substrate**: Shows that Google's `before:` filter leaks post-cutoff content in 71% of queries — a direct threat to the chronological-split integrity of the prompt-only baseline and any retrieval-augmented inference path. Required reading before designing the temporal isolation protocol for the FDA test set.
- **Estimated read time**: careful
- **Status**: queued

#### A1-008 — On Calibration of Modern Neural Networks

- **Authors**: Guo, C.; Pleiss, G.; Sun, Y.; Weinberger, K.Q.
- **Venue / Year**: ICML 2017
- **Link**: <https://arxiv.org/abs/1706.04599>
- **Why it matters for substrate**: Establishes temperature scaling and Platt calibration as the standard post-hoc methods — both are named in the Vol. 1 design as required calibration steps after ensemble generation. The Brier measurement gate requires well-calibrated probabilities; this paper is the theoretical ground for that requirement.
- **Estimated read time**: careful
- **Status**: queued

#### A1-009 — Wisdom of the Silicon Crowd: LLM Ensemble Prediction Capabilities Rival Human Crowd Accuracy

- **Authors**: Schoenegger, P.; Tuminauskaite, I.; Park, P.S.; et al.
- **Venue / Year**: arXiv 2024
- **Link**: <https://arxiv.org/abs/2402.19379>
- **Why it matters for substrate**: Demonstrates that a 12-model ensemble reaches human-crowd-level forecasting accuracy — directly informs the ensemble component of the Vol. 1 prompt-only baseline design, including how many samples are needed and what aggregation function to use before Platt calibration.
- **Estimated read time**: careful
- **Status**: queued

#### A1-010 — ReAct: Synergizing Reasoning and Acting in Language Models

- **Authors**: Yao, S.; Zhao, J.; Yu, D.; et al.
- **Venue / Year**: ICLR 2023
- **Link**: <https://arxiv.org/abs/2210.03629>
- **Why it matters for substrate**: The Vol. 1 design explicitly names ReAct prompting as the extraction loop architecture for the two-stage FDA briefing pipeline. This is the original paper defining the interleaved reasoning + tool-call pattern that the substrate's multi-agent orchestrator will implement.
- **Estimated read time**: careful
- **Status**: queued

#### A1-011 — Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

- **Authors**: Wei, J.; Wang, X.; Schuurmans, D.; et al.
- **Venue / Year**: NeurIPS 2022
- **Link**: <https://arxiv.org/abs/2201.11903>
- **Why it matters for substrate**: Chain-of-thought is the foundation for both subquestion decomposition (A1-006) and the ReAct prompting loop (A1-010). Required to understand the scaling properties that determine when CoT gains activate, which informs base-model size selection for local M2 inference.
- **Estimated read time**: skim
- **Status**: queued

#### A1-012 — Self-Consistency Improves Chain of Thought Reasoning in Language Models

- **Authors**: Wang, X.; Wei, J.; Schuurmans, D.; et al.
- **Venue / Year**: ICLR 2023
- **Link**: <https://arxiv.org/abs/2203.11171>
- **Why it matters for substrate**: Self-consistency (sample diverse paths, take majority vote) is the ensemble strategy underlying the Vol. 1 prompt-only baseline. Provides the theoretical basis for how many reasoning paths to sample before passing to Platt calibration, directly sizing compute budget for the 24-hour baseline experiment.
- **Estimated read time**: skim
- **Status**: queued

#### A1-013 — Docling Technical Report

- **Authors**: Auer, C.; Lysak, M.; Nassar, A.; et al.
- **Venue / Year**: arXiv 2024 (IBM Research)
- **Link**: <https://arxiv.org/abs/2408.09869>
- **Why it matters for substrate**: Docling is the named first-stage layout parser in the Vol. 1 two-stage extraction pipeline. This report documents its AI-based layout analysis and table structure recognition — essential for understanding failure modes when processing FDA Advisory Committee briefing PDFs, which are dense multi-column documents with complex tables.
- **Estimated read time**: careful
- **Status**: queued

#### A1-014 — ExtractBench: A Benchmark and Evaluation Methodology for Complex Structured Extraction

- **Authors**: Ferguson, N.; Pennington, J.; Beghian, N.; et al.
- **Venue / Year**: arXiv 2026
- **Link**: <https://arxiv.org/abs/2602.12247>
- **Why it matters for substrate**: Benchmarks frontier models on PDF-to-JSON extraction under enterprise-scale schemas and shows performance degrades sharply with schema breadth — a direct warning for the Vol. 1 FDA briefing extraction schema. The evaluation methodology (semantic equivalence, omission vs. hallucination distinction) maps onto the substrate's claim-accuracy ≥75% measurement metric.
- **Estimated read time**: careful
- **Status**: queued

#### A1-015 — RLAIF vs. RLHF: Scaling Reinforcement Learning from Human Feedback with AI Feedback

- **Authors**: Lee, H.; Phatale, S.; Mansoor, H.; et al.
- **Venue / Year**: ICML 2024
- **Link**: <https://arxiv.org/abs/2309.00267>
- **Why it matters for substrate**: The substrate uses RLAIF exclusively as teacher signal (<$50/cycle constraint from [AGENTS.md](../../AGENTS.md) cost discipline). This paper establishes that RLAIF matches RLHF at scale and introduces a direct RLAIF path that bypasses reward-model training — directly informs the Vol. 1 teacher architecture choice.
- **Estimated read time**: careful
- **Status**: queued

#### A1-016 — BioBERT: A Pre-trained Biomedical Language Representation Model for Biomedical Text Mining

- **Authors**: Lee, J.; Yoon, W.; Kim, S.; et al.
- **Venue / Year**: Bioinformatics 2020
- **Link**: <https://arxiv.org/abs/1901.08746>
- **Why it matters for substrate**: Vol. 1 processes FDA briefing PDFs which are dense with biomedical entity mentions (drug names, adverse event terms, indication codes). BioBERT is the canonical domain-adapted NER model for this vocabulary — relevant for the NER component of the semantic extraction stage and for understanding what a modern GLiNER-BioMed model improves over.
- **Estimated read time**: skim
- **Status**: queued

#### A1-017 — GLiNER: Generalist Model for Named Entity Recognition Using Bidirectional Transformer

- **Authors**: Zaratiana, U.; Tomeh, N.; Holat, P.; Charnois, T.
- **Venue / Year**: NAACL 2024
- **Link**: <https://arxiv.org/abs/2311.08526>
- **Why it matters for substrate**: GLiNER is a zero-shot NER model that outperforms ChatGPT and fine-tuned LLMs on NER benchmarks while running efficiently on CPU — a practical fit for the M2 Ultra substrate. Covers the gap between BioBERT's supervised approach and the substrate's need for entity extraction across heterogeneous FDA document types without per-type fine-tuning.
- **Estimated read time**: careful
- **Status**: queued

#### A1-028 — Calibrating Verbalized Probabilities for Large Language Models

- **Authors**: Wang, C.; Szarvas, G.; Balazs, G.; Danchenko, P.; Ernst, P.
- **Venue / Year**: arXiv 2024 (Amazon)
- **Link**: <https://arxiv.org/abs/2410.06707>
- **Why it matters for substrate**: Documents the "invert-softmax trick" for calibrating verbalized probabilities. Empirical: ECE on Emotion (6-way) Claude-v3 7.8% → 3.9%; IMDB Claude-v3 5.2% → 1.0%. **Critical pre-read** before the Vol. 1 prompt-only Brier baseline because applying temperature scaling naively to verbalized probability outputs introduces a double-softmax bias that invalidates the calibration step.
- **Estimated read time**: careful
- **Status**: queued

#### A1-029 — Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback

- **Authors**: Tian, K.; Mitchell, E.; Zhou, A.; et al.
- **Venue / Year**: EMNLP 2023
- **Link**: <https://arxiv.org/abs/2305.14975>
- **Why it matters for substrate**: Verbalized numeric probabilities from RLHF-tuned LLMs (ChatGPT, GPT-4, Claude) reduce relative ECE by ~50% vs token conditional probabilities on TriviaQA, SciQ, TruthfulQA. Establishes the empirical baseline for confidence elicitation strategy in the FDA baseline experiment — for black-box API models, verbalized numeric probabilities beat logprob extraction.
- **Estimated read time**: careful
- **Status**: queued

#### A1-030 — AIA Forecaster: Technical Report

- **Authors**: Alur, R.; Stadie, B.C.; Kang, D.; et al.
- **Venue / Year**: arXiv 2025 (Bridgewater AIA Labs technical report)
- **Link**: <https://arxiv.org/abs/2511.07678>
- **Why it matters for substrate**: Most operationally complete published recipe for LLM forecasting calibration: 10-sample ensemble + arithmetic mean + Platt scaling with fixed coefficient √3 ≈ 1.73, validated on real binary forecasting questions. Brier 0.1076 (calibrated) vs 0.1140 (uncalibrated) vs 0.1110 (SuperForecaster baseline). Crucially demonstrates **Platt > isotonic when calibration data is small** — directly applicable to the FDA-baseline regime (20–50 resolved events per year).
- **Estimated read time**: careful
- **Status**: queued

#### A1-031 — A Survey of Confidence Estimation and Calibration in Large Language Models

- **Authors**: Geng, J.; Cai, F.; Wang, Y.; Koeppl, H.; Nakov, P.; Gurevych, I.
- **Venue / Year**: NAACL 2024
- **Link**: <https://arxiv.org/abs/2311.08298>
- **Why it matters for substrate**: Canonical reference covering white-box (logprob), black-box (verbalized, consistency), and post-hoc (temperature, Platt, isotonic) calibration methods for LLMs. Reading prerequisite before locking in the Vol. 1 calibration recipe — distinguishes which methods apply to which input/output regimes and where each fails.
- **Estimated read time**: careful
- **Status**: queued

#### A1-032 — Calibrating Language Models with Adaptive Temperature Scaling

- **Authors**: Xie, J.; Chen, A.S.; Lee, Y.; Mitchell, E.; Finn, C.
- **Venue / Year**: EMNLP 2024
- **Link**: <https://arxiv.org/abs/2409.19817>
- **Why it matters for substrate**: Token-adaptive temperature scaling beats global temperature on RLHF-tuned models. Llama-2-7b-Chat MMLU ECE 0.298 → 0.125 (58% reduction); Brier 0.313 → 0.227. Direct evidence that single-temperature Platt is suboptimal for RLHF base models — relevant if Vol. 1 baseline uses Claude / GPT / Llama-Instruct and can afford the per-query overhead.
- **Estimated read time**: careful
- **Status**: queued

### Priority: Medium

#### A1-018 — DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines

- **Authors**: Khattab, O.; Singhvi, A.; Maheshwari, P.; et al.
- **Venue / Year**: ICLR 2024
- **Link**: <https://arxiv.org/abs/2310.03714>
- **Why it matters for substrate**: DSPy's optimizer-driven pipeline compilation is a candidate architecture for the multi-agent synthesis orchestrator. Relevant when the Vol. 1 two-stage extraction pipeline matures and needs systematic prompt optimization rather than manual tuning, particularly for the RLAIF teacher feedback loop.
- **Estimated read time**: deep
- **Status**: queued

#### A1-019 — Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

- **Authors**: Lewis, P.; Perez, E.; Piktus, A.; et al.
- **Venue / Year**: NeurIPS 2020
- **Link**: <https://arxiv.org/abs/2005.11401>
- **Why it matters for substrate**: Foundational RAG paper establishing the parametric + non-parametric memory architecture that the substrate's KG snapshot retrieval path extends. Prerequisite for reading GraphRAG (A1-021) and Self-RAG (A1-020) coherently.
- **Estimated read time**: skim
- **Status**: queued

#### A1-020 — Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

- **Authors**: Asai, A.; Wu, Z.; Wang, Y.; Sil, A.; Hajishirzi, H.
- **Venue / Year**: ICLR 2024
- **Link**: <https://arxiv.org/abs/2310.11511>
- **Why it matters for substrate**: Self-RAG's adaptive retrieval and critique tokens are directly applicable to the substrate's claim-accuracy measurement harness — the model can flag when retrieved FDA evidence is insufficient, reducing hallucination in the semantic extraction stage.
- **Estimated read time**: careful
- **Status**: queued

#### A1-021 — From Local to Global: A Graph RAG Approach to Query-Focused Summarization

- **Authors**: Edge, D.; Trinh, H.; Cheng, N.; et al.
- **Venue / Year**: arXiv 2024 (Microsoft Research)
- **Link**: <https://arxiv.org/abs/2404.16130>
- **Why it matters for substrate**: GraphRAG's community-summary approach is the closest published antecedent to the substrate's KG snapshot retrieval design (catalyst-event graph queried at synthesis time). Informs the Vol. 1 KG snapshot schema and query interface before those components are formally designed.
- **Estimated read time**: careful
- **Status**: queued

#### A1-022 — Unifying Large Language Models and Knowledge Graphs: A Roadmap

- **Authors**: Pan, S.; Luo, L.; Wang, Y.; Chen, C.; Wang, J.; Wu, X.
- **Venue / Year**: IEEE TKDE 2024
- **Link**: <https://arxiv.org/abs/2306.08302>
- **Why it matters for substrate**: Taxonomizes KG-enhanced LLMs, LLM-augmented KGs, and synergized approaches — the conceptual map for positioning the substrate's KG snapshot design within the literature and selecting the right integration pattern for Vol. 1.
- **Estimated read time**: skim
- **Status**: queued

#### A1-023 — Improving Factuality and Reasoning in Language Models through Multiagent Debate

- **Authors**: Du, Y.; Li, S.; Torralba, A.; Tenenbaum, J.B.; Mordatch, I.
- **Venue / Year**: arXiv 2023 (ICML 2024)
- **Link**: <https://arxiv.org/abs/2305.14325>
- **Why it matters for substrate**: Multi-agent debate as a factuality mechanism is a candidate for the substrate's claim-accuracy verification step — having specialized agents challenge each other's extraction results before the KG write. Relevant to the ≥75% claim-accuracy measurement gate.
- **Estimated read time**: careful
- **Status**: queued

#### A1-024 — AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation

- **Authors**: Wu, Q.; Bansal, G.; Zhang, J.; et al.
- **Venue / Year**: arXiv 2023 (Microsoft)
- **Link**: <https://arxiv.org/abs/2308.08155>
- **Why it matters for substrate**: AutoGen's conversable-agent framework is the practical orchestration layer the substrate may use. Understanding its design constraints (conversation loops, human-in-the-loop hooks) is needed before committing to the multi-agent synthesis orchestrator architecture in Vol. 1.
- **Estimated read time**: careful
- **Status**: queued

#### A1-025 — Constitutional AI: Harmlessness from AI Feedback

- **Authors**: Bai, Y.; Kadavath, S.; Kundu, S.; et al.
- **Venue / Year**: arXiv 2022 (Anthropic)
- **Link**: <https://arxiv.org/abs/2212.08073>
- **Why it matters for substrate**: CAI establishes the RLAIF teacher methodology that the substrate budget rule (<$50/cycle) is built around. The constitutional revision step is directly applicable to iterative claim-cleaning in the KG write pipeline — a model critiques and revises its own extraction before commit.
- **Estimated read time**: careful
- **Status**: queued

#### A1-026 — ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems

- **Authors**: Saad-Falcon, J.; Khattab, O.; Potts, C.; Zaharia, M.
- **Venue / Year**: NAACL 2024
- **Link**: <https://arxiv.org/abs/2311.09476>
- **Why it matters for substrate**: ARES provides a measurement harness for context relevance, answer faithfulness, and answer relevance using LLM judges with minimal human annotations — a direct candidate for the substrate's claim-accuracy ≥75% gate implementation before the King Geedorah Golden Dataset Regression Suite is available.
- **Estimated read time**: careful
- **Status**: queued

#### A1-027 — Can LLMs Help Decentralized Dispute Arbitration? A Case Study of UMA-Resolved Markets on Polymarket

- **Authors**: Wen, J.; Zhou, J.; Huang, J.
- **Venue / Year**: arXiv 2026
- **Link**: <https://arxiv.org/abs/2604.15674>
- **Why it matters for substrate**: Web-enabled LLMs agree with UMA's final dispute resolutions at 89.58% across the full Polymarket dispute history (~$972M disputed volume). For substrate-side ground-truth verification on FDA / weather / macro contracts in Vol. 2, this paper validates an LLM-based fallback resolution-verification step for divergence-event labelling where the prediction-market oracle outcome is itself contested. Cross-cuts Area 1 (LLM as feature extractor) and Area 4 (Polymarket data quality), so flagged here in Area 1 as the agentic-system contribution.
- **Estimated read time**: careful
- **Status**: queued

#### A1-033 — TIES-Merging: Resolving Interference When Merging Models

- **Authors**: Yadav, P.; Tam, D.; Choshen, L.; Raffel, C.; Bansal, M.
- **Venue / Year**: NeurIPS 2023
- **Link**: <https://arxiv.org/abs/2306.01708>
- **Why it matters for substrate**: Three-step merge (trim, elect majority sign, merge sign-agreeing parameters) reduces interference from sign-conflicting parameters. Strongest single-pass static-merge baseline for conflicting-domain adapters. Vol. 2+ design that merges FDA + weather + macro LoRAs into one artifact must include TIES as the default merge path; magnitude-based trimming at density=0.5 is the effective default per PEFT integration testing.
- **Estimated read time**: careful
- **Status**: queued

#### A1-034 — Language Models are Super Mario: Absorbing Abilities from Homologous Models as a Free Lunch (DARE)

- **Authors**: Yu, L.; Yu, B.; Yu, H.; Huang, F.; Li, Y.
- **Venue / Year**: ICML 2024
- **Link**: <https://arxiv.org/abs/2311.03099>
- **Why it matters for substrate**: Drop-And-REscale random sparsification at rate p with 1/(1-p) rescaling exploits the extreme redundancy in SFT delta parameters; 90–99% of delta parameters can be dropped with minimal performance impact, especially at scale. Used as preprocessor before TIES (`dare_ties` in PEFT). Reduces merged-artifact size, directly relevant to Vol. 2 release pipeline.
- **Estimated read time**: careful
- **Status**: queued

#### A1-035 — MergeBench: A Benchmark for Merging Domain-Specialized LLMs

- **Authors**: He, Y.; Zeng, S.; Hu, Y.; Yang, R.; Zhang, T.; Zhao, H.
- **Venue / Year**: NeurIPS 2025 (Datasets and Benchmarks Track)
- **Link**: <https://arxiv.org/abs/2505.10833>
- **Why it matters for substrate**: Best static merging methods retain ~80% of specialized performance for 2–3B models and >90% for 8–9B models across instruction / math / multilingual / coding / safety domains. The empirical prior for Vol. 2 FDA + weather + macro merge expectations. Suggests using a 13B+ instruction-tuned base model preserves the most capability post-merge — an early base-model-selection signal.
- **Estimated read time**: careful
- **Status**: queued

#### A1-036 — Merging LoRAs like Playing LEGO: Pushing the Modularity of LoRA to Extremes Through Rank-Wise Clustering (LoRA-LEGO)

- **Authors**: Zhao, Z.; Shen, T.; Zhu, D.; Li, Z.; Su, J.; Wang, X.; Kuang, K.; Wu, F.
- **Venue / Year**: ICLR 2025
- **Link**: <https://arxiv.org/abs/2409.16167>
- **Why it matters for substrate**: Only confirmed method for clean merging of LoRAs trained at different ranks (decomposes adapters into Minimal Semantic Units, K-means clusters across adapters, reconstructs at any target rank). On 7-task Llama2-7B merge: 62.21% avg vs TIES 58.30%, task arithmetic 54.77%; 92% retention at 50% parameter budget. Vol. 2 escape hatch if substrate LoRAs end up at heterogeneous ranks because per-domain training-data volume differs.
- **Estimated read time**: careful
- **Status**: queued

#### A1-037 — Editing Models with Task Arithmetic

- **Authors**: Ilharco, G.; Ribeiro, M.T.; Wortsman, M.; Gururangan, S.; Schmidt, L.; Hajishirzi, H.; Farhadi, A.
- **Venue / Year**: ICLR 2023
- **Link**: <https://arxiv.org/abs/2212.04089>
- **Why it matters for substrate**: Foundational. Constructs "task vectors" (fine-tuned − pretrained weights), combines via vector arithmetic — addition to merge capabilities, negation to forget. Every subsequent merging method (TIES A1-033, DARE A1-034, AdaMerging) measures against this baseline. Required reading before evaluating which advanced merge method to use for Vol. 2.
- **Estimated read time**: skim
- **Status**: queued

#### A1-038 — Model Soups: Averaging Weights of Multiple Fine-Tuned Models

- **Authors**: Wortsman, M.; Ilharco, G.; Gadre, S.Y.; Roelofs, R.; Gontijo-Lopes, R.; Morcos, A.S.; et al.
- **Venue / Year**: ICML 2022 Spotlight
- **Link**: <https://arxiv.org/abs/2203.05482>
- **Why it matters for substrate**: Establishes the theoretical precondition for all later merging work: adapters trained from the same base model are in the same loss basin and can be linearly interpolated. Vol. 2 substrate LoRAs sharing a base (Llama-Instruct or Qwen-Instruct) satisfy this directly, making simple weight averaging the sensible first baseline before reaching for TIES (A1-033) or LoRA-LEGO (A1-036).
- **Estimated read time**: skim
- **Status**: queued

---

## Area 4 — Cross-Domain Signal Networks

### Priority: High

#### A4-001 — Co-Integration and Error Correction: Representation, Estimation, and Testing

- **Authors**: Engle, R.F.; Granger, C.W.J.
- **Venue / Year**: Econometrica 1987 (vol. 55, no. 2, pp. 251–276)
- **Link**: <https://www.jstor.org/stable/1913236>
- **Why it matters for substrate**: The mathematical foundation for all cointegration-based spread construction. Vol. 2 Polymarket × NOAA and Kalshi × CME pairs will be screened for cointegration before any correlation matrix entry is stored; Engle-Granger two-step residuals are the canonical spread series those downstream scorers will mean-revert against.
- **Estimated read time**: careful
- **Status**: queued

#### A4-002 — Investigating Causal Relations by Econometric Models and Cross-Spectral Methods

- **Authors**: Granger, C.W.J.
- **Venue / Year**: Econometrica 1969 (vol. 37, no. 3, pp. 424–438)
- **Link**: <https://www.jstor.org/stable/1912791>
- **Why it matters for substrate**: Defines Granger causality as the primary operational definition of "lead-lag" the substrate's lead-lag analysis module will implement. Polymarket → Kalshi price discovery directionality and NOAA forecast → weather contract lead are both framed as Granger tests; understanding the formal definition is prerequisite to calibrating the confidence gates.
- **Estimated read time**: careful
- **Status**: queued

#### A4-003 — Pairs Trading: Performance of a Relative-Value Arbitrage Rule

- **Authors**: Gatev, E.; Goetzmann, W.N.; Rouwenhorst, K.G.
- **Venue / Year**: Review of Financial Studies 2006 (vol. 19, no. 3, pp. 797–827)
- **Link**: <https://doi.org/10.1093/rfs/hhj020>
- **Why it matters for substrate**: Canonical empirical benchmark for distance-based spread convergence, directly applicable to cross-venue contract pairs (Polymarket FDA × biotech equity). The 11% average excess return in the paper sets a realistic ceiling; the substrate's divergence-detection threshold calibration should reference this as an upper bound before decay assumptions are applied.
- **Estimated read time**: careful
- **Status**: queued

#### A4-004 — On Covariance Estimation of Non-Synchronously Observed Diffusion Processes

- **Authors**: Hayashi, T.; Yoshida, N.
- **Venue / Year**: Bernoulli 2005 (vol. 11, no. 2, pp. 359–379)
- **Link**: <https://projecteuclid.org/journals/bernoulli/volume-11/issue-2/On-covariance-estimation-of-non-synchronously-observed-diffusion-processes/10.3150/bj/1116340299.full>
- **Why it matters for substrate**: The Hayashi-Yoshida estimator is the correct tool for tick-level lead-lag estimation when Polymarket (on-chain block times), Kalshi (REST poll), and CME (exchange feed) trade at incommensurable timestamps. Naive Pearson with interpolated grids induces Epps-effect bias; HY corrects this and is directly implementable via the `highfrequency` R package or equivalent Python port.
- **Estimated read time**: careful
- **Status**: queued

#### A4-005 — One Security, Many Markets: Determining the Contributions to Price Discovery

- **Authors**: Hasbrouck, J.
- **Venue / Year**: Journal of Finance 1995 (vol. 50, no. 4, pp. 1175–1199)
- **Link**: <https://doi.org/10.1111/j.1540-6261.1995.tb04054.x>
- **Why it matters for substrate**: Introduces information share (IS) decomposition, the standard metric for attributing price discovery across venues. The substrate's lead-lag analysis module should output Hasbrouck IS alongside raw Granger p-values; IS handles the simultaneous-move case (both venues update at once) that Granger tests miss and that will be common in fast-moving prediction market events.
- **Estimated read time**: careful
- **Status**: queued

#### A4-006 — Kalshi and the Rise of Macro Markets

- **Authors**: Diercks, A.M.; Katz, J.D.; Wright, J.H.
- **Venue / Year**: NBER Working Paper 34702 / FEDS Working Paper 2026-010
- **Link**: <https://www.nber.org/papers/w34702>
- **Why it matters for substrate**: Only CFTC-licensed macro prediction market evaluated against professional survey forecasters at scale. The ~22% MAE improvement over Bloomberg consensus on Fed rate paths directly anchors the substrate's "is Kalshi informative enough to correlate against CME futures?" decision gate for Vol. 2. Perfect forecast record in the 24-hour window before FOMC sets the resolution-latency assumption. Already on the citation-hygiene whitelist as the corrected anchor for the "40-60% MAE" myth.
- **Estimated read time**: careful
- **Status**: queued

#### A4-007 — Price Discovery and Trading in Modern Prediction Markets

- **Authors**: Ng, H.; Peng, L.; Tao, Y.; Zhou, D.
- **Venue / Year**: SSRN Working Paper 5331995, January 2026
- **Link**: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5331995>
- **Why it matters for substrate**: First cross-platform lead-lag study using matched contracts on Polymarket, Kalshi, PredictIt, and Robinhood during the 2024 election. Directly quantifies Polymarket-leads-Kalshi during high-liquidity periods — the substrate's Polymarket × Kalshi divergence-event log and lead-lag confidence scores should reproduce and generalize this finding to non-election categories.
- **Estimated read time**: careful
- **Status**: queued

#### A4-008 — The Anatomy of Polymarket: Evidence from the 2024 Presidential Election

- **Authors**: Yang, Z.; Tsang, K.P.
- **Venue / Year**: arXiv / SSRN 2026
- **Link**: <https://arxiv.org/abs/2603.03136>
- **Why it matters for substrate**: Complete on-chain transaction-level analysis of Polymarket's largest market, providing the volume decomposition (exchange-equivalent vs. net inflow vs. gross activity) needed to interpret on-chain data correctly. The substrate's multi-venue ingestion layer will face the same blockchain-vs-exchange data ambiguity; this paper's methodology is the reference implementation.
- **Estimated read time**: careful
- **Status**: queued

#### A4-009 — Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets

- **Authors**: Saguillo, O.; Ghafouri, V.; Kiffer, L.; Suarez-Tangil, G.
- **Venue / Year**: ACM AFT 2025 (arXiv 2508.03474)
- **Link**: <https://arxiv.org/abs/2508.03474>
- **Why it matters for substrate**: Identifies and quantifies two distinct arbitrage structures on Polymarket: within-market rebalancing arb and multi-market combinatorial arb. The $40M realized figure (April 2024–April 2025) calibrates how quickly divergence events are closed; the substrate's divergence-event predictive accuracy gate (≥60%) must account for the fact that most cross-market divergences are captured by bots in seconds, leaving only structural or slow-resolution opportunities.
- **Estimated read time**: careful
- **Status**: queued

#### A4-010 — Stock Market Reactions to FDA Complete Response Letter Disclosures

- **Authors**: Muralitharan, P.; Banerjee, A.
- **Venue / Year**: SSRN Working Paper 6027774, January 2026
- **Link**: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6027774>
- **Why it matters for substrate**: Directly measures the signal the substrate's biotech equity × Polymarket FDA contract correlation layer is designed to exploit. The −4.34% mean CAR[-1,+1] on CRL events (222 events, 124 firms, 2010–2025) is the ground-truth magnitude; the substrate needs to detect this divergence between prediction-market expectations and equity pricing in the pre-event window. CMC-deficiency CRLs showing ~5pp less negative returns indicates heterogeneity that divergence-detection thresholds must accommodate.
- **Estimated read time**: careful
- **Status**: queued

#### A4-011 — What's the "Interest" in FDA Drug Advisory Committee Conflicts of Interest? [unverified for exact CAR figures]

- **Authors**: Golec, J.H.; Vernon, J.A.
- **Venue / Year**: NBER Working Paper 14932, April 2009
- **Link**: <https://www.nber.org/papers/w14932>
- **Why it matters for substrate**: Provides event-study evidence of equity price movements around FDA Advisory Committee meetings — the substrate predecessor to Muralitharan 2026 (A4-010) and the cited anchor for the −2.48% T-1/T+1 and −11.15% T-5/T+5 CARs in [vol-1-fda-ac-feasibility.md](vol-1-fda-ac-feasibility.md). Note: the abstract characterizes effects as "weak or statistically insignificant" for most meetings; the specific CAR figures cited may be for company-specific meeting subsets. Read the body to confirm exact numbers before committing them to the measurement spec.
- **Estimated read time**: careful
- **Status**: queued

#### A4-012 — Informed Options Trading Before FDA Drug Advisory Committee Meetings

- **Authors**: Wu, Z.; Borochin, P.; Golec, J.H.
- **Venue / Year**: Journal of Corporate Finance 2024 (vol. 84, article 102495)
- **Link**: <https://doi.org/10.1016/j.jcorpfin.2023.102495>
- **Why it matters for substrate**: Documents significant abnormal options activity before FDA AC meetings for small-cap biotechs — pre-event signal leak that corrupts naive event windows. The substrate's divergence-detection timing for Polymarket FDA contracts must be calibrated against this pre-event information leakage; the paper establishes that informed trading begins weeks before the AC meeting, not just T-1.
- **Estimated read time**: careful
- **Status**: queued

#### A4-013 — Decoding Inside Information

- **Authors**: Cohen, L.; Malloy, C.; Pomorski, L.
- **Venue / Year**: Journal of Finance 2012 (vol. 67, no. 3, pp. 1009–1043)
- **Link**: <https://doi.org/10.1111/j.1540-6261.2012.01740.x>
- **Why it matters for substrate**: Decomposes SEC Form 4 insider trades into "routine" (non-informative) vs. "opportunistic" (informative), yielding +1.55% CAR over 10 days for opportunistic buys. Already on the citation-hygiene whitelist as the corrected anchor for the "+2.41%" myth. Relevant to Area 4 because insider trades in biotech are a cross-asset signal that can be correlated against Polymarket FDA contract movements; the substrate's cross-asset feature snapshots should include an opportunistic-insider-buy indicator keyed to this paper's classification method.
- **Estimated read time**: careful
- **Status**: queued

#### A4-023 — The Anatomy of a Decentralized Prediction Market: Microstructure Evidence from the Polymarket Order Book

- **Authors**: Dubach, P.D.
- **Venue / Year**: arXiv 2026
- **Link**: <https://arxiv.org/abs/2604.24366>
- **Why it matters for substrate**: ~30B WebSocket events across 385,198 Polymarket markets in a 52-day window (Feb-Apr 2026), pre-registered stratified panel of 600 markets. Reports category-conditional effective half-spread (Crypto −0.039 pp → Sports +0.008 pp), median wash-trading 1% with a 22% upper tail, and Kyle's lambda flipping sign on the majority of markets. Direct empirical input to the substrate's divergence-detection significance gate (≥60% predictive accuracy) — wash-trading 22% upper-tail is the noise floor the gate must clear. Also flags that off-chain WebSocket trade-direction inference matches on-chain ground truth only ~59% of the time — a binding data-quality constraint on any tick-level Polymarket study.
- **Estimated read time**: deep
- **Status**: queued

#### A4-024 — Who Wins and Who Loses In Prediction Markets? Evidence from Polymarket

- **Authors**: Akey, P.; Grégoire, V.; Harvie, N.; Martineau, C.
- **Venue / Year**: SSRN Working Paper 6443103, March 2026 (University of Toronto)
- **Link**: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6443103>
- **Why it matters for substrate**: ~70 million Polymarket trades, 1.4 million users (Nov 2022–Oct 2025). Bots = ~5% of wallets but capture ~75% of trading volume; 69% of traders lose money; top 1% capture ~75% of profits. Crucially: retail traders pick winning outcomes more often than bots but lose because they get worse execution prices (adverse execution, not adverse forecasting). Calibrates the substrate's expectation that any divergence-event signal extracted from Polymarket will be discovered by bots first; the substrate's edge must come from cross-venue or cross-asset signal not visible inside Polymarket's own book.
- **Estimated read time**: careful
- **Status**: queued

#### A4-025 — Network-Based Detection of Wash Trading on Polymarket

- **Authors**: Sirolly, A.; Ma, H.; Kanoria, Y.; Sethi, R.
- **Venue / Year**: SSRN Working Paper 5714122, November 2025 (Columbia)
- **Link**: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5714122>
- **Why it matters for substrate**: ~25% of all Polymarket buying/selling over three years is wash-trading-consistent; peaked ~60% of weekly volume in December 2024; 14% of 1.26M wallets flagged. The network-clustering methodology is the direct precursor to the on-chain data-cleaning step the substrate's multi-venue ingestion layer needs before computing any volume-weighted correlation between Polymarket prices and biotech equities or NOAA weather data.
- **Estimated read time**: careful
- **Status**: queued

#### A4-026 — Do Prediction Markets Forecast Cryptocurrency Volatility? Evidence from Kalshi Macro Contracts

- **Authors**: Mohanty, H.; Krishnamachari, B.
- **Venue / Year**: arXiv 2604.01431, April 2026 (USC Viterbi)
- **Link**: <https://arxiv.org/abs/2604.01431>
- **Why it matters for substrate**: First empirical demonstration that Kalshi macro contracts contain information *orthogonal to* Fed funds futures and treasury yields. Kalshi Fed-rate (KXFED) → Bitcoin realized volatility lead with t=3.63, p<0.001; CPI repricing (KXCPI) predicts ETH volatility out-of-sample (Clark-West p=0.010). The orthogonalization (first-stage R²=2.3% on futures + yields) is the closest available evidence that PM contracts add incremental information share above conventional macro futures — the methodological template for the substrate's Vol. 2 PM × CME futures lead-lag module.
- **Estimated read time**: careful
- **Status**: queued

#### A4-027 — Prediction Market Accuracy: Crowd Wisdom or Informed Minority?

- **Authors**: Gomez-Cram, R.; Guo, Y.; Jensen, T.I.; Kung, H.
- **Venue / Year**: SSRN Working Paper 6617059, April 2026 (LBS / Yale)
- **Link**: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6617059>
- **Why it matters for substrate**: Complete Polymarket transaction history (98,906 events, $13.76B volume, 1.72M accounts). Only 3.14% of accounts qualify as "skilled" with 44% out-of-sample retention (vs. 10% for skilled mutual funds); skilled traders + market makers capture 30%+ of all profits. Platform accuracy is produced by an informed minority, not crowd wisdom. Direct implication for the substrate: in niche FDA / weather / macro contracts, fewer skilled traders → noisier prices → wider divergence-detection thresholds. The ≥60% predictive-accuracy gate must account for this.
- **Estimated read time**: careful
- **Status**: queued

#### A4-028 — Semantic Non-Fungibility and Violations of the Law of One Price

- **Authors**: Gebele, J.; Matthes, F.
- **Venue / Year**: arXiv 2601.01706, January 2026
- **Link**: <https://arxiv.org/abs/2601.01706>
- **Why it matters for substrate**: 100,000+ events across 10 platforms (Kalshi, Polymarket, PredictIt, Augur, Omen, Limitless, Myriad, Seer, Truemarkets, Futuur), 2018–2025. Semantically equivalent contracts persistently exhibit 2–4% execution-aware price deviations across categories including Health & Environment and Science & Research — not just elections. The LOOP-violation magnitude is the structural friction floor for the substrate's cross-platform divergence-event detection: spreads below 2% are within noise; meaningful divergence signals must clear this floor.
- **Estimated read time**: careful
- **Status**: queued

#### A4-029 — Adverse Selection in Prediction Markets: Evidence from Kalshi

- **Authors**: Bartlett, R.; O'Hara, M.
- **Venue / Year**: SSRN Working Paper, April 2026 (UC Berkeley / Cornell)
- **Link**: <https://law.stanford.edu/press/adverse-selection-in-prediction-markets-evidence-from-kalshi/>
- **Why it matters for substrate**: 41.6 million Kalshi trades. Single-name markets exhibit greater informed price impact than broad-based markets via Glosten-Harris decomposition; VPIN toxicity adapted to event-contract context. Direct relevance to Vol. 2: an FDA approval contract is a "single-name" market and therefore expected to have higher adverse selection than a broad macro or weather contract — the substrate's per-category divergence-detection thresholds should be calibrated separately for single-name vs. broad-based markets.
- **Estimated read time**: careful
- **Status**: queued

### Priority: Medium

#### A4-014 — Dynamic Conditional Correlation: A Simple Class of Multivariate GARCH Models

- **Authors**: Engle, R.F.
- **Venue / Year**: Journal of Business & Economic Statistics 2002 (vol. 20, no. 3, pp. 339–350)
- **Link**: <https://doi.org/10.1198/073500102288618487>
- **Why it matters for substrate**: DCC-GARCH is the standard model for time-varying correlation — directly implementable as the "regime-conditional correlation" layer in the substrate's correlation computation engine. Correlation decay analyses between Polymarket contracts and biotech equity options will use DCC to detect whether correlations are expanding or collapsing in real time.
- **Estimated read time**: careful
- **Status**: queued

#### A4-015 — A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle

- **Authors**: Hamilton, J.D.
- **Venue / Year**: Econometrica 1989 (vol. 57, no. 2, pp. 357–384)
- **Link**: <https://www.jstor.org/stable/1912559>
- **Why it matters for substrate**: The Markov switching model is the canonical framework for detecting regime changes that break previously-stable cross-venue correlations. The substrate's correlation decay analyses need a regime indicator; Hamilton's HMM is the reference implementation. Calibrating the "correlation-is-live" vs. "correlation-has-collapsed" gate for FDA AC event divergences requires understanding how regime transitions propagate through the correlation matrix.
- **Estimated read time**: careful
- **Status**: queued

#### A4-016 — Better to Give than to Receive: Predictive Directional Measurement of Volatility Spillovers

- **Authors**: Diebold, F.X.; Yilmaz, K.
- **Venue / Year**: International Journal of Forecasting 2012 (vol. 28, no. 1, pp. 57–66)
- **Link**: <https://doi.org/10.1016/j.ijforecast.2011.02.006>
- **Why it matters for substrate**: The Diebold-Yilmaz connectedness index (FEVD-based directional spillover) is the most citation-dense tool for building the substrate's correlation knowledge graph edges. Directed spillover from biotech equity volatility → Polymarket FDA contract volatility (or vice versa) is exactly the edge-weight computation the Area 4 KG requires; the DY framework produces a scalar "to" and "from" measure per pair, suitable as a graph edge attribute.
- **Estimated read time**: careful
- **Status**: queued

#### A4-017 — Statistical Arbitrage Pairs Trading Strategies: Review and Outlook

- **Authors**: Krauss, C.
- **Venue / Year**: Journal of Economic Surveys 2017 (vol. 31, no. 2, pp. 513–545)
- **Link**: <https://doi.org/10.1111/joes.12153>
- **Why it matters for substrate**: Comprehensive survey covering distance, cointegration, time-series, and stochastic-control approaches. Useful for Vol. 2 design because it quantifies which method families decay fastest (distance approach degrades over 18 months in equities); the substrate's correlation matrix refresh cadence and divergence-detection window selection can be anchored to these empirical decay timelines.
- **Estimated read time**: skim
- **Status**: queued

#### A4-018 — Prediction Markets

- **Authors**: Wolfers, J.; Zitzewitz, E.
- **Venue / Year**: Journal of Economic Perspectives 2004 (vol. 18, no. 2, pp. 107–126)
- **Link**: <https://doi.org/10.1257/0895330041371321>
- **Why it matters for substrate**: Foundational primer on how prediction market prices aggregate information. Establishes conditions under which price = probability and where that mapping breaks (risk aversion, market power, thin liquidity) — directly relevant to interpreting Polymarket FDA approval probabilities as calibrated signals for divergence detection rather than as literal probability estimates.
- **Estimated read time**: skim
- **Status**: queued

#### A4-019 — Trading and Arbitrage in Cryptocurrency Markets

- **Authors**: Makarov, I.; Schoar, A.
- **Venue / Year**: Journal of Financial Economics 2020 (vol. 135, no. 2, pp. 293–319)
- **Link**: <https://doi.org/10.1016/j.jfineco.2019.07.001>
- **Why it matters for substrate**: Measures actual cross-exchange arbitrage spreads, capital-flow friction, and arbitrage convergence speeds in crypto markets — the closest analogue to Polymarket ↔ Kalshi cross-venue divergence. The finding that arb deviations are larger across jurisdictions than across coins (capital controls dominate) maps onto the prediction market case where regulatory and liquidity barriers determine how fast cross-venue divergences close.
- **Estimated read time**: careful
- **Status**: queued

#### A4-030 — Arbitrage Analysis in Polymarket NBA Markets

- **Authors**: Yang, J.; Cheng, G.; Zou, H.
- **Venue / Year**: SSRN Working Paper 6624718, April 2026
- **Link**: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6624718>
- **Why it matters for substrate**: First intra-category convergence-speed measurement for a non-election Polymarket category. NBA single-market mispricings resolve at a median of 3.614 seconds (7 executable episodes); top 1% anomaly cohort captures 11.7% of aggregate market profits. Bounds the substrate's Vol. 2 expectation that FDA / weather / macro convergence will be slower than NBA but still on the order of seconds-to-minutes for liquid contracts — informs both refresh cadence and divergence-event time-window selection.
- **Estimated read time**: skim
- **Status**: queued

#### A4-031 — Exploring Decentralized Prediction Markets: Accuracy, Skill, and Bias on Polymarket

- **Authors**: Reichenbach, F.; Walther, M.
- **Venue / Year**: SSRN Working Paper 5910522, December 2025
- **Link**: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5910522>
- **Why it matters for substrate**: ~124M trades across all Polymarket categories. Documents overtrading of default/Yes options but finds no evidence of a general longshot bias; market prices closely track realized probabilities and slightly outperform bookmaker odds. Implies Polymarket FDA contract prices can be treated as approximately calibrated probabilities without a blanket downward correction — though no per-category Brier breakdown is published, so contract-by-contract liquidity gating still required. Confidence Medium per local sweep due to SSRN abstract page returning 403; verify directly before propagating.
- **Estimated read time**: careful
- **Status**: queued

#### A4-032 — Prediction Markets as a Public Health Threat (Policy Forum)

- **Authors**: Packin, N.G.; Rabinovitz, S.
- **Venue / Year**: *Science* 2024 (Policy Forum)
- **Link**: <https://www.science.org/doi/10.1126/science.aee3932>
- **Why it matters for substrate**: Peer-reviewed *Science* policy commentary documenting that thin liquidity in prediction markets (including Polymarket) means small trades can substantially shift prices and manufacture the appearance of consensus. The microstructure constraint (small trades shift thin books) is the binding caveat for Polymarket FDA contracts at ~$73K average volume per market — substrate divergence-detection must filter for genuine information vs. price-pressure artefacts before treating moves as signal.
- **Estimated read time**: skim
- **Status**: queued

#### A4-033 — FinDKG: Dynamic Knowledge Graphs with Large Language Models for Detecting Global Trends in Financial Markets

- **Authors**: Li, X.; Sanna Passino, F.
- **Venue / Year**: ACM ICAIF 2024 (4th ACM International Conference on AI in Finance)
- **Link**: <https://doi.org/10.1145/3677052.3698603>
- **Why it matters for substrate**: Concrete published example of a financial-domain dynamic knowledge graph constructed via LLM extraction — entity / event / relation typing, temporal evolution, query-time retrieval. The Area 4 correlation-KG pillar (asset / event / venue nodes with correlation edges + decay characteristics) is structurally similar; FinDKG is the closest published antecedent for the schema and ingestion-pipeline design when the substrate's correlation KG construction begins in Vol. 2.
- **Estimated read time**: careful
- **Status**: queued

### Priority: Low

#### A4-020 — Results from a Dozen Years of Election Futures Markets Research

- **Authors**: Berg, J.E.; Forsythe, R.; Nelson, F.E.; Rietz, T.A.
- **Venue / Year**: Handbook of Experimental Economics Results (Elsevier) 2008
- **Link**: <https://www.sciencedirect.com/science/article/abs/pii/S1574072207000807>
- **Why it matters for substrate**: Historical benchmark for prediction market accuracy (IEM: 1.37% MAE in presidential elections). Necessary for contextualizing how much worse Polymarket 2024 election markets performed relative to this baseline, which in turn calibrates how much the substrate's signal quality should discount from PM prices in adversarial or low-liquidity environments.
- **Estimated read time**: skim
- **Status**: queued

#### A4-021 — It Takes All Sorts: A Heterogeneous Agent Explanation for Prediction Market Mispricing

- **Authors**: Restocchi, V.; McGroarty, F.; Gerding, E.; Johnson, J.E.V.
- **Venue / Year**: European Journal of Operational Research 2018 (vol. 270, no. 2, pp. 556–569)
- **Link**: <https://doi.org/10.1016/j.ejor.2018.04.011>
- **Why it matters for substrate**: Models the favourite-longshot bias (FLB) in prediction markets as an emergent property of heterogeneous trader types. Relevant to the substrate's divergence-detection significance gate: when Polymarket prices systematically deviate from calibrated probability near p=0 and p=1, the bias confounds whether a divergence is genuine signal or structural mispricing. The substrate should implement an FLB correction layer before flagging low-probability contract divergences.
- **Estimated read time**: skim
- **Status**: queued

#### A4-022 — Measuring Information Transfer

- **Authors**: Schreiber, T.
- **Venue / Year**: Physical Review Letters 2000 (vol. 85, no. 2, pp. 461–464)
- **Link**: <https://doi.org/10.1103/PhysRevLett.85.461>
- **Why it matters for substrate**: Introduces transfer entropy (TE) as a non-linear, asymmetric alternative to Granger causality for detecting lead-lag. TE detects non-linear information flow between venues that Granger tests miss; potentially useful for Polymarket ↔ NOAA weather-forecast correlation where the information transmission mechanism may be non-linear (binary resolution events). Read alongside Granger 1969 (A4-002) and Hayashi-Yoshida 2005 (A4-004) to understand the full lead-lag detection toolkit before choosing which to implement first.
- **Estimated read time**: skim
- **Status**: queued

---

## Vol. 2 operational notes from local sweep

The 2026-04-30 local sweep on Polymarket non-election empirical work surfaced several incident records and data-infrastructure findings that don't warrant their own paper-queue entries (they are journalism, platform documentation, or GitHub issues — not papers to read) but do bind specific Vol. 2 design decisions. Capturing them here so they are not lost.

### Incident evidence — adversarial actors against Polymarket non-election contracts

- **UMA governance attack ($7M Ukraine mineral deal, March 2025).** A single UMA token holder with 25% of total votes across three accounts forced a $7M geopolitical contract to resolve YES despite no underlying agreement; odds shifted from 9% → 100% between March 24-25, 2025. Polymarket declined refunds. *Implication for Vol. 2*: any FDA / weather / macro contract substrate signal must include an oracle-risk flag tracking UMA token concentration. Sources: [The Block](https://www.theblock.co/post/348171/polymarket-says-governance-attack-by-uma-whale-to-hijack-a-bets-resolution-is-unprecedented), CoinDesk, CoinTelegraph.
- **Paris weather sensor manipulation (April 2026, two incidents, ~$34K total).** A Polymarket weather contract resolved on a single Météo-France sensor at Charles-de-Gaulle airport (Station LFPG) was exploited via physical heating of the sensor on April 6 (+$14K) and April 15 (+$20K); Météo-France filed criminal complaints. *Implication for Vol. 2*: Polymarket × NOAA correlation features cannot treat single-sensor-resolved weather contracts as clean signal — need sensor-anomaly detection as a data-quality filter. Sources: [Le Monde](https://www.lemonde.fr/), [Benzinga coverage](https://www.benzinga.com/markets/prediction-markets/26/04/51989428/polymarket-bettor-uses-hair-dryer-to-change-the-weather-in-paris-prediction-market-manipulation-controversy-intensifies), NPR, CoinDesk Opinion.
- **Military insider trading + CFTC enforcement (Operation Absolute Resolve, charges April 2026).** US Army Special Forces MSG used classified knowledge of Venezuelan operation to place 13 Polymarket bets ($33K invested → $410K profit, 12× return); CFTC's first event-contract insider-trading enforcement action under the "Eddie Murphy Rule." Israeli Air Force personnel separately indicted for Iran-strike bets (~$244K). *Implication for Vol. 2*: regulatory enforcement intent now spans all event-contract categories including FDA approvals; any substrate signal exploiting clinical-trial insider information would face the same enforcement risk. Source: [Debevoise & Plimpton legal analysis](https://www.debevoise.com/insights/publications/2026/04/polymarket-insider-trading-charges-illustrate-doj).
- **Polymarket → Chainalysis surveillance partnership (April 30, 2026).** Real-time on-chain anomaly detection now deployed across all Polymarket contract categories. *Implication for Vol. 2*: pre-April-2026 historical Polymarket data may contain insider-driven price moves that post-April-2026 data won't; treat that boundary as a regime break in any cross-asset lead-lag backtest involving Polymarket. Source: [CoinDesk April 30, 2026](https://www.coindesk.com/business/2026/04/30/polymarket-taps-chainalysis-to-bring-wall-street-level-oversight-to-crypto-prediction-markets).

### FDA category snapshot (April 2026)

- **Polymarket "drug" category**: 108 active markets, ~$7.9M cumulative volume (~$73K average per market per platform self-report at <https://polymarket.com/predictions/drug>). Compare to election markets where individual contracts cleared $450M.
- **Tech & Science aggregate volume** (which contains FDA approvals + AI / space / other): ~$123M annual per Keyrock × Dune 2025 industry report. Per-FDA-contract isolated dollar volume remains unmeasured in any academic source.
- *Implication for Vol. 2*: FDA contracts are thin enough that a single $5-10K position can move price materially without information content. Substrate signal-quality gate must filter for liquidity before treating a price move as informative.

### Data-infrastructure constraints

- **Polymarket CLOB API `/prices-history` endpoint**: returns only 12+ hour granularity for resolved markets, regardless of historical trading volume. Sub-hour tick history requires on-chain reconstruction from Polygon CTF Exchange V1 events or third-party data vendors (PolymarketData.co, Telonex, PolyBackTest). Source: [Polymarket py-clob-client GitHub issue #216](https://github.com/Polymarket/py-clob-client/issues/216). *Implication*: Vol. 2 FDA × biotech lead-lag backtests on resolved contracts cannot use the standard API — a data-pipeline dependency.
- **Gamma API `closed` parameter defaults to `false`**: naive queries silently exclude all resolved (i.e., outcome-labelled) contracts. Source: [Polymarket Gamma API docs](https://docs.polymarket.com/market-data/fetching-markets). *Implication*: survivorship bias is the default; substrate ingest must explicitly include resolved markets to obtain a labeled dataset.
- **Off-chain WebSocket trade-direction inference accuracy ~59%** (per Dubach 2026, A4-023): aggressor-side inference from the standard feed matches on-chain ground truth only marginally above random. *Implication*: any Polymarket microstructure feature using only WebSocket data — without a Polygon on-chain join — systematically misdirects ~41% of trades. Tick-level lead-lag work must use on-chain data or accept a known noise floor.

### UMA dispute aggregate (operational baseline)

- **~1.3% aggregate dispute rate** across all Polymarket markets per UMA's Managed Proposers post (July 2024 figures: 11,093 settled / 217 disputed). Whitelisted proposers achieve 99.7% accuracy; non-whitelisted 85.8%. Weather / sports / crypto-price categories characterized as "non-contentious" qualitatively. *Implication*: aggregate dispute risk is low enough not to gate the substrate, but contract-by-contract resolution-language ambiguity should still be a Vol. 2 ingestion-time check. Source: [UMA blog](https://blog.uma.xyz/articles/managed-proposers).

---

## Topical gaps recommended for Gemini DR sessions

These topics are thin or missing in the queue. None block the 30-paper precondition, but each would strengthen specific Vol. 1 / Vol. 2 design decisions if filled. Per cost-discipline mandate, do a local subagent sweep first; only escalate to Gemini DR if local searches genuinely don't surface enough.

1. ~~**Polymarket non-election empirical work.**~~ **ADDRESSED 2026-04-30** via local subagent sweep. 38 candidate findings surfaced; 11 strongest queued (A1-027, A4-023 through A4-032) and operational findings captured above. Residual gap: direct Polymarket × biotech equity / options lead-lag empirical study. Local sweep confirms this is genuinely not yet in the literature — the gap is real but not addressable by external DR until someone publishes such a study. The substrate's Vol. 2 design will need to *generate* this evidence rather than read it.
2. ~~**Multi-LoRA adapter merging / composition.**~~ **ADDRESSED 2026-04-30** via local subagent sweep. 17 candidate findings surfaced; 6 strongest queued (A1-033 through A1-038). Residual gap: quantitative capability preservation specifically for financial + biomedical + weather domain combinations (MergeBench A1-035 covers instruction / math / coding / safety / multilingual but not these substrate-specific combinations) and pre-merge rank selection strategy. Both gaps narrow enough to address empirically during Vol. 2 design rather than via more reading.
3. ~~**Calibration applied specifically to LLM forecast distributions.**~~ **ADDRESSED 2026-04-30** via local subagent sweep. 16 candidate findings surfaced; 5 strongest queued (A1-028 through A1-032). Residual gap: compositional calibration for subquestion-decomposed forecasts (no paper directly measures how AND/OR probability composition propagates calibration error) and calibration stability under distribution drift (FDA approval rates shift with administration policy). Both gaps narrow enough to surface as substrate-side measurement work in Vol. 1.
4. **Knowledge graph update / provenance for append-only versioned snapshots.** A1-021 (GraphRAG) and A1-022 (Pan et al.) cover the integration pattern but not the mechanics of versioned KG commits, which is a substrate architecture constraint per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §1 (artifacts are versioned and immutable). **Not addressed yet** — defer until Vol. 2 KG snapshot design begins; cross-cuts ML-MLOps and database-versioning literature.
5. **Crypto on-chain lead-lag specifically.** A4-019 (Makarov & Schoar) covers cross-exchange fiat arb but not on-chain timing (block-time price discovery, MEV influence on Polymarket pricing). **Not addressed yet** — Vol. 2+ scope; useful breadth if the substrate ingests on-chain data beyond Polymarket's USDC contract.
6. ~~**Correlation knowledge graph construction in finance.**~~ **ADDRESSED 2026-04-30** by adding FinDKG (Li & Sanna Passino, ACM ICAIF 2024) directly as A4-033 at Medium priority. No further action needed.

---

## Operator workflow

1. Read at least 30 entries (any priority, any area) and update each entry's `Status` field to `read` or `skipped`.
2. For each `read` entry, write one sentence in the entry tying it back to a Vol. 1 / Vol. 2 design decision. If the rationale in the existing "Why it matters for substrate" block is wrong, edit it.
3. When a `skipped` entry is added, include a one-line reason (e.g., "skipped — superseded by A1-026") in the Status line.
4. When ≥30 entries are `read` AND the operator can produce a brief synthesis tying each Area 1 and Area 4 to specific Vol. 1 / Vol. 2 design decisions, the Phase 0 reading box is complete (per [ROADMAP.md](../ROADMAP.md) §"Phase 0").

This file is append-only as a research record. New papers can be added at the bottom of each priority block (use the next free A1-NNN or A4-NNN ID). Do not delete entries — `skipped` is the terminal state for unwanted entries, with the reason captured inline.
