import markdown
from django.apps import apps
from django.conf import settings
from django.contrib.admin import AdminSite
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django_ratelimit.decorators import ratelimit

from apps.core.models import SiteSettings


class EskozAdminSite(AdminSite):
    site_header = "Eskoz"
    index_template = "admin/eskoz_index.html"

    @method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT_LOGIN_IP, method="POST", block=True))
    @method_decorator(ratelimit(key="post:username", rate=settings.RATELIMIT_LOGIN_USERNAME, method="POST", block=True))
    def login(self, request, extra_context=None):
        return super().login(request, extra_context)

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
        """Render the dashboard with content stats + recent activity.

        The default Django admin index just lists apps; we keep that list
        further down the page (via ``admin/index.html`` which extends the
        original) and surface the operational data first: counts, audit
        trail, quick actions to the most-used create forms.
        """
        from auditlog.models import LogEntry

        from apps.blog.models import Article, Project
        from apps.core.models import Page
        from apps.education.models import Course, Lesson
        from apps.infosec.models import CVE, Writeup

        def _public(model):
            return model.objects.filter(visibility="public").count() if hasattr(model, "visibility") else model.objects.count()

        site_settings = SiteSettings.objects.first()
        site_settings_url = None
        if site_settings:
            model_admin = self._registry.get(SiteSettings)
            if model_admin:
                from django.urls import reverse as _reverse

                site_settings_url = _reverse(
                    "admin:core_sitesettings_change",
                    args=[site_settings.pk],
                    current_app=self.name,
                )

        stats = [
            {"label": "Articles", "total": Article.objects.count(), "public": _public(Article), "add_url": "admin:blog_article_add"},
            {"label": "Writeups", "total": Writeup.objects.count(), "public": _public(Writeup), "add_url": "admin:infosec_writeup_add"},
            {"label": "Lessons", "total": Lesson.objects.count(), "public": Lesson.objects.count(), "add_url": "admin:education_lesson_add"},
            {"label": "CVEs", "total": CVE.objects.count(), "public": CVE.objects.count(), "add_url": "admin:infosec_cve_add"},
            {"label": "Projects", "total": Project.objects.count(), "public": Project.objects.count(), "add_url": "admin:blog_project_add"},
            {"label": "Courses", "total": Course.objects.count(), "public": Course.objects.count(), "add_url": "admin:education_course_add"},
            {"label": "Pages", "total": Page.objects.count(), "public": _public(Page), "add_url": "admin:core_page_add"},
        ]

        recent_activity = LogEntry.objects.select_related("actor", "content_type").order_by("-timestamp")[:8]

        context = {
            **(extra_context or {}),
            "dashboard_stats": stats,
            "dashboard_recent_activity": recent_activity,
            "dashboard_site_settings_url": site_settings_url,
        }
        return super().index(request, context)

    def get_urls(self):
        from apps.core.views import verify_2fa_view

        urls = super().get_urls()
        custom_urls = [
            path(
                "content_preview/",
                self.admin_view(self.content_preview),
                name="content_preview",
            ),
            # Logged-in (post-password) users land here when they have 2FA
            # active and the session has not been verified yet. We do NOT
            # wrap with self.admin_view because the user IS authenticated —
            # they just need the second factor before any other admin URL
            # is reachable (Force2FAMiddleware handles the gate).
            path(
                "verify/",
                verify_2fa_view,
                name="verify_2fa",
            ),
            path(
                "set_visibility/<str:app_label>/<str:model_name>/<int:pk>/",
                self.admin_view(self.set_visibility),
                name="set_visibility",
            ),
        ]
        return custom_urls + urls

    def set_visibility(self, request, app_label, model_name, pk):
        """Swap the ``visibility`` of a single object from a changelist
        click. Validates that the user has change perms for the model and
        that ``protected`` is only set on objects that already have a
        password configured. Returns the new badge HTML so the JS can
        update in place.
        """
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return HttpResponseBadRequest("Unknown model")

        model_admin = self._registry.get(model)
        if model_admin is None:
            return HttpResponseBadRequest("Model not registered")

        if not request.user.has_perm(f"{app_label}.change_{model._meta.model_name}"):
            return JsonResponse({"error": "forbidden"}, status=403)

        new_value = request.POST.get("visibility", "").strip()
        valid = {c[0] for c in model._meta.get_field("visibility").choices}
        if new_value not in valid:
            return HttpResponseBadRequest("Invalid visibility")

        obj = model.objects.filter(pk=pk).first()
        if obj is None:
            return JsonResponse({"error": "not_found"}, status=404)

        if new_value == "protected" and not getattr(obj, "password", None):
            return JsonResponse(
                {
                    "error": "needs_password",
                    "message": str(_("Set a password on the object first.")),
                },
                status=400,
            )

        obj.visibility = new_value
        obj.save(update_fields=["visibility"])

        label = obj.get_visibility_display()
        return JsonResponse({"value": new_value, "label": str(label), "css": new_value})

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
                    "pymdownx.blocks.admonition",
                    "pymdownx.arithmatex",
                    "pymdownx.details",
                    "pymdownx.superfences",
                ],
                extension_configs={
                    "pymdownx.arithmatex": {
                        "generic": True,
                    },
                    "pymdownx.blocks.admonition": {
                        "types": [
                            "note",
                            "info",
                            "tip",
                            "success",
                            "warning",
                            "caution",
                            "danger",
                            "error",
                            "example",
                            "abstract",
                            "summary",
                            "tldr",
                            "quote",
                            "cite",
                            "question",
                            "faq",
                            "help",
                            "bug",
                            "security",
                            "flag",
                            "ctf",
                        ]
                    },
                },
            )
            return JsonResponse({"html": (html)})
        return HttpResponse(request, status="401")


admin_site = EskozAdminSite(name="admin")
