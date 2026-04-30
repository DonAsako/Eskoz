from django.conf import settings

from .models import SiteSettings


def site_settings(request):
    site_settings = SiteSettings.objects.first()
    return {"site_settings": site_settings}


def active_theme(request):
    return {
        "ACTIVE_THEME": settings.ACTIVE_THEME,
    }


def pagination(request):
    """Expose pagination choices and the active per-page value to templates."""
    from apps.core.views import resolve_per_page

    return {
        "POSTS_PER_PAGE_CHOICES": settings.POSTS_PER_PAGE_CHOICES,
        "POSTS_PER_PAGE": resolve_per_page(request),
    }
