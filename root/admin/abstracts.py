from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from root.admin.utils import backup
from root.forms import AbstractTranslatableMarkdownItemAdminForm
from root.models import TranslatableMarkdownItemImage


class TranslatableMarkdownImageAdmin(GenericTabularInline):
    model = TranslatableMarkdownItemImage
    extra = 1
    fields = ("picture", "image_display", "image_url")
    readonly_fields = ("image_display", "image_url")

    def image_display(self, obj):
        if obj.pk and obj.picture:
            return format_html('<img src="{}" width="75" />', obj.picture.url)
        return _("No image yet")

    image_display.short_description = "Image"

    def image_url(self, obj):
        if obj.pk and obj.picture:
            return format_html(
                '<p style="text-decoration:underline;" '
                "onclick=\"navigator.clipboard.writeText('{url}')\">"
                "{}"
                "</p>",
                obj.picture.url,
                url=obj.picture.url,
            )
        return ""

    image_url.short_description = "URL"


class AbstractTranslatableMarkdownItemTranslationAdmin(admin.StackedInline):
    abstract = True
    extra = 1
    can_delete = True
    form = AbstractTranslatableMarkdownItemAdminForm

    readonly_fields = ["reading_time"]

    def reading_time(self, obj):
        return f"{obj.get_reading_time()} {_('min')}"

    reading_time.short_description = _("Reading time")

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        return (
            1 if not self.model.objects.filter(translatable_content=obj).exists() else 0
        )


class AbstractTranslatableMarkdownItemAdmin(admin.ModelAdmin):
    """Base adnin for all AbstractTranslatableMarkdownItem-like models."""

    abstract = True
    actions = [backup]
    inlines = [TranslatableMarkdownImageAdmin]


class AbstractPostTranslationAdmin(
    AbstractTranslatableMarkdownItemTranslationAdmin
): ...


class AbstractPostAdmin(AbstractTranslatableMarkdownItemAdmin):
    """Base admin for all Post-like models."""

    abstract = True
    list_display = ("title", "published_on", "visibility")
    autocomplete_fields = ["tags", "category"]
    readonly_fields = ["edited_on"]
    prepopulated_fields = {"slug": ("title",)}
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
        js = ("admin/js/post_visibility_edit.js",)


class AbstractCategoryAdmin(admin.ModelAdmin):
    abstract = True
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug")
    search_fields = ["title"]


class AbstractCategoryTranslationAdmin(admin.StackedInline):
    abstract = True
    extra = 1
    can_delete = True

    parent_field_name = "category"

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1

        parent_field = {self.parent_field_name: obj}
        has_existing = self.model.objects.filter(**parent_field).exists()
        return 1 if not has_existing else 0


class AbstractTagAdmin(admin.ModelAdmin):
    abstract = True

    search_fields = ["title"]
