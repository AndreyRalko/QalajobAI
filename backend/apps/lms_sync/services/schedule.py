import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.lms_sync.models import LmsSyncSchedule

logger = logging.getLogger(__name__)


def get_schedule_payload(schedule=None):
    schedule = schedule or LmsSyncSchedule.load()
    now = timezone.localtime()
    next_run = _next_run_at(schedule, now)
    return {
        "enabled": schedule.enabled,
        "hour": schedule.hour,
        "minute": schedule.minute,
        "time": f"{schedule.hour:02d}:{schedule.minute:02d}",
        "timezone": settings.TIME_ZONE,
        "last_scheduled_run": schedule.last_scheduled_run,
        "next_run_at": next_run,
        "updated_at": schedule.updated_at,
    }


def update_schedule(*, enabled, hour, minute):
    if hour < 0 or hour > 23:
        raise ValueError("Hour must be between 0 and 23.")
    if minute < 0 or minute > 59:
        raise ValueError("Minute must be between 0 and 59.")

    schedule = LmsSyncSchedule.load()
    schedule.enabled = bool(enabled)
    schedule.hour = hour
    schedule.minute = minute
    schedule.save(update_fields=["enabled", "hour", "minute", "updated_at"])
    return get_schedule_payload(schedule)


def _next_run_at(schedule, now):
    if not schedule.enabled:
        return None

    candidate = now.replace(
        hour=schedule.hour,
        minute=schedule.minute,
        second=0,
        microsecond=0,
    )
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def maybe_trigger_scheduled_sync():
    if not settings.LMS_SYNC_ENABLED:
        return {"triggered": False, "reason": "disabled_in_env"}

    now = timezone.localtime()
    with transaction.atomic():
        schedule = LmsSyncSchedule.objects.select_for_update().get_or_create(
            pk=1,
            defaults={
                "enabled": settings.LMS_SYNC_ENABLED,
                "hour": settings.LMS_SYNC_CRON_HOUR,
                "minute": settings.LMS_SYNC_CRON_MINUTE,
            },
        )[0]

        if not schedule.enabled:
            return {"triggered": False, "reason": "disabled_in_admin"}

        if now.hour != schedule.hour or now.minute != schedule.minute:
            return {"triggered": False, "reason": "not_scheduled_minute"}

        if schedule.last_scheduled_run:
            last = timezone.localtime(schedule.last_scheduled_run)
            if (
                last.date() == now.date()
                and last.hour == schedule.hour
                and last.minute == schedule.minute
            ):
                return {"triggered": False, "reason": "already_ran_today"}

        schedule.last_scheduled_run = now
        schedule.save(update_fields=["last_scheduled_run", "updated_at"])

    from apps.lms_sync.tasks import sync_lms_daily_task

    sync_lms_daily_task.delay()
    logger.info(
        "Scheduled LMS sync triggered for %02d:%02d (%s)",
        schedule.hour,
        schedule.minute,
        settings.TIME_ZONE,
    )
    return {"triggered": True, "scheduled_for": f"{schedule.hour:02d}:{schedule.minute:02d}"}
