import logging

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(name="apps.lms_sync.tasks.check_lms_sync_schedule_task")
def check_lms_sync_schedule_task():
    from apps.lms_sync.services.schedule import maybe_trigger_scheduled_sync

    result = maybe_trigger_scheduled_sync()
    if result.get("triggered"):
        logger.info("LMS sync schedule check triggered daily sync")
    return result


@shared_task(name="apps.lms_sync.tasks.sync_lms_daily_task", bind=True, max_retries=2)
def sync_lms_daily_task(self, full=False):
    if not settings.LMS_SYNC_ENABLED:
        logger.info("LMS sync skipped: LMS_SYNC_ENABLED=false")
        return {"skipped": True}

    from apps.lms_sync.services.sync import run_lms_sync

    try:
        log, stats = run_lms_sync(incremental=not full)
    except Exception as exc:
        logger.exception("Scheduled LMS sync failed")
        raise self.retry(exc=exc, countdown=300)

    return {
        "log_id": log.id,
        **stats,
    }
