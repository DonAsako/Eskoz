from django.contrib import admin

from apps.core.admin.abstracts import (
    AbstractCategoryAdmin,
    AbstractCategoryTranslationAdmin,
    AbstractTranslatableMarkdownItemAdmin,
    AbstractTranslatableMarkdownItemTranslationAdmin,
)
from apps.core.admin.site import admin_site
from apps.core.admin.utils import visibility_badge_field

from .models import (
    Category,
    CategoryTranslation,
    Course,
    Lesson,
    LessonTranslation,
    Module,
)


class CategoryTranslationAdmin(AbstractCategoryTranslationAdmin):
    model = CategoryTranslation


class CategoryAdmin(AbstractCategoryAdmin):
    inlines = [CategoryTranslationAdmin]


class CourseAdmin(admin.ModelAdmin):
    list_display = ("category", "title")

    prepopulated_fields = {"slug": ("title",)}


class ModuleAdmin(admin.ModelAdmin):
    list_display = ("course__category", "course", "title", "order")
    prepopulated_fields = {"slug": ("title",)}


class LessonTranslationAdmin(AbstractTranslatableMarkdownItemTranslationAdmin):
    model = LessonTranslation


class LessonAdmin(AbstractTranslatableMarkdownItemAdmin):
    fieldsets = [
        (
            "Course information",
            {"fields": [("title", "module", "order"), ("slug"), ("visibility",)]},
        ),
    ]
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("module__course", "module", "title", "order", "visibility_badge")
    visibility_badge = visibility_badge_field("visibility")
    inlines = AbstractTranslatableMarkdownItemAdmin.inlines + [LessonTranslationAdmin]

    class Media:
        js = ("admin/js/visibility_toggle.js",)


admin_site.register(Course, CourseAdmin)
admin_site.register(Module, ModuleAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(Category, CategoryAdmin)
