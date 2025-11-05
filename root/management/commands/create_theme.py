import os
import re
import shutil

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
        parser.add_argument(
            "base_theme",
            type=str,
            nargs="?",
            default=None,
            help="Copy from an existing theme",
        )

    def handle(self, *args, **options):
        theme_name = options["name"]
        base_theme_name = options["base_theme"]
        themes_dir = settings.BASE_DIR / "themes"
        if not os.path.isdir(themes_dir):
            raise CommandError(f"There is no themes directory in {themes_dir}.")

        if not re.fullmatch(r"^[A-Za-z_]+$", theme_name):
            raise CommandError(
                "Invalid theme name. Use only letters (A-Z, a-z) and underscores (_)."
            )

        existing_themes = [
            name for name in os.listdir(themes_dir) if (themes_dir / name).is_dir()
        ]

        if theme_name in existing_themes:
            raise CommandError(
                f"There is already a theme named '{theme_name}' existing !"
            )

        new_theme_path = themes_dir / theme_name
        if base_theme_name:
            base_theme_path = themes_dir / base_theme_name
            if not base_theme_path.exists() or not base_theme_path.is_dir():
                raise CommandError(f"Base theme '{base_theme_name}' does not exist.")

            shutil.copytree(base_theme_path, new_theme_path)

            # Rename themes/THEME/static/THEME
            old_static_path = new_theme_path / "static" / base_theme_name
            new_static_path = new_theme_path / "static" / theme_name
            if old_static_path.exists():
                old_static_path.rename(new_static_path)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Theme '{theme_name}' created by copying '{base_theme_name}'!"
                )
            )
        else:
            path_template = new_theme_path / "templates"
            path_static = new_theme_path / "static" / theme_name
            # List of files to create
            paths = [
                path_template / "root" / "index.html",
                path_template / "root" / "page.html",
                path_template / "blog" / "article_detail.html",
                path_template / "blog" / "article_list.html",
                path_template / "blog" / "article_password.html",
                path_template / "blog" / "members.html",
                path_template / "blog" / "project_list.html",
                path_template / "education" / "course_list.html",
                path_template / "education" / "lesson_detail.html",
                path_template / "education" / "lesson_list.html",
                path_template / "education" / "module_list.html",
                path_template / "infosec" / "certification_list.html",
                path_template / "infosec" / "cve_list.html",
                path_template / "infosec" / "writeup_detail.html",
                path_template / "infosec" / "writeup_list.html",
                path_template / "infosec" / "writeup_password.html",
                path_template / "400.html",
                path_template / "403.html",
                path_template / "403_csrf.html",
                path_template / "404.html",
                path_template / "500.html",
                path_static / "css" / "style.css",
                path_static / "js" / "script.js",
            ]
            for path in paths:
                if path.suffix:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch(exist_ok=True)
                else:
                    path.mkdir(parents=True, exist_ok=True)

            self.stdout.write(
                self.style.SUCCESS(f"Theme '{theme_name}' created with success !")
            )
