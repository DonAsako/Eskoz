"""Cross-app search service for translated post types.

PostgreSQL backend uses ``SearchVector + SearchQuery + SearchRank`` with the
language-specific text-search config (``french``, ``english``, ``italian``)
so stemming and stop-words match the user's content. SQLite (dev only)
falls back to ``icontains`` chains so local development doesn't require
Postgres. The dev fallback returns no rank but preserves the same shape so
templates don't branch.

Search is scoped to translations in the active language only — Google's
hreflang strategy means each language is a distinct content surface, so
mixing them in results would dilute relevance.
"""

from dataclasses import dataclass

from django.db import connection
from django.db.models import Case, Q, Value, When

from apps.blog.models import Article, ArticleTranslation
from apps.core.decorators import is_feature_active
from apps.core.models import SiteSettings
from apps.education.models import Lesson, LessonTranslation
from apps.infosec.models import Writeup, WriteupTranslation

# Map our short language codes to PostgreSQL ts_config names. Postgres ships
# with stemming for these ~16 languages out of the box; anything else falls
# back to ``simple`` (no stemming, no stop-words — exact-token match only).
# Source: SELECT cfgname FROM pg_ts_config in a stock Postgres install.
PG_TEXT_SEARCH_CONFIG = {
    "ar": "arabic",
    "ca": "catalan",
    "da": "danish",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "eu": "basque",
    "fi": "finnish",
    "fr": "french",
    "ga": "irish",
    "hi": "hindi",
    "hu": "hungarian",
    "hy": "armenian",
    "id": "indonesian",
    "it": "italian",
    "lt": "lithuanian",
    "ne": "nepali",
    "nl": "dutch",
    "no": "norwegian",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sr": "serbian",
    "sv": "swedish",
    "ta": "tamil",
    "tr": "turkish",
    "yi": "yiddish",
}

# (result key, post model, translation model, settings module, settings feature)
# The module/feature pair mirrors the ``feature_active_required`` gate on the
# matching list/detail views: if the section is switched off in Site
# Settings, its posts must not leak through search either.
POST_TYPES = (
    ("articles", Article, ArticleTranslation, "blog", "articles"),
    ("writeups", Writeup, WriteupTranslation, "infosec", "writeups"),
    ("lessons", Lesson, LessonTranslation, "education", "courses"),
)


@dataclass
class SearchHit:
    post: object  # Article | Writeup | Lesson
    translation: object  # the matched *Translation row
    rank: float  # 0.0 on SQLite fallback


def search_posts(query: str, language: str) -> dict[str, list[SearchHit]]:
    """Return matching posts grouped by type, ordered by rank desc."""
    query = (query or "").strip()
    if not query:
        return {key: [] for key, *_ in POST_TYPES}

    site_settings = SiteSettings.objects.first()
    enabled = [
        (key, translation_model)
        for key, _, translation_model, module, feature in POST_TYPES
        if is_feature_active(site_settings, module, feature)
    ]
    results = {key: [] for key, *_ in POST_TYPES}
    if connection.vendor == "postgresql":
        results.update(_postgres_search(query, language, enabled))
    else:
        results.update(_fallback_search(query, language, enabled))
    return results


def _public_translations(translation_model, language: str):
    """Translations in ``language`` whose parent post is publicly listed.

    Only ``public`` posts are searchable: ``unlisted`` and ``protected`` are
    reachable by direct link only, ``private`` never — search is a
    public-content discovery surface, even for authenticated users. Filtered
    in SQL (not after slicing) so hidden rows don't eat the result budget.
    """
    return translation_model.objects.filter(language=language, translatable_content__visibility="public")


def _postgres_search(query: str, language: str, enabled) -> dict[str, list[SearchHit]]:
    from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

    config = PG_TEXT_SEARCH_CONFIG.get(language, "simple")
    search_query = SearchQuery(query, config=config, search_type="websearch")
    vector = (
        SearchVector("title", weight="A", config=config)
        + SearchVector("description", weight="B", config=config)
        + SearchVector("content", weight="C", config=config)
    )

    results: dict[str, list[SearchHit]] = {}
    for key, translation_model in enabled:
        translations = (
            _public_translations(translation_model, language)
            .annotate(rank=SearchRank(vector, search_query))
            .filter(rank__gt=0)
            .select_related("translatable_content")
            .order_by("-rank")[:30]
        )
        results[key] = [SearchHit(post=t.translatable_content, translation=t, rank=float(t.rank)) for t in translations]
    return results


def _fallback_search(query: str, language: str, enabled) -> dict[str, list[SearchHit]]:
    """SQLite-friendly substring search. Used in dev only — Postgres in prod."""
    needle = Q(title__icontains=query) | Q(description__icontains=query) | Q(content__icontains=query)
    # Bias title hits to the top so ordering is at least roughly useful.
    rank_expr = Case(
        When(title__icontains=query, then=Value(3.0)),
        When(description__icontains=query, then=Value(2.0)),
        default=Value(1.0),
    )

    results: dict[str, list[SearchHit]] = {}
    for key, translation_model in enabled:
        translations = (
            _public_translations(translation_model, language)
            .filter(needle)
            .annotate(rank=rank_expr)
            .select_related("translatable_content")
            .order_by("-rank", "-id")[:30]
        )
        results[key] = [SearchHit(post=t.translatable_content, translation=t, rank=float(t.rank)) for t in translations]
    return results
