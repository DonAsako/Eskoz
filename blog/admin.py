import io
import zipfile

from django.contrib import admin
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .forms import PostTranslationAdminForm
from .models import (
    Article,
    Category,
    CategoryTranslation,
    PostTranslation,
    Tag,
    Writeup,
)


@admin.action(description=_("Backup selected articles"))
def backup(self, request, queryset):
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for article in queryset:
            for translation in article.translations.all():
                lang = translation.language
                title = translation.title or f"article-{article.pk}"
                filename = f"{slugify(title)}/{lang}.md"

                content = f"# {translation.title}\n\n"
                if translation.description:
                    content += f"> {translation.description}\n\n"
                content += translation.content or ""

                zip_file.writestr(filename, content)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="articles_backup.zip"'
    return response


class CategoryTranslationAdmin(admin.StackedInline):
    model = CategoryTranslation
    extra = 1
    can_delete = True

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        return 1 if not CategoryTranslation.objects.filter(category=obj).exists() else 0


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    inlines = [CategoryTranslationAdmin]


class TagAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class PostTranslationAdmin(admin.StackedInline):
    model = PostTranslation

    def reading_time(self, obj):
        reading_time = obj.get_reading_time()
        return f"{reading_time} {_("min")}"

    reading_time.short_description = _("Reading time")
    readonly_fields = ["reading_time"]
    form = PostTranslationAdminForm
    extra = 1
    can_delete = True

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        return 1 if not PostTranslation.objects.filter(article=obj).exists() else 0


class PostAdmin(admin.ModelAdmin):
    inlines = [PostTranslationAdmin]
    list_display = ("title", "published_on", "visibility")
    autocomplete_fields = ["tags", "category"]
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
        ("Visiblity", {"fields": [("visibility", "password")]}),
        ("Metadata", {"fields": ["published_on"]}),
        ("Information", {"fields": ["edited_on", "slug"]}),
    ]
    readonly_fields = ["edited_on"]
    prepopulated_fields = {"slug": ("title",)}
    actions = [backup]

    class Media:
        js = ("script/article_edit.js",)

class ArticleAdmin(PostAdmin):
    ...

class Writeupdmin(PostAdmin):
    ...


admin.site.register(Article, ArticleAdmin)
admin.site.register(Writeup, WriteupAdmin)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
