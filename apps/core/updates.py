"""Opt-in update check against the project's GitHub releases.

Server-side and fail-silent by design: a self-hosted (often infosec) instance
must never be *forced* to phone home, and a dashboard render must never block
or raise because GitHub is slow/unreachable. Gated by
``SiteSettings.check_for_updates`` (default off) and cached for a day.

No third-party HTTP dependency — stdlib ``urllib`` is enough for one GET.
"""

import json
import urllib.error
import urllib.request

from django.conf import settings
from django.core.cache import cache
from packaging.version import InvalidVersion, Version

from eskoz import __version__

_CACHE_KEY = "core:update_check"
_CACHE_TTL = 60 * 60 * 24  # cache a successful check for a day
_FAIL_TTL = 60 * 60  # on failure, back off an hour before retrying
_TIMEOUT = 3  # seconds — a slow GitHub must not stall the dashboard


def _repo():
    return getattr(settings, "ESKOZ_GITHUB_REPO", "DonAsako/eskoz")


def _fetch_latest_tag():
    url = f"https://api.github.com/repos/{_repo()}/releases/latest"
    req = urllib.request.Request(  # noqa: S310 — fixed https host, not user input
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"eskoz/{__version__}",
        },
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
        data = json.load(resp)
    return data.get("tag_name"), data.get("html_url")


def get_update_info():
    """Return ``{"current", "latest", "url", "available"}`` or ``None``.

    ``None`` means "couldn't determine" (network error, no release yet,
    unparsable version) — callers treat it as "show nothing".
    """
    cached = cache.get(_CACHE_KEY)
    if cached is not None:
        # ``False`` is the failure sentinel (distinct from a cache miss of None).
        return cached or None

    try:
        tag, html_url = _fetch_latest_tag()
        latest = Version((tag or "").lstrip("v"))
        current = Version(__version__)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, InvalidVersion):
        cache.set(_CACHE_KEY, False, _FAIL_TTL)
        return None

    info = {
        "current": str(current),
        "latest": str(latest),
        "url": html_url or f"https://github.com/{_repo()}/releases/latest",
        "available": latest > current,
    }
    cache.set(_CACHE_KEY, info, _CACHE_TTL)
    return info
