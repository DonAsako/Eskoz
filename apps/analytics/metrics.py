"""Aggregations feeding the admin dashboard analytics panels.

Exposes ``add_dashboard_metrics(context)``, called by the core dashboard
callback. Kept here so all page-view logic lives in the analytics app.
"""

from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.analytics.models import PageView


def add_dashboard_metrics(context):
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

    # Daily series for the last 30 days (oldest -> newest), zero-filled, with
    # each bar's height as a percentage of the busiest day for the sparkline.
    today = timezone.localdate()
    start = today - timedelta(days=29)
    rows = (
        views.filter(created_at__date__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(n=Count("id"))
    )
    counts = {r["day"]: r["n"] for r in rows}
    series = [{"day": start + timedelta(days=i), "count": counts.get(start + timedelta(days=i), 0)} for i in range(30)]
    peak = max((s["count"] for s in series), default=0) or 1
    for s in series:
        s["pct"] = max(round(s["count"] / peak * 100), 3) if s["count"] else 0
    context["views_series"] = series
    context["views_peak"] = peak
