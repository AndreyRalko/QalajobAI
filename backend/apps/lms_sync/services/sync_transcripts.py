import logging

from django.conf import settings

from apps.transcripts.models import Transcript

from .mappers import map_transcript_row
from .mysql_client import fetch_rows

logger = logging.getLogger(__name__)


def sync_transcripts_from_rows(rows):
    created = 0
    updated = 0

    for row in rows:
        mapped = map_transcript_row(row)
        if not mapped:
            continue

        lms_id, defaults = mapped
        _, was_created = Transcript.objects.update_or_create(
            lms_id=lms_id,
            defaults=defaults,
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return {
        "transcripts_created": created,
        "transcripts_updated": updated,
    }


def sync_transcripts_from_lms(connection, student_ids, *, modified_since=None):
    """
    Load transcript rows per StudentID (SELECT * FROM transcript WHERE StudentID = ?).
    Smaller queries are more stable over SSH tunnel than one large IN (...) query.
    """
    base_sql = settings.LMS_TRANSCRIPTS_SQL.strip().rstrip(";")
    created = 0
    updated = 0
    total = len(student_ids)

    for index, student_id in enumerate(student_ids, start=1):
        sql = f"{base_sql} WHERE StudentID = %s"
        params = [student_id]
        if modified_since:
            sql += " AND modified >= %s"
            params.append(modified_since)

        rows = fetch_rows(connection, sql, tuple(params))
        batch = sync_transcripts_from_rows(rows)
        created += batch["transcripts_created"]
        updated += batch["transcripts_updated"]
        logger.info(
            "Transcripts for StudentID %s: %s rows (%s/%s students)",
            student_id,
            len(rows),
            index,
            total,
        )

    return {
        "transcripts_created": created,
        "transcripts_updated": updated,
    }
