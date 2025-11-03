from django.contrib import admin

from root.admin import (
    AbstractPostAdmin,
    AbstractPostTranslationAdmin,
    AbstractCategoryAdmin,
    AbstractCategoryTranslationAdmin,
    AbstractTagAdmin,
)

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


class CategoryTranslationAdmin(AbstractCategoryTranslationAdmin):
    model = CategoryTranslation


class CategoryAdmin(AbstractCategoryAdmin):
    inlines = [CategoryTranslationAdmin]


class TagAdmin(AbstractTagAdmin): ...


admin.site.register(Writeup, WritupAdmin)
admin.site.register(CTF, admin.ModelAdmin)
admin.site.register(Certification, admin.ModelAdmin)
admin.site.register(Issuer, admin.ModelAdmin)
admin.site.register(CVE, admin.ModelAdmin)
admin.site.register(WriteupTag, TagAdmin)
admin.site.register(Category, CategoryAdmin)
