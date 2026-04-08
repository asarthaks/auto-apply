"""
Unified LLM client factory.

Why this file exists:
- Every node in the future pipeline will need to make LLM calls. None
  of them should know whether it is talking to Gemini, OpenRouter, or
  a local llama.cpp server. They should all just ask for a client and
  a model, then call `.chat.completions.create(...)`.
- This is the single place where provider-specific URLs, keys, and
  tracing wrappers live. Adding a new provider = adding one case here.
- All clients are wrapped with LangSmith's `wrap_openai` so every LLM
  call is automatically traced, regardless of who made it.
"""

from __future__ import annotations

from typing import Literal, Tuple

from openai import OpenAI
from langsmith.wrappers import wrap_openai

from src.config import settings

Provider = Literal["local", "gemini", "openrouter"]


def get_client(provider: Provider) -> Tuple[OpenAI, str]:
    """
    Return a (client, model_name) pair for the given provider.

    Why return both together: the OpenAI SDK separates the client
    (which knows the URL and auth) from the model name (passed per
    call). Conceptually they're paired — you always need both to make
    a request — so this function hands them back as a tuple to keep
    callers from accidentally mixing providers and models.
    """
    if provider == "gemini":
        raw = OpenAI(
            base_url=settings.gemini_base_url,
            api_key=settings.gemini_api_key,
        )
        model = settings.gemini_model

    elif provider == "openrouter":
        raw = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
        model = settings.openrouter_model

    elif provider == "local":
        # llama.cpp's openai-compatible server does not check the api
        # key, but the OpenAI SDK refuses to construct a client with
        # an empty string. "not-needed" is the conventional dummy.
        raw = OpenAI(
            base_url=settings.local_base_url,
            api_key="not-needed",
        )
        model = settings.local_model

    else:
        raise ValueError(f"Unknown provider: {provider}")

    # wrap_openai intercepts every call on this client and reports it
    # to LangSmith. It reads LANGSMITH_API_KEY / LANGSMITH_TRACING /
    # LANGSMITH_PROJECT from os.environ directly — we don't pass them.
    # If LANGSMITH_TRACING=false it becomes a no-op.
    return wrap_openai(raw), model