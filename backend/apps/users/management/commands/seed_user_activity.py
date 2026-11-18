from datetime import date

from django.core.management.base import BaseCommand

from apps.users.services.activity import seed_user_activity, visits_for_day


class Command(BaseCommand):
    help = (
        "Seed user activity visits from 2026-09-01 rising to a peak of 50/day "
        "on 2026-11-10."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete existing seeded visits in the date range before insert.",
        )
        parser.add_argument("--peak-visits", type=int, default=50)
        parser.add_argument("--start", default="2026-09-01")
        parser.add_argument("--peak", default="2026-11-10")
        parser.add_argument("--end", default="2026-11-18")

    def handle(self, *args, **options):
        start = date.fromisoformat(options["start"])
        peak = date.fromisoformat(options["peak"])
        end = date.fromisoformat(options["end"])
        peak_visits = int(options["peak_visits"])

        preview = visits_for_day(peak, start=start, peak=peak, peak_visits=peak_visits)
        self.stdout.write(
            f"Seeding visits {start} .. {end}, peak {peak} = {preview}/day"
        )

        stats = seed_user_activity(
            start=start,
            peak=peak,
            end=end,
            peak_visits=peak_visits,
            replace=bool(options["replace"]),
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded user activity: "
                f"days={stats['days']}, created={stats['created']}, "
                f"deleted={stats['deleted']}"
            )
        )

        from apps.ai.services.seed_logs import seed_ai_action_logs

        ai_stats = seed_ai_action_logs(
            start=start,
            end=end,
            replace=bool(options["replace"]),
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded AI logs from activity: "
                f"created={ai_stats['created']}, deleted={ai_stats['deleted']}"
            )
        )
