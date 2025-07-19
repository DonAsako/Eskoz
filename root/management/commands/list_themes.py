import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def truncate(text, max_length):
    return text if len(text) <= max_length else text[: max_length - 1] + "…"


class Command(BaseCommand):
    help = "List all available themes in the /themes directory."

    def handle(self, *args, **options):
        themes_dir = settings.BASE_DIR / "themes"

        if not os.path.isdir(themes_dir):
            raise CommandError(f"There is no 'themes' directory at {themes_dir}")

        active_theme = getattr(settings, "ACTIVE_THEME", None)

        existing_themes = sorted(
            [name for name in os.listdir(themes_dir) if (themes_dir / name).is_dir()]
        )

        if not existing_themes:
            self.stdout.write("No themes found.")
            return

        # Max width per column
        name_width = 25
        path_width = 60
        active_width = 6

        # Header
        header = (
            f"{'Name':<{name_width}} {'Path':<{path_width}} {'Active':<{active_width}}"
        )
        self.stdout.write(header)
        self.stdout.write("-" * len(header))

        for theme in existing_themes:
            theme_path = str(themes_dir / theme)
            is_active = "Yes" if theme == active_theme else "No"

            # Truncate if too long
            theme_name = truncate(theme, name_width)
            theme_path = truncate(theme_path, path_width)

            row = f"{theme_name:<{name_width}} {theme_path:<{path_width}} {is_active:<{active_width}}"
            self.stdout.write(row)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully listed {len(existing_themes)} theme(s).")
        )
