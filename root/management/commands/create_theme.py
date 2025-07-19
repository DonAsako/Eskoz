import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a new theme in the /themes directory."

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            type=str,
            help="Name of the new theme",
        )

    def handle(self, *args, **options):
        theme_name = options["name"]
        themes_dir = settings.BASE_DIR / "themes"
        if not os.path.isdir(themes_dir):
            raise CommandError(f"There is no themes directory in {themes_dir}.")

        existing_themes = [
            name for name in os.listdir(themes_dir) if (themes_dir / name).is_dir()
        ]

        if theme_name in existing_themes:
            raise CommandError(
                f"There is already a theme named '{theme_name}' existing !"
            )

        new_theme_path = themes_dir / theme_name
        paths = [
            new_theme_path / "templates" / theme_name / "root" / "index.html",
            new_theme_path / "templates" / theme_name / "root" / "page.html",
            new_theme_path / "templates" / theme_name / "blog" / "article_detail.html",
            new_theme_path
            / "templates"
            / theme_name
            / "blog"
            / "article_password.html",
            new_theme_path / "templates" / theme_name / "blog" / "article_list.html",
            new_theme_path / "templates" / theme_name / "400.html",
            new_theme_path / "templates" / theme_name / "403.html",
            new_theme_path / "templates" / theme_name / "404.html",
            new_theme_path / "templates" / theme_name / "500.html",
            new_theme_path / "static" / theme_name / "css" / "style.css",
            new_theme_path / "static" / theme_name / "js",
        ]
        for path in paths:
            if path.suffix:  # C'est un fichier (ex: .html, .css)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch(exist_ok=True)
            else:  # C'est un dossier
                path.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.SUCCESS(f"'{theme_name}' created with success !"))
