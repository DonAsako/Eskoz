from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.core.admin.abstracts import AbstractSubModuleInline
from apps.core.admin.site import admin_site
from apps.core.forms import PageAdminForm, UserProfileAdminForm
from apps.core.models import (
    BlogSettings,
    EducationSettings,
    InfosecSettings,
    Page,
    SeoSettings,
    SiteSettings,
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
    form = UserProfileAdminForm

    verbose_name = _("Profil")
    fieldsets = [
        (_("Description"), {"fields": ["avatar", "bio"]}),
        (_("Security"), {"fields": ["otp_is_active", "otp_code", "qr_code"]}),
    ]
    readonly_fields = ("qr_code",)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser and obj.id != request.user.id:
            new_fieldsets = []
            for title, options in fieldsets:
                fields = options.get("fields", [])
                fields = [f for f in fields if f not in ("otp_is_active", "otp_code", "qr_code")]
                new_fieldsets.append((title, {"fields": fields}))
            return new_fieldsets
        return fieldsets

    @admin.display(description=_("Authentication QR Code"))
    def qr_code(self, obj):
        return format_html(
            '<div style="border-radius:5px; background: white; display: flex; align-items:center; justify-content:center;">{}</div>',
            format_html(obj.get_otp_qr_code()),
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
    inlines = [UserProfileInline, UserLinkInline]

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
