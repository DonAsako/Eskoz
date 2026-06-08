"""Aggregations feeding the dedicated Analytics admin page.

Exposes ``full_metrics(context)``, called by the analytics view. Kept here so
all page-view logic lives in the analytics app.
"""

from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.analytics.models import PageView


def _pct_change(current, previous):
    """Signed % change vs the previous equal-length window."""
    if not previous:
        return None
    return round((current - previous) / previous * 100)


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


def _minute_series(views, minutes=60):
    """Per-minute counts over the last ``minutes`` for the realtime sparkline."""
    now = timezone.now()
    cur = now.replace(second=0, microsecond=0)
    start = cur - timedelta(minutes=minutes - 1)
    buckets = [0] * minutes
    for ts in views.filter(created_at__gte=start).values_list("created_at", flat=True):
        idx = int((ts - start).total_seconds() // 60)
        if 0 <= idx < minutes:
            buckets[idx] += 1
    series = [{"min": start + timedelta(minutes=i), "count": c} for i, c in enumerate(buckets)]
    peak = max(buckets, default=0) or 1
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


def full_metrics(context):
    """Richer analytics for the dedicated Analytics admin page."""
    now = timezone.now()
    d7 = now - timedelta(days=7)
    d14 = now - timedelta(days=14)
    d30 = now - timedelta(days=30)
    d60 = now - timedelta(days=60)
    views = PageView.objects.all()

    v7 = views.filter(created_at__gte=d7).count()
    v7_prev = views.filter(created_at__gte=d14, created_at__lt=d7).count()
    v30 = views.filter(created_at__gte=d30).count()
    v30_prev = views.filter(created_at__gte=d60, created_at__lt=d30).count()
    u7 = views.filter(created_at__gte=d7).values("visitor_hash").distinct().count()
    u7_prev = views.filter(created_at__gte=d14, created_at__lt=d7).values("visitor_hash").distinct().count()
    u30 = views.filter(created_at__gte=d30).values("visitor_hash").distinct().count()
    u30_prev = views.filter(created_at__gte=d60, created_at__lt=d30).values("visitor_hash").distinct().count()

    metrics = {
        "views_7d": v7,
        "views_30d": v30,
        "views_all": views.count(),
        "uniques_7d": u7,
        "uniques_30d": u30,
    }
    context["metrics"] = metrics
    # (label, value, delta%) — delta is None for the all-time card (no baseline).
    context["cards"] = [
        (_("Views (7 days)"), v7, _pct_change(v7, v7_prev)),
        (_("Views (30 days)"), v30, _pct_change(v30, v30_prev)),
        (_("Views (all time)"), metrics["views_all"], None),
        (_("Unique visitors (7 days)"), u7, _pct_change(u7, u7_prev)),
        (_("Unique visitors (30 days)"), u30, _pct_change(u30, u30_prev)),
    ]
    context["views_series"], context["views_peak"] = _daily_series(views, days=30)

    rt = views.filter(created_at__gte=now - timedelta(hours=1))
    context["realtime"] = {
        "views_1h": rt.count(),
        "uniques_1h": rt.values("visitor_hash").distinct().count(),
    }
    context["realtime_series"], context["realtime_peak"] = _minute_series(views, minutes=60)
    context["realtime_pages"] = list(rt.values("path").annotate(n=Count("id")).order_by("-n")[:5])

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
    context["top_campaigns"] = list(
        views.filter(created_at__gte=d30)
        .exclude(utm_source="")
        .values("utm_source", "utm_medium", "utm_campaign")
        .annotate(n=Count("id"))
        .order_by("-n")[:10]
    )
