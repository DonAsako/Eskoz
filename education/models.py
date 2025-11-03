from django.db import models
from django.utils.text import slugify
from root.models.abstracts import (
    Post,
    PostTranslation,
    TranslatableCategory,
    TranslatableCategoryTranslation,
)
from django.utils.translation import gettext_lazy as _


class Category(TranslatableCategory): ...


class CategoryTranslation(TranslatableCategoryTranslation):
    """Concrete category translation."""

    category = models.ForeignKey(
        Category,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
    )


class Course(models.Model):
    """
    Represents a full course containing multiple modules.

    Attributes:
        title (CharField): The title of the course.
        description (TextField, optional): A detailed description of the course.
        version (FloatField): Version number of the course.
        category (ForeignKey[Category], optional): The category this course belongs to.
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    version = models.FloatField(default=0.01)

    def __str__(self):
        """Return the course title as its string representation"""

        return self.title

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")


class Module(models.Model):
    """
    Represents a module within a course. A module groups multiple lessons
    and has a specific order for display.

    Fields:
        course (ForeignKey[Course]): The course this module belongs to.
        title (CharField): Title of the module.
        description (TextField, optional): Description of the module.
        order (PositiveIntegerField): Display order of the module in the course.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        """Return the module title as its string representation"""
        return f"{self.title}"

    class Meta:
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")


class Lesson(Post):
    """
    Represents an individual lesson within a module.

    Fields:
        module (ForeignKey[Module]): The module this lesson belongs to.
        title (CharField): Title of the lesson.
        content (TextField): The lesson content (text, HTML, or Markdown).
        order (PositiveIntegerField): Display order of the lesson in the module.
    """

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Module"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    def __str__(self):
        """Return the lesson title as its string representation"""
        return f"{self.title}"

    class Meta(Post.Meta):
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")


class LessonTranslation(PostTranslation):
    """
    Represents a translation for a lesson.
    """

    translatable_content = models.ForeignKey(
        Lesson,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Translatable Lesson"),
    )

    class Meta(PostTranslation.Meta):
        verbose_name = _("Lesson Translation")
        verbose_name_plural = _("Lesson Translations")

    @property
    def parent(self):
        return self.translatable_content
