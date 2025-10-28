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
    title = models.CharField(max_length=255, unique=True, verbose_name=_("Title"))
    slug = models.SlugField(unique=True, blank=False, null=True, verbose_name=_("Slug"))

    def get_translation(self, language=None):
        lang = language or get_language()
        translation = self.translations.filter(language=lang).first()
        if not translation:
            translation = (
                self.translations.filter(language="en").first()
                or self.translations.filter().first()
            )
        return translation

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class CategoryTranslation(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
    )
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255, verbose_name=_("Title"))

    def __str__(self):
        return f"{self.category.slug} ({self.language})"


class Post(models.Model):
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
        lang = language or get_language()
        translation = self.translations.filter(language=lang).first()
        if not translation:
            translation = (
                self.translations.filter(language="en").first()
                or self.translations.filter().first()
            )
        return translation

    def save(self, *args, **kwargs):
        # Defined published_on on the first save.
        if not self.published_on:
            self.published_on = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PostTranslation(models.Model):
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
        return len(self.content.split(" ")) // 200

    def get_content_as_html(self):
        html = markdown.markdown(
            self.content, extensions=["extra", "codehilite", "fenced_code", "toc"]
        )
        return mark_safe(html)

    def __str__(self):
        return f"{self.post.slug} ({self.language})"


class Article(Post):
    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")


class CTF(models.Model):
    name = models.CharField(
        max_length=100, blank=False, null=False, verbose_name=_("Name")
    )
    date_beginning = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("CTF")
        verbose_name_plural = _("CTFs")
        ordering = ["-date_beginning"]


class Writeup(Post):
    DIFFICULTY_CHOICES = [
        ("easy", _("Easy")),
        ("medium", _("Medium")),
        ("hard", _("Hard")),
        ("insane", _("Insane")),
    ]
    ctf = models.ForeignKey(
        CTF,
        related_name="ctf",
        on_delete=models.SET_NULL,
        verbose_name=_("CTF"),
        null=True,
        blank=True,
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default="medium",
        verbose_name=_("Difficulty"),
    )
    points = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Points"),
        help_text=_("Score or point value for this challenge."),
    )
    solver_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Number of solvers"),
        help_text=_("Optional: number of people who solved it."),
    )

    def __str__(self):
        return f"{self.title} ({self.ctf.name if self.ctf else 'No CTF'})"

    class Meta:
        verbose_name = _("Writeup")
        verbose_name_plural = _("Writeups")


class Project(models.Model):
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
        return (
            (self.description[:75] + "...")
            if len(self.description) > 75
            else self.description
        )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")


class Issuer(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name=_("Name"))
    website = models.URLField(
        max_length=255, blank=True, null=True, verbose_name=_("Website")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Issuer")
        verbose_name_plural = _("Issuers")
        ordering = ("name",)

    def __str__(self):
        return self.name


class Certification(models.Model):
    name = models.CharField(
        max_length=100, blank=False, null=False, verbose_name=_("Name")
    )
    description = models.TextField()
    certification_detail_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Certification URL"),
        help_text=_("Link to the official page of the certification"),
    )
    obtained_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Obtained Date"),
        help_text=_("Date when the certification was obtained"),
    )
    picture = models.ImageField(
        upload_to="pictures/", blank=True, null=True, verbose_name=_("Picture")
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="certification",
        verbose_name=_("Related Article"),
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="certifications",
        verbose_name=_("Owner"),
    )
    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="certifications",
        verbose_name=_("Issuer"),
        help_text=_("Organization or platform that issued the certification"),
    )

    def __str__(self):
        return self.name


class CVE(models.Model):
    cve_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("cve_id"),
        help_text=_("the unique identifier for the CVE (e.g., CVE-2025-12345)"),
    )
    description = models.TextField(
        verbose_name=_("description"),
        help_text=_("a detailed description of the vulnerability"),
    )
    published_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("published_date"),
        help_text=_("date when the CVE was published"),
    )
    last_modified_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("last_modified_date"),
        help_text=_("date when the CVE was last updated"),
    )
    cvss_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name=_("cvss_score"),
        help_text=_("the severity score of the vulnerability"),
    )
    vulnerable_product = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("vulnerable_product"),
        help_text=_("the affected product(s)"),
    )
    references_url = models.URLField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name=_("references_url"),
        help_text=_("link to official references or advisories"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cve",
        verbose_name=_("Author"),
    )

    def __str__(self):
        return self.cve_id
