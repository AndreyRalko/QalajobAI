"""Seed AI action logs aligned with user activity visits."""

from __future__ import annotations

import random
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from apps.ai.models import AiActionLog, AiActionLogStatus, AIFeatureType
from apps.users.identity import get_user_login
from apps.users.models import UserActivityAction, UserActivityLog, UserProfile

PATH_FEATURES = {
    "/app/student/ai/resume/": (
        AIFeatureType.RESUME_ANALYSIS,
        AIFeatureType.RESUME_ENHANCEMENT,
        AIFeatureType.RESUME_IMPORT,
        AIFeatureType.ASSISTANT,
    ),
    "/app/student/ai/jobs/": (
        AIFeatureType.VACANCY_MATCHING,
        AIFeatureType.JOB_RECOMMENDATIONS,
        AIFeatureType.HH_ADAPT,
        AIFeatureType.COVER_LETTER,
    ),
    "/app/student/jobs/": (
        AIFeatureType.VACANCY_MATCHING,
        AIFeatureType.JOB_RECOMMENDATIONS,
        AIFeatureType.COVER_LETTER,
    ),
    "/app/student/settings/": (AIFeatureType.ASSISTANT,),
    "/app/student/ai/": (
        AIFeatureType.CAREER_COACH,
        AIFeatureType.INTERVIEW_PREP,
        AIFeatureType.SKILL_GAP,
        AIFeatureType.ASSISTANT,
    ),
}

FEATURE_ENDPOINTS = {
    AIFeatureType.RESUME_ANALYSIS: "/api/v1/ai/resume/analyze/",
    AIFeatureType.RESUME_ENHANCEMENT: "/api/v1/ai/resume/enhance/",
    AIFeatureType.RESUME_IMPORT: "/api/v1/ai/resume/import/",
    AIFeatureType.VACANCY_MATCHING: "/api/v1/ai/vacancy/match/",
    AIFeatureType.JOB_RECOMMENDATIONS: "/api/v1/ai/jobs/recommend/",
    AIFeatureType.HH_ADAPT: "/api/v1/ai/hh/adapt/",
    AIFeatureType.COVER_LETTER: "/api/v1/ai/cover-letter/",
    AIFeatureType.INTERVIEW_PREP: "/api/v1/ai/interview/",
    AIFeatureType.SKILL_GAP: "/api/v1/ai/skill-gap/",
    AIFeatureType.CAREER_COACH: "/api/v1/ai/career-coach/",
    AIFeatureType.ASSISTANT: "/api/v1/ai/assistant/",
}

SAMPLE_OUTPUTS = {
    AIFeatureType.RESUME_ANALYSIS: "Сильные стороны: структура, навыки. Рекомендации: добавить метрики.",
    AIFeatureType.RESUME_ENHANCEMENT: "Резюме улучшено: усилены формулировки достижений.",
    AIFeatureType.VACANCY_MATCHING: "Совпадение с вакансией: 78%. Недостающие навыки: Docker.",
    AIFeatureType.COVER_LETTER: "Сопроводительное письмо подготовлено в профессиональном тоне.",
    AIFeatureType.INTERVIEW_PREP: "Подготовлены 8 вопросов к собеседованию и краткие ответы.",
    AIFeatureType.CAREER_COACH: "Рекомендован следующий шаг: стажировка / junior-роль.",
    AIFeatureType.JOB_RECOMMENDATIONS: "Найдено 12 релевантных вакансий на hh.kz.",
    AIFeatureType.ASSISTANT: "Ответ ассистента сформирован.",
    AIFeatureType.RESUME_IMPORT: "Резюме импортировано и разобрано.",
    AIFeatureType.HH_ADAPT: "Резюме адаптировано под выбранную вакансию.",
    AIFeatureType.SKILL_GAP: "Выявлены пробелы: SQL, коммуникация, английский.",
}


def _features_for_path(path: str) -> tuple[str, ...]:
    path = path or ""
    if path in PATH_FEATURES:
        return PATH_FEATURES[path]
    for prefix, features in PATH_FEATURES.items():
        if path.startswith(prefix.rstrip("/")):
            return features
    return (
        AIFeatureType.ASSISTANT,
        AIFeatureType.CAREER_COACH,
        AIFeatureType.RESUME_ANALYSIS,
    )


def _should_create_ai_log(path: str) -> bool:
    path = path or ""
    if "/app/student/ai/" in path:
        return random.random() < 0.82
    if path.startswith("/app/student/jobs"):
        return random.random() < 0.45
    if path.startswith("/app/student/"):
        return random.random() < 0.18
    return random.random() < 0.05


def seed_ai_action_logs(
    *,
    start: date = date(2026, 9, 1),
    end: date | None = None,
    replace: bool = False,
    tz_name: str = "Asia/Qyzylorda",
) -> dict:
    """
    Create AiActionLog rows from UserActivityLog visits so timelines match.
    """
    end = end or date(2026, 11, 18)
    tz = ZoneInfo(tz_name)

    deleted = 0
    if replace:
        deleted, _ = AiActionLog.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end,
            request_payload__seeded=True,
        ).delete()

    activities = (
        UserActivityLog.objects.filter(
            action=UserActivityAction.VISIT,
            created_at__date__gte=start,
            created_at__date__lte=end,
            user_id__isnull=False,
        )
        .select_related("user", "user__profile")
        .order_by("created_at")
    )

    student_ids = {
        p.user_id: (p.student_id or "")
        for p in UserProfile.objects.filter(
            user_id__in=activities.values_list("user_id", flat=True).distinct()
        ).only("user_id", "student_id")
    }

    batch: list[AiActionLog] = []
    created = 0
    scanned = 0

    for act in activities.iterator(chunk_size=500):
        scanned += 1
        if not _should_create_ai_log(act.path):
            continue

        feature = random.choice(_features_for_path(act.path))
        status = (
            AiActionLogStatus.SUCCESS
            if random.random() < 0.92
            else AiActionLogStatus.FAILED
        )
        delay = timedelta(seconds=random.randint(20, 900))
        created_at = act.created_at + delay
        if timezone.is_naive(created_at):
            created_at = created_at.replace(tzinfo=tz)

        login = act.user_login or get_user_login(act.user)
        batch.append(
            AiActionLog(
                user_id=act.user_id,
                student_id=student_ids.get(act.user_id) or None,
                user_login=(login or "")[:150],
                feature=feature,
                endpoint=FEATURE_ENDPOINTS.get(feature, "/api/v1/ai/")[:64],
                status=status,
                model_name=random.choice(["gpt-4o-mini", "gpt-4o-mini", "local-qwen"]),
                provider=random.choice(["openai", "openai", "local"]),
                duration_ms=random.randint(450, 8200),
                request_payload={
                    "seeded": True,
                    "from_activity_id": act.id,
                    "path": act.path,
                },
                ai_input={"messages": [{"role": "user", "content": f"Seeded {feature}"}]},
                ai_output=""
                if status == AiActionLogStatus.FAILED
                else SAMPLE_OUTPUTS.get(feature, "OK"),
                error_message="Upstream timeout" if status == AiActionLogStatus.FAILED else "",
                created_at=created_at,
            )
        )
        if len(batch) >= 400:
            with transaction.atomic():
                AiActionLog.objects.bulk_create(batch, batch_size=400)
            created += len(batch)
            batch.clear()

    if batch:
        with transaction.atomic():
            AiActionLog.objects.bulk_create(batch, batch_size=400)
        created += len(batch)

    return {
        "scanned_activities": scanned,
        "created": created,
        "deleted": deleted,
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
