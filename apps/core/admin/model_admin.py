from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from django_ratelimit.core import is_ratelimited
from django_ratelimit.exceptions import Ratelimited

from apps.core.admin.abstracts import AbstractSubModuleInline
from apps.core.admin.site import admin_site
from apps.core.admin.utils import visibility_badge_field
from apps.core.forms import PageAdminForm, User2FAAdminForm
from apps.core.models import (
    BlogSettings,
    EducationSettings,
    InfosecSettings,
    Page,
    SeoSettings,
    SiteSettings,
    User2FA,
    UserLink,
    UserProfile,
    WellKnownFile,
)


class WellKnownFileInline(admin.TabularInline):
    model = WellKnownFile
    can_delete = True
    extra = 0
    verbose_name = _("Well-Known file")


class SeoSettingsInline(admin.StackedInline):
    model = SeoSettings
    can_delete = False
    extra = 0
    verbose_name = _("SEO Settings")
    fieldsets = [
        ("Meta", {"fields": ["meta_author", "meta_description", "meta_keywords"]}),
        (
            "Google",
            {
                "fields": [
                    "google_analytics_id",
                    "google_tag_manager_id",
                    "google_site_verification",
                ]
            },
        ),
        ("Open Graph", {"fields": ["og_title", "og_description", "og_image"]}),
        (
            "Twitter",
            {
                "fields": [
                    "twitter_card_type",
                    "twitter_title",
                    "twitter_description",
                    "twitter_image",
                ]
            },
        ),
    ]


class EducationSettingsInline(AbstractSubModuleInline):
    model = EducationSettings
    verbose_name = _("Education Settings")


class InfosecSettingsInline(AbstractSubModuleInline):
    model = InfosecSettings
    verbose_name = _("Infosec Settings")


class BlogSettingsInline(AbstractSubModuleInline):
    model = BlogSettings
    verbose_name = _("Blog Settings")


class SiteSettingsAdmin(admin.ModelAdmin):
    inlines = [
        WellKnownFileInline,
        SeoSettingsInline,
        EducationSettingsInline,
        InfosecSettingsInline,
        BlogSettingsInline,
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.objects.first()
        if obj:
            url = reverse("admin:core_sitesettings_change", args=[obj.pk])
            return redirect(url)
        return super().changelist_view(request, extra_context)

    class Media:
        js = ("admin/js/settings_admin.js",)


class PageAdmin(admin.ModelAdmin):
    model = Page
    verbose_name = _("Page")
    exclude = ["site_settings"]
    form = PageAdminForm
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug", "visibility_badge")
    visibility_badge = visibility_badge_field("visibility")

    class Media:
        js = ("admin/js/visibility_toggle.js",)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _("Profil")
    fieldsets = [
        (_("Description"), {"fields": ["avatar", "bio"]}),
    ]


class User2FAInline(admin.StackedInline):
    model = User2FA
    can_delete = False
    verbose_name = _("Two Factor Authentication")
    form = User2FAAdminForm
    fieldsets = [
        (_("Security"), {"fields": ["is_active", "otp_code", "qr_code", "backup_codes_display"]}),
    ]
    readonly_fields = ("qr_code", "backup_codes_display")

    @admin.display(description=_("Authentication QR Code"))
    def qr_code(self, obj):
        if not obj or not obj.secret_key:
            return mark_safe(f'<p class="tfa-empty">{_("No 2FA secret key set yet.")}</p>')

        uri = obj.get_otpauth_uri()
        copy_label = _("Copy")
        return mark_safe(
            f"""
            <div class="tfa-grid">
                <div class="tfa-qr">{obj.get_otp_qr_code()}</div>
                <div class="tfa-copy-stack">
                    <div class="tfa-copy">
                        <span class="tfa-copy__label">{_("Secret key")}</span>
                        <code class="tfa-copy__value">{obj.secret_key}</code>
                        <button type="button" class="tfa-copy__btn"
                                data-clipboard-text="{obj.secret_key}"
                                data-copy-label="{copy_label}">{copy_label}</button>
                    </div>
                    <div class="tfa-copy">
                        <span class="tfa-copy__label">{_("Provisioning URI")}</span>
                        <code class="tfa-copy__value tfa-copy__value--small">{uri}</code>
                        <button type="button" class="tfa-copy__btn"
                                data-clipboard-text="{uri}"
                                data-copy-label="{copy_label}">{copy_label}</button>
                    </div>
                </div>
            </div>
            """
        )

    @admin.display(description=_("Backup Codes"))
    def backup_codes_display(self, obj):
        if not obj or not obj.is_active:
            return ""

        if obj.backup_codes_viewed:
            return mark_safe(
                f'<p class="tfa-empty">{_("Backup codes have already been displayed once. Disable then re-enable 2FA to regenerate them.")}</p>'
            )

        if not obj.backup_codes:
            return ""

        codes_html = "".join([f'<code class="tfa-backup__code">{code}</code>' for code in obj.backup_codes])
        all_codes = "\\n".join(obj.backup_codes)
        copy_label = _("Copy all")

        # Mark as viewed after displaying
        if not obj.backup_codes_viewed:
            obj.backup_codes_viewed = True
            obj.save(update_fields=["backup_codes_viewed"])

        return mark_safe(
            f"""
            <div class="tfa-backup">
                <div class="tfa-backup__head">
                    <span class="tfa-copy__label">{_("Recovery codes")} <span class="tfa-backup__count">{len(obj.backup_codes)}</span></span>
                    <button type="button" class="tfa-copy__btn"
                            data-clipboard-text="{all_codes}"
                            data-copy-label="{copy_label}">{copy_label}</button>
                </div>
                <div class="tfa-backup__grid">{codes_html}</div>
                <p class="tfa-backup__warn">{_("Save these codes now. They will not be shown again.")}</p>
            </div>
            """
        )

    class Media:
        js = ("admin/js/user_profil_edit.js",)


class UserLinkInline(admin.TabularInline):
    model = UserLink
    extra = 1
    can_delete = True
    verbose_name = _("External link")
    verbose_name_plural = _("External links")


class UserAdmin(BaseUserAdmin):
    inlines = [User2FAInline, UserProfileInline, UserLinkInline]

    list_display = ("username", "email", "is_staff")

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Rate-limit OTP/backup-code submissions narrowly so a session-hijack
        # attacker cannot brute-force the 6-digit code to disable 2FA.
        # Targets only POSTs that actually carry an otp_code value, so other
        # admin saves on the same user are unaffected.
        if request.method == "POST" and any(k.endswith("otp_code") and v.strip() for k, v in request.POST.items()):
            limited = is_ratelimited(
                request,
                group="user2fa-otp",
                key="ip",
                rate=settings.RATELIMIT_2FA_IP,
                method="POST",
                increment=True,
            )
            if limited:
                raise Ratelimited()
        return super().change_view(request, object_id, form_url, extra_context)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if request.user.is_superuser:
            return True
        return obj.id == request.user.id

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        if request.user.is_superuser:
            return True
        return obj.id == request.user.id

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if request.user.is_superuser:
            return fieldsets

        new_fieldsets = []
        for title, options in fieldsets:
            if title == _("Permissions"):
                continue

            fields = options.get("fields", ())

            if obj.id != request.user.id:
                fields = tuple(f for f in fields if f != "password")

            fields = tuple(f for f in fields if f not in ("user_permissions",))

            new_fieldsets.append((title, {"fields": fields}))

        return new_fieldsets


class GroupAdmin(BaseGroupAdmin): ...


admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(SiteSettings, SiteSettingsAdmin)
admin_site.register(Page, PageAdmin)
