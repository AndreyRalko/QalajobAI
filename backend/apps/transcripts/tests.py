from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.transcripts.models import Transcript
from apps.transcripts.seed_data import (
    STUDENT_ID,
    TEST_STUDENT_ID,
    load_all_demo_transcripts,
    load_lms_transcript,
)
from apps.users.services.preset_users import load_preset_users


class TranscriptAPITests(TestCase):
    def setUp(self):
        load_preset_users()
        load_lms_transcript()
        self.client = APIClient()
        login = self.client.post(
            reverse("users:login"),
            {"login": "Иванов_Иван", "password": "Student123"},
        )
        token = login.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_seeded_rows(self):
        self.assertEqual(Transcript.objects.filter(student_id=STUDENT_ID).count(), 46)

    def test_list_current_student_transcript(self):
        response = self.client.get(reverse("transcripts:transcript-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 46)
        self.assertEqual(response.data["data"][0]["student_id"], STUDENT_ID)

    def test_summary(self):
        response = self.client.get(reverse("transcripts:transcript-summary"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["student_id"], STUDENT_ID)
        self.assertEqual(response.data["data"]["subjects"], 46)
        self.assertIsNotNone(response.data["data"]["gpa"])

    def test_excludes_deleted_rows(self):
        Transcript.objects.filter(student_id=STUDENT_ID).update(deleted=1)
        Transcript.objects.filter(student_id=STUDENT_ID, lms_id=1956633).update(
            deleted=0
        )

        response = self.client.get(reverse("transcripts:transcript-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["lms_id"], 1956633)

        summary = self.client.get(reverse("transcripts:transcript-summary"))
        self.assertEqual(summary.data["data"]["subjects"], 1)


class TestStudentTranscriptTests(TestCase):
    def setUp(self):
        load_preset_users()
        load_all_demo_transcripts()
        self.client = APIClient()
        login = self.client.post(
            reverse("users:login"),
            {"login": "Демо_Алина", "password": "Student123"},
        )
        token = login.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_seeded_rows(self):
        self.assertEqual(Transcript.objects.filter(student_id=TEST_STUDENT_ID).count(), 15)

    def test_list_current_student_transcript(self):
        response = self.client.get(reverse("transcripts:transcript-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 15)
        self.assertEqual(response.data["data"][0]["student_id"], TEST_STUDENT_ID)
