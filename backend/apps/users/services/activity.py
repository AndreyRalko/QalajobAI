"""Helpers for user activity logging and historical seeding."""

from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from apps.users.identity import get_user_login
from apps.users.models import UserActivityAction, UserActivityLog

# Weighted toward AI workspace so activity aligns with AI journal usage.
DEFAULT_PATHS = (
    "/app/student/ai/resume/",
    "/app/student/ai/resume/",
    "/app/student/ai/resume/",
    "/app/student/ai/jobs/",
    "/app/student/ai/jobs/",
    "/app/student/ai/",
    "/app/student/jobs/",
    "/app/student/settings/",
    "/login/",
    "/",
)


def _client_ip(request) -> str | None:
    if not request:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_user_activity(
    *,
    user: User | None,
    action: str = UserActivityAction.VISIT,
    path: str = "",
    request=None,
    created_at=None,
    user_login: str = "",
) -> UserActivityLog:
    login = user_login or (get_user_login(user) if user else "")
    return UserActivityLog.objects.create(
        user=user,
        user_login=login[:150],
        action=action,
        path=(path or "")[:255],
        ip_address=_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "")[:500] if request else ""),
        created_at=created_at or timezone.now(),
    )


def visits_for_day(day: date, *, start: date, peak: date, peak_visits: int = 50) -> int:
    """
    Overall rising trend to peak_visits on peak day, with periodic dips
    (weekly troughs + a slower secondary wave). Mild decline after peak.
    """
    import math

    if day < start:
        return 0

    day_index = (day - start).days
    if day <= peak:
        total = (peak - start).days or 1
        progress = day_index / total
        # Base growth (ease-in)
        base = 1 + (peak_visits - 1) * (progress**1.2)
        # Weekly dip: weekends lower (Mon=0 ... Sun=6)
        weekday = day.weekday()  # 0=Mon .. 6=Sun
        weekly = 1.0 - (0.28 if weekday >= 5 else 0.08 if weekday == 0 else 0.0)
        # Secondary wave every ~9-11 days
        wave = 0.82 + 0.18 * math.sin(day_index / 9.5 * math.pi * 2)
        # Occasional sharper mid-cycle dips
        pulse = 0.72 if (day_index % 14 in (5, 6)) else 1.0
        value = base * weekly * wave * pulse
        # Keep peak day near target
        if day == peak:
            value = peak_visits
        return max(1, int(round(value)))

    after = (day - peak).days
    value = peak_visits - after * 2.2
    weekday = day.weekday()
    if weekday >= 5:
        value *= 0.75
    return max(10, int(round(value)))


def seed_user_activity(
    *,
    start: date = date(2026, 9, 1),
    peak: date = date(2026, 11, 10),
    end: date | None = None,
    peak_visits: int = 50,
    replace: bool = False,
    tz_name: str = "Asia/Qyzylorda",
) -> dict:
    """
    Insert synthetic visits from start..end with a peak of `peak_visits` on `peak`.
    """
    end = end or date(2026, 11, 18)
    tz = ZoneInfo(tz_name)
    user_ids = list(User.objects.order_by("id").values_list("id", flat=True)[:2000])
    if not user_ids:
        return {"days": 0, "created": 0, "deleted": 0}

    login_by_id = {}
    for user in User.objects.filter(id__in=user_ids).select_related("profile"):
        login_by_id[user.id] = get_user_login(user) or f"user-{user.id}"

    deleted = 0
    if replace:
        deleted, _ = UserActivityLog.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end,
            action=UserActivityAction.VISIT,
        ).delete()

    created = 0
    days = 0
    batch: list[UserActivityLog] = []

    day = start
    while day <= end:
        days += 1
        count = visits_for_day(day, start=start, peak=peak, peak_visits=peak_visits)
        chosen = random.sample(user_ids, k=min(count, len(user_ids)))
        # If need more visits than unique users, allow repeats.
        while len(chosen) < count:
            chosen.append(random.choice(user_ids))

        for user_id in chosen:
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            created_at = datetime.combine(day, time(hour, minute, second), tzinfo=tz)
            batch.append(
                UserActivityLog(
                    user_id=user_id,
                    user_login=login_by_id.get(user_id, "")[:150],
                    action=UserActivityAction.VISIT,
                    path=random.choice(DEFAULT_PATHS),
                    ip_address=f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                    user_agent="Mozilla/5.0 (seeded)",
                    created_at=created_at,
                )
            )
            if len(batch) >= 500:
                with transaction.atomic():
                    UserActivityLog.objects.bulk_create(batch, batch_size=500)
                created += len(batch)
                batch.clear()
        day += timedelta(days=1)

    if batch:
        with transaction.atomic():
            UserActivityLog.objects.bulk_create(batch, batch_size=500)
        created += len(batch)

    return {
        "days": days,
        "created": created,
        "deleted": deleted,
        "start": start.isoformat(),
        "peak": peak.isoformat(),
        "end": end.isoformat(),
        "peak_visits": peak_visits,
    }
