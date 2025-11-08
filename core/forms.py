import pyotp
from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import Page, UserProfile
from core.widgets import ContentEditorWidget


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}


class UserProfileAdminForm(forms.ModelForm):
    otp_code = forms.CharField(
        max_length=6,
        required=False,
        label=_("OTP code"),
        help_text=_("Enter the code displayed on your authentication app"),
    )

    class Meta:
        model = UserProfile
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        otp_code = cleaned_data.get("otp_code")
        otp_secret_key = self.instance.otp_secret_key
        otp_is_active_from_form = cleaned_data.get("otp_is_active")
        if otp_is_active_from_form and not self.instance.otp_is_active:
            if not otp_code:
                raise forms.ValidationError(
                    _(
                        "To enable OTP you must scan the QR code and enter a valid OTP code."
                    )
                )
            if otp_secret_key:
                totp = pyotp.TOTP(otp_secret_key)
                if not totp.verify(otp_code, valid_window=1):
                    raise forms.ValidationError(_("OTP code is invalide."))

        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        otp_code = self.cleaned_data.get("otp_code")

        if otp_code:
            profile.otp_is_active = True

        if commit:
            profile.save()
        return profile


class AbstractTranslatableMarkdownItemAdminForm(forms.ModelForm):
    class Meta:
        abstract = True
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}
