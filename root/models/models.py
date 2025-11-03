import pyotp
import qrcode
import qrcode.image.svg
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from root.utils import upload_to_users


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to=upload_to_users, blank=True, null=True, verbose_name=_("Avatar")
    )
    bio = models.TextField(blank=True, verbose_name=_("Biography"))
    otp_is_active = models.BooleanField(verbose_name=_("Is 2FA active"), default=False)
    otp_secret_key = models.CharField(
        default=pyotp.random_base32, max_length=64, verbose_name=_("OTP secret key")
    )

    def get_otpauth(self):
        return pyotp.totp.TOTP(self.otp_secret_key).provisioning_uri(
            name=self.user.get_username(), issuer_name="Eskoz"
        )

    def verify_otp(self, token):
        return pyotp.TOTP(self.otp_secret_key).verify(token)

    def get_otp_qr_code(self):
        qrcode_uri = self.get_otpauth()
        qr_code_image_factory = qrcode.image.svg.SvgPathImage
        qr_code_image = qrcode.make(qrcode_uri, image_factory=qr_code_image_factory)
        return qr_code_image.to_string().decode("utf_8")

    def __str__(self):
        return f"{self.user.get_username()}"


class UserLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="links")
    name = models.CharField(max_length=100, verbose_name=_("Title"))
    url = models.URLField(verbose_name=_("URL"))
    icon = models.ImageField(
        upload_to=upload_to_users, blank=True, null=True, verbose_name=_("Icon")
    )

    def __str__(self):
        return f"{self.name} - {self.user.username}"
