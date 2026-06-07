from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _
from unfold.admin import GenericTabularInline, ModelAdmin, StackedInline

from apps.core.admin.utils import backup, visibility_badge_field
from apps.core.forms import AbstractPostAdminForm, AbstractTranslatableMarkdownItemAdminForm
from apps.core.models import TranslatableMarkdownItemImage


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
                '<p style="text-decoration:underline;" onclick="navigator.clipboard.writeText(\'{url}\')">{}</p>',
                obj.picture.url,
                url=obj.picture.url,
            )
        return ""

    image_url.short_description = "URL"


class AbstractTranslatableMarkdownItemTranslationAdmin(StackedInline):
    abstract = True
    extra = 1
    can_delete = True
    form = AbstractTranslatableMarkdownItemAdminForm

    readonly_fields = ["reading_time"]

    class Media:
        js = ("admin/js/translation_tabs.js",)

    def reading_time(self, obj):
        return f"{obj.get_reading_time()} {_('min')}"

    reading_time.short_description = _("Reading time")

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        return 1 if not self.model.objects.filter(translatable_content=obj).exists() else 0


class AbstractTranslatableMarkdownItemAdmin(ModelAdmin):
    """Base admin for all AbstractTranslatableMarkdownItem-like models."""

    abstract = True
    actions = [backup]
    inlines = [TranslatableMarkdownImageAdmin]


class AbstractPostTranslationAdmin(AbstractTranslatableMarkdownItemTranslationAdmin): ...


class AuthorsAdminMixin:
    """Shared author handling for any admin whose model has an ``authors``
    M2M: a multi-select widget, an authors changelist column (prefetched),
    plus auto-filling the creating editor so a freshly created object is
    never left author-less."""

    filter_horizontal = ("authors",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("authors")

    @admin.display(description=_("Authors"))
    def authors_list(self, obj):
        names = [a.get_full_name() or a.get_username() for a in obj.authors.all()]
        return ", ".join(names) if names else "—"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not change and not form.instance.authors.exists():
            form.instance.authors.add(request.user)


class AbstractPostAdmin(AuthorsAdminMixin, AbstractTranslatableMarkdownItemAdmin):
    """Base admin for all Post-like models."""

    abstract = True
    warn_unsaved_form = True
    change_form_show_cancel_button = True
    form = AbstractPostAdminForm
    list_display = ("title", "authors_list", "languages_list", "views_count", "published_on", "visibility_badge")
    list_filter = ("visibility", "category", "authors", "published_on")
    date_hierarchy = "published_on"
    visibility_badge = visibility_badge_field("visibility")
    filter_horizontal = (*AuthorsAdminMixin.filter_horizontal, "tags")
    autocomplete_fields_excluded_from_warnings = ["tags", "category"]
    readonly_fields = ["edited_on"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("translations").annotate(_views=Count("page_views"))

    @admin.display(description=_("Views"), ordering="_views")
    def views_count(self, obj):
        return obj._views

    @admin.display(description=_("Languages"))
    def languages_list(self, obj):
        codes = sorted({t.language.upper() for t in obj.translations.all()})
        if not codes:
            return format_html('<span style="opacity:.5">—</span>')
        return format_html_join(
            "",
            '<span class="status-badge status-badge--index" style="margin:0 2px">{}</span>',
            ((c,) for c in codes),
        )

    prepopulated_fields = {"slug": ("title",)}
    fieldsets = [
        (
            "General",
            {
                "fields": [
                    ("title", "picture"),
                    "category",
                    "tags",
                    "authors",
                ]
            },
        ),
        ("Visibility", {"fields": [("visibility", "password")]}),
        ("Metadata", {"fields": ["published_on"]}),
        ("Information", {"fields": ["edited_on", "slug"]}),
    ]

    class Media:
        js = (
            "admin/js/post_visibility_edit.js",
            "admin/js/visibility_toggle.js",
        )


class AbstractCategoryAdmin(ModelAdmin):
    abstract = True
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug")
    search_fields = ["title"]

    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
        except ValidationError as e:
            self.message_user(
                request,
                f"Cannot delete category '{obj}': {e.messages[0]}",
                level=messages.ERROR,
            )

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            try:
                obj.delete()
            except ValidationError as e:
                self.message_user(
                    request,
                    f"Cannot delete category '{obj}': {e.messages[0]}",
                    level=messages.ERROR,
                )


class AbstractCategoryTranslationAdmin(StackedInline):
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


class AbstractTagAdmin(ModelAdmin):
    abstract = True

    search_fields = ["title"]


class AbstractSubModuleInline(StackedInline):
    abstract = True
    can_delete = False
    extra = 0
