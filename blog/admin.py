from django.contrib import admin
from django import forms
from .models import Article, Tag
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
import markdown


class TagAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class ArticleAdmin(admin.ModelAdmin):
    def reading_time(self, obj):
        reading_time = obj.get_reading_time()
        return f"{reading_time} {_("min")}"

    def preview(self, obj):
        if not obj.content:
            return ""
        html = markdown.markdown(obj.content, extensions=["extra"])
        return mark_safe(f"<div class='preview'>{html}</div>")

    autocomplete_fields = ["tags"]
    fieldsets = [
        (
            "General",
            {"fields": ["title", ("content", "preview"), "picture", "tags", "author"]},
        ),
        ("Visiblity", {"fields": [("visibility", "password")]}),
        ("Metadata", {"fields": ["published_on"]}),
        ("Information", {"fields": ["edited_on", "slug", "reading_time"]}),
    ]
    readonly_fields = ["reading_time", "edited_on", "preview"]
    prepopulated_fields = {"slug": ("title",)}

    reading_time.short_description = _("Reading time")
    preview.short_description = _("Markdown preview")

    class Media:
        js = ("script/article_edit.js",)
        css = {
            "all": ("css/article_edit.css",),
        }


admin.site.register(Article, ArticleAdmin)
admin.site.register(Tag, TagAdmin)
