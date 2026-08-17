from django.core.management.base import BaseCommand

from apps.users.services.preset_users import load_preset_users


class Command(BaseCommand):
    help = "Load preloaded accounts with MD5 passwords"

    def handle(self, *args, **options):
        created, updated = load_preset_users()
        self.stdout.write(
            self.style.SUCCESS(f"Preset users loaded: {created} created, {updated} updated")
        )
