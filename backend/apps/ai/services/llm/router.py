"""
Route AI features to local (Qwen) or OpenAI providers.
"""

from __future__ import annotations

from django.conf import settings

LOCAL_FEATURES = frozenset(
    {
        "assistant",
        "resume_enhancement",
    }
)

OPENAI_FEATURES = frozenset(
    {
        "job_recommendations",
        "skill_gap",
        "vacancy_matching",
    }
)

HYBRID_FEATURES = frozenset(
    {
        "resume_analysis",
        "cover_letter",
        "interview_prep",
        "career_coach",
        "resume_import",
        "hh_adapt_resume",
    }
)


def _normalize_feature(feature: str) -> str:
    return str(feature or "").strip().lower()


def _is_kazakh(language: str) -> bool:
    raw = str(language or "").strip().lower().replace("_", "-")
    short = raw.split("-")[0]
    return short in ("kk", "kz", "kaz")


def pick_provider(feature: str, *, language: str = "") -> str:
    """
    Return 'local' or 'openai'.
    Hybrid features prefer local unless Kazakh routing sends them to OpenAI.
    """
    if not getattr(settings, "LLM_HYBRID_ENABLED", False):
        return "openai"

    name = _normalize_feature(feature)

    if name in OPENAI_FEATURES:
        return "openai"
    if name in LOCAL_FEATURES:
        return "local"
    if name in HYBRID_FEATURES:
        if getattr(settings, "LLM_KK_USE_OPENAI", True) and _is_kazakh(language):
            return "openai"
        return "local"

    default = getattr(settings, "LLM_DEFAULT_PROVIDER", "local") or "local"
    return default if default in ("local", "openai") else "local"


def allows_openai_fallback(feature: str, *, primary_provider: str) -> bool:
    if primary_provider != "local":
        return False
    if not getattr(settings, "LLM_FALLBACK_TO_OPENAI", True):
        return False
    name = _normalize_feature(feature)
    if name in OPENAI_FEATURES:
        return False
    return True
