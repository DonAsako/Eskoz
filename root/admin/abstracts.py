from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from root.admin.utils import backup
from root.forms import PostTranslationAdminForm


class AbstractPostTranslationAdmin(admin.StackedInline):
    abstract = True
    form = PostTranslationAdminForm
    readonly_fields = ["reading_time"]
    extra = 1
    can_delete = True

    def reading_time(self, obj):
        return f"{obj.get_reading_time()} {_('min')}"

    reading_time.short_description = _("Reading time")

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        return (
            1 if not self.model.objects.filter(translatable_content=obj).exists() else 0
        )


class AbstractPostAdmin(admin.ModelAdmin):
    """Base admin for all Post-like models."""

    list_display = ("title", "published_on", "visibility")
    autocomplete_fields = ["tags", "category"]
    readonly_fields = ["edited_on"]
    prepopulated_fields = {"slug": ("title",)}
    actions = [backup]

    fieldsets = [
        (
            "General",
            {
                "fields": [
                    ("title", "picture"),
                    ("tags", "category"),
                    "author",
                ]
            },
        ),
        ("Visibility", {"fields": [("visibility", "password")]}),
        ("Metadata", {"fields": ["published_on"]}),
        ("Information", {"fields": ["edited_on", "slug"]}),
    ]

    class Media:
        js = ("script/article_edit.js",)
