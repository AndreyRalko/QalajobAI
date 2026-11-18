from datetime import date

from django.core.management.base import BaseCommand

from apps.ai.services.seed_logs import seed_ai_action_logs


class Command(BaseCommand):
    help = (
        "Seed AI action logs from user activity visits "
        "(same dates / users, correlated timestamps)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete previously seeded AI logs in the date range first.",
        )
        parser.add_argument("--start", default="2026-09-01")
        parser.add_argument("--end", default="2026-11-18")

    def handle(self, *args, **options):
        start = date.fromisoformat(options["start"])
        end = date.fromisoformat(options["end"])
        stats = seed_ai_action_logs(
            start=start,
            end=end,
            replace=bool(options["replace"]),
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded AI logs: "
                f"scanned_activities={stats['scanned_activities']}, "
                f"created={stats['created']}, deleted={stats['deleted']}"
            )
        )
