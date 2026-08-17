from __future__ import annotations

import contextvars
import logging
from contextlib import contextmanager
from typing import Any

from django.contrib.auth.models import AnonymousUser, User

logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 12000

_ai_log_context: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "ai_log_context",
    default=None,
)


def _truncate(value: Any, limit: int = MAX_TEXT_LENGTH) -> Any:
    if isinstance(value, str):
        if len(value) <= limit:
            return value
        return value[:limit] + f"... [truncated {len(value) - limit} chars]"
    if isinstance(value, list):
        return [_truncate(item, limit) for item in value[:50]]
    if isinstance(value, dict):
        return {key: _truncate(val, limit) for key, val in list(value.items())[:50]}
    return value


def sanitize_request_payload(payload: Any) -> dict:
    if payload is None:
        return {}
    if hasattr(payload, "dict"):
        try:
            payload = payload.dict()
        except Exception:
            payload = dict(payload)
    if not isinstance(payload, dict):
        return {"raw": _truncate(str(payload))}
    return _truncate(payload)


def get_student_id(user) -> str | None:
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return None
    profile = getattr(user, "profile", None)
    student_id = getattr(profile, "student_id", None) if profile else None
    return str(student_id).strip() if student_id else None


def bind_ai_log(*, user, feature: str, endpoint: str, request_payload: Any = None) -> None:
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return
    _ai_log_context.set(
        {
            "user": user,
            "feature": feature,
            "endpoint": endpoint,
            "request_payload": sanitize_request_payload(request_payload),
        }
    )


def clear_ai_log() -> None:
    _ai_log_context.set(None)


@contextmanager
def ai_log_binding(*, user, feature: str, endpoint: str, request_payload: Any = None):
    bind_ai_log(
        user=user,
        feature=feature,
        endpoint=endpoint,
        request_payload=request_payload,
    )
    try:
        yield
    finally:
        clear_ai_log()


def log_openai_exchange(
    *,
    messages: list[dict],
    response_text: str,
    model_name: str,
    duration_ms: int,
    status: str,
    error_message: str = "",
) -> None:
    ctx = _ai_log_context.get()
    if not ctx or not ctx.get("user"):
        return

    from apps.ai.models import AiActionLog

    user: User = ctx["user"]
    try:
        AiActionLog.objects.create(
            user=user,
            student_id=get_student_id(user),
            user_login=user.username,
            feature=ctx.get("feature") or "unknown",
            endpoint=ctx.get("endpoint") or "",
            status=status,
            model_name=model_name or "",
            duration_ms=max(duration_ms, 0),
            request_payload=ctx.get("request_payload") or {},
            ai_input={"messages": _truncate(messages)},
            ai_output=_truncate(response_text or ""),
            error_message=error_message or "",
        )
    except Exception as exc:
        logger.warning("Failed to write AiActionLog: %s", exc)
