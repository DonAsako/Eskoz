"""Emergency lockout escape: disable 2FA for a user from the host shell.

Usage:
    python manage.py disable_2fa <username>

Use when a staff member has lost their authenticator AND has no remaining
backup codes. Run this on the production host (SSH access required), then
the user can log in with just their password and re-enroll a fresh device
from their profile.
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from apps.core.models import User2FA


class Command(BaseCommand):
    help = "Disable 2FA for a user (emergency lockout escape)."

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **options):
        username = options["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"No user named {username!r}") from exc

        try:
            tfa = user.two_factor
        except User2FA.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"{username} has no 2FA configured — nothing to do."))
            return

        if not tfa.is_active:
            self.stdout.write(self.style.WARNING(f"2FA already inactive for {username}."))
            return

        # reset_secret() flips is_active off, regenerates the secret, and
        # wipes backup codes so the next enrolment starts from a clean slate.
        tfa.reset_secret()
        self.stdout.write(self.style.SUCCESS(f"2FA disabled and secret rotated for {username}."))
