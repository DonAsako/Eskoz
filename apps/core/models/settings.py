from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from apps.core.utils import get_content_as_html, upload_to_settings


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, verbose_name=_("Site name"))
    logo = models.ImageField(upload_to=upload_to_settings, blank=True, null=True, verbose_name=_("Logo"))
    favicon = models.ImageField(upload_to=upload_to_settings, blank=True, null=True, verbose_name=_("Favicon"))
    contact_email = models.EmailField(blank=True, verbose_name=_("Contact mail"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    footer_credits = models.TextField(
        verbose_name=_("Footer credits"),
        default='Powered with ❤️ by <a href="https://github.com/DonAsako/eskoz">Eskoz</a>',
        null=True,
        blank=True,
    )
    under_maintenance = models.BooleanField(default=False, verbose_name=_("Under maintenance"))
    show_transition = models.BooleanField(default=False, verbose_name=_("Show transition between page"))

    def __str__(self):
        return gettext("Site settings")

    def get_page_referenced(self):
        return self.pages.filter(visibility="referenced")

    def save(self, *args, **kwargs):
        if not self.footer_credits:
            self.footer_credits = 'Powered with ❤️ by <a href="https://github.com/DonAsako/eskoz">Eskoz</a>'

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = verbose_name_plural = _("Site settings")


class SeoSettings(models.Model):
    site_settings = models.OneToOneField(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="seo_settings",
        verbose_name=_("SEO settings"),
    )

    meta_author = models.CharField(max_length=100, blank=True, verbose_name=_("Meta author"))
    meta_description = models.CharField(max_length=255, blank=True, verbose_name=_("Meta description"))
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name=_("Meta keywords"))

    google_analytics_id = models.CharField(max_length=20, blank=True, verbose_name=_("Google analytics id"))
    google_tag_manager_id = models.CharField(max_length=30, blank=True, verbose_name=_("Google tag manager id"))
    google_site_verification = models.CharField(max_length=255, blank=True, verbose_name=_("Google site verification"))

    # Open Graph
    og_title = models.CharField(max_length=100, blank=True, verbose_name=_("Open Graph title"))
    og_description = models.CharField(max_length=200, blank=True, verbose_name=_("Open Graph description"))
    og_image = models.ImageField(
        upload_to=upload_to_settings,
        blank=True,
        null=True,
        verbose_name=_("Open Graph image"),
    )

    # Twitter
    twitter_card_type = models.CharField(
        max_length=20,
        choices=[
            ("summary", _("Summary")),
            ("summary_large_image", _("Summary Large Image")),
        ],
        default="summary",
        blank=True,
        verbose_name=_("Twitter card type"),
    )
    twitter_title = models.CharField(max_length=70, blank=True, verbose_name=_("Twitter title"))
    twitter_description = models.CharField(max_length=200, blank=True, verbose_name=_("Twitter description"))
    twitter_image = models.ImageField(
        upload_to=upload_to_settings,
        blank=True,
        null=True,
        verbose_name=_("Twitter image"),
    )

    def __str__(self):
        return ""


class WellKnownFile(models.Model):
    filename = models.CharField(max_length=255, verbose_name=_("Filename"))
    content = models.TextField(verbose_name=_("Content"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    site_settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, related_name="well_knowns")

    def __str__(self):
        return self.filename

    class Meta:
        verbose_name = _("WellKnown File")
        verbose_name_plural = _("WellKnown Files")


class BlogSettings(models.Model):
    site_settings = models.OneToOneField(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="blog",
        verbose_name=_("Blog settings"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Activate Blog Module"))
    activate_members_view = models.BooleanField(default=False, verbose_name=_("Show members page"))
    activate_projects_page = models.BooleanField(default=True, verbose_name=_("Show projects page"))
    activate_articles_page = models.BooleanField(default=True, verbose_name=_("Show articles page"))

    def __str__(self):
        return gettext("Active") if self.is_active else ""


class InfosecSettings(models.Model):
    site_settings = models.OneToOneField(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="infosec",
        verbose_name=_("Infosec settings"),
    )
    is_active = models.BooleanField(default=False, verbose_name=_("Activate Infosec Module"))
    activate_certifications_page = models.BooleanField(default=True, verbose_name=_("Show certifications page"))

    activate_cves_page = models.BooleanField(default=True, verbose_name=_("Show CVEs page"))
    activate_writeups_page = models.BooleanField(default=True, verbose_name=_("Show writeups page"))

    def __str__(self):
        return gettext("Active") if self.is_active else ""


class EducationSettings(models.Model):
    site_settings = models.OneToOneField(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="education",
        verbose_name=_("Education settings"),
    )
    is_active = models.BooleanField(default=False, verbose_name=_("Activate Education Module"))
    activate_courses_page = models.BooleanField(default=False, verbose_name=_("Show courses page"))

    def __str__(self):
        return gettext("Active") if self.is_active else ""


class Page(models.Model):
    VISIBILITY_CHOICES = [
        ("public", _("Public")),
        ("private", _("Private")),
        ("referenced", _("Referenced")),
        ("index", _("Index")),
    ]
    title = models.CharField(max_length=150, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
        verbose_name=_("Visibility"),
    )
    site_settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, related_name="pages", null=True)

    slug = models.SlugField(unique=True, blank=False, verbose_name=_("Slug"))

    def save(self, *args, **kwargs):
        if not self.site_settings:
            self.site_settings = SiteSettings.objects.first()

        self.full_clean()

        super().save(*args, **kwargs)

    def get_content_as_html(self):
        return get_content_as_html(self.content)

    def clean(self):
        if self.visibility == "referenced":
            pages = Page.objects.filter(visibility="referenced")
            if self.pk:
                pages = pages.exclude(pk=self.pk)

            if pages.count() >= 4:
                raise ValidationError({"visibility": _("You can only have up to 3 pages marked as 'referenced'.")})
        if self.visibility == "index":
            pages = Page.objects.filter(visibility="index")
            if self.pk:
                pages = pages.exclude(pk=self.pk)

            if pages.count() >= 4:
                raise ValidationError({"visibility": _("You can only have up to 1 page marked as 'index'.")})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
