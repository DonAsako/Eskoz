"""Delete old PageView rows so the analytics table stays bounded.

Raw page views accumulate forever otherwise. Run on a schedule (cron), e.g.
daily:

    python manage.py prune_pageviews --days 365

The dashboard only ever looks at the last 30 days, so a generous retention
(months) keeps history without unbounded growth.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.analytics.models import PageView

DEFAULT_DAYS = 365


class Command(BaseCommand):
    help = "Delete PageView rows older than --days (default 365)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_DAYS,
            help=f"Retention window in days (default {DEFAULT_DAYS}).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report how many rows would be deleted without deleting.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        cutoff = timezone.now() - timedelta(days=days)
        qs = PageView.objects.filter(created_at__lt=cutoff)
        count = qs.count()

        if options["dry_run"]:
            self.stdout.write(f"[dry-run] {count} page views older than {days} days would be deleted.")
            return

        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} page views older than {days} days."))
