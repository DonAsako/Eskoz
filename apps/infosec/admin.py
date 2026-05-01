from django.contrib import admin

from apps.core.admin import (
    AbstractCategoryAdmin,
    AbstractCategoryTranslationAdmin,
    AbstractPostAdmin,
    AbstractPostTranslationAdmin,
    AbstractTagAdmin,
)
from apps.core.admin.site import admin_site
from apps.core.admin.utils import visibility_badge_field

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
    list_display = ("ctf", "difficulty", "points", "visibility_badge")
    inlines = AbstractPostAdmin.inlines + [WriteupTranslationAdmin]


class CategoryTranslationAdmin(AbstractCategoryTranslationAdmin):
    model = CategoryTranslation


class CategoryAdmin(AbstractCategoryAdmin):
    inlines = [CategoryTranslationAdmin]


class TagAdmin(AbstractTagAdmin): ...


class CVEAdmin(admin.ModelAdmin):
    list_display = ("cve_id", "cvss_score", "published_date", "visibility_badge")
    visibility_badge = visibility_badge_field("visibility")
    search_fields = ("cve_id", "vulnerable_product")

    class Media:
        js = ("admin/js/visibility_toggle.js",)


admin_site.register(Writeup, WritupAdmin)
admin_site.register(CTF, admin.ModelAdmin)
admin_site.register(Certification, admin.ModelAdmin)
admin_site.register(Issuer, admin.ModelAdmin)
admin_site.register(CVE, CVEAdmin)
admin_site.register(WriteupTag, TagAdmin)
admin_site.register(Category, CategoryAdmin)
