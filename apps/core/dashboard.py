"""Dashboard data for the unfold admin index.

Surfaces the most recent audit-log activity (who created / updated / deleted
what, and when) so the landing page is useful to a content team rather than a
bare app list. Wired via ``UNFOLD["DASHBOARD_CALLBACK"]``.
"""

from auditlog.models import LogEntry
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

# action id -> (label, css modifier matching our status-badge--* styles)
_ACTION_META = {
    LogEntry.Action.CREATE: (_("created"), "public"),
    LogEntry.Action.UPDATE: (_("updated"), "unlisted"),
    LogEntry.Action.DELETE: (_("deleted"), "protected"),
    LogEntry.Action.ACCESS: (_("accessed"), "private"),
}


def _change_url(entry):
    """Best-effort link to the changed object's admin page."""
    ct = entry.content_type
    if not ct or not entry.object_pk:
        return None
    try:
        return reverse(f"admin:{ct.app_label}_{ct.model}_change", args=[entry.object_pk])
    except NoReverseMatch:
        return None


def dashboard_callback(request, context):
    entries = LogEntry.objects.select_related("actor", "content_type").order_by("-timestamp")[:12]

    activity = []
    for entry in entries:
        label, css = _ACTION_META.get(entry.action, (_("changed"), "private"))
        actor = entry.actor
        activity.append(
            {
                "actor": (actor.get_full_name() or actor.get_username()) if actor else _("System"),
                "action": label,
                "action_css": css,
                "repr": entry.object_repr,
                "model": entry.content_type.name if entry.content_type else "",
                "timestamp": entry.timestamp,
                "url": _change_url(entry),
            }
        )

    context["recent_activity"] = activity
    return context
