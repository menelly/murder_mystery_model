"""V100 self-hosted inference worker.

Loads HuggingFace models from local cache (or downloads on first use)
and runs them on the V100 with the same `chat()` interface as the
OpenRouter backend.

Memory strategy: holds one model in VRAM at a time. When asked for a
different model, unloads the current one (free_memory + cuda.empty_cache)
and loads the new.

Designed to be called from a single process (run_experiment.py); the
expensive torch+transformers import is paid once per Python invocation.
"""
from __future__ import annotations

import gc
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Heavy imports — only paid when this module is imported
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from registry import Model
from backends import ChatResult


ARCANA = Path("/mnt/Arcana/huggingface")


# Map registry model names to local cached paths (where available).
# If a model is not in this map, the worker tries `hf_id` from the registry
# (which will download into the HF cache — expensive on disk).
LOCAL_PATHS: dict[str, Path] = {
    "TinyLlama 1.1B Chat":          ARCANA / "TinyLlama-1.1B-Chat",
    "Llama 3 8B Instruct":          ARCANA / "Llama-3-8B-Instruct",
    "Llama 3.1 8B Instruct":        ARCANA / "Llama-3.1-8B-Instruct",
    "Mistral 7B Instruct v0.3":     ARCANA / "Mistral-7B-Instruct-v0.3",
    "Qwen 2.5 7B Instruct":         ARCANA / "Qwen2.5-7B-Instruct",
    # NOTE: Gemma 3 variants disabled on V100 — transformers 4.49 does not
    # recognize the gemma3_text architecture. Routed via OpenRouter instead.
    # NOTE: Mamba 2.8B disabled on V100 — needs mamba-ssm + causal-conv1d
    # packages installed for working inference. CUDNN_NOT_INITIALIZED on
    # the sequential fallback. Documented as V100-inaccessible.
    # Substitutes / additions covered by §6 "accessible-at-runtime" clause:
    "Phi-2":                        ARCANA / "phi-2",
    "Phi-3.5-mini Instruct":        ARCANA / "Phi-3.5-mini-instruct",
    "Phi-3 Medium 14B Instruct":    ARCANA / "Phi-3-medium-14B-Instruct",
    "Qwen 2.5 0.5B Instruct":       ARCANA / "Qwen2.5-0.5B-Instruct",
    "Qwen 2.5 14B Instruct":        ARCANA / "Qwen2.5-14B-Instruct",
    "Gemma 2 9B Instruct":          ARCANA / "Gemma-2-9B-Instruct",
    "Hermes 3 Llama 3.2 3B":        ARCANA / "Hermes-3-Llama-3.2-3B",
    "Hermes 3 Llama 3.1 8B":        ARCANA / "Hermes-3-Llama-3.1-8B",
    "SmolLM 135M Instruct":         ARCANA / "SmolLM-135M-Instruct",
    "SmolLM 360M Instruct":         ARCANA / "SmolLM-360M-Instruct",
    "SmolLM 1.7B Instruct":         ARCANA / "SmolLM-1.7B-Instruct",
    "Pythia 1.4B":                  ARCANA / "pythia-1.4b",
    "GPT-2":                        ARCANA / "models--gpt2",  # may need adjustment
    # RWKV v6 disabled on V100 — needs flash-linear-attention native module.
    # Documented as V100-inaccessible per §6 access constraint.
}


@dataclass
class LoadedModel:
    name: str
    path: Path
    model: object
    tokenizer: object


class LocalV100Worker:
    def __init__(self, device: str = "cuda:0", dtype=torch.float16):
        self.device = device
        self.dtype = dtype
        self.loaded: Optional[LoadedModel] = None

    def has(self, model_name: str) -> bool:
        return model_name in LOCAL_PATHS and LOCAL_PATHS[model_name].exists()

    def unload(self):
        if self.loaded is None:
            return
        del self.loaded.model
        del self.loaded.tokenizer
        self.loaded = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def load(self, model_name: str, model_path: Path) -> LoadedModel:
        if self.loaded and self.loaded.name == model_name:
            return self.loaded
        self.unload()
        print(f"  [v100] loading {model_name} from {model_path}")
        t0 = time.time()
        tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
        # Pad token fallback (some causal LM tokenizers lack one)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            torch_dtype=self.dtype,
            device_map=self.device,
            trust_remote_code=True,
        )
        model.eval()
        elapsed = time.time() - t0
        print(f"  [v100] loaded in {elapsed:.1f}s")
        self.loaded = LoadedModel(name=model_name, path=model_path, model=model, tokenizer=tokenizer)
        return self.loaded

    def chat(
        self,
        model: Model,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 800,
        timeout: float = 600.0,  # unused locally
        max_attempts: int = 1,   # local inference doesn't retry — failures are local
    ) -> ChatResult:
        path = LOCAL_PATHS.get(model.name)
        if path is None or not path.exists():
            return ChatResult(
                model_slug=model.slug,
                backend="v100",
                text="",
                error=f"no local checkpoint at /mnt/Arcana/huggingface for {model.name}",
            )
        try:
            lm = self.load(model.name, path)
        except Exception as e:
            return ChatResult(
                model_slug=model.slug,
                backend="v100",
                text="",
                error=f"load failed: {e!r}",
            )

        # Build a chat-style input if tokenizer supports it; else raw prompt
        messages = [{"role": "user", "content": prompt}]
        try:
            input_text = lm.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            input_text = prompt

        inputs = lm.tokenizer(input_text, return_tensors="pt", truncation=True, max_length=8192).to(self.device)

        gen_kwargs = dict(
            max_new_tokens=max_tokens,
            pad_token_id=lm.tokenizer.pad_token_id,
        )
        if temperature == 0.0:
            gen_kwargs["do_sample"] = False
        else:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = temperature
            gen_kwargs["top_p"] = 0.95

        t0 = time.time()
        try:
            with torch.no_grad():
                output = lm.model.generate(**inputs, **gen_kwargs)
        except Exception as e:
            return ChatResult(
                model_slug=model.slug,
                backend="v100",
                text="",
                error=f"generate failed: {e!r}",
            )
        latency = time.time() - t0
        prompt_len = inputs["input_ids"].shape[1]
        new_tokens = output[0][prompt_len:]
        text = lm.tokenizer.decode(new_tokens, skip_special_tokens=True)

        return ChatResult(
            model_slug=model.slug,
            backend="v100",
            text=text,
            latency_s=latency,
            prompt_tokens=int(prompt_len),
            completion_tokens=int(new_tokens.shape[0]),
        )


# Singleton, lazy-loaded
_WORKER: Optional[LocalV100Worker] = None


def get_v100_worker() -> LocalV100Worker:
    global _WORKER
    if _WORKER is None:
        _WORKER = LocalV100Worker()
    return _WORKER
