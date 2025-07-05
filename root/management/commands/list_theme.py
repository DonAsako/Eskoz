import json
import os
from django.core.management.base import BaseCommand, CommandError
from root.models import Theme
from django.conf import settings


class Command(BaseCommand):
    help = "List all themes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--active",
            type=str,
            help="Filter themes by active status: true / false",
            required=False,
            default=None,
        )

    def handle(self, *args, **options):
        themes = Theme.objects.all()
        active = options.get("active")

        if active:
            active_val = active.lower()
            if active_val in ["yes", "1", "true"]:
                themes = themes.filter(is_active=True)
            elif active_val in ["no", "0", "false"]:
                themes = themes.filter(is_active=False)
            else:
                raise CommandError("Invalid value for --active. Use 'true' or 'false'.")

        self.stdout.write(
            f"{'Name'.ljust(20)}{'Slug'.ljust(10)}{'Path'.ljust(25)}{'Active'}"
        )
        for theme in themes:
            self.stdout.write(
                f"{theme.name.ljust(20)}{theme.slug.ljust(10)}{theme.path.ljust(25)}{theme.is_active}"
            )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully displayed {themes.count()} theme(s) !")
        )
