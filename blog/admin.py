from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext_lazy as _
from .forms import ArticleTranslationAdminForm
from .models import Article, Tag, Category, ArticleTranslation


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["title"]


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

    class Media:
        js = ("script/article_edit.js",)


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
