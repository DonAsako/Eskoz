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


class SearchVisibilityTests(TestCase):
    """Search must only surface what the public site itself exposes."""

    def setUp(self):
        from apps.core.models import SiteSettings
        from apps.infosec.models import Writeup, WriteupTranslation

        # post_migrate seeds a SiteSettings row; reuse it (views read .first()).
        self.site = SiteSettings.objects.first() or SiteSettings.objects.create(site_name="Test")
        self.site.infosec.is_active = True
        self.site.infosec.activate_writeups_page = True
        self.site.infosec.save()

        for visibility in ("public", "unlisted", "protected", "private"):
            post = Writeup.objects.create(title=f"w-{visibility}", slug=f"w-{visibility}", visibility=visibility)
            WriteupTranslation.objects.create(
                translatable_content=post, language="en", title=f"needle {visibility}", content="body"
            )

    def _titles(self):
        from apps.core.search import search_posts

        return {hit.translation.title for hit in search_posts("needle", "en")["writeups"]}

    def test_only_public_posts_are_returned(self):
        assert self._titles() == {"needle public"}

    def test_disabled_writeups_page_hides_writeups(self):
        self.site.infosec.activate_writeups_page = False
        self.site.infosec.save()
        assert self._titles() == set()

    def test_disabled_infosec_module_hides_writeups(self):
        self.site.infosec.is_active = False
        self.site.infosec.save()
        assert self._titles() == set()
