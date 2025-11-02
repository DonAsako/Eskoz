from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from root.admin import AbstractPostAdmin, AbstractPostTranslationAdmin

from .models import Article, ArticleTag, ArticleTranslation, Category, Project


class TagAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class ArticleTranslationAdmin(AbstractPostTranslationAdmin):
    model = ArticleTranslation


class ArticleAdmin(AbstractPostAdmin):
    inlines = AbstractPostAdmin.inlines + [ArticleTranslationAdmin]


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    # inlines = [ArticleTranslationAdmin]


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
admin.site.register(Category, CategoryAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ArticleTag, TagAdmin)
