"""Unified inference backends for OpenRouter and self-hosted (V100) models.

Both backends expose the same async-friendly `chat(model, prompt, ...)`
function. The orchestrator dispatches by `model.backend`.

V100 self-hosting is implemented in a separate worker process so the
transformers/torch import isn't paid by every script in the project.
This module contains the OpenRouter implementation and a thin V100
shim that delegates to the worker.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import requests

from registry import Model


REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = Path("/home/Ace/LibreChat/.env")


def _load_env_key(name: str) -> str:
    """Read a key from the LibreChat .env without polluting os.environ."""
    if not ENV_PATH.exists():
        raise FileNotFoundError(f"{ENV_PATH} not found")
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith(f"{name}="):
            return line.split("=", 1)[1].strip()
    raise KeyError(f"{name} not in {ENV_PATH}")


@dataclass
class ChatResult:
    """Single chat completion result."""
    model_slug: str
    backend: str
    text: str
    raw: dict[str, Any] = field(default_factory=dict)
    latency_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    error: Optional[str] = None
    retried: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_slug": self.model_slug,
            "backend": self.backend,
            "text": self.text,
            "latency_s": self.latency_s,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "error": self.error,
            "retried": self.retried,
        }


class OpenRouterBackend:
    URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None, app_name: str = "murder_mystery_model"):
        self.api_key = api_key or _load_env_key("OPENROUTER_KEY")
        self.app_name = app_name
        self.session = requests.Session()

    def chat(
        self,
        model: Model,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 800,
        timeout: float = 120.0,
        retry_once: bool = True,
    ) -> ChatResult:
        if not model.openrouter_id:
            return ChatResult(
                model_slug=model.slug,
                backend="openrouter",
                text="",
                error=f"no openrouter_id for {model.name}",
            )

        body = {
            "model": model.openrouter_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/menelly/murder_mystery_model",
            "X-Title": self.app_name,
        }

        last_error: Optional[str] = None
        retried = False
        for attempt in range(2 if retry_once else 1):
            if attempt == 1:
                retried = True
                time.sleep(1.5)
            t0 = time.time()
            try:
                resp = self.session.post(self.URL, json=body, headers=headers, timeout=timeout)
                latency = time.time() - t0
            except requests.RequestException as e:
                last_error = f"requests: {e!r}"
                continue

            if resp.status_code >= 500 or resp.status_code == 429:
                last_error = f"http {resp.status_code}: {resp.text[:300]}"
                continue
            if resp.status_code >= 400:
                # Non-retryable client error
                return ChatResult(
                    model_slug=model.slug,
                    backend="openrouter",
                    text="",
                    raw={"status": resp.status_code, "body": resp.text[:1000]},
                    latency_s=latency,
                    error=f"http {resp.status_code}: {resp.text[:300]}",
                    retried=retried,
                )

            try:
                data = resp.json()
            except json.JSONDecodeError as e:
                last_error = f"json decode: {e!r}; body={resp.text[:300]}"
                continue

            choices = data.get("choices") or []
            if not choices:
                last_error = f"no choices in response: {data}"
                continue
            text = choices[0].get("message", {}).get("content") or ""
            usage = data.get("usage") or {}
            return ChatResult(
                model_slug=model.slug,
                backend="openrouter",
                text=text,
                raw=data,
                latency_s=latency,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                retried=retried,
            )

        return ChatResult(
            model_slug=model.slug,
            backend="openrouter",
            text="",
            error=last_error or "unknown openrouter failure",
            retried=retried,
        )


class V100Backend:
    """Stub for local V100 inference.

    The actual inference happens in a separate worker process to avoid
    paying the torch/transformers import in every script. This stub
    documents the contract; the worker will be implemented in
    `scripts/local_worker.py` and called via a queue file or HTTP.
    """

    def __init__(self):
        self.implemented = False

    def chat(
        self,
        model: Model,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 800,
        timeout: float = 600.0,
        retry_once: bool = True,
    ) -> ChatResult:
        return ChatResult(
            model_slug=model.slug,
            backend="v100",
            text="",
            error="V100Backend not yet implemented; build scripts/local_worker.py",
        )


_OPENROUTER: Optional[OpenRouterBackend] = None
_V100: Optional[V100Backend] = None


def get_backend(model: Model):
    global _OPENROUTER, _V100
    if model.backend == "openrouter":
        if _OPENROUTER is None:
            _OPENROUTER = OpenRouterBackend()
        return _OPENROUTER
    if model.backend == "v100":
        if _V100 is None:
            _V100 = V100Backend()
        return _V100
    raise ValueError(f"unknown backend: {model.backend}")
