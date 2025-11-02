from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Represents a category for courses

    Attributes:
        name (CharField): The name of the category.
        description (TextField, optional): Detailed description of the category.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        """Return the category name as its string representation"""

        return self.name

    def save(self, *args, **kwargs):
        """
        Automatically generate a slug from the title if not provided,
        then save the category instance.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


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

class Lesson(models.Model):
    """
    Represents an individual lesson within a module.

    Fields:
        module (ForeignKey[Module]): The module this lesson belongs to.
        title (CharField): Title of the lesson.
        content (TextField): The lesson content (text, HTML, or Markdown).
        order (PositiveIntegerField): Display order of the lesson in the module.
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        """Return the lesson title as its string representation"""
        return f"{self.title}"
