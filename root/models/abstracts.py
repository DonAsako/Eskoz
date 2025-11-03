import markdown
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import checks
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from root.utils import upload_to_posts, upload_to_settings


class AbstractTranslatableCategory(models.Model):
    """
    Abstract base model for categories that can have translations.

    Attributes:
        title (CharField): The title of the category.
        slug (SlugField): URL-friendly identifier for the category. Must be unique per concrete model.

    Methods:
        get_translation(language=None): Returns the translation for the given language,
                                       falling back to English or any available translation.
        save(*args, **kwargs): Automatically generates a slug from the title if not provided.
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
        abstract = True
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class AbstractTranslatableCategoryTranslation(models.Model):
    """
    Return the translation of the category for the specified language.

    If no translation exists for the given language, fallback to English
    or any available translation.

    Args:
        language (str, optional): Language code to get the translation.
                                    Defaults to current active language.

    Returns:
        Model instance: The corresponding translation instance.
    """

    category = models.ForeignKey(
        AbstractTranslatableCategory,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
    )
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255, verbose_name=_("Title"))

    def __str__(self):
        """Return the category slug and language code as the string representation."""
        return f"{self.category.slug} ({self.language})"

    class Meta:
        unique_together = ("category", "language")
        abstract = True
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")


class AbstractTranslatableMarkdownItem(models.Model):
    """
    Base model representing a translatable markdown item.

    Attributes:
        title (CharField): The title of the translatable markdown item.
        slug (SlugField): URL-friendly identifier.
    """

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(unique=True, blank=False, verbose_name=_("Slug"))

    def get_translation(self, language=None):
        """
        Get the translation of the Item for the specified language.

        If no translation exists for the given language, fallback to English
        or any available translation.

        Args:
            language (str, optional): Language code to get the translation. Defaults to None (current language).

        Returns:
            TranslatableMarkdownItemTranslation: The corresponding translation instance.
        """
        lang = language or get_language()
        translation = self.translations.filter(language=lang).first()
        if not translation:
            translation = (
                self.translations.filter(language="en").first()
                or self.translations.filter().first()
            )
        return translation

    def __str__(self):
        """Return the title of the translatable markdown item as its string representation."""
        return self.title

    class Meta:
        abstract = True
        verbose_name = _("Translatable Markdown Item")
        verbose_name_plural = _("Translatable Markdown Items")


class AbstractTranslatableMarkdownItemTranslation(models.Model):
    """
    Represents a translation of a translatable markdown item into a specific language.

    Attributes:
        translatable_content (ForeignKey): The TranslatableMarkdownItem being translated.
        language (CharField): Language code of the translation.
        title (CharField): Translated title.
        description (TextField): Short description of the translatable markdown item content.
        content (TextField): Full translatable markdown item content in the specified language.
    """

    translatable_content = models.ForeignKey(
        AbstractTranslatableMarkdownItem,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Translatable Content"),
    )
    language = models.CharField(
        max_length=10, choices=settings.LANGUAGES, verbose_name=_("Language")
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(
        max_length=512, blank=True, null=True, verbose_name=_("Description")
    )
    content = models.TextField(verbose_name=_("Content"))

    def get_reading_time(self):
        """
        Estimate the reading time of the TranslatableMarkdownItem content in minutes.

        Returns:
            int: Approximate reading time based on 200 words per minute.
        """
        return len(self.content.split(" ")) // 200

    def get_content_as_html(self):
        """
        Convert the Markdown content of the translatable markdown item to safe HTML.

        Returns:
            str: HTML representation of the post content.
        """
        html = markdown.markdown(
            self.content,
            extensions=[
                "extra",
                "codehilite",
                "fenced_code",
                "toc",
                "pymdownx.arithmatex",
            ],
            extension_configs={
                "pymdownx.arithmatex": {
                    "generic": True,
                }
            },
        )
        return mark_safe(html)

    def __str__(self):
        """Return the TranslatableMarkdownItem slug and language code as the string representation."""
        return f"{self.translatable_content.slug} ({self.language})"

    class Meta:
        unique_together = ("translatable_content", "language")
        abstract = True
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")


class AbstractPost(AbstractTranslatableMarkdownItem):
    """
    Base model representing a post.

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
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Author"))
    published_on = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Published on")
    )
    edited_on = models.DateTimeField(auto_now=True, verbose_name=_("Edited on"))
    picture = models.ImageField(
        upload_to=upload_to_posts, blank=True, null=True, verbose_name=_("Picture")
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

    class Meta:
        abstract = True
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        if not cls._meta.abstract and not any(
            f.name == "category" for f in cls._meta.local_fields
        ):
            errors.append(
                checks.Error(
                    "'category' field is required.",
                    obj=cls,
                    id="post.E001",
                )
            )
        return errors


class AbstractPostTranslation(AbstractTranslatableMarkdownItemTranslation):
    """
    Abstract base class for Post translations.

    Subclasses must define a concrete ForeignKey to their Post subclass.
    """

    class Meta:
        abstract = True
        verbose_name = _("Post Translation")
        verbose_name_plural = _("Post Translations")

    @property
    def parent(self):
        """
        Returns the parent post (must be implemented by subclass if ForeignKey name differs).
        """
        raise NotImplementedError(
            "Each subclass of AbstractPostTranslation must define a ForeignKey to its Post model."
        )


class AbstractTag(models.Model):
    """
    Base model representing tag that can be associated with an element.

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
        abstract = True


class TranslatableMarkdownItemImage(models.Model):
    """
    Model representing additional images for a post.
    Each Post can have multiple images.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    picture = models.ImageField(upload_to=upload_to_settings, verbose_name=_("Picture"))
    uploaded_on = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded on"))

    class Meta:
        verbose_name = _("Markdown Image")
        verbose_name_plural = _("Markdown Images")
        ordering = ["uploaded_on"]

    def __str__(self):
        title = getattr(self.content_object, "title", "Objet")
        return f"{title} -  {self.uploaded_on}"
