from django.contrib.auth.models import User
from django.db.models.signals import post_migrate, post_save
from django.db.utils import OperationalError, ProgrammingError
from django.dispatch import receiver

from .models import SeoSettings, SiteSettings, UserProfile, ViewPageSettings


# Create SiteSettings on start
@receiver(post_migrate)
def create_site_settings(sender, **kwargs):
    try:
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(site_name="Eskoz")
    except (OperationalError, ProgrammingError):
        pass


@receiver(post_save, sender=SiteSettings)
def create_related_settings(sender, instance, **kwargs):
    SeoSettings.objects.get_or_create(site_settings=instance)
    ViewPageSettings.objects.get_or_create(site_settings=instance)


# Create UserProfile on creation of User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
