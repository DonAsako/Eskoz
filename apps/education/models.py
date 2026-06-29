from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import F, Q, Window
from django.db.models.functions import RowNumber
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models.abstracts import (
    AbstractTranslatableCategory,
    AbstractTranslatableCategoryTranslation,
    AbstractTranslatableMarkdownItem,
    AbstractTranslatableMarkdownItemTranslation,
)


class Category(AbstractTranslatableCategory): ...


class CategoryTranslation(AbstractTranslatableCategoryTranslation):
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
    slug = models.SlugField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    page_views = GenericRelation("analytics.PageView")

    def save(self, *args, **kwargs):
        if not self.category_id:
            self.category = Category.objects.get_or_create(slug="undefined", defaults={"title": "Undefined"})[0]
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the course title as its string representation"""

        return self.title

    def get_absolute_url(self):
        return reverse("education:module_list", args=[self.slug])

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")


class ModuleQuerySet(models.QuerySet):
    def with_position(self):
        """Annotate each row with its 1-based rank within its course.

        A single window-function pass computes every module's position, so
        listing modules and reading ``module.position`` costs no extra query
        per row (the property picks up the annotated value).
        """
        return self.annotate(
            _position=Window(
                expression=RowNumber(),
                partition_by=[F("course_id")],
                order_by=[F("order").asc(), F("id").asc()],
            )
        )


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
    order = models.PositiveIntegerField(default=0, db_index=True)
    slug = models.SlugField()
    page_views = GenericRelation("analytics.PageView")

    objects = ModuleQuerySet.as_manager()

    def __str__(self):
        """Return the module title as its string representation"""
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("education:lesson_list", args=[self.course.slug, self.slug])

    @property
    def position(self):
        """1-based rank within its course (ordered by ``order`` then ``id``).

        Prefers the value annotated by ``Module.objects.with_position()`` so
        listing modules triggers no per-row query; otherwise falls back to a
        single COUNT for a standalone instance.
        """
        annotated = self.__dict__.get("_position")
        if annotated is not None:
            return annotated
        if not self.pk:
            return 1
        return (
            Module.objects.filter(course_id=self.course_id)
            .filter(Q(order__lt=self.order) | Q(order=self.order, id__lte=self.id))
            .count()
        )

    class Meta:
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")


class Lesson(AbstractTranslatableMarkdownItem):
    """
    Represents an individual lesson within a module.

    Fields:
        module (ForeignKey[Module]): The module this lesson belongs to.
        title (CharField): Title of the lesson.
        content (TextField): The lesson content (text, HTML, or Markdown).
        order (PositiveIntegerField): Display order of the lesson in the module.
        visibility (CharField): Public/private gate.
    """

    VISIBILITY_CHOICES = [
        ("public", _("Public")),
        ("private", _("Private")),
    ]

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Module"),
    )
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name=_("Order"))
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
        db_index=True,
        verbose_name=_("Visibility"),
    )
    page_views = GenericRelation("analytics.PageView")

    def __str__(self):
        """Return the lesson title as its string representation"""
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("education:lesson_detail", args=[self.module.course.slug, self.module.slug, self.slug])

    class Meta(AbstractTranslatableMarkdownItem.Meta):
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        constraints = [models.UniqueConstraint(fields=["module", "slug"], name="unique_slug_per_module")]


class LessonTranslation(AbstractTranslatableMarkdownItemTranslation):
    """
    Represents a translation for a lesson.
    """

    translatable_content = models.ForeignKey(
        Lesson,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Translatable Lesson"),
    )

    class Meta(AbstractTranslatableMarkdownItemTranslation.Meta):
        verbose_name = _("Lesson Translation")
        verbose_name_plural = _("Lesson Translations")

    @property
    def parent(self):
        return self.translatable_content
