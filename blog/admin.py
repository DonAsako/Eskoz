import io
import zipfile

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .forms import PostTranslationAdminForm
from .models import (
    Article,
    Category,
    CategoryTranslation,
    PostTranslation,
    Project,
    Tag,
    Writeup,
    CTF,
    CVE,
    Certification,
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
        return 1 if not PostTranslation.objects.filter(post=obj).exists() else 0


class PostAdmin(admin.ModelAdmin):
    inlines = [PostTranslationAdmin]
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
        ("Visiblity", {"fields": [("visibility", "password")]}),
        ("Metadata", {"fields": ["published_on"]}),
        ("Information", {"fields": ["edited_on", "slug"]}),
    ]

    class Media:
        js = ("script/article_edit.js",)


class ArticleAdmin(PostAdmin): ...


class WritupApdmin(PostAdmin):
    fieldsets = PostAdmin.fieldsets + [
        (
            "CTF Information",
            {
                "fields": [
                    ("ctf", "difficulty", "points", "solver_count"),
                ]
            },
        ),
    ]
    list_display = ("ctf", "difficulty", "points")


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_description",
        "source_link",
        "website",
        "picture_thumbnail",
    )
    search_fields = ("name", "description")
    list_filter = ()
    ordering = ("name",)

    def picture_thumbnail(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" width="75" height="75" style="object-fit:cover; border-radius:5px;" />',
                obj.picture.url,
            )
        return "-"

    picture_thumbnail.short_description = _("Thumbnail")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Writeup, WritupApdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(CTF, admin.ModelAdmin)
admin.site.register(Certification, admin.ModelAdmin)
admin.site.register(CVE, admin.ModelAdmin)
