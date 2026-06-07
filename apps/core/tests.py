import re
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from eskoz import __version__


class VersionTests(TestCase):
    def test_version_is_exposed(self):
        # release-please bumps this string; guard against an accidental wipe.
        assert re.match(r"^\d+\.\d+\.\d+", __version__)


class PublicEndpointTests(TestCase):
    def test_robots_txt_serves_sitemap_directive(self):
        response = self.client.get("/robots.txt")
        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "text/plain"
        assert "Sitemap:" in response.content.decode()

    def test_homepage_renders(self):
        # Default language prefix is required (prefix_default_language=True).
        response = self.client.get(reverse("core:index"))
        assert response.status_code == HTTPStatus.OK
