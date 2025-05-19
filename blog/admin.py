import markdown
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .forms import ArticleAdminForm
from .models import Article, Tag, Category


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class TagAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class ArticleAdmin(admin.ModelAdmin):
    def reading_time(self, obj):
        reading_time = obj.get_reading_time()
        return f"{reading_time} {_("min")}"

    autocomplete_fields = ["tags", "category"]
    fieldsets = [
        (
            "General",
            {
                "fields": [
                    ("title", "description", "picture"),
                    "content",
                    ("tags", "category"),
                    "author",
                ]
            },
        ),
        ("Visiblity", {"fields": [("visibility", "password")]}),
        ("Metadata", {"fields": ["published_on"]}),
        ("Information", {"fields": ["edited_on", "slug", "reading_time"]}),
    ]
    form = ArticleAdminForm
    readonly_fields = ["reading_time", "edited_on"]
    prepopulated_fields = {"slug": ("title",)}

    reading_time.short_description = _("Reading time")

    class Media:
        js = ("script/article_edit.js", )
        css = {
            "all": ("css/article_edit.css",),
        }


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
