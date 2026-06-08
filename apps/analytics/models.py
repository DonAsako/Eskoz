from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class PageView(models.Model):
    """A single (de-duplicated) page visit.

    Recorded server-side by `PageViewMiddleware` so it is immune to ad
    blockers. No personal data is stored: `visitor_hash` is a non-reversible,
    daily-rotating hash of IP + user-agent used only to estimate unique
    visitors. When the visited page is a content object (article, writeup…),
    the generic FK links the view to it for per-object counts.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    path = models.CharField(max_length=512, db_index=True)
    visitor_hash = models.CharField(max_length=64, db_index=True)
    referrer = models.CharField(max_length=512, blank=True)
    utm_source = models.CharField(max_length=128, blank=True)
    utm_medium = models.CharField(max_length=128, blank=True)
    utm_campaign = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("Page view")
        verbose_name_plural = _("Page views")
        indexes = [
            models.Index(fields=["content_type", "object_id", "created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.path} @ {self.created_at:%Y-%m-%d %H:%M}"
