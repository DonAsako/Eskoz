from django.apps import apps
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django_ratelimit.decorators import ratelimit
from unfold.sites import UnfoldAdminSite

from apps.core.models import SiteSettings
from apps.core.utils import get_content_as_html


class EskozAdminSite(UnfoldAdminSite):
    @method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT_LOGIN_IP, method="POST", block=True))
    @method_decorator(ratelimit(key="post:username", rate=settings.RATELIMIT_LOGIN_USERNAME, method="POST", block=True))
    def login(self, request, extra_context=None):
        return super().login(request, extra_context)

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
            else:
                filtered_apps.append(app)

        return filtered_apps

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
            path(
                "image_upload/",
                self.admin_view(self.image_upload),
                name="image_upload",
            ),
        ]
        return custom_urls + urls

    def image_upload(self, request):
        """Store an image dropped/pasted into the Markdown editor and return
        its URL so the JS can insert the corresponding ``![](...)``. Staff-only
        (wrapped by ``admin_view``); the file is validated as a real image by
        Pillow before being written under ``posts/``.
        """
        import uuid

        from django.core.files.storage import default_storage
        from PIL import Image, UnidentifiedImageError

        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        upload = request.FILES.get("image")
        if not upload:
            return HttpResponseBadRequest("No file")
        if upload.size > 10 * 1024 * 1024:
            return JsonResponse({"error": str(_("Image too large (max 10 MB)."))}, status=400)

        try:
            probe = Image.open(upload)
            probe.verify()
        except (UnidentifiedImageError, OSError):
            return JsonResponse({"error": str(_("Invalid image file."))}, status=400)

        ext = {"jpeg": "jpg", "png": "png", "gif": "gif", "webp": "webp"}.get((probe.format or "").lower())
        if not ext:
            return JsonResponse({"error": str(_("Unsupported image format."))}, status=400)

        upload.seek(0)
        name = default_storage.save(f"posts/{uuid.uuid4()}.{ext}", upload)
        return JsonResponse({"url": default_storage.url(name)})

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
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        content = request.POST.get("content", "")
        return JsonResponse({"html": get_content_as_html(content)})


admin_site = EskozAdminSite(name="admin")
