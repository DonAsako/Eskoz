from django.utils.text import slugify
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.utils.translation import get_language, gettext_lazy as _
from django.conf import settings
import markdown


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


class Category(models.Model):
    """
    Represents a category for posts, which can have translations.

    Attributes:
        title (CharField): The title of the category.
        slug (SlugField): URL-friendly identifier for the category.
    """

    title = models.CharField(max_length=255, unique=True, verbose_name=_("Title"))
    slug = models.SlugField(unique=True, blank=False, null=True, verbose_name=_("Slug"))

    def get_translation(self, language=None):
        """
        Get the translation of the category for the specified language.

        If no translation exists for the given language, fallback to English
        or any available translation.

        Args:
            language (str, optional): Language code to get the translation. Defaults to None (current language).

        Returns:
            CategoryTranslation: The corresponding translation instance.
        """
        lang = language or get_language()
        translation = self.translations.filter(language=lang).first()
        if not translation:
            translation = (
                self.translations.filter(language="en").first()
                or self.translations.filter().first()
            )
        return translation

    def save(self, *args, **kwargs):
        """
        Automatically generate a slug from the title if not provided,
        then save the category instance.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the title of the category as its string representation."""
        return self.title

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class CategoryTranslation(models.Model):
    """
    Represents a translated version of a Category.

    Attributes:
        category (ForeignKey): The category being translated.
        language (CharField): Language code of the translation.
        title (CharField): Translated title.
    """

    category = models.ForeignKey(
        Category,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
    )
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255, verbose_name=_("Title"))

    def __str__(self):
        """Return the category slug and language code as the string representation."""
        return f"{self.category.slug} ({self.language})"


class Post(models.Model):
    """
    Base model representing a blog post or article.

    Attributes:
        title (CharField): The title of the post.
        slug (SlugField): URL-friendly identifier.
        author (ForeignKey): User who created the post.
        tags (ManyToManyField): Tags associated with the post.
        category (ForeignKey): Category of the post.
        published_on (DateTimeField): Date when the post was first published.
        edited_on (DateTimeField): Date when the post was last edited.
        picture (ImageField): Optional image for the post.
        visibility (CharField): Visibility of the post (public, unlisted, protected, private).
        password (CharField): Optional password for protected posts.
    """

    VISIBILITY_CHOICES = [
        ("public", _("Public")),
        ("unlisted", _("Unlisted")),
        ("protected", _("Protected")),
        ("private", _("Private")),
    ]
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(unique=True, blank=False, verbose_name=_("Slug"))
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Author"))
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
    published_on = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Published on")
    )
    edited_on = models.DateTimeField(auto_now=True, verbose_name=_("Edited on"))
    picture = models.ImageField(
        upload_to="pictures/", blank=True, null=True, verbose_name=_("Picture")
    )
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
        verbose_name=_("Visibility"),
    )
    password = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Password")
    )

    def get_translation(self, language=None):
        """
        Get the translation of the post for the specified language.

        If no translation exists for the given language, fallback to English
        or any available translation.

        Args:
            language (str, optional): Language code to get the translation. Defaults to None (current language).

        Returns:
            PostTranslation: The corresponding translation instance.
        """
        lang = language or get_language()
        translation = self.translations.filter(language=lang).first()
        if not translation:
            translation = (
                self.translations.filter(language="en").first()
                or self.translations.filter().first()
            )
        return translation

    def save(self, *args, **kwargs):
        """
        Save the post instance.

        If this is the first save and published_on is not set, automatically
        set published_on to the current time.
        """
        if not self.published_on:
            self.published_on = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        """Return the title of the post as its string representation."""
        return self.title


class PostTranslation(models.Model):
    """
    Represents a translation of a Post into a specific language.

    Attributes:
        post (ForeignKey): The post being translated.
        language (CharField): Language code of the translation.
        title (CharField): Translated title.
        description (TextField): Short description of the post content.
        content (TextField): Full post content in the specified language.
    """

    post = models.ForeignKey(
        Post,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Post"),
    )
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(
        max_length=512, blank=True, null=True, verbose_name=_("Description")
    )
    content = models.TextField(verbose_name=_("Content"))

    class Meta:
        unique_together = ("post", "language")
        verbose_name = _("Post Translation")
        verbose_name_plural = _("Post Translations")

    def get_reading_time(self):
        """
        Estimate the reading time of the post content in minutes.

        Returns:
            int: Approximate reading time based on 200 words per minute.
        """
        return len(self.content.split(" ")) // 200

    def get_content_as_html(self):
        """
        Convert the Markdown content of the post to safe HTML.

        Returns:
            str: HTML representation of the post content.
        """
        html = markdown.markdown(
            self.content, extensions=["extra", "codehilite", "fenced_code", "toc"]
        )
        return mark_safe(html)

    def __str__(self):
        """Return the post slug and language code as the string representation."""
        return f"{self.post.slug} ({self.language})"


class Article(Post):
    """
    Represents an article, which is a specialized type of Post.
    """

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
