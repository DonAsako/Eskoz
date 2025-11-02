import markdown
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from root.models.abstracts import Post, TranslatableCategory


class Category(TranslatableCategory): ...


class Tag(models.Model):
    """
    Represents a tag that can be associated with posts.

    Attributes:
        title (CharField): The unique name of the tag.
    """

    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """Return the title of the tag as its string representation."""
        return self.title

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Article(Post):
    """
    Represents an article, which is a specialized type of Post.
    """

    tags = models.ManyToManyField(
        Tag, related_name="posts", blank=True, verbose_name=_("Tags")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="category",
        verbose_name=_("Category"),
    )

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")


class Project(models.Model):
    """
    Represents a project associated with articles.

    Attributes:
        name (CharField): Name of the project.
        description (TextField): Description of the project.
        source_link (URLField): URL to the project's source code repository.
        website (URLField): URL to the project website.
        picture (ImageField): Optional image representing the project.
        maintainer (ForeignKey): User responsible for maintaining the project.
        article (ForeignKey): Related article describing the project.
        date_beginning (DateField): Project start date.
        date_end (DateField): Project end date.
    """

    name = models.CharField(
        max_length=100, blank=False, null=False, verbose_name=_("Name")
    )
    description = models.TextField()
    source_link = models.URLField(max_length=200, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    picture = models.ImageField(
        upload_to="pictures/", blank=True, null=True, verbose_name=_("Picture")
    )
    maintainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name=_("Maintainer"),
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="project",
        verbose_name=_("Related Article"),
    )
    date_beginning = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)

    def short_description(self):
        """
        Return a shortened version of the project description.

        Returns:
            str: First 75 characters of the description followed by "..." if truncated.
        """
        return (
            (self.description[:75] + "...")
            if len(self.description) > 75
            else self.description
        )

    def __str__(self):
        """Return the name of the project as its string representation."""
        return f"{self.name}"

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
