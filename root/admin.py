from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    SiteSettings,
    WellKnownFile,
    UserProfile,
    UserLink,
    SeoSettings,
    Page,
    ViewPageSettings,
)
from .forms import PageAdminForm, UserProfileAdminForm


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


class ViewPageSettingsInline(admin.StackedInline):
    model = ViewPageSettings
    can_delete = False
    extra = 0
    verbose_name = _("View Page Settings")


class SiteSettingsAdmin(admin.ModelAdmin):
    inlines = [WellKnownFileInline, SeoSettingsInline, ViewPageSettingsInline]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


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

    def qr_code(self, obj):
        return format_html('<img src="{}" />', obj.get_otp_qr_code())

    qr_code.short_description = "Authentication QR Code"

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


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(Page, PageAdmin)
