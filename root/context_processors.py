from .models import SiteSettings
from django.conf import settings


def site_settings(request):
    site_settings = SiteSettings.objects.first()
    return {"site_settings": site_settings}


def active_theme(request):
    return {
        "ACTIVE_THEME": settings.ACTIVE_THEME,
    }
