from django.core.management.base import BaseCommand

from apps.transcripts.seed_data import STUDENT_ID, load_lms_transcript
from apps.users.services.preset_users import load_preset_users


class Command(BaseCommand):
    help = "Load LMS transcript rows for the demo student"

    def handle(self, *args, **options):
        load_preset_users()
        created, updated = load_lms_transcript(STUDENT_ID)
        self.stdout.write(
            self.style.SUCCESS(
                f"Transcript loaded for StudentID {STUDENT_ID}: {created} created, {updated} updated"
            )
        )
