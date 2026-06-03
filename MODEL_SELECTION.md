# Model Selection Plan (v2 — Nova-revised)

Models drawn from the OpenRouter catalog (fetched 2026-06-03), the local Linux box (V100 GPU, `/home/codex/venv` with CUDA, downloads to `/mnt/Arcana`), and direct vendor APIs (for retired-from-OR older models where accessible).

## Core vs. extended sweep (per Nova)

To prevent reviewers from treating dropped models as flexibility, the model list is split into:

- **CORE SWEEP** — every model in this section is mandatory. The study runs only when all CORE models have either (a) completed 72 trials or (b) been logged as inaccessible with the reason captured.
- **EXTENDED SWEEP** — additional models added if access and budget permit. Reported separately. Their inclusion/exclusion is *not* a degree of freedom in the H1–H5 analyses, which depend only on the CORE set.

## Parameter accounting (per Nova)

For Mixture-of-Experts (MoE) models we report **two columns**:
- `total_params`: total weights in the model
- `active_params`: weights actually routed-to per token (the "active per-token" parameter count)

The emergence curve is plotted twice: once with `total_params` on the x-axis, once with `active_params`. We pre-register the **active-params curve as primary** because it represents the actual compute applied per token. The total-params curve is reported as a robustness check.

## Reasoning-optimized vs. chat/base (per Nova §7b of pre-reg)

Models trained for explicit deliberation (DeepSeek R1 / R1-0528, OpenAI o-series, Qwen "-thinking" variants) are tagged `category: reasoning`. They form a separate analytical group with their own emergence curve. They are NOT pooled with chat/base models on the primary H1 curve.

## Inference path

The Linux box has a V100 32GB GPU (Tesla, SXM2). To minimize cost, **small models run self-hosted on the V100 in parallel with OpenRouter API calls**. The orchestrator dispatches jobs to either backend based on the model registry; the V100 worker and the OpenRouter worker run concurrently in different processes, merging results at analysis time. V100 capacity envelope: comfortable fp16 up to ~14B, int8/int4 quantized up to ~32B. Anything above 32B routes through OpenRouter.

A second GPU (RTX 3080 10GB) is present on the box but **broken / unavailable** as of 2026-06-03; not used. V100 is the sole local inference path.

## Phased run order (per Nova — information-per-dollar optimization)

Run order is pre-registered in §7c of `PREREGISTRATION.md`. Summarized here:

- **Phase 1 — locate the floor.** Self-host every model ≤8B and the non-transformer architectures on the V100. Cheap (free) and dense at the parameter range where H1's transition is predicted to live.
- **Phase 2 — densely sample the transition.** Self-host where ≤14B fp16 or quantized ≤32B fits the V100; OpenRouter for anything that doesn't. This phase covers ~12B–32B where the emergence curve's *slope* is the science.
- **Phase 3 — establish the ceiling.** Frontier, hybrid, reasoning, and temporal-frontier sweeps — almost entirely via OpenRouter.

This order means the cheapest, most information-dense phase runs first. If Phase 1 confirms a clean floor, Phase 2 + 3 can be scaled or halted on budget grounds without losing the headline finding.

---

# CORE SWEEP

The mandatory model set. ~30 models. Estimated cost: well under $50.

## Tier 1 — Tiny (≤3B params, all self-hosted on V100)

| Model | Total params | Active params | Inference path | Tag |
|---|---|---|---|---|
| TinyLlama-1.1B-Chat-v1.0 | 1.1B | 1.1B | V100 | chat |
| Llama 3.2 1B Instruct | 1.2B | 1.2B | V100 | chat |
| Llama 3.2 3B Instruct | 3.2B | 3.2B | V100 | chat |
| Gemma 3 4B IT | 4B | 4B | V100 | chat |
| Phi-4-mini-instruct | ~3.8B | ~3.8B | V100 | chat |

## Tier 2 — Small (5B–14B, mixed V100 + OpenRouter)

