import io
import zipfile
from django.utils.text import slugify
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from .forms import ArticleTranslationAdminForm
from .models import Article, Tag, Category, ArticleTranslation, CategoryTranslation


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


class ArticleTranslationAdmin(admin.StackedInline):
    model = ArticleTranslation

    def reading_time(self, obj):
        reading_time = obj.get_reading_time()
        return f"{reading_time} {_("min")}"

    reading_time.short_description = _("Reading time")
    readonly_fields = ["reading_time"]
    form = ArticleTranslationAdminForm
    extra = 1
    can_delete = True

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        return 1 if not ArticleTranslation.objects.filter(article=obj).exists() else 0


class ArticleAdmin(admin.ModelAdmin):
    inlines = [ArticleTranslationAdmin]
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


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
