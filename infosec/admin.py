from django.contrib import admin

from root.admin import (
    AbstractCategoryAdmin,
    AbstractCategoryTranslationAdmin,
    AbstractPostAdmin,
    AbstractPostTranslationAdmin,
    AbstractTagAdmin,
)
from root.admin.site import admin_site

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


admin_site.register(Writeup, WritupAdmin)
admin_site.register(CTF, admin.ModelAdmin)
admin_site.register(Certification, admin.ModelAdmin)
admin_site.register(Issuer, admin.ModelAdmin)
admin_site.register(CVE, admin.ModelAdmin)
admin_site.register(WriteupTag, TagAdmin)
admin_site.register(Category, CategoryAdmin)
