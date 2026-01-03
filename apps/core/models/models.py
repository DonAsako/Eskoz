import secrets

import pyotp
import qrcode
import qrcode.image.svg
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.utils import upload_to_users

from .settings import SiteSettings


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to=upload_to_users, blank=True, null=True, verbose_name=_("Avatar"))
    bio = models.TextField(blank=True, verbose_name=_("Biography"))

    def __str__(self):
        return f"{self.user.get_username()}"


class User2FA(models.Model):
    BACKUP_CODE_COUNT = 10
    BACKUP_CODE_LENGTH = 8

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="two_factor",
        verbose_name=_("User"),
    )
    is_active = models.BooleanField(verbose_name=_("Is 2FA active"), default=False)
    secret_key = models.CharField(default=pyotp.random_base32, max_length=64, verbose_name=_("OTP secret key"))
    backup_codes = models.JSONField(default=list, blank=True, verbose_name=_("Backup codes"))
    backup_codes_viewed = models.BooleanField(default=False, verbose_name=_("Backup codes viewed"))

    def get_otpauth_uri(self):
        totp = pyotp.TOTP(self.secret_key)
        return totp.provisioning_uri(
            name=self.user.get_username(),
            issuer_name=SiteSettings.objects.first().site_name,
        )

    def verify_otp(self, token):
        return pyotp.TOTP(self.secret_key).verify(token)

    def get_otp_qr_code(self):
        uri = self.get_otpauth_uri()
        qr_code_image = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage)

        return qr_code_image.to_string().decode("utf_8")

    def generate_backup_codes(self):
        """Generate new backup codes and return them."""
        codes = [secrets.token_hex(self.BACKUP_CODE_LENGTH // 2).upper() for _ in range(self.BACKUP_CODE_COUNT)]
        self.backup_codes = codes
        return codes

    def verify_backup_code(self, code):
        """Verify and consume a backup code. Returns True if valid."""
        code = code.strip().upper().replace("-", "").replace(" ", "")
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False

    def reset_secret(self):
        self.secret_key = pyotp.random_base32()
        self.backup_codes = []
        self.backup_codes_viewed = False
        self.is_active = False
        self.save()

    def __str__(self):
        return f"2FA for {self.user.username}"


class UserLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="links")
    name = models.CharField(max_length=100, verbose_name=_("Title"))
    url = models.URLField(verbose_name=_("URL"))
    icon = models.ImageField(upload_to=upload_to_users, blank=True, null=True, verbose_name=_("Icon"))

    def __str__(self):
        return f"{self.name} - {self.user.username}"
