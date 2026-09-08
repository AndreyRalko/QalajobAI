from django.core.management.base import BaseCommand, CommandError

from apps.lms_sync.services.sync import run_lms_sync


class Command(BaseCommand):
    help = (
        "Sync student logins/passwords from LMS MySQL. "
        "Open the SSH tunnel manually first, then run this command."
    )

    def handle(self, *args, **options):
        try:
            log, stats = run_lms_sync(sync_students=True)
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "LMS sync completed: "
                f"students {stats['students_created']} created, "
                f"{stats['students_updated']} updated, "
                f"{stats['students_skipped']} skipped "
                f"(log id={log.id})"
            )
        )
