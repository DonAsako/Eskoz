"""Server-side page-view tracking helpers.

No personal data is persisted: the visitor identifier is a non-reversible
SHA-256 of IP + user-agent + a daily-rotating salt, used only to estimate
unique visitors. Counting happens server-side, so it is not defeated by ad
blockers (relevant for an infosec audience).
"""

import hashlib
import re

from django.conf import settings
from django.utils import timezone

_BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|facebookexternalhit|embedly|quora link preview|"
    r"outbrain|pinterest|monitor|uptime|curl|wget|python-requests|httpx|headless|lighthouse|"
    r"semrush|ahrefs|mj12bot|dotbot|petalbot",
    re.IGNORECASE,
)


def is_bot(user_agent):
    return not user_agent or bool(_BOT_RE.search(user_agent))


def client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def visitor_hash(request):
    """Daily-rotating, non-reversible visitor fingerprint (no PII stored)."""
    raw = "|".join(
        [
            client_ip(request),
            request.META.get("HTTP_USER_AGENT", ""),
            timezone.localdate().isoformat(),
            settings.SECRET_KEY,
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
