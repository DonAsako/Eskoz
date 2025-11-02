import base64
from io import BytesIO

import pyotp
import qrcode
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Page(models.Model):
    VISIBILITY_CHOICES = [
        ("public", _("Public")),
        ("private", _("Private")),
        ("referenced", _("Referenced")),
        ("index", _("Index")),
    ]
    title = models.CharField(max_length=150, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
        verbose_name=_("Visibility"),
    )

    slug = models.SlugField(unique=True, blank=False, verbose_name=_("Slug"))

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

    def clean(self):
        if self.visibility == "referenced":
            pages = Page.objects.filter(visibility="referenced")
            if self.pk:
                pages = pages.exclude(pk=self.pk)

            if pages.count() >= 4:
                raise ValidationError(
                    {
                        "visibility": _(
                            "You can only have up to 3 pages marked as 'referenced'."
                        )
                    }
                )
        if self.visibility == "index":
            pages = Page.objects.filter(visibility="index")
            if self.pk:
                pages = pages.exclude(pk=self.pk)

            if pages.count() >= 4:
                raise ValidationError(
                    {
                        "visibility": _(
                            "You can only have up to 1 page marked as 'index'."
                        )
                    }
                )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name=_("Avatar")
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
        uri = self.get_otpauth()
        img = qrcode.make(uri)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    def __str__(self):
        return f"{self.user.get_username()}"


class UserLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="links")
    name = models.CharField(max_length=100, verbose_name=_("Title"))
    url = models.URLField(verbose_name=_("URL"))
    icon = models.ImageField(
        upload_to="icons/", blank=True, null=True, verbose_name=_("Icon")
    )

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Tag(models.Model):
    """
    Represents a tag that can be associated with posts.

    Attributes:
        title (CharField): The unique name of the tag.
    """

    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """Return the title of the tag as its string representation."""
        return self.title

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
