from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.core.admin.abstracts import AbstractSubModuleInline
from apps.core.admin.site import admin_site
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
            return _("No 2FA secret key set")

        uri = obj.get_otpauth_uri()
        return mark_safe(
            f"""
            <div style="padding:10px; background:white; border-radius:6px; display:flex; justify-content:center; margin-bottom:12px;">
                {obj.get_otp_qr_code()}
            </div>
            <div style="background:#1a1a1a; border:1px solid #333; border-radius:6px; padding:12px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="color:#888; font-size:12px; text-transform:uppercase;">{_("Secret Key")}</span>
                    <button type="button" style="background:#2563eb; color:white; border:none;
                            padding:4px 10px; border-radius:4px; cursor:pointer; font-size:12px;"
                            onclick="navigator.clipboard.writeText('{obj.secret_key}')
                            .then(() => this.textContent = '✓')">{_("Copy")}</button>
                </div>
                <code style="color:#e8e8e8; font-family:monospace; word-break:break-all;">{obj.secret_key}</code>
            </div>
            <div style="background:#1a1a1a; border:1px solid #333; border-radius:6px; padding:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="color:#888; font-size:12px; text-transform:uppercase;">{_("Full URI")}</span>
                    <button type="button" style="background:#2563eb; color:white; border:none;
                            padding:4px 10px; border-radius:4px; cursor:pointer; font-size:12px;"
                            onclick="navigator.clipboard.writeText('{uri}')
                            .then(() => this.textContent = '✓')">{_("Copy")}</button>
                </div>
                <code style="color:#e8e8e8; font-family:monospace; word-break:break-all; font-size:11px;">{uri}</code>
            </div>
            """
        )

    @admin.display(description=_("Backup Codes"))
    def backup_codes_display(self, obj):
        if not obj or not obj.is_active:
            return ""

        # Codes already viewed - show nothing
        if obj.backup_codes_viewed:
            return ""

        if not obj.backup_codes:
            return ""

        code_style = (
            "display:inline-block; background:#2a2a2a; padding:4px 8px; "
            "margin:3px; border-radius:4px; font-family:monospace; letter-spacing:1px;"
        )
        codes_html = "".join([f'<code style="{code_style}">{code}</code>' for code in obj.backup_codes])

        all_codes = "\\n".join(obj.backup_codes)

        # Mark as viewed after displaying
        if not obj.backup_codes_viewed:
            obj.backup_codes_viewed = True
            obj.save(update_fields=["backup_codes_viewed"])

        return mark_safe(
            f"""
            <div style="background:#1a1a1a; border:1px solid #333; border-radius:6px; padding:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="color:#888; font-size:12px; text-transform:uppercase;">
                        {_("Recovery Codes")} ({len(obj.backup_codes)} {_("remaining")})
                    </span>
                    <button type="button" style="background:#2563eb; color:white; border:none;
                            padding:4px 10px; border-radius:4px; cursor:pointer; font-size:12px;"
                            onclick="navigator.clipboard.writeText('{all_codes}')
                            .then(() => this.textContent = '✓')">{_("Copy All")}</button>
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:4px; color:#e8e8e8;">
                    {codes_html}
                </div>
                <p style="color:#dc2626; font-size:12px; margin-top:12px; margin-bottom:0; font-weight:bold;">
                    ⚠️ {_("SAVE THESE CODES NOW! They will never be shown again.")}
                </p>
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
