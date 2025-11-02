from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, verbose_name=_("Site name"))
    logo = models.ImageField(
        upload_to="logos/", blank=True, null=True, verbose_name=_("Logo")
    )
    favicon = models.ImageField(
        upload_to="favicons/", blank=True, null=True, verbose_name=_("Favicon")
    )
    contact_email = models.EmailField(blank=True, verbose_name=_("Contact mail"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    footer_credits = models.CharField(
        max_length=250,
        verbose_name=_("Footer credits"),
        default='Powered with ❤️ by <a href="https://github.com/DonAsako/eskoz">Eskoz</a>',
        null=True,
        blank=True,
    )
    under_maintenance = models.BooleanField(
        default=False, verbose_name=_("Under maintenance")
    )
    show_transition = models.BooleanField(
        default=False, verbose_name=_("Show transition between page")
    )

    def __str__(self):
        return gettext("Site settings")

    def get_page_referenced(self):
        return self.page.filter(visibility="referenced")

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

    meta_author = models.CharField(
        max_length=100, blank=True, verbose_name=_("Meta author")
    )
    meta_description = models.CharField(
        max_length=255, blank=True, verbose_name=_("Meta description")
    )
    meta_keywords = models.CharField(
        max_length=255, blank=True, verbose_name=_("Meta keywords")
    )

    google_analytics_id = models.CharField(
        max_length=20, blank=True, verbose_name=_("Google analytics id")
    )
    google_tag_manager_id = models.CharField(
        max_length=30, blank=True, verbose_name=_("Google tag manager id")
    )
    google_site_verification = models.CharField(
        max_length=255, blank=True, verbose_name=_("Google site verification")
    )

    # Open Graph
    og_title = models.CharField(
        max_length=100, blank=True, verbose_name=_("Open Graph title")
    )
    og_description = models.CharField(
        max_length=200, blank=True, verbose_name=_("Open Graph description")
    )
    og_image = models.ImageField(
        upload_to="SEO/", blank=True, null=True, verbose_name=_("Open Graph image")
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
    twitter_title = models.CharField(
        max_length=70, blank=True, verbose_name=_("Twitter title")
    )
    twitter_description = models.CharField(
        max_length=200, blank=True, verbose_name=_("Twitter description")
    )
    twitter_image = models.ImageField(
        upload_to="SEO/", blank=True, null=True, verbose_name=_("Twitter image")
    )

    def __str__(self):
        return ""


class WellKnownFile(models.Model):
    filename = models.CharField(max_length=255, verbose_name=_("Filename"))
    content = models.TextField(verbose_name=_("Content"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    site_settings = models.ForeignKey(
        SiteSettings, on_delete=models.CASCADE, related_name="well_knowns"
    )

    def __str__(self):
        return self.filename

    class Meta:
        verbose_name = _("WellKnown File")
        verbose_name_plural = _("WellKnown Files")


class ViewPageSettings(models.Model):
    site_settings = models.OneToOneField(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="view_page_settings",
        verbose_name=_("View page settings"),
    )
    activate_certifications_page = models.BooleanField(
        default=True, verbose_name=_("Show certification page")
    )
    activate_projects_page = models.BooleanField(
        default=True, verbose_name=_("Show project page")
    )
    activate_articles_page = models.BooleanField(
        default=True, verbose_name=_("Show article page")
    )
    activate_cves_page = models.BooleanField(
        default=True, verbose_name=_("Show cve page")
    )
    activate_writeups_page = models.BooleanField(
        default=True, verbose_name=_("Show writeup page")
    )
    activate_members_page = models.BooleanField(
        default=True, verbose_name=_("Show member page")
    )

    def __str__(self):
        return ""
