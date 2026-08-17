import logging

from django.conf import settings
from django.utils import timezone

from apps.lms_sync.models import LmsSyncLog, LmsSyncStatus
from apps.users.models import UserProfile, UserRole

from .mysql_client import fetch_rows, lms_mysql_connection
from .sync_students import sync_students_from_rows
from .sync_transcripts import sync_transcripts_from_lms

logger = logging.getLogger(__name__)


def run_lms_sync(*, sync_students=True, sync_transcripts=True, incremental=True):
    """
    Open SSH tunnel, pull data from LMS MySQL, upsert local users and transcripts.
    Tunnel is closed before returning.
    """
    if not settings.LMS_SYNC_ENABLED:
        raise RuntimeError("LMS sync is disabled. Set LMS_SYNC_ENABLED=true in .env")

    log = LmsSyncLog.objects.create(status=LmsSyncStatus.RUNNING)
    stats = {
        "students_created": 0,
        "students_updated": 0,
        "students_skipped": 0,
        "transcripts_created": 0,
        "transcripts_updated": 0,
    }

    try:
        with lms_mysql_connection() as connection:
            if sync_students:
                stats.update(_sync_students_from_lms(connection))

            if sync_transcripts:
                student_ids = _get_loaded_student_ids()
                if not student_ids:
                    logger.info("No loaded students — transcript sync skipped")
                else:
                    modified_since = _last_sync_timestamp() if incremental else None
                    stats.update(
                        sync_transcripts_from_lms(
                            connection,
                            student_ids,
                            modified_since=modified_since,
                        )
                    )

        log.status = LmsSyncStatus.SUCCESS
    except Exception as exc:
        logger.exception("LMS sync failed")
        log.status = LmsSyncStatus.FAILED
        log.error_message = str(exc)
        log.finished_at = timezone.now()
        log.save(
            update_fields=[
                "status",
                "error_message",
                "finished_at",
                *stats.keys(),
            ]
        )
        raise

    for field, value in stats.items():
        setattr(log, field, value)
    log.finished_at = timezone.now()
    log.save()

    return log, stats


def _sync_students_from_lms(connection):
    base_sql = settings.LMS_STUDENTS_SQL.strip().rstrip(";")
    page_size = settings.LMS_STUDENTS_PAGE_SIZE
    totals = {
        "students_created": 0,
        "students_updated": 0,
        "students_skipped": 0,
    }

    if page_size <= 0:
        rows = fetch_rows(connection, base_sql)
        logger.info("Fetched %s student rows from LMS", len(rows))
        return sync_students_from_rows(rows)

    offset = 0
    while True:
        sql = (
            f"SELECT * FROM ({base_sql}) AS lms_students "
            "ORDER BY student_id LIMIT %s OFFSET %s"
        )
        rows = fetch_rows(connection, sql, (page_size, offset))
        if not rows:
            break

        logger.info(
            "Fetched %s student rows from LMS (offset %s)",
            len(rows),
            offset,
        )
        batch = sync_students_from_rows(rows)
        for key in totals:
            totals[key] += batch[key]

        if len(rows) < page_size:
            break
        offset += page_size

    logger.info(
        "Student sync finished: %s created, %s updated, %s skipped",
        totals["students_created"],
        totals["students_updated"],
        totals["students_skipped"],
    )
    return totals


def _get_loaded_student_ids():
    return list(
        UserProfile.objects.filter(
            role=UserRole.STUDENT,
            student_id__isnull=False,
        )
        .exclude(student_id="")
        .values_list("student_id", flat=True)
        .distinct()
    )


def _last_sync_timestamp():
    last_success = (
        LmsSyncLog.objects.filter(status=LmsSyncStatus.SUCCESS, finished_at__isnull=False)
        .order_by("-finished_at")
        .first()
    )
    if not last_success or not last_success.finished_at:
        return None

    since = last_success.finished_at
    if timezone.is_aware(since):
        since = timezone.localtime(since)
    return since.strftime("%Y-%m-%d %H:%M:%S")
