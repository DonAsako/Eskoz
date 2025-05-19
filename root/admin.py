from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import (
    SiteSettings,
    WellKnownFile,
    UserProfile,
    UserLink,
    Theme,
    SeoSettings,
    Page,
)


class WellKnownFileInline(admin.TabularInline):
    model = WellKnownFile
    can_delete = True
    extra = 0
    verbose_name = _("Well-Known file")


class ThemeInline(admin.StackedInline):
    model = Theme
    can_delete = True
    extra = 0
    verbose_name = _("Theme")


class SeoSettingsInline(admin.StackedInline):
    model = SeoSettings
    can_delete = False
    extra = 0
    verbose_name = "SEO Settings"
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


class SiteSettingsAdmin(admin.ModelAdmin):
    inlines = [WellKnownFileInline, ThemeInline, SeoSettingsInline]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class PageAdmin(admin.ModelAdmin):
    model = Page
    verbose_name = _("Page")
    exclude = ["site_settings"]
    prepopulated_fields = {"slug": ("title",)}


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    can_delete = False
    verbose_name = _("Profil")


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