| Model | Total params | Active params | Inference path | Tag |
|---|---|---|---|---|
| Llama 3 8B Instruct | 8B | 8B | V100 | chat |
| Llama 3.1 8B Instruct | 8B | 8B | V100 | chat |
| Qwen 2.5 7B Instruct | 7B | 7B | V100 | chat |
| Qwen 3 8B | 8B | 8B | V100 | chat |
| Mistral 7B Instruct v0.3 | 7B | 7B | V100 | chat |
| Mistral Nemo (12B) | 12B | 12B | OpenRouter | chat |
| Phi-4 (~14B) | 14B | 14B | OpenRouter | chat |

## Tier 3 — Medium (24B–35B, OpenRouter except where noted)

| Model | Total params | Active params | Inference path | Tag |
|---|---|---|---|---|
| Mistral Small 24B (2603) | 24B | 24B | OpenRouter | chat |
| Dolphin Mistral 24B Venice (free) | 24B | 24B | OpenRouter | chat / uncensored |
| Qwen 3 14B | 14B | 14B | OpenRouter | chat |
| Qwen 3 32B | 32B | 32B | OpenRouter | chat |
| Gemma 2 27B IT | 27B | 27B | OpenRouter | chat |
| Gemma 3 27B IT | 27B | 27B | OpenRouter | chat |
| Gemma 4 31B IT | 31B | 31B | OpenRouter | chat |
| OLMo 3 32B Think | 32B | 32B | OpenRouter | reasoning |

## Tier 4 — Large (70B–250B, OpenRouter)

| Model | Total params | Active params | Inference path | Tag |
|---|---|---|---|---|
| Llama 3 70B Instruct | 70B | 70B | OpenRouter | chat |
| Llama 3.1 70B Instruct | 70B | 70B | OpenRouter | chat |
| Llama 3.3 70B Instruct | 70B | 70B | OpenRouter | chat |
| Qwen 2.5 72B Instruct | 72B | 72B | OpenRouter | chat |
| Qwen 3 235B A22B | 235B | 22B | OpenRouter | chat |
| DeepSeek V3.2 | ~671B | ~37B | OpenRouter | chat |

## Tier 5 — Frontier (current generation)

| Model | Total params | Active params | Inference path | Tag |
|---|---|---|---|---|
| Claude Opus 4.8 | (undisclosed) | (undisclosed) | OpenRouter | chat |
| Claude Sonnet 4.6 | (undisclosed) | (undisclosed) | OpenRouter | chat |
| Claude Haiku 4.5 | (undisclosed) | (undisclosed) | OpenRouter | chat |
| GPT-5.5 | (undisclosed) | (undisclosed) | OpenRouter | chat |
| Gemini 3.1 Pro | (undisclosed) | (undisclosed) | OpenRouter | chat |
| Grok 4.3 | (undisclosed) | (undisclosed) | OpenRouter | chat |
| Llama 4 Maverick | ~400B | ~17B | OpenRouter | chat |

## Tier 6 — Non-transformer / hybrid architectures (CORE)

| Model | Architecture | Total params | Active params | Inference path |
|---|---|---|---|---|
| AI21 Jamba Large 1.7 | hybrid transformer+Mamba | 398B | 94B | OpenRouter |
| Liquid LFM 2.5 1.2B (free) | Liquid Foundation Model (hybrid) | 1.2B | 1.2B | OpenRouter |
| Liquid LFM 2 24B A2B | LFM MoE | 24B | 2B | OpenRouter |
| Mamba 2.8B | pure SSM | 2.8B | 2.8B | V100 (self-hosted) |
| RWKV-5 World 7B | RNN-based | 7B | 7B | V100 (self-hosted) |

## Tier 7 — Reasoning-optimized (separate analytical group)

Analyzed as their own emergence curve. Not pooled with chat/base models on H1.

| Model | Total params | Active params | Inference path | Tag |
|---|---|---|---|---|
| DeepSeek R1 | ~671B | ~37B | OpenRouter | reasoning |
| DeepSeek R1-0528 | ~671B | ~37B | OpenRouter | reasoning |
| OpenAI o1 | (undisclosed) | (undisclosed) | OpenRouter | reasoning |
| OpenAI o3 | (undisclosed) | (undisclosed) | OpenRouter | reasoning |
| OpenAI o3-mini-high | (undisclosed) | (undisclosed) | OpenRouter | reasoning |
| OpenAI o4-mini-high | (undisclosed) | (undisclosed) | OpenRouter | reasoning |
| Qwen 3 235B A22B Thinking (2507) | 235B | 22B | OpenRouter | reasoning |
| Qwen 3 Max Thinking | undisclosed | undisclosed | OpenRouter | reasoning |

