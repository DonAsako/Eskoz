from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.blog.models import Article
from apps.core.models.abstracts import (
    AbstractPost,
    AbstractPostTranslation,
    AbstractTag,
    AbstractTranslatableCategory,
    AbstractTranslatableCategoryTranslation,
)
from apps.core.utils import upload_to_certifications


class Issuer(models.Model):
    """
    Represents the issuer of a certification in the system.

    Attributes:
        name (CharField): Name of the issuer.
        website (URLField): Url's of the website of the issuer.
        description (URLField): Detailed description of the issuer.
    """

    name = models.CharField(max_length=150, unique=True, verbose_name=_("Name"))
    website = models.URLField(
        max_length=255, blank=True, null=True, verbose_name=_("Website")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Issuer")
        verbose_name_plural = _("Issuers")
        ordering = ("name",)

    def __str__(self) -> str:
        """Return the issuer name as its string representation"""
        return self.name


class Certification(models.Model):
    """
    Represents a certification in the system.

    Attributes:
        name (CharField): Name of the certification.
        description (TextField): Detailed description of the certification.
        certification_detail_url (URLField): Link to the official page of the certification.
        obtained_date (DateField): Date when the certification was obtained.
        picture (ImageField): Image or logo of the certification.
        article (ForeignKey): Optional related blog article.
        owner (ForeignKey): The user who holds the certification.
        issuer (ForeignKey): Organization or platform that issued the certification.
    """

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
        upload_to=upload_to_certifications,
        blank=True,
        null=True,
        verbose_name=_("Picture"),
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
        """Return the certification name as its string representation"""
        return self.name


class CVE(models.Model):
    """
    Represents a Common Vulnerabilities and Exposures (CVE) entry.

    Attributes:
        cve_id (CharField): Unique identifier for the CVE (e.g., CVE-2025-12345).
        description (TextField): Detailed description of the vulnerability.
        published_date (DateField): Date when the CVE was first published.
        last_modified_date (DateField): Date when the CVE was last updated.
        cvss_score (DecimalField): Severity score of the vulnerability (CVSS).
        vulnerable_product (CharField): The affected product(s).
        references_url (URLField): Link to official references or advisories.
        author (ForeignKey): User who submitted or authored the CVE entry.
    """

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
        """Return the cve id as its string representation"""
        return self.cve_id


class CTF(models.Model):
    """
    Represents a Capture The Flag (CTF) event.

    Attributes:
        name (CharField): Name of the CTF.
        date_beginning (DateTimeField): Start date and time of the CTF.
        date_end (DateTimeField): End date and time of the CTF.
    """

    name = models.CharField(
        max_length=100, blank=False, null=False, verbose_name=_("Name")
    )
    date_beginning = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        """Return the CTF name as its string representation."""
        return self.name

    class Meta:
        verbose_name = _("CTF")
        verbose_name_plural = _("CTFs")
        ordering = ["-date_beginning"]


class Category(AbstractTranslatableCategory): ...


class CategoryTranslation(AbstractTranslatableCategoryTranslation):
    """Concrete category translation."""

    category = models.ForeignKey(
        Category,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
    )


class WriteupTag(AbstractTag): ...


class Writeup(AbstractPost):
    """
    Represents a writeup for a CTF challenge.

    Attributes:
        ctf (ForeignKey): The CTF event this writeup belongs to (optional).
        difficulty (CharField): Difficulty level of the challenge; choices are easy, medium, hard, insane.
        points (PositiveIntegerField): Score or point value assigned to this challenge.
        solver_count (PositiveIntegerField): Number of users who have solved this challenge (optional).
    """

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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writeups",
        verbose_name=_("Category"),
    )
    tags = models.ManyToManyField(
        WriteupTag, related_name="posts", blank=True, verbose_name=_("Tags")
    )

    def save(self, *args, **kwargs):
        if not self.category_id:
            self.category = Category.objects.get(slug="undefined")
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the title of the writeup and its associated CTF name."""
        return f"{self.title} ({self.ctf.name if self.ctf else 'No CTF'})"

    class Meta(AbstractPostTranslation.Meta):
        verbose_name = _("Writeup")
        verbose_name_plural = _("Writeups")


class WriteupTranslation(AbstractPostTranslation):
    """
    Represents a translation for an Writeup.
    """

    translatable_content = models.ForeignKey(
        Writeup,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Translatable Writeup"),
    )

    class Meta(AbstractPostTranslation.Meta):
        verbose_name = _("Writeup Translation")
        verbose_name_plural = _("Writeup Translations")

    @property
    def parent(self):
        return self.translatable_content
