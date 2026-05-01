from django.conf import settings
from django.utils.translation import get_language

from .models import SiteSettings

OG_LOCALE_MAP = {
    "fr": "fr_FR",
    "en": "en_US",
    "it": "it_IT",
}


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


def seo(request):
    """
    Expose SEO helpers: og:locale derivation and the canonical URL for the
    current request (current path with UI-only params like ``per_page``
    stripped, but ``page`` preserved).
    """
    lang = (get_language() or "en").split("-")[0]
    og_locale = OG_LOCALE_MAP.get(lang, "en_US")
    og_locale_alternates = [v for k, v in OG_LOCALE_MAP.items() if k != lang]

    canonical_path = request.path
    page_param = request.GET.get("page")
    if page_param and page_param != "1":
        canonical_path = f"{canonical_path}?page={page_param}"
    canonical_url = request.build_absolute_uri(canonical_path)

    return {
        "OG_LOCALE": og_locale,
        "OG_LOCALE_ALTERNATES": og_locale_alternates,
        "CANONICAL_URL": canonical_url,
    }
