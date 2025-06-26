from django.utils.text import slugify
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.utils.translation import get_language, gettext_lazy as _
from django.conf import settings
import markdown


class Tag(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Article(models.Model):
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
        Tag, related_name="articles", blank=True, verbose_name=_("Tags")
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

    def save(self, *args, **kwargs):
        # Defined published_on on the first save.
        if not self.published_on:
            self.published_on = timezone.now()

        super().save(*args, **kwargs)

    def get_translation(self, language=None):
        lang = language or get_language()
        translation = self.translations.filter(language=lang).first()
        if not translation:
            translation = (
                self.translations.filter(language="en").first()
                or self.translations.filter().first()
            )
        return translation

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")


class ArticleTranslation(models.Model):
    LANGUAGE_CHOICES = settings.LANGUAGES
    article = models.ForeignKey(
        Article,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Article"),
    )
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(
        max_length=512, blank=True, null=True, verbose_name=_("Description")
    )
    content = models.TextField(verbose_name=_("Content"))

    class Meta:
        unique_together = ("article", "language")
        verbose_name = _("Article Translation")
        verbose_name_plural = _("Article Translations")

    def get_reading_time(self):
        return len(self.content.split(" ")) // 200

    def get_content_as_html(self):
        html = markdown.markdown(
            self.content, extensions=["extra", "codehilite", "fenced_code", "toc"]
        )
        return mark_safe(html)

    def __str__(self):
        return f"{self.article.slug} ({self.language})"
