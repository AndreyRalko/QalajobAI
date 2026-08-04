"""
Legacy helper — now uses OpenAI via openai_client.
"""

from .openai_client import get_client


def check_rate_limit(user_id: int) -> bool:
    from django.conf import settings
    from django.core.cache import cache

    key = f"ai_rate_{user_id}"
    count = cache.get(key, 0)
    limit = getattr(settings, "AI_RATE_LIMIT_PER_HOUR", 100)
    if count >= limit:
        return False
    cache.set(key, count + 1, 3600)
    return True


def openrouter_chat(messages: list[dict[str, str]], system: str = "") -> str:
    client = get_client()
    payload = ([{"role": "system", "content": system}] if system else []) + list(messages)
    return client._call(payload)
