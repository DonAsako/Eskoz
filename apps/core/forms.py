import pyotp
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.models import Page, User2FA
from apps.core.widgets import ContentEditorWidget


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}


class User2FAAdminForm(forms.ModelForm):
    otp_code = forms.CharField(
        max_length=10,
        required=False,
        label=_("OTP / Backup code"),
        help_text=_("Enter the code from your authentication app or a backup code"),
    )

    class Meta:
        model = User2FA
        fields = ["is_active"]

    def clean(self):
        cleaned_data = super().clean()
        otp_code = cleaned_data.get("otp_code")
        is_active_from_form = cleaned_data.get("is_active")

        if not self.instance.pk:
            return cleaned_data

        try:
            db_instance = User2FA.objects.get(pk=self.instance.pk)
        except User2FA.DoesNotExist:
            return cleaned_data

        was_active = db_instance.is_active
        is_enabling = is_active_from_form and not was_active
        is_disabling = not is_active_from_form and was_active

        if not (is_enabling or is_disabling):
            return cleaned_data

        if not otp_code:
            if is_enabling:
                raise forms.ValidationError(_("To enable 2FA you must enter a valid OTP code."))
            raise forms.ValidationError(_("To disable 2FA you must enter a valid OTP or backup code."))

        code = otp_code.strip().replace(" ", "").replace("-", "")
        totp = pyotp.TOTP(db_instance.secret_key)

        if is_enabling:
            if not totp.verify(code, valid_window=2):
                raise forms.ValidationError(_("OTP code is invalid."))
            return cleaned_data

        # Disabling: accept OTP or any unused backup code.
        is_valid_otp = totp.verify(code, valid_window=2)
        is_valid_backup = code.upper() in (db_instance.backup_codes or [])

        if not is_valid_otp and not is_valid_backup:
            raise forms.ValidationError(_("Invalid OTP or backup code."))

        # No need to consume the backup code here: save() wipes the full list
        # when 2FA is disabled.
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        is_active_from_form = self.cleaned_data.get("is_active")

        if instance.pk:
            try:
                db_instance = User2FA.objects.get(pk=instance.pk)
                was_active = db_instance.is_active

                # Generate backup codes when enabling 2FA
                if is_active_from_form and not was_active:
                    instance.generate_backup_codes()
                    instance.backup_codes_viewed = False

                # Regenerate secret key when disabling 2FA (fresh secret for next activation)
                if not is_active_from_form and was_active:
                    instance.secret_key = pyotp.random_base32()
                    instance.backup_codes = []
                    instance.backup_codes_viewed = False
            except User2FA.DoesNotExist:
                pass

        instance.is_active = is_active_from_form

        if commit:
            instance.save()
        return instance


class AbstractTranslatableMarkdownItemAdminForm(forms.ModelForm):
    class Meta:
        abstract = True
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}


class AbstractPostAdminForm(forms.ModelForm):
    """
    Base ModelForm for AbstractPost subclasses.

    Renders ``password`` as a PasswordInput that never re-displays the stored
    hash. If the admin submits an empty value while editing, the existing
    value in DB is preserved instead of being wiped.
    """

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        label=_("Password"),
        help_text=_("Leave empty to keep the current password."),
    )

    class Meta:
        abstract = True
        fields = "__all__"

    def clean_password(self):
        new_password = self.cleaned_data.get("password")
        if not new_password and self.instance and self.instance.pk:
            return self.instance.password
        return new_password
