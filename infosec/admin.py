from django.contrib import admin

from root.admin import AbstractPostAdmin, AbstractPostTranslationAdmin

from .models import (
    CTF,
    CVE,
    Category,
    CategoryTranslation,
    Certification,
    Issuer,
    Writeup,
    WriteupTag,
    WriteupTranslation,
)


class WriteupTranslationAdmin(AbstractPostTranslationAdmin):
    model = WriteupTranslation


class WritupAdmin(AbstractPostAdmin):
    fieldsets = AbstractPostAdmin.fieldsets + [
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
    inlines = AbstractPostAdmin.inlines + [WriteupTranslationAdmin]


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


admin.site.register(Writeup, WritupAdmin)
admin.site.register(CTF, admin.ModelAdmin)
admin.site.register(Certification, admin.ModelAdmin)
admin.site.register(Issuer, admin.ModelAdmin)
admin.site.register(CVE, admin.ModelAdmin)
admin.site.register(WriteupTag, TagAdmin)
admin.site.register(Category, CategoryAdmin)
