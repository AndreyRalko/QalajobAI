"""
Hybrid LLM client: route by feature, fallback local → OpenAI.
"""

from __future__ import annotations

import json
import logging

from ..action_log import get_ai_log_context
from .factory import get_llm_client
from .router import allows_openai_fallback, pick_provider

logger = logging.getLogger("apps")


class HybridLLMClient:
    """Same interface as OpenAIClient (_call / _call_json)."""

    def _resolve_route(self) -> tuple[str, str]:
        ctx = get_ai_log_context() or {}
        feature = ctx.get("feature") or ""
        language = ctx.get("language") or ""
        provider = pick_provider(feature, language=language)
        return feature, provider

    def _call(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        feature, provider = self._resolve_route()
        client = get_llm_client(provider)
        result = client._call(messages, temperature, max_tokens)
        if result:
            return result

        if allows_openai_fallback(feature, primary_provider=provider):
            logger.warning(
                "Local LLM failed for feature=%s — falling back to OpenAI",
                feature,
            )
            fallback = get_llm_client("openai")
            return fallback._call(
                messages,
                temperature,
                max_tokens,
                log_provider="fallback",
            )
        return ""

    def _call_json(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> dict:
        feature, provider = self._resolve_route()
        result = self._call_json_with_client(
            get_llm_client(provider),
            messages,
            temperature,
            max_tokens,
        )
        if result:
            return result

        if allows_openai_fallback(feature, primary_provider=provider):
            logger.warning(
                "Local LLM JSON failed for feature=%s — falling back to OpenAI",
                feature,
            )
            return self._call_json_with_client(
                get_llm_client("openai"),
                messages,
                temperature,
                max_tokens,
                log_provider="fallback",
            )
        return {}

    @staticmethod
    def _call_json_with_client(
        client,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        *,
        log_provider: str | None = None,
    ) -> dict:
        payload = [dict(m) for m in messages]
        payload[-1]["content"] += (
            "\n\nRespond ONLY with valid JSON. No markdown, no code blocks."
        )
        raw = client._call(
            payload,
            temperature,
            max_tokens,
            log_provider=log_provider,
        )
        if not raw:
            return {}

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [line for line in lines if not line.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from AI response: %s", raw[:200])
            return {}
