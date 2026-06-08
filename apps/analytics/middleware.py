import contextlib

from django.conf import settings


class PageViewMiddleware:
    """Record a de-duplicated, server-side page view for public HTML pages.

    Runs after the view, so detail views can annotate ``request.tracked_object``
    to link the view to a content object. Refreshes by the same visitor on the
    same path within 30 min are collapsed (cache-backed). Never lets an
    analytics error break the page.
    """

    DEDUP_WINDOW = 60 * 30

    def __init__(self, get_response):
        self.get_response = get_response
        self._excluded = (
            f"/{settings.ADMIN_URL.strip('/')}/",
            settings.STATIC_URL,
            settings.MEDIA_URL,
        )

    def __call__(self, request):
        response = self.get_response(request)
        with contextlib.suppress(Exception):
            self._record(request, response)
        return response

    def _record(self, request, response):
        if request.method != "GET" or response.status_code != 200:
            return
        if "text/html" not in response.get("Content-Type", ""):
            return
        path = request.path
        if any(path.startswith(p) for p in self._excluded):
            return

        from apps.analytics.tracking import external_referrer, is_bot, visitor_hash

        if is_bot(request.META.get("HTTP_USER_AGENT", "")):
            return

        from django.core.cache import cache

        vhash = visitor_hash(request)
        cache_key = f"pv:{vhash}:{path}"
        if cache.get(cache_key):
            return
        cache.set(cache_key, 1, self.DEDUP_WINDOW)

        from django.contrib.contenttypes.models import ContentType

        from apps.analytics.models import PageView

        obj = getattr(request, "tracked_object", None)
        ct = ContentType.objects.get_for_model(obj.__class__) if obj is not None else None
        PageView.objects.create(
            content_type=ct,
            object_id=getattr(obj, "pk", None),
            path=path[:512],
            visitor_hash=vhash,
            referrer=external_referrer(request)[:512],
            utm_source=request.GET.get("utm_source", "")[:128],
            utm_medium=request.GET.get("utm_medium", "")[:128],
            utm_campaign=request.GET.get("utm_campaign", "")[:128],
        )
