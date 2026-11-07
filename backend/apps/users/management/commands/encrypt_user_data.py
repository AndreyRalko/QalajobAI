from django.core.management.base import BaseCommand

from apps.users.services.encrypt_existing import encrypt_existing_users


class Command(BaseCommand):
    help = (
        "Encrypt existing users' login, password and FIO with SECRET_KEY (Fernet). "
        "Safe to re-run; already encrypted values are skipped."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = bool(options.get("dry_run"))
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode: no DB writes."))

        stats = encrypt_existing_users(dry_run=dry_run)

        self.stdout.write(
            self.style.SUCCESS(
                "User data encryption finished"
                + (" (dry-run)" if dry_run else "")
                + f": scanned={stats['users_scanned']}, "
                f"users_updated={stats['users_updated']}, "
                f"logins={stats['logins_encrypted']}, "
                f"passwords={stats['passwords_encrypted']}, "
                f"names={stats['names_encrypted']}, "
                f"profile_logins={stats['profiles_login_encrypted']}"
            )
        )
