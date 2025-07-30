import os
import sys
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dotenv import dotenv_values


def truncate(text, max_length):
    return text if len(text) <= max_length else text[: max_length - 1] + "…"


class Command(BaseCommand):
    help = "Configure your parameters"

    def print_env(self, env_dict: dict):
        # Max width per column
        key_width = 25
        value_width = 60

        # Header
        header = f"{'Key':<{key_width}} {'Value':<{value_width}}"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))

        for key, value in env_dict.items():
            # Truncate if too long
            key = truncate(key, key_width)
            value = truncate(value, value_width)

            row = f"{key:<{key_width}} {value:<{value_width}}"
            self.stdout.write(row)

    def update_value(self, env_dict: dict, env_key: str, env_path: str):
        # Update .env
        try:
            with open(env_path, "w") as f:
                for key, value in env_dict.items():
                    f.write(f"{key}={value}\n")
                self.stdout.write(
                    self.style.SUCCESS(f"Updated '{env_key}' in .env file.")
                )
        except:
            self.stderr.write(self.style.ERROR(f"Failed to update .env: {e}"))

    def handle(self, *args, **options):
        env_path = settings.BASE_DIR / ".env"
        env_template_path = settings.BASE_DIR / ".env.example"

        if os.path.exists(settings.BASE_DIR / ".env"):
            env_dict = dotenv_values(dotenv_path=env_path)
            self.print_env(env_dict)
            while True:
                env_key = input(
                    "Select a key to update (or press Enter to leave): "
                ).strip()
                if not env_key:
                    self.stdout.write("Exiting...")
                    break
                if env_key and env_key in env_dict:
                    env_value = input(f"Enter a new value for '{env_key}' : ")
                    env_dict[env_key] = env_value
                    self.update_value(env_dict, env_key, env_path)

        else:
            self.stdout.write("Creating .env file...")
            try:
                with open(env_template_path, "r") as f:
                    data = f.read()
                    try:
                        with open(env_path, "w") as f_env:
                            f_env.write(data)
                    except:
                        self.stderr.write(
                            self.style.ERROR(f"Failed to create .env: {e}")
                        )

            except:
                self.stderr.write(self.style.ERROR(f"Failed to open .env.example: {e}"))
            self.stdout.write(self.style.SUCCESS("'.env' file created with success !"))
            env_dict = dotenv_values(dotenv_path=env_path)
            self.print_env(env_dict)
            for key, value in env_dict.items():
                env_value = ""
                while env_value == "":
                    env_value = input(
                        f"Enter a new value for '{key}' {f"(default : '{value}')" if value else ""}: "
                    )
                    if env_value or value:
                        env_dict[key] = env_value or value
                        self.update_value(env_dict, key, env_path)
                        break
