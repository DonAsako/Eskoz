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
from typing import Iterable

from django.db import connection
from django.db.models import Case, Q, Value, When

from apps.blog.models import Article, ArticleTranslation
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

POST_TYPES = (
    ("articles", Article, ArticleTranslation),
    ("writeups", Writeup, WriteupTranslation),
    ("lessons", Lesson, LessonTranslation),
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
        return {key: [] for key, _, _ in POST_TYPES}

    if connection.vendor == "postgresql":
        return _postgres_search(query, language)
    return _fallback_search(query, language)


def _postgres_search(query: str, language: str) -> dict[str, list[SearchHit]]:
    from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

    config = PG_TEXT_SEARCH_CONFIG.get(language, "simple")
    search_query = SearchQuery(query, config=config, search_type="websearch")
    vector = (
        SearchVector("title", weight="A", config=config)
        + SearchVector("description", weight="B", config=config)
        + SearchVector("content", weight="C", config=config)
    )

    results: dict[str, list[SearchHit]] = {}
    for key, post_model, translation_model in POST_TYPES:
        translations = (
            translation_model.objects.filter(language=language)
            .annotate(rank=SearchRank(vector, search_query))
            .filter(rank__gt=0)
            .select_related("translatable_content")
            .order_by("-rank")[:30]
        )
        results[key] = [
            SearchHit(post=t.translatable_content, translation=t, rank=float(t.rank)) for t in _filter_published(translations, post_model)
        ]
    return results


def _fallback_search(query: str, language: str) -> dict[str, list[SearchHit]]:
    """SQLite-friendly substring search. Used in dev only — Postgres in prod."""
    needle = Q(title__icontains=query) | Q(description__icontains=query) | Q(content__icontains=query)
    # Bias title hits to the top so ordering is at least roughly useful.
    rank_expr = Case(
        When(title__icontains=query, then=Value(3.0)),
        When(description__icontains=query, then=Value(2.0)),
        default=Value(1.0),
    )

    results: dict[str, list[SearchHit]] = {}
    for key, post_model, translation_model in POST_TYPES:
        translations = (
            translation_model.objects.filter(language=language)
            .filter(needle)
            .annotate(rank=rank_expr)
            .select_related("translatable_content")
            .order_by("-rank", "-id")[:30]
        )
        results[key] = [
            SearchHit(post=t.translatable_content, translation=t, rank=float(t.rank)) for t in _filter_published(translations, post_model)
        ]
    return results


def _filter_published(translations: Iterable, post_model) -> list:
    """Drop hits whose parent post isn't publicly visible.

    Lessons don't carry a ``visibility`` field — they're gated by the parent
    Module/Course access, so we accept all of them here and let the existing
    view-level checks handle restrictions.
    """
    if not hasattr(post_model, "visibility"):
        return list(translations)
    return [t for t in translations if getattr(t.translatable_content, "visibility", "public") == "public"]
