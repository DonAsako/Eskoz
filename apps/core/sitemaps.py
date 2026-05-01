from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import translation

from apps.blog.models import Article
from apps.education.models import Course, Lesson
from apps.infosec.models import Writeup

from .models import Page


class StaticViewSitemap(Sitemap):
    """Sitemap entries for the always-on landing/list URLs.

    UI labels are translated per language, so each list lives at a different
    URL per language (``/fr/articles/``, ``/en/articles/``, …).
    """

    priority = 0.6
    changefreq = "weekly"
    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return [
            "core:index",
            "blog:article_list",
            "blog:project_list",
            "infosec:writeup_list",
            "infosec:certification_list",
            "infosec:cve_list",
            "education:course_list",
        ]

    def location(self, item):
        return reverse(item)


class _TranslatablePostSitemap(Sitemap):
    """
    Base for sitemap classes whose items have a ``translations`` related set.

    Emits one entry per language the post is *actually* translated into and
    cross-links them via ``rel=alternate hreflang=...``. We deliberately
    skip languages without a translation so Google does not waste crawl
    budget on URLs that 301 back to the canonical version.
    """

    i18n = True
    alternates = True
    x_default = True

    def get_languages_for_item(self, item):
        return list(item.translations.values_list("language", flat=True))


class ArticleSitemap(_TranslatablePostSitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(visibility="public").prefetch_related("translations").select_related("category").order_by("-edited_on")

    def lastmod(self, obj):
        return obj.edited_on

    def location(self, obj):
        return reverse("blog:article_detail", args=[obj.category.slug, obj.slug])


class WriteupSitemap(_TranslatablePostSitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Writeup.objects.filter(visibility="public").prefetch_related("translations").select_related("category").order_by("-edited_on")

    def lastmod(self, obj):
        return obj.edited_on

    def location(self, obj):
        return reverse("infosec:writeup_detail", args=[obj.category.slug, obj.slug])


class LessonSitemap(_TranslatablePostSitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Lesson.objects.prefetch_related("translations").select_related("module__course").order_by("module__course_id", "module_id", "order")

    def location(self, obj):
        return reverse(
            "education:lesson_detail",
            args=[obj.module.course.slug, obj.module.slug, obj.slug],
        )


class _MonolingualSitemap(Sitemap):
    """
    For models that don't carry per-language content (Page, Course): emit a
    single URL in the configured default language. Avoids advertising
    alternates that would all serve the same untranslated content.
    """

    def location(self, obj):
        with translation.override(settings.LANGUAGE_CODE):
            return self._reverse(obj)

    def _reverse(self, obj):  # pragma: no cover - overridden by subclasses
        raise NotImplementedError


class CourseSitemap(_MonolingualSitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Course.objects.all().order_by("title")

    def _reverse(self, obj):
        return reverse("education:module_list", args=[obj.slug])


class PageSitemap(_MonolingualSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        # 'private' pages are auth-only; 'index' is the homepage already in
        # StaticViewSitemap; only surface 'public' or 'referenced' pages.
        return Page.objects.filter(visibility__in=["public", "referenced"]).order_by("slug")

    def _reverse(self, obj):
        return reverse("core:page_detail", args=[obj.slug])


sitemaps = {
    "static": StaticViewSitemap,
    "articles": ArticleSitemap,
    "writeups": WriteupSitemap,
    "lessons": LessonSitemap,
    "courses": CourseSitemap,
    "pages": PageSitemap,
}
