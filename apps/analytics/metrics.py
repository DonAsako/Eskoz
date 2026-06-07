"""Aggregations feeding the admin dashboard analytics panels.

Exposes ``add_dashboard_metrics(context)``, called by the core dashboard
callback. Kept here so all page-view logic lives in the analytics app.
"""

from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.analytics.models import PageView


def _daily_series(views, days=30):
    """Zero-filled daily counts (oldest -> newest) with bar heights as a
    percentage of the busiest day, for the sparkline / bar chart."""
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    rows = (
        views.filter(created_at__date__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(n=Count("id"))
    )
    counts = {r["day"]: r["n"] for r in rows}
    series = [
        {"day": start + timedelta(days=i), "count": counts.get(start + timedelta(days=i), 0)} for i in range(days)
    ]
    peak = max((s["count"] for s in series), default=0) or 1
    for s in series:
        s["pct"] = max(round(s["count"] / peak * 100), 3) if s["count"] else 0
    return series, peak


def _top_content(views, since, limit=10):
    """Most-viewed content objects (resolved to title + admin/site links)."""
    rows = (
        views.filter(content_type__isnull=False, created_at__gte=since)
        .values("content_type", "object_id")
        .annotate(n=Count("id"))
        .order_by("-n")[:limit]
    )
    items = []
    for r in rows:
        try:
            ct = ContentType.objects.get_for_id(r["content_type"])
            obj = ct.get_object_for_this_type(pk=r["object_id"])
        except Exception:  # noqa: S112 - object deleted / unresolvable → just skip it
            continue
        try:
            url = reverse(f"admin:{ct.app_label}_{ct.model}_change", args=[r["object_id"]])
        except NoReverseMatch:
            url = None
        items.append({"title": str(obj), "model": ct.name, "count": r["n"], "url": url})
    return items


def add_dashboard_metrics(context):
    """Compact analytics for the admin dashboard landing page."""
    now = timezone.now()
    d7 = now - timedelta(days=7)
    d30 = now - timedelta(days=30)
    views = PageView.objects.all()

    context["metrics"] = {
        "views_7d": views.filter(created_at__gte=d7).count(),
        "views_30d": views.filter(created_at__gte=d30).count(),
        "uniques_7d": views.filter(created_at__gte=d7).values("visitor_hash").distinct().count(),
    }
    context["top_pages"] = list(
        views.filter(created_at__gte=d30).values("path").annotate(n=Count("id")).order_by("-n")[:8]
    )
    context["views_series"], context["views_peak"] = _daily_series(views, days=30)


def full_metrics(context):
    """Richer analytics for the dedicated Analytics admin page."""
    now = timezone.now()
    d7 = now - timedelta(days=7)
    d30 = now - timedelta(days=30)
    views = PageView.objects.all()

    metrics = {
        "views_7d": views.filter(created_at__gte=d7).count(),
        "views_30d": views.filter(created_at__gte=d30).count(),
        "views_all": views.count(),
        "uniques_7d": views.filter(created_at__gte=d7).values("visitor_hash").distinct().count(),
        "uniques_30d": views.filter(created_at__gte=d30).values("visitor_hash").distinct().count(),
    }
    context["metrics"] = metrics
    context["cards"] = [
        (_("Views (7 days)"), metrics["views_7d"]),
        (_("Views (30 days)"), metrics["views_30d"]),
        (_("Views (all time)"), metrics["views_all"]),
        (_("Unique visitors (7 days)"), metrics["uniques_7d"]),
        (_("Unique visitors (30 days)"), metrics["uniques_30d"]),
    ]
    context["views_series"], context["views_peak"] = _daily_series(views, days=30)
    context["top_content"] = _top_content(views, d30, limit=10)
    context["top_pages"] = list(
        views.filter(created_at__gte=d30).values("path").annotate(n=Count("id")).order_by("-n")[:15]
    )
    context["top_referrers"] = list(
        views.filter(created_at__gte=d30)
        .exclude(referrer="")
        .values("referrer")
        .annotate(n=Count("id"))
        .order_by("-n")[:10]
    )
