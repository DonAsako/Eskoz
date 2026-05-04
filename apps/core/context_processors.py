from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language

from .models import SiteSettings

OG_LOCALE_MAP = {
    "fr": "fr_FR",
    "en": "en_US",
    "it": "it_IT",
}

# Languages exposed to the navbar switcher are derived from real DB content
# (any translation row counts), not from settings.LANGUAGES which now spans
# the full ~100 Django locales. Cached aggressively — invalidated by signals
# on every translation save/delete (apps/core/signals.py).
ACTIVE_LANGUAGES_CACHE_KEY = "site:active_languages"
ACTIVE_LANGUAGES_CACHE_TTL = 60 * 60  # 1h


def get_active_language_codes():
    """Return the set of language codes that have at least one translation."""
    cached = cache.get(ACTIVE_LANGUAGES_CACHE_KEY)
    if cached is not None:
        return cached

    from apps.blog.models import ArticleTranslation
    from apps.blog.models import CategoryTranslation as BlogCategoryTranslation
    from apps.education.models import CategoryTranslation as EducationCategoryTranslation
    from apps.education.models import LessonTranslation
    from apps.infosec.models import CategoryTranslation as InfosecCategoryTranslation
    from apps.infosec.models import WriteupTranslation

    codes = set()
    for model in (
        ArticleTranslation,
        WriteupTranslation,
        LessonTranslation,
        BlogCategoryTranslation,
        InfosecCategoryTranslation,
        EducationCategoryTranslation,
    ):
        codes.update(model.objects.values_list("language", flat=True).distinct())
    # Default language must always be reachable even on a brand-new install
    # with no translations yet, so the user still sees their own language.
    codes.add(settings.LANGUAGE_CODE)

    cache.set(ACTIVE_LANGUAGES_CACHE_KEY, codes, ACTIVE_LANGUAGES_CACHE_TTL)
    return codes


def site_settings(request):
    site_settings = SiteSettings.objects.first()
    return {"site_settings": site_settings}


# Single source of truth for third-party assets pulled in by theme detail
# pages (KaTeX for math, highlight.js for code). Bumping a version means
# updating both the URL and the SRI integrity hash here, in one place.
MARKDOWN_CDN = {
    "katex": {
        "version": "0.16.25",
        "css": "https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/katex.min.css",
        "css_sri": "sha384-WcoG4HRXMzYzfCgiyfrySxx90XSl2rxY5mnVY5TwtWE6KLrArNKn0T/mOgNL0Mmi",
        "js": "https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/katex.min.js",
        "js_sri": "sha384-J+9dG2KMoiR9hqcFao0IBLwxt6zpcyN68IgwzsCSkbreXUjmNVRhPFTssqdSGjwQ",
        "auto_render": "https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/contrib/auto-render.min.js",
        "auto_render_sri": "sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh",
    },
    "highlight": {
        "version": "11.11.1",
        "css_light": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/github.min.css",
        "css_dark": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/github-dark.min.css",
        "js": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js",
        "js_sri": "sha512-EBLzUL8XLl+va/zAsmXwS7Z2B1F9HUHkZwyS/VKwh3S7T/U0nF4BaU29EP/ZSf6zgiIxYAnKLu6bJ8dqpmX5uw==",
    },
}


def active_theme(request):
    return {
        "ACTIVE_THEME": settings.ACTIVE_THEME,
        "MARKDOWN_CDN": MARKDOWN_CDN,
    }


def pagination(request):
    """Expose pagination choices and the active per-page value to templates."""
    from apps.core.views import resolve_per_page

    return {
        "POSTS_PER_PAGE_CHOICES": settings.POSTS_PER_PAGE_CHOICES,
        "POSTS_PER_PAGE": resolve_per_page(request),
    }


def languages(request):
    """Expose the languages the site has actual content in for the switcher.

    Also pre-computes ``PATH_AFTER_LANG`` — the request path with its leading
    ``/<active-lang>/`` stripped — so the template can build alternate-lang
    URLs without doing fragile slicing (which would break for multi-char
    codes like ``zh-hans``).
    """
    codes = get_active_language_codes()
    label_map = dict(settings.LANGUAGES)
    site_languages = sorted(((c, str(label_map.get(c, c.upper()))) for c in codes), key=lambda x: x[0])

    active = get_language() or settings.LANGUAGE_CODE
    prefix = f"/{active}/"
    path = request.path
    path_after_lang = path[len(prefix) - 1 :] if path.startswith(prefix) else path

    return {
        "SITE_LANGUAGES": site_languages,
        "PATH_AFTER_LANG": path_after_lang,
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
