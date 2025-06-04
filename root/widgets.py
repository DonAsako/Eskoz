from django.forms import Widget
from django.utils.safestring import mark_safe
from django.templatetags.static import static


class ContentEditorWidget(Widget):
    template_name = "widgets/content_editor_widget.html"

    class Media:
        css = {"all": ("admin/css/content_editor_widget.css",)}
        js = ("admin/js/content_editor_widget.js",)


class ColorPickerWidget(Widget):
    template_name = "widgets/color_picker_widget.html"

    class Media:
        css = {"all": ("admin/css/color_picker_widget.css",)}
        js = ("admin/js/color_picker_widget.js",)
