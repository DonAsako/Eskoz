from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _


def analytics_view(request):
    """Dedicated Analytics admin page. Mounted on the admin site (staff-only,
    behind the 2FA gate) via ``admin_view`` — see EskozAdminSite.get_urls."""
    from apps.analytics.metrics import full_metrics
    from apps.core.admin.site import admin_site

    context = admin_site.each_context(request)
    context["title"] = _("Analytics")
    full_metrics(context)
    return TemplateResponse(request, "admin/analytics.html", context)
