from django.conf import settings
from django.http import HttpResponseRedirect
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


class Force2FAMiddleware:
    """
    Force users with active 2FA through the OTP verify page before they can
    reach any admin URL beyond login/logout/static.

    Flow:
      1. Standard admin password login completes — user is authenticated.
      2. On the next admin request, this middleware checks:
         - the user is authenticated (not anonymous)
         - the user has ``User2FA.is_active=True``
         - the session has NOT been marked ``2fa_verified``
         If all three hold, redirect to ``admin:verify_2fa``.
      3. The verify view marks the session ``2fa_verified=True`` on a valid
         OTP/backup-code submission and lets the user proceed.

    The exempt list keeps logout reachable so a user who lost their device
    AND has no backup codes can at least sign out (then run the
    ``disable_2fa`` management command from the host).

    Sits AFTER AuthenticationMiddleware so ``request.user`` is populated.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._admin_prefix = "/" + settings.ADMIN_URL.strip("/") + "/"

    def __call__(self, request):
        if not request.path.startswith(self._admin_prefix):
            return self.get_response(request)

        # Allowlist URLs that must be reachable in the unverified-2FA state.
        path = request.path
        exempt_suffixes = ("login/", "logout/", "verify/", "jsi18n/")
        if any(path.endswith("/" + s) or path.endswith(s) for s in exempt_suffixes):
            return self.get_response(request)
        # Static/media files served by Django in dev shouldn't trip the gate.
        if "/static/" in path or "/media/" in path:
            return self.get_response(request)

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return self.get_response(request)

        if request.session.get("2fa_verified"):
            return self.get_response(request)

        # Lazy import — User2FA lives in apps.core which imports this module.
        from apps.core.models import User2FA

        try:
            tfa = user.two_factor
        except User2FA.DoesNotExist:
            return self.get_response(request)

        if not tfa.is_active:
            return self.get_response(request)

        from django.urls import reverse

        verify_url = reverse("admin:verify_2fa")
        if request.get_full_path() != verify_url:
            verify_url = f"{verify_url}?next={request.get_full_path()}"
        return HttpResponseRedirect(verify_url)


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
