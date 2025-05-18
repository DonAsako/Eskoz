from django.utils.text import slugify
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
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
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("Slug"))
    content = models.TextField(verbose_name=_("Content"))
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Author"))
    tags = models.ManyToManyField(
        Tag, related_name="articles", blank=True, verbose_name=_("Tags")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
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
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug

        # Defined published_on on the first save.
        if not self.published_on:
            self.published_on = timezone.now()

        super().save(*args, **kwargs)

    def content_as_html(self):
        # Comvert markdown into html
        html = markdown.markdown(self.content, extensions=["extra"])
        return mark_safe(html)

    def get_reading_time(self):
        return len(self.content.split(" ")) // 200

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
