import markdown
from django.urls import path
from django.http import JsonResponse, HttpResponse

from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from core.models import SiteSettings


class EskozAdminSite(AdminSite):
    site_header = "Eskoz"

    APP_ORDER = ["core", "auth", "infosec", "blog", "education"]

    def get_app_list(self, request, extra_context=None):
        app_list = super().get_app_list(request, extra_context)

        site_settings = SiteSettings.objects.first()
        if not site_settings:
            return []

        filtered_apps = []
        for app in app_list:
            label = app["app_label"]

            if label == "infosec" and getattr(site_settings, "infosec", None):
                if site_settings.infosec.is_active:
                    filtered_apps.append(app)
            elif label == "blog" and getattr(site_settings, "blog", None):
                if site_settings.blog.is_active:
                    filtered_apps.append(app)
            elif label == "education" and getattr(site_settings, "education", None):
                if site_settings.education.is_active:
                    filtered_apps.append(app)

            elif label == "core":
                app["name"] = _("Site")
                filtered_apps.append(app)

            else:
                filtered_apps.append(app)

        filtered_apps.sort(key=lambda a: self.APP_ORDER.index(a["app_label"]))
        return filtered_apps

    def index(self, request, extra_context=None):
        site_settings = SiteSettings.objects.first()
        if site_settings:
            model_admin = self._registry.get(SiteSettings)
            if model_admin:
                return model_admin.change_view(
                    request, str(site_settings.pk), extra_context=extra_context
                )
        return super().index(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "content_preview/",
                self.admin_view(self.content_preview),
                name="content_preview",
            ),
        ]
        return custom_urls + urls

    def content_preview(self, request):
        if request.method == "POST":
            content = request.POST.get("content", "")
            html = markdown.markdown(
                content,
                extensions=[
                    "extra",
                    "codehilite",
                    "fenced_code",
                    "toc",
                    "pymdownx.arithmatex",
                ],
                extension_configs={
                    "pymdownx.arithmatex": {
                        "generic": True,
                    }
                },
            )
            return JsonResponse({"html": (html)})
        return HttpResponse(request, status="401")


admin_site = EskozAdminSite(name="admin")
