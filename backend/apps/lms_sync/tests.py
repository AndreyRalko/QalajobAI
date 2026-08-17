from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth.models import User

from apps.transcripts.models import Transcript
from apps.users.models import UserProfile, UserRole

from .services.mappers import map_student_row, map_transcript_row
from .services.paramiko_compat import ensure_paramiko_dsskey_compat
from .services.sync_students import sync_students_from_rows
from .services.sync_transcripts import sync_transcripts_from_rows


class MapperTests(TestCase):
    def test_paramiko_compat_allows_sshtunnel_import(self):
        ensure_paramiko_dsskey_compat()
        import paramiko

        self.assertTrue(hasattr(paramiko, "DSSKey"))
        from sshtunnel import SSHTunnelForwarder  # noqa: F401

    def test_map_student_row_uses_external_login(self):
        row = {
            "StudentID": 48958,
            "lastname": "Иванов",
            "firstname": "Иван",
            "patronymic": "Иванович",
            "Login": "ivanov.student",
            "Password": "e4a6a34a2c625d52f26846f5e3d22064",
        }
        mapped = map_student_row(row)
        self.assertEqual(mapped["student_id"], "48958")
        self.assertEqual(mapped["login"], "ivanov.student")
        self.assertEqual(mapped["patronymic"], "Иванович")

    def test_map_transcript_row(self):
        row = {
            "id": 1956633,
            "StudentID": "48958",
            "code": "_HIST61108",
            "credits": 5,
            "alpha": "C+",
            "numeral": "2.33",
            "total": "72.8285714286",
            "ru": "История Казахстана",
            "deleted": 0,
        }
        lms_id, defaults = map_transcript_row(row)
        self.assertEqual(lms_id, 1956633)
        self.assertEqual(defaults["student_id"], "48958")
        self.assertEqual(defaults["subject_code"], "_HIST61108")


class SyncStudentsTests(TestCase):
    def test_sync_students_creates_user_with_external_login(self):
        rows = [
            {
                "StudentID": 77701,
                "lastname": "Тестов",
                "firstname": "Студент",
                "patronymic": "Тестович",
                "Login": "test.student77701",
                "Password": "e4a6a34a2c625d52f26846f5e3d22064",
            }
        ]
        stats = sync_students_from_rows(rows)
        self.assertEqual(stats["students_created"], 1)

        user = User.objects.get(username="test.student77701")
        self.assertTrue(user.check_password("Student123"))
        self.assertEqual(user.profile.student_id, "77701")
        self.assertEqual(user.profile.role, UserRole.STUDENT)
        self.assertEqual(user.student_profile.name, "Тестов Студент Тестович")

    def test_sync_students_skips_non_student_login(self):
        User.objects.create_user(username="employer.login", password="x")
        UserProfile.objects.create(
            user=User.objects.get(username="employer.login"),
            role=UserRole.EMPLOYER,
        )
        rows = [
            {
                "StudentID": 88801,
                "lastname": "Работод",
                "firstname": "Алекс",
                "Login": "employer.login",
                "Password": "e4a6a34a2c625d52f26846f5e3d22064",
            }
        ]
        stats = sync_students_from_rows(rows)
        self.assertEqual(stats["students_skipped"], 1)
        self.assertFalse(UserProfile.objects.filter(student_id="88801").exists())


class SyncTranscriptsTests(TestCase):
    def test_sync_transcripts_upsert(self):
        rows = [
            {
                "id": 900001,
                "StudentID": "48958",
                "code": "_TEST0001",
                "credits": 3,
                "alpha": "B",
                "deleted": 0,
            }
        ]
        stats = sync_transcripts_from_rows(rows)
        self.assertEqual(stats["transcripts_created"], 1)
        self.assertTrue(Transcript.objects.filter(lms_id=900001).exists())

        rows[0]["alpha"] = "A"
        stats = sync_transcripts_from_rows(rows)
        self.assertEqual(stats["transcripts_updated"], 1)
        self.assertEqual(
            Transcript.objects.get(lms_id=900001).alpha_mark,
            "A",
        )


class LmsSyncScheduleTests(TestCase):
    def test_update_schedule(self):
        from apps.lms_sync.services.schedule import get_schedule_payload, update_schedule

        payload = update_schedule(enabled=True, hour=3, minute=15)
        self.assertEqual(payload["hour"], 3)
        self.assertEqual(payload["minute"], 15)
        self.assertEqual(payload["time"], "03:15")
        self.assertTrue(payload["enabled"])

        current = get_schedule_payload()
        self.assertEqual(current["hour"], 3)

    def test_maybe_trigger_scheduled_sync_runs_once_per_day(self):
        from apps.lms_sync.models import LmsSyncSchedule
        from apps.lms_sync.services.schedule import maybe_trigger_scheduled_sync
        from django.utils import timezone

        now = timezone.localtime()
        LmsSyncSchedule.objects.update_or_create(
            pk=1,
            defaults={
                "enabled": True,
                "hour": now.hour,
                "minute": now.minute,
                "last_scheduled_run": None,
            },
        )

        with self.settings(LMS_SYNC_ENABLED=True):
            with patch("apps.lms_sync.tasks.sync_lms_daily_task.delay") as delay_mock:
                first = maybe_trigger_scheduled_sync()
                second = maybe_trigger_scheduled_sync()

        self.assertTrue(first["triggered"])
        self.assertFalse(second["triggered"])
        delay_mock.assert_called_once()
