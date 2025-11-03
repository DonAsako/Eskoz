from django.contrib import admin
from root.admin.abstracts import AbstractPostAdmin, AbstractPostTranslationAdmin
from .models import Lesson, LessonTranslation


class WriteupTranslationAdmin(AbstractPostTranslationAdmin):
    model = LessonTranslation


class LessonAdmin(AbstractPostAdmin):
    fieldsets = AbstractPostAdmin.fieldsets + [
        (
            "Course information",
            {
                "fields": [
                    ("module", "order"),
                ]
            },
        ),
    ]
    list_display = ("module", "order")
    inlines = AbstractPostAdmin.inlines + [WriteupTranslationAdmin]
