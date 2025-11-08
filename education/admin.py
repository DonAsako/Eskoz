from django.contrib import admin
from core.admin.site import admin_site
from core.admin.abstracts import (
    AbstractTranslatableMarkdownItemAdmin,
    AbstractTranslatableMarkdownItemTranslationAdmin,
    AbstractCategoryAdmin,
    AbstractCategoryTranslationAdmin,
)
from .models import (
    Lesson,
    LessonTranslation,
    CategoryTranslation,
    Category,
    Course,
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
            {"fields": [("title", "module", "order"), ("slug")]},
        ),
    ]
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("module__course", "module", "title", "order")
    inlines = AbstractTranslatableMarkdownItemAdmin.inlines + [LessonTranslationAdmin]


admin_site.register(Course, CourseAdmin)
admin_site.register(Module, ModuleAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(Category, CategoryAdmin)
