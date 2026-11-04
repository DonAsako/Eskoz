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

    def test_well_known_is_served_at_origin_root(self):
        # RFC 8615 / RFC 9116: security.txt must be reachable without a
        # language prefix (it used to redirect to /<lang>/.well-known/ → 404).
        from apps.core.models import SiteSettings, WellKnownFile

        site = SiteSettings.objects.create(site_name="Test")
        WellKnownFile.objects.create(site_settings=site, filename="security.txt", content="Contact: mailto:a@b.c")
        response = self.client.get("/.well-known/security.txt")
        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "text/plain"
        assert response.content.decode() == "Contact: mailto:a@b.c"

    def test_unknown_well_known_file_is_404(self):
        response = self.client.get("/.well-known/does-not-exist.txt")
        assert response.status_code == HTTPStatus.NOT_FOUND
