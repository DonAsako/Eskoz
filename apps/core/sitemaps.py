from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import Article
from apps.education.models import Course, Lesson
from apps.infosec.models import Writeup

from .models import Page


class StaticViewSitemap(Sitemap):
    """Sitemap entries for the always-on landing/list URLs."""

    priority = 0.6
    changefreq = "weekly"

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


class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(visibility="public").select_related("category").order_by("-edited_on")

    def lastmod(self, obj):
        return obj.edited_on

    def location(self, obj):
        return reverse("blog:article_detail", args=[obj.category.slug, obj.slug])


class WriteupSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Writeup.objects.filter(visibility="public").select_related("category").order_by("-edited_on")

    def lastmod(self, obj):
        return obj.edited_on

    def location(self, obj):
        return reverse("infosec:writeup_detail", args=[obj.category.slug, obj.slug])


class LessonSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Lesson.objects.select_related("module__course").order_by("module__course_id", "module_id", "order")

    def location(self, obj):
        return reverse(
            "education:lesson_detail",
            args=[obj.module.course.slug, obj.module.slug, obj.slug],
        )


class CourseSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Course.objects.all().order_by("title")

    def location(self, obj):
        return reverse("education:module_list", args=[obj.slug])


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        # 'private' pages are auth-only; 'index' is the homepage already in
        # StaticViewSitemap; only surface 'public' or 'referenced' pages.
        return Page.objects.filter(visibility__in=["public", "referenced"]).order_by("slug")

    def location(self, obj):
        return reverse("core:page_detail", args=[obj.slug])


sitemaps = {
    "static": StaticViewSitemap,
    "articles": ArticleSitemap,
    "writeups": WriteupSitemap,
    "lessons": LessonSitemap,
    "courses": CourseSitemap,
    "pages": PageSitemap,
}
