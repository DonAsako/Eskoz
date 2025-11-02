from django.contrib import admin

from blog.admin import PostAdmin

from .models import (
    CTF,
    CVE,
    Certification,
    Issuer,
    Writeup,
)


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


admin.site.register(Writeup, WritupApdmin)
admin.site.register(CTF, admin.ModelAdmin)
admin.site.register(Certification, admin.ModelAdmin)
admin.site.register(Issuer, admin.ModelAdmin)
admin.site.register(CVE, admin.ModelAdmin)
