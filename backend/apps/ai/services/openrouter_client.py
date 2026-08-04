"""
Backward-compatible re-exports. Prefer openai_client.
"""

from .openai_client import (  # noqa: F401
    OpenAIClient as OpenRouterClient,
    analyze_resume,
    analyze_skill_gap,
    assistant_chat,
    career_coach_chat,
    enhance_resume,
    generate_cover_letter,
    generate_vacancy_description,
    get_client,
    match_vacancy,
    prepare_interview,
    resume_assistant_chat,
)

from .openai_client import get_client as _get_client


def openrouter_chat(messages: list[dict[str, str]], system: str = "") -> str:
    client = _get_client()
    payload = ([{"role": "system", "content": system}] if system else []) + list(messages)
    return client._call(payload)
