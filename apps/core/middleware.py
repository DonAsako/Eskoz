from django.conf import settings
from django.utils import translation


class ActiveThemeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.theme = getattr(settings, "ACTIVE_THEME", "Eskoz")

        response = self.get_response(request)
        return response


PERMISSIONS_POLICY = (
    "accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), "
    "camera=(), display-capture=(), document-domain=(), encrypted-media=(), "
    "fullscreen=(self), geolocation=(), gyroscope=(), magnetometer=(), "
    "microphone=(), midi=(), payment=(), picture-in-picture=(), "
    "publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), "
    "usb=(), web-share=(), xr-spatial-tracking=(), interest-cohort=()"
)


class SecurityHeadersMiddleware:
    """Adds extra security headers Django's SecurityMiddleware doesn't cover."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        response.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        response.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        return response


class AdminDefaultLanguageMiddleware:
    """
    Force ``settings.LANGUAGE_CODE`` for any request to the admin URLs.

    The public site lives under ``/<lang>/`` thanks to ``i18n_patterns``, but
    the back-office stays under a flat ``/admin/`` (or whatever ``ADMIN_URL``
    is) and must always render in the configured site default language —
    regardless of the staff member's browser, cookie, or session preference.
    Must run BEFORE LocaleMiddleware so the activation sticks for the whole
    request lifecycle.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._admin_prefix = "/" + settings.ADMIN_URL.strip("/") + "/"

    def __call__(self, request):
        if request.path.startswith(self._admin_prefix):
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
        return self.get_response(request)


class LegacyURLPermanentRedirectMiddleware:
    """
    Upgrade Django's automatic 302 redirects from un-prefixed URLs (e.g.
    ``/articles/foo``) to the language-prefixed equivalent (e.g.
    ``/fr/articles/foo``) into 301s.

    LocaleMiddleware emits 302 by default, which loses ranking when migrating
    an indexed site to ``i18n_patterns``. 301s tell Google "this URL moved
    permanently" and preserve the accumulated SEO juice. Must run AFTER
    LocaleMiddleware so the 302 is already produced.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._lang_prefixes = tuple(f"/{code}/" for code, _ in settings.LANGUAGES)

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 302:
            return response
        location = response.headers.get("Location", "")
        # Only upgrade redirects that point to a language-prefixed path AND
        # whose source path itself was NOT language-prefixed — i.e. the
        # specific case we want to make permanent for SEO.
        if location.startswith(self._lang_prefixes) and not request.path.startswith(self._lang_prefixes) and request.path != "/":
            response.status_code = 301
        return response
