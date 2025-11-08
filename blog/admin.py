from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from core.admin.site import admin_site
from core.admin import (
    AbstractPostAdmin,
    AbstractPostTranslationAdmin,
    AbstractCategoryAdmin,
    AbstractCategoryTranslationAdmin,
    AbstractTagAdmin,
)

from .models import (
    Article,
    ArticleTag,
    ArticleTranslation,
    Category,
    CategoryTranslation,
    Project,
    ProjectTag,
)


class ArticleTranslationAdmin(AbstractPostTranslationAdmin):
    model = ArticleTranslation


class ArticleAdmin(AbstractPostAdmin):
    inlines = AbstractPostAdmin.inlines + [ArticleTranslationAdmin]


class CategoryTranslationAdmin(AbstractCategoryTranslationAdmin):
    model = CategoryTranslation


class CategoryAdmin(AbstractCategoryAdmin):
    inlines = [CategoryTranslationAdmin]


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
    autocomplete_fields = ["tags"]

    def picture_thumbnail(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" width="75" height="75" style="object-fit:cover; border-radius:5px;" />',
                obj.picture.url,
            )
        return "-"

    picture_thumbnail.short_description = _("Thumbnail")


class TagAdmin(AbstractTagAdmin): ...


admin_site.register(Article, ArticleAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(ArticleTag, TagAdmin)
admin_site.register(ProjectTag, TagAdmin)
