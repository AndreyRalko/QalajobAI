from django.core.management.base import BaseCommand

from apps.transcripts.seed_data import (
    STUDENT_ID,
    TEST_STUDENT_ID,
    load_all_demo_transcripts,
)
from apps.users.services.preset_users import load_preset_users


class Command(BaseCommand):
    help = "Load LMS transcript rows for demo students"

    def handle(self, *args, **options):
        load_preset_users()
        created, updated = load_all_demo_transcripts()
        self.stdout.write(
            self.style.SUCCESS(
                f"Transcripts loaded for {STUDENT_ID} and {TEST_STUDENT_ID}: "
                f"{created} created, {updated} updated"
            )
        )
