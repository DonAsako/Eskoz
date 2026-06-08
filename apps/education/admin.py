from unfold.admin import ModelAdmin, TabularInline

from apps.core.admin.abstracts import (
    AbstractCategoryAdmin,
    AbstractCategoryTranslationAdmin,
    AbstractTranslatableMarkdownItemAdmin,
    AbstractTranslatableMarkdownItemTranslationAdmin,
    PageViewsAdminMixin,
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


class ModuleInline(TabularInline):
    """Modules of a course, reorderable by drag-and-drop (the numeric order
    field is hidden behind the drag handle)."""

    model = Module
    fields = ("title", "slug", "order")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order",)
    ordering_field = "order"
    hide_ordering_field = True
    extra = 0


class LessonInline(TabularInline):
    """Lessons of a module, reorderable by drag-and-drop. Content is edited on
    the lesson's own page (it lives in translations)."""

    model = Lesson
    fields = ("title", "slug", "visibility", "order")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order",)
    ordering_field = "order"
    hide_ordering_field = True
    extra = 0


class CourseAdmin(PageViewsAdminMixin, ModelAdmin):
    list_display = ("category", "title", "views_count")
    list_select_related = ("category",)
    inlines = [ModuleInline]

    prepopulated_fields = {"slug": ("title",)}


class ModuleAdmin(PageViewsAdminMixin, ModelAdmin):
    list_display = ("course__category", "course", "title", "order", "views_count")
    list_select_related = ("course", "course__category")
    inlines = [LessonInline]
    prepopulated_fields = {"slug": ("title",)}


class LessonTranslationAdmin(AbstractTranslatableMarkdownItemTranslationAdmin):
    model = LessonTranslation


class LessonAdmin(PageViewsAdminMixin, AbstractTranslatableMarkdownItemAdmin):
    fieldsets = [
        (
            "Course information",
            {"fields": [("title", "module", "order"), ("slug"), ("visibility",)]},
        ),
    ]
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("module__course", "module", "title", "order", "views_count", "visibility_badge")
    list_select_related = ("module", "module__course")
    visibility_badge = visibility_badge_field("visibility")
    inlines = [*AbstractTranslatableMarkdownItemAdmin.inlines, LessonTranslationAdmin]

    class Media:
        js = ("admin/js/visibility_toggle.js",)


admin_site.register(Course, CourseAdmin)
admin_site.register(Module, ModuleAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(Category, CategoryAdmin)
