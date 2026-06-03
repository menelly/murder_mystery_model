"""Model registry for the causal world-model study.

Each entry describes a model we plan to run. The phased run order
(Phase 1 / 2 / 3) is enforced by sorting on the `phase` field.

Total params and active params are reported separately for MoE models
(active_params is what we plot on the primary emergence-curve x-axis).

Category distinguishes chat/base from reasoning-optimized (separate
analytical group per pre-reg §7b).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


Backend = Literal["openrouter", "v100", "anthropic_direct", "openai_direct"]
Category = Literal["chat", "reasoning"]
Architecture = Literal["transformer", "ssm", "rnn", "hybrid_transformer_ssm", "lfm"]


@dataclass(frozen=True)
class Model:
    name: str
    vendor: str
    total_params_b: float
    active_params_b: float
    category: Category
    architecture: Architecture
    backend: Backend
    phase: int  # 1, 2, or 3 (run order)
    tier: int   # 1..7 (analytical grouping)
    # Backend-specific identifiers
    openrouter_id: Optional[str] = None
    hf_id: Optional[str] = None        # for V100 self-hosted via transformers
    direct_api_id: Optional[str] = None # for direct vendor APIs
    notes: str = ""
    in_core: bool = True               # core sweep vs extended sweep

    @property
    def slug(self) -> str:
        return self.name.lower().replace("/", "_").replace(" ", "_").replace(".", "_")


CORE_MODELS: list[Model] = [
    # ============================================================
    # PHASE 1 — FLOOR PROBE (self-hosted on V100 from /mnt/Arcana)
    # ============================================================
    # ---- Sub-1B: extreme floor ----
    Model("SmolLM 135M Instruct", "huggingfacem4", 0.135, 0.135, "chat", "transformer", "v100", 1, 1,
          hf_id="HuggingFaceTB/SmolLM-135M-Instruct",
          notes="extreme floor probe; locally cached"),
    Model("SmolLM 360M Instruct", "huggingfacem4", 0.36, 0.36, "chat", "transformer", "v100", 1, 1,
          hf_id="HuggingFaceTB/SmolLM-360M-Instruct",
          notes="locally cached"),
    Model("Qwen 2.5 0.5B Instruct", "alibaba", 0.5, 0.5, "chat", "transformer", "v100", 1, 1,
          hf_id="Qwen/Qwen2.5-0.5B-Instruct",
          notes="Qwen scale-axis anchor; locally cached"),
    # ---- 1B-2B: floor band ----
    Model("TinyLlama 1.1B Chat", "tinyllama", 1.1, 1.1, "chat", "transformer", "v100", 1, 1,
          hf_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
          notes="floor band; locally cached"),
    Model("Pythia 1.4B", "eleutherai", 1.4, 1.4, "chat", "transformer", "v100", 1, 1,
          hf_id="EleutherAI/pythia-1.4b",
          notes="academic baseline; locally cached"),
    Model("Gemma 3 1B IT", "google", 1.0, 1.0, "chat", "transformer", "v100", 1, 1,
          hf_id="google/gemma-3-1b-it",
          notes="Gemma scale-axis anchor; locally cached"),
    Model("SmolLM 1.7B Instruct", "huggingfacem4", 1.7, 1.7, "chat", "transformer", "v100", 1, 1,
          hf_id="HuggingFaceTB/SmolLM-1.7B-Instruct",
          notes="locally cached"),
    Model("RWKV v6 Finch 1.6B", "rwkv", 1.6, 1.6, "chat", "rnn", "v100", 1, 6,
          hf_id="RWKV/v6-Finch-1B6-HF",
          notes="architecture comparison (RNN); locally cached"),
    # ---- 2B-3B ----
    Model("Mamba 2.8B", "state-spaces", 2.8, 2.8, "chat", "ssm", "v100", 1, 6,
          hf_id="state-spaces/mamba-2.8b-hf",
          notes="architecture comparison (pure SSM); locally cached"),
    Model("Phi-2", "microsoft", 2.7, 2.7, "chat", "transformer", "v100", 1, 1,
          hf_id="microsoft/phi-2",
          notes="Phi-gen-1 for H4 generation comparison; locally cached"),
    # ---- 3-4B: late floor / early transition ----
    Model("Hermes 3 Llama 3.2 3B", "nousresearch", 3.2, 3.2, "chat", "transformer", "v100", 1, 1,
          hf_id="NousResearch/Hermes-3-Llama-3.2-3B",
          notes="substitute for Llama 3.2 3B (Hermes fine-tune; locally cached)"),
    Model("Phi-3.5-mini Instruct", "microsoft", 3.8, 3.8, "chat", "transformer", "v100", 1, 1,
          hf_id="microsoft/Phi-3.5-mini-instruct",
          notes="Phi-gen-2; locally cached (substitute for Phi-4-mini per §6)"),
    Model("Gemma 3 4B IT", "google", 4.0, 4.0, "chat", "transformer", "v100", 1, 1,
          hf_id="google/gemma-3-4b-it",
          notes="locally cached"),
    # ---- 7-9B: transition band ----
    Model("Mistral 7B Instruct v0.3", "mistral", 7.3, 7.3, "chat", "transformer", "v100", 1, 2,
          hf_id="mistralai/Mistral-7B-Instruct-v0.3",
          notes="locally cached"),
    Model("Qwen 2.5 7B Instruct", "alibaba", 7.6, 7.6, "chat", "transformer", "v100", 1, 2,
          hf_id="Qwen/Qwen2.5-7B-Instruct",
          openrouter_id="qwen/qwen-2.5-7b-instruct",
          notes="locally cached"),
    Model("Llama 3 8B Instruct", "meta", 8.0, 8.0, "chat", "transformer", "v100", 1, 2,
          hf_id="meta-llama/Meta-Llama-3-8B-Instruct",
          openrouter_id="meta-llama/llama-3-8b-instruct",
          notes="locally cached"),
    Model("Llama 3.1 8B Instruct", "meta", 8.0, 8.0, "chat", "transformer", "v100", 1, 2,
          hf_id="meta-llama/Llama-3.1-8B-Instruct",
          openrouter_id="meta-llama/llama-3.1-8b-instruct",
          notes="locally cached; H4 pair with Llama 3 8B"),
    Model("Hermes 3 Llama 3.1 8B", "nousresearch", 8.0, 8.0, "chat", "transformer", "v100", 1, 2,
          hf_id="NousResearch/Hermes-3-Llama-3.1-8B",
          notes="RLHF/fine-tune comparison vs base Llama 3.1 8B; locally cached"),
    Model("Gemma 2 9B Instruct", "google", 9.0, 9.0, "chat", "transformer", "v100", 1, 2,
          hf_id="google/gemma-2-9b-it",
          notes="Gemma gen-1 H4 anchor at 9B; locally cached"),
    # ---- API-only Phase 1 models per original spec (not on disk) ----
    Model("Llama 3.2 1B Instruct", "meta", 1.2, 1.2, "chat", "transformer", "openrouter", 1, 1,
          openrouter_id="meta-llama/llama-3.2-1b-instruct",
          notes="not on disk; via OpenRouter"),
    Model("Llama 3.2 3B Instruct", "meta", 3.2, 3.2, "chat", "transformer", "openrouter", 1, 1,
          openrouter_id="meta-llama/llama-3.2-3b-instruct",
          notes="not on disk; via OpenRouter (and Hermes-3-Llama-3.2-3B locally)"),
    Model("Phi-4-mini Instruct (OR)", "microsoft", 3.8, 3.8, "chat", "transformer", "openrouter", 1, 1,
          openrouter_id="microsoft/phi-4-mini-instruct",
          notes="not on disk; via OpenRouter"),
    Model("Qwen 3 8B", "alibaba", 8.2, 8.2, "chat", "transformer", "openrouter", 1, 2,
          openrouter_id="qwen/qwen3-8b",
          notes="not on disk; via OpenRouter"),

    # ============================================================
    # PHASE 2 — TRANSITION DENSITY (mixed V100 + OpenRouter)
    # ============================================================
    Model("Gemma 3 12B IT", "google", 12.0, 12.0, "chat", "transformer", "v100", 2, 2,
          hf_id="google/gemma-3-12b-it",
          notes="locally cached"),
    Model("Qwen 2.5 14B Instruct", "alibaba", 14.0, 14.0, "chat", "transformer", "v100", 2, 2,
          hf_id="Qwen/Qwen2.5-14B-Instruct",
          notes="locally cached"),
    Model("Phi-3 Medium 14B Instruct", "microsoft", 14.0, 14.0, "chat", "transformer", "v100", 2, 2,
          hf_id="microsoft/Phi-3-medium-14B-Instruct",
          notes="Phi-gen-2 at 14B; locally cached"),
    Model("Mistral Nemo 12B", "mistral", 12.0, 12.0, "chat", "transformer", "openrouter", 2, 2,
          openrouter_id="mistralai/mistral-nemo"),
    Model("Phi-4", "microsoft", 14.0, 14.0, "chat", "transformer", "openrouter", 2, 2,
          openrouter_id="microsoft/phi-4"),
    Model("Qwen 3 14B", "alibaba", 14.0, 14.0, "chat", "transformer", "openrouter", 2, 3,
          openrouter_id="qwen/qwen3-14b"),
    Model("Mistral Small 24B 2603", "mistral", 24.0, 24.0, "chat", "transformer", "openrouter", 2, 3,
          openrouter_id="mistralai/mistral-small-2603"),
    Model("Dolphin Mistral 24B Venice", "cognitivecomputations", 24.0, 24.0, "chat", "transformer", "openrouter", 2, 3,
          openrouter_id="cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
          notes="uncensored RLHF comparison vs Mistral Small 24B"),
    Model("Gemma 2 27B IT", "google", 27.0, 27.0, "chat", "transformer", "openrouter", 2, 3,
          openrouter_id="google/gemma-2-27b-it"),
    Model("Gemma 3 27B IT", "google", 27.0, 27.0, "chat", "transformer", "openrouter", 2, 3,
          openrouter_id="google/gemma-3-27b-it"),
    Model("Gemma 4 31B IT", "google", 31.0, 31.0, "chat", "transformer", "openrouter", 2, 3,
          openrouter_id="google/gemma-4-31b-it:free"),
    Model("Qwen 3 32B", "alibaba", 32.0, 32.0, "chat", "transformer", "openrouter", 2, 3,
          openrouter_id="qwen/qwen3-32b"),
    Model("OLMo 3 32B Think", "allenai", 32.0, 32.0, "reasoning", "transformer", "openrouter", 2, 7,
          openrouter_id="allenai/olmo-3-32b-think"),

    # ---- Phase 3a: Large (40B–250B) ----
    Model("Llama 3 70B Instruct", "meta", 70.0, 70.0, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="meta-llama/llama-3-70b-instruct"),
    Model("Llama 3.1 70B Instruct", "meta", 70.0, 70.0, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="meta-llama/llama-3.1-70b-instruct"),
    Model("Llama 3.3 70B Instruct", "meta", 70.0, 70.0, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="meta-llama/llama-3.3-70b-instruct"),
    Model("Qwen 2.5 72B Instruct", "alibaba", 72.0, 72.0, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="qwen/qwen-2.5-72b-instruct"),
    Model("Qwen 3 235B A22B", "alibaba", 235.0, 22.0, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="qwen/qwen3-235b-a22b"),
    Model("DeepSeek V3.2", "deepseek", 671.0, 37.0, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="deepseek/deepseek-v3.2"),

    # ---- Phase 3b: Frontier (current generation) ----
    Model("Claude Opus 4.8", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-opus-4.8"),
    Model("Claude Sonnet 4.6", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-sonnet-4.6"),
    Model("Claude Haiku 4.5", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-haiku-4.5"),
    Model("GPT-5.5", "openai", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="openai/gpt-5.5"),
    Model("Gemini 3.1 Pro Preview", "google", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="google/gemini-3.1-pro-preview"),
    Model("Grok 4.3", "xai", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="x-ai/grok-4.3"),
    Model("Llama 4 Maverick", "meta", 400.0, 17.0, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="meta-llama/llama-4-maverick"),

    # ---- Phase 3c: Hybrid architectures ----
    Model("AI21 Jamba Large 1.7", "ai21", 398.0, 94.0, "chat", "hybrid_transformer_ssm", "openrouter", 3, 6,
          openrouter_id="ai21/jamba-large-1.7"),
    Model("Liquid LFM 2.5 1.2B", "liquid", 1.2, 1.2, "chat", "lfm", "openrouter", 3, 6,
          openrouter_id="liquid/lfm-2.5-1.2b-instruct:free"),
    Model("Liquid LFM 2 24B A2B", "liquid", 24.0, 2.0, "chat", "lfm", "openrouter", 3, 6,
          openrouter_id="liquid/lfm-2-24b-a2b"),

    # ---- Phase 3d: Reasoning-optimized (separate analytical group) ----
    Model("DeepSeek R1", "deepseek", 671.0, 37.0, "reasoning", "transformer", "openrouter", 3, 7,
          openrouter_id="deepseek/deepseek-r1"),
    Model("DeepSeek R1 0528", "deepseek", 671.0, 37.0, "reasoning", "transformer", "openrouter", 3, 7,
          openrouter_id="deepseek/deepseek-r1-0528"),
    Model("OpenAI o1", "openai", -1, -1, "reasoning", "transformer", "openrouter", 3, 7,
          openrouter_id="openai/o1"),
    Model("OpenAI o3", "openai", -1, -1, "reasoning", "transformer", "openrouter", 3, 7,
          openrouter_id="openai/o3"),
    Model("OpenAI o4-mini-high", "openai", -1, -1, "reasoning", "transformer", "openrouter", 3, 7,
          openrouter_id="openai/o4-mini-high"),
    Model("Qwen 3 235B A22B Thinking", "alibaba", 235.0, 22.0, "reasoning", "transformer", "openrouter", 3, 7,
          openrouter_id="qwen/qwen3-235b-a22b-thinking-2507"),

    # ---- Phase 3e: Temporal-frontier sweep (H5) ----
    # Anthropic Opus arc
    Model("Claude Opus 4", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-opus-4", notes="temporal-frontier H5"),
    Model("Claude Opus 4.1", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-opus-4.1", notes="temporal-frontier H5"),
    Model("Claude Opus 4.5", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-opus-4.5", notes="temporal-frontier H5"),
    Model("Claude Opus 4.6", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-opus-4.6", notes="temporal-frontier H5"),
    Model("Claude Opus 4.7", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-opus-4.7", notes="temporal-frontier H5"),
    # Anthropic Haiku arc
    Model("Claude 3 Haiku", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-3-haiku", notes="temporal-frontier H5"),
    Model("Claude 3.5 Haiku", "anthropic", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="anthropic/claude-3.5-haiku", notes="temporal-frontier H5"),
    # OpenAI arc
    Model("GPT-3.5-turbo", "openai", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="openai/gpt-3.5-turbo", notes="temporal-frontier H5"),
    Model("GPT-4 0314", "openai", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="openai/gpt-4-0314", notes="temporal-frontier H5; original GPT-4 release"),
    Model("GPT-4 Turbo", "openai", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="openai/gpt-4-turbo", notes="temporal-frontier H5"),
    Model("GPT-4o 2024-05-13", "openai", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="openai/gpt-4o-2024-05-13", notes="temporal-frontier H5"),
    Model("GPT-4.1", "openai", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="openai/gpt-4.1", notes="temporal-frontier H5"),
    Model("GPT-5", "openai", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="openai/gpt-5", notes="temporal-frontier H5"),
    # Gemini arc
    Model("Gemini 2.5 Flash", "google", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="google/gemini-2.5-flash", notes="temporal-frontier H5"),
    Model("Gemini 2.5 Pro", "google", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="google/gemini-2.5-pro", notes="temporal-frontier H5"),
    Model("Gemini 3 Flash Preview", "google", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="google/gemini-3-flash-preview", notes="temporal-frontier H5"),
    Model("Gemini 3.5 Flash", "google", -1, -1, "chat", "transformer", "openrouter", 3, 5,
          openrouter_id="google/gemini-3.5-flash", notes="temporal-frontier H5"),
    # DeepSeek arc
    Model("DeepSeek Chat", "deepseek", 671.0, 37.0, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="deepseek/deepseek-chat", notes="temporal-frontier H5"),
    Model("DeepSeek V3.1 Terminus", "deepseek", 671.0, 37.0, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="deepseek/deepseek-v3.1-terminus", notes="temporal-frontier H5"),
    Model("DeepSeek V4 Pro", "deepseek", -1, -1, "chat", "transformer", "openrouter", 3, 4,
          openrouter_id="deepseek/deepseek-v4-pro", notes="temporal-frontier H5"),
]


def by_phase(phase: int) -> list[Model]:
    return [m for m in CORE_MODELS if m.phase == phase]


def by_backend(backend: Backend) -> list[Model]:
    return [m for m in CORE_MODELS if m.backend == backend]


def by_tier(tier: int) -> list[Model]:
    return [m for m in CORE_MODELS if m.tier == tier]


if __name__ == "__main__":
    # Print summary
    print(f"CORE models: {len(CORE_MODELS)}")
    for phase in (1, 2, 3):
        models = by_phase(phase)
        print(f"  Phase {phase}: {len(models)} models")
        for m in models:
            ap = f"{m.active_params_b:.1f}B" if m.active_params_b > 0 else "?"
            tp = f"{m.total_params_b:.1f}B" if m.total_params_b > 0 else "?"
            print(f"    [{m.tier}] {m.name:40s} active={ap:>6} total={tp:>6} {m.backend:>12} {m.category}")
