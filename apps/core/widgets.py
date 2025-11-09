from django.forms import Widget
from django.urls import reverse


class ContentEditorWidget(Widget):
    template_name = "widgets/content_editor_widget.html"

    class Media:
        css = {"all": ("admin/css/content_editor_widget.css",)}
        js = ("admin/js/content_editor_widget.js",)

    def get_context(self, name, value, attrs):
        return {
            **super().get_context(name, value, attrs),
            "content_preview_url": reverse("admin:content_preview"),
        }
