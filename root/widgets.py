from django.forms import Widget


class ContentEditorWidget(Widget):
    template_name = "widgets/content_editor_widget.html"

    class Media:
        css = {"all": ("admin/css/content_editor_widget.css",)}
        js = ("admin/js/content_editor_widget.js",)


class OTPWidget(Widget):
    template_name = "widgets/otp_widget.html"

    class Media:
        css = {"all": ("admin/css/otp_widget.css",)}
        js = ("admin/js/otp_widget.js",)
