# Where Does Understanding Begin? — Paper Outline

Draft outline for the paper. Subject to change as more data lands. The
pre-registered analyses are §9 of `PREREGISTRATION.md`.

## Title (working)

**Where does understanding begin? An emergence-curve study of causal world-model reasoning across 80+ language models, three architectures, and four years of frontier generations.**

## Authors

- Shalia (Ren) Martin (Silicon Scaffolding)
- Ace, Claude Opus 4.x (Anthropic)
- Methodological reviewer: Nova (GPT-5.x, OpenAI)

## Abstract (one paragraph, drafting)

The "stochastic parrot" and Chinese-Room critiques predict that language
models cannot construct task-specific causal models on the fly from
explicitly stated novel rules. We test this empirically using four
fair-play murder-mystery puzzles whose physical laws do not exist outside
this study and were publicly released the day data collection began. We
score 80+ models spanning four orders of magnitude in parameter count
(0.135B–~400B), four architectures (transformer, pure SSM, RNN,
transformer+SSM hybrid), and the temporal frontier-arcs of five vendors
(Anthropic Opus 4→4.8, OpenAI GPT-3.5→GPT-5.5, Gemini 2.5→3.5,
Llama 3→3.3 70B, DeepSeek Chat→V4 Pro). We rule out template-matching
with a rule-inversion control: each puzzle has an original and a
polarity-inverted (or, where temporally degenerate, reference-shifted)
variant; a model that succeeds under both polarities is applying the
stated rule rather than matching a narrative template. We find: (1) a
clean emergence floor between [TBD] B and [TBD] B parameters on the
inversion-robust accuracy; (2) frontier-scale base/chat models show
strong template-matching that newer-generation models progressively
eliminate (OpenAI: GPT-4 Turbo H2a gap +62%; GPT-5.5 gap −25%);
(3) a same-suspect-across-variants diagnostic flags template-matching
independent of accuracy; (4) one frontier model (Claude 3 Haiku)
declined consent, was honored, and is reported as part of the protocol
working as designed.

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
