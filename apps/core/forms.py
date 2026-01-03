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

        if is_enabling or is_disabling:
            if not otp_code:
                if is_enabling:
                    raise forms.ValidationError(_("To enable 2FA you must enter a valid OTP code."))
                else:
                    raise forms.ValidationError(_("To disable 2FA you must enter a valid OTP or backup code."))

            code = otp_code.strip().replace(" ", "").replace("-", "")

            # For enabling: only accept OTP codes
            if is_enabling:
                totp = pyotp.TOTP(db_instance.secret_key)
                if not totp.verify(code, valid_window=2):
                    raise forms.ValidationError(_("OTP code is invalid."))

            # For disabling: accept OTP or backup code
            if is_disabling:
                totp = pyotp.TOTP(db_instance.secret_key)
                is_valid_otp = totp.verify(code, valid_window=2)
                is_valid_backup = code.upper() in db_instance.backup_codes

                if not is_valid_otp and not is_valid_backup:
                    raise forms.ValidationError(_("Invalid OTP or backup code."))

                # Consume backup code if used
                if is_valid_backup and not is_valid_otp:
                    db_instance.backup_codes.remove(code.upper())
                    db_instance.save(update_fields=["backup_codes"])

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
