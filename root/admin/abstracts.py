from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from root.admin.utils import backup
from root.forms import AbstractTranslatableMarkdownItemAdminForm
from root.models import TranslatableMarkdownItemImage


class ImagePostAdmin(GenericTabularInline):
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


class AbstractPostTranslationAdmin(admin.StackedInline):
    abstract = True
    form = AbstractTranslatableMarkdownItemAdminForm
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
    inlines = [ImagePostAdmin]
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


class AbstractCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ["title"]


class AbstractCategoryTranslationAdmin(admin.StackedInline):
    abstract = True
    extra = 1
    can_delete = True

    # Nom du champ pointant vers le parent (à redéfinir dans les sous-classes)
    parent_field_name = "category"  # valeur par défaut

    def get_extra(self, request, obj=None, **kwargs):
        """
        Ajoute dynamiquement un formulaire vide uniquement si
        aucune traduction n’existe encore pour l’objet parent.
        """
        if obj is None:
            return 1

        parent_field = {self.parent_field_name: obj}
        has_existing = self.model.objects.filter(**parent_field).exists()
        return 1 if not has_existing else 0
