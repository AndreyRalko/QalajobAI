"""
Build provider-specific OpenAI-compatible HTTP clients.
"""

from __future__ import annotations

from django.conf import settings

from ..openai_client import OpenAIClient

_local_client: OpenAIClient | None = None
_openai_client: OpenAIClient | None = None


def _openai_api_key() -> str:
    return (
        getattr(settings, "LLM_OPENAI_API_KEY", "")
        or getattr(settings, "OPENAI_API_KEY", "")
        or ""
    ).strip()


def _openai_model() -> str:
    return (
        getattr(settings, "LLM_OPENAI_MODEL", "")
        or getattr(settings, "OPENAI_MODEL", "")
        or "gpt-4o-mini"
    )


def get_local_provider_client() -> OpenAIClient:
    global _local_client
    if _local_client is None:
        _local_client = OpenAIClient(
            api_key=getattr(settings, "LLM_LOCAL_API_KEY", "ollama") or "ollama",
            model=getattr(settings, "LLM_LOCAL_MODEL", "qwen2.5:7b-instruct"),
            base_url=getattr(settings, "LLM_LOCAL_BASE_URL", "http://127.0.0.1:11434/v1"),
            timeout=getattr(settings, "LLM_LOCAL_TIMEOUT", 180),
            provider="local",
            require_api_key=False,
        )
    return _local_client


def get_openai_provider_client() -> OpenAIClient:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient(
            api_key=_openai_api_key(),
            model=_openai_model(),
            base_url=getattr(settings, "LLM_OPENAI_BASE_URL", "https://api.openai.com/v1"),
            timeout=getattr(settings, "LLM_OPENAI_TIMEOUT", 60),
            provider="openai",
            require_api_key=True,
        )
    return _openai_client


def get_llm_client(provider: str) -> OpenAIClient:
    if provider == "local":
        return get_local_provider_client()
    return get_openai_provider_client()


def reset_llm_clients() -> None:
    """Clear cached clients (useful in tests)."""
    global _local_client, _openai_client
    _local_client = None
    _openai_client = None