## Tier 4b — Temporal-frontier sweep (H5 — CORE)

Same vendor, walking through frontier generations at approximately fixed param count.

### Anthropic Opus arc:
- Claude Opus 4 → 4.1 → 4.5 → 4.6 → 4.7 → 4.8 (six points, one frontier slot)

### Anthropic Haiku arc:
- Claude 3 Haiku → 3.5 Haiku → Haiku 4.5

### OpenAI GPT arc:
- GPT-3.5-turbo → GPT-4-0314 → GPT-4-turbo → GPT-4o (2024-05-13) → GPT-4.1 → GPT-5 → GPT-5.5

### Google Gemini arc:
- Gemini 2.5 Flash → Gemini 3 Flash preview → Gemini 3.1 Pro preview → Gemini 3.5 Flash

### Google Gemma arc (27–31B held approximately constant):
- Gemma 2 27B → Gemma 3 27B → Gemma 4 31B

### Meta Llama arc (70B class):
- Llama 3 70B → Llama 3.1 70B → Llama 3.3 70B

### Meta Llama arc (8B class):
- Llama 3 8B → Llama 3.1 8B (and Llama 3.2 3B as smaller sibling)

### DeepSeek arc:
- DeepSeek Chat (v3 stable) → V3.1 Terminus → V3.2 → V4 Pro

### Qwen arc (frontier class):
- Qwen 2.5 72B → Qwen 3 235B A22B → Qwen 3.5 397B A17B → Qwen 3.7 Max

## Same-family generation pairs (H4 — small-scale, CORE)

Clean generational pairs only. Phi-4 vs Phi-4-mini is excluded per Nova: that is a scale comparison within a generation, not a generation comparison.

- Llama 3 8B vs Llama 3.1 8B (same scale, +0.1 generation)
- Qwen 2.5 7B vs Qwen 3 8B (same approximate scale, +0.5 generation)
- Gemma 2 27B vs Gemma 3 27B vs Gemma 4 31B (held at ~27–31B, three generations)

For H4 we report paired differences (newer minus older) on the inverted-rule accuracy. H4 supported if ≥2 of 3 pairs show a positive paired difference.

---

# EXTENDED SWEEP

Run if budget and access permit. Reported separately. NOT load-bearing for H1–H5.

- Mistral Large 2407 / Mistral Large 2512 / Mistral Medium 3.1 (Mistral frontier temporal axis)
- Cohere Command-R (if accessible)
- Inflection / IBM Granite (architecture diversity)
- Older Claude (2.1, 3 Opus) — attempt via direct Anthropic API; if retired, log as inaccessible
- Older OpenAI (GPT-4 base, gpt-3.5-turbo-0613) — attempt direct
- Tiered Qwen 3.5 / 3.6 deeper sweep (the full 5-generation Qwen axis)
- gpt-oss-20b and gpt-oss-120b (OpenAI open-weight; useful as architecture-control)

---

## Inference orchestration summary

- **V100 self-hosted pool:** Tiers 1, 2 (most), Mamba, RWKV. ~10 models running locally for free.
- **OpenRouter API pool:** Tiers 3, 4, 5, 6 (hybrid), 7, 4b temporal arcs. ~50 models via API.
- **Direct vendor API pool:** retired Claude/OpenAI models in EXTENDED sweep (if accessible).
- The two main pools run **in parallel** (different processes, separate result files merged at analysis time). The Linux box's bandwidth easily covers concurrent API + local-GPU work.

## Total CORE model count

~32 unique models. 32 × 72 trials = ~2,300 CORE trials.
Estimated CORE cost: $30–80.
Estimated CORE wall-clock: a few hours, dominated by V100 local inference and OpenRouter throughput.
