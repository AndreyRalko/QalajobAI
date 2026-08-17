from django.core.management.base import BaseCommand, CommandError

from apps.lms_sync.services.sync import run_lms_sync


class Command(BaseCommand):
    help = "Sync students and transcripts from external LMS MySQL via SSH tunnel"

    def add_arguments(self, parser):
        parser.add_argument(
            "--students-only",
            action="store_true",
            help="Sync only student accounts (FIO, login, password, StudentID)",
        )
        parser.add_argument(
            "--transcripts-only",
            action="store_true",
            help="Sync only transcript rows",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Full transcript sync (ignore last successful sync timestamp)",
        )

    def handle(self, *args, **options):
        students_only = options["students_only"]
        transcripts_only = options["transcripts_only"]
        if students_only and transcripts_only:
            raise CommandError("Use only one of --students-only or --transcripts-only")

        sync_students = not transcripts_only
        sync_transcripts = not students_only

        try:
            log, stats = run_lms_sync(
                sync_students=sync_students,
                sync_transcripts=sync_transcripts,
                incremental=not options["full"],
            )
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "LMS sync completed: "
                f"students {stats['students_created']} created, "
                f"{stats['students_updated']} updated, "
                f"{stats['students_skipped']} skipped; "
                f"transcripts {stats['transcripts_created']} created, "
                f"{stats['transcripts_updated']} updated "
                f"(log id={log.id})"
            )
        )
