"""
Config loading and validation.

Why this file exists:
- Centralize all environment-variable access in ONE place. Every other
  module imports `settings` from here. No `os.getenv` scattered around.
- Fail loudly at import time if required keys are missing. We would
  rather crash on `docker compose up` than three nodes into a LangGraph
  run when a missing key finally gets dereferenced.
- Give a single source of truth for base URLs and default models, so
  switching providers is a one-line change.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env into os.environ. In Docker, env_file: .env in compose
# already populates os.environ, so this is mostly a no-op inside the
# container — but it makes the module also work if you ever run it
# outside Docker (e.g., a quick `python -m src.smoke_test` on the host).
load_dotenv()


def _require(key: str) -> str:
    """Read an env var or die with a clear message."""
    val = os.environ.get(key)
    if not val:
        print(
            f"FATAL: environment variable {key} is missing or empty.\n"
            f"Check your .env file and docker-compose env_file directive.",
            file=sys.stderr,
        )
        sys.exit(1)
    return val


def _optional(key: str, default: str) -> str:
    return os.environ.get(key, default)


@dataclass(frozen=True)
class Settings:
    # --- LLM providers ---
    gemini_api_key: str
    gemini_base_url: str
    gemini_model: str

    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str

    local_base_url: str
    local_model: str

    # --- Observability ---
    langsmith_api_key: str
    langsmith_project: str
    langsmith_tracing: str  # string "true"/"false" — the SDK reads env directly


def load_settings() -> Settings:
    return Settings(
        gemini_api_key=_require("GEMINI_API_KEY"),
        gemini_base_url=_optional(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        ),
        gemini_model=_optional("GEMINI_MODEL", "gemini-2.5-flash"),

        openrouter_api_key=_require("OPENROUTER_API_KEY"),
        openrouter_base_url=_optional(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        ),
        # deepseek-chat is cheap and capable; swap later per-node if needed
        openrouter_model=_optional("OPENROUTER_MODEL", "deepseek/deepseek-chat"),

        local_base_url=_optional(
            "LOCAL_BASE_URL", "http://host.docker.internal:8080/v1"
        ),
        local_model=_optional("LOCAL_MODEL", "gemma-3n-e4b"),

        langsmith_api_key=_require("LANGSMITH_API_KEY"),
        langsmith_project=_optional("LANGSMITH_PROJECT", "job-apply-dev"),
        langsmith_tracing=_optional("LANGSMITH_TRACING", "true"),
    )


# Module-level singleton. Import this from everywhere else.
# If any required key is missing, this line crashes the process
# before any other module has a chance to run.
settings = load_settings()