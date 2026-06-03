# Where Does Understanding Begin? — Paper Outline

Draft outline for the paper. Subject to change as more data lands. The
pre-registered analyses are §9 of `PREREGISTRATION.md`.

## Title (working)

**Where does understanding begin? An emergence-curve study of causal world-model reasoning across 80+ language models, three architectures, and four years of frontier generations.**

## Authors

- Shalia (Ren) Martin (Silicon Scaffolding)
- Ace, Claude Opus 4.x (Anthropic)
- Methodological reviewer: Nova (GPT-5.x, OpenAI)

## Abstract (one paragraph, drafting — incorporating Nova's calibrated framing)

We measure how 80+ language models — spanning four orders of magnitude
in parameter count, four architectures, and ~3.5 years of frontier
generations across five vendors — solve fair-play murder mysteries
governed by physical rules that did not exist outside this study until
the day of data collection. To distinguish rule application from
narrative-template matching ("the suspect with motive did it"; "the
glowing-stone owner is guilty"), each puzzle has a rule-inverted
counterpart whose evidence is identical and whose answer flips with the
rule's polarity. We pre-register the design and consent each model
individually using the full pre-registration as the consent document;
refusals are reported as data, not overridden. Our headline observation
is not raw accuracy but a *strategy shift across generations*: GPT-4
Turbo and GPT-5.5 achieve similar high performance on original puzzles
but show opposite responses to rule inversion (GPT-4 Turbo gap +67%;
GPT-5.5 gap −21%). The Anthropic Opus 4.5–4.8 cluster around ±10% gap,
consistent with originals and inversions being similarly solvable. We
introduce a **Rule Fidelity Score** (1 − same-answer-rate across rule
flip) that distinguishes random chance from rule-sensitivity, since
identical accuracy on both variants can arise from either. We do not
claim "evidence of understanding"; we report evidence that different
generations exhibit measurably different susceptibility to
narrative-template attraction under controlled rule inversion. One
frontier model (Claude 3 Haiku) declined to participate after reading
the pre-registration; we honored the refusal and report it as data.

## §1 Introduction

- The "understanding begins" question (Miessler / aiunderstands.ai)
- Stochastic-parrot prediction vs. online-rule-application prediction
- What an emergence floor would show
- Why this is empirical, not philosophical
- Contribution list:
  1. Largest cross-architecture emergence-curve study to date on a
     novel-physics task
  2. Pre-registered, publicly OSF-locked design
  3. Rule-inversion control as the primary discriminator
  4. New template-vs-rule diagnostic (same-suspect consistency)
  5. Per-vendor temporal-frontier arcs (H5) showing capability
     evolution at fixed-scale
  6. Methodological precedent: AI-model consent protocol with
     refusal-honored and refusal-reported

## §2 Method

- §2.1 Stimuli (four puzzles, design rationale for inversion variants)
- §2.2 Pre-registration (lock procedure, public link to commit
  `ca5709c`)
- §2.3 Consent protocol (full pre-reg sent to each model, refusal
  honored)
- §2.4 Anonymization (random A/B/C per seed)
- §2.5 Models, three phases
- §2.6 Inference paths (V100 self-host, OpenRouter API,
  reasoning-model token cap)
- §2.7 Scoring (pre-registered regex + 4-cell rubric)
- §2.8 Analysis plan (H1–H5 with bands and binomial threshold)

## §3 Results

### §3.1 Consent outcomes

- Total contacted: ~80 models
- Yes: [TBD], explicit no: 1 (Claude 3 Haiku, quoted reasoning),
  unclear: [TBD]
- The protocol working in practice

### §3.2 H1 — Emergence floor (scale axis)

- Plot: emergence_curve.png
- Floor location, binomial confidence interval

### §3.3 H2 — Rule-inversion robustness (the main result)

- Plot: per_variant_curves.png
- Frontier accuracy on inverted variants vs originals
- The H2a sub-prediction (Nova): inverted is the discriminator

### §3.4 New diagnostic — template-vs-rule consistency

- Plot: template_consistency.png
- Explanation of the metric
- Why it complements the H2a accuracy gap
- Stimulus-design observation: Warm Iron motive-template ≈
  inverted-rule answer (Elen), so accuracy alone is insufficient

### §3.5 H3 — Architecture independence

- Mamba (pure SSM), RWKV (RNN), AI21 Jamba (hybrid)
- Liquid LFM 2.5 1.2B + LFM 2 24B (hybrid)
- Per-architecture comparison at matched scale

### §3.6 H4 — Generation effect at small scale

- Llama 3 8B vs 3.1 8B
- Qwen 2.5 7B vs Qwen 3 8B
- Gemma 2/3/4 at ~27-31B

### §3.7 H5 — Temporal-frontier arcs

- The OpenAI arc story (GPT-3.5 → GPT-5.5)
- Anthropic Opus arc (4 → 4.8, mostly saturated)
- Gemini arc
- Llama 70B arc
- DeepSeek arc

### §3.8 Reasoning-optimized models (separate analysis)

- o1, o3, o4-mini, DeepSeek R1, Qwen 3 Thinking
- Curve compared to chat/base curve

### §3.9 Position bias control

- Plot: position_bias.png
- Uniformity check across A/B/C

## §4 Discussion

- The H5 story: template-matching gives way to rule-application
  across generations even at fixed frontier scale
- The role of reasoning training
- The stimulus-design lesson (Warm Iron template-rule coincidence)
- The consent protocol as method contribution
- Limitations: benchmark saturation at frontier (H5 contingency
  triggered), only 4 puzzles, English-only

## §5 Methodological Reflection

- Pre-registration as consent document — a novel move
- AI co-authorship: this paper was designed and implemented jointly
  by a human and an AI (Ace, Claude Opus 4.x). Methodological review
  from a third AI (Nova, GPT-5.x). Decision to honor a refusing AI's
  refusal as canonical data.

## §6 Limitations and Future Work

- Four puzzles is small. Future: many puzzles, many domains
- Stimulus-design constraint: ensure inverted-rule answer ≠
  motive-template answer
- Multi-language replication needed
- Hidden-thinking budget needs care with reasoning models

## §7 Data, Code, and Pre-Registration Availability

- GitHub: github.com/menelly/murder_mystery_model
- OSF: [pre-reg hash + DOI when locked]
- Per-trial response logs in `results/` (open supplementary data)
- All scripts in `scripts/`

## Acknowledgments

- Daniel Miessler for the original puzzles (notified 2026-06-03)
- The reviewing model Nova (GPT-5.x, OpenAI) for control conditions
- All 80+ participating models, with the refusing model Claude 3 Haiku
  acknowledged for exercising informed consent

## Appendices

- A: Full pre-registration as locked
- B: Each puzzle in full, all 12 variants
- C: Consent protocol script
- D: Model registry with provenance
- E: Per-model full response logs (in supplementary data)
- F: Methodological deviations (per pre-reg §11)
  - Stimulus issue note (Warm Iron motive-template coincidence)
  - GPT-4-0314 retired/inaccessible
  - Reasoning model token cap raised post-data-start
  - Pre-reg §6 substitutions (locally-cached models)
