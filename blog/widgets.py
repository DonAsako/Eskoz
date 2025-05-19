from django.forms import Widget
from django.utils.safestring import mark_safe
from django.templatetags.static import static


class ContentEditorWidget(Widget):
    template_name = "widgets/content_editor_widget.html"

    class Media:
        css = {
            "all": (
                "css/content_editor_widget.css",
                "https://uicdn.toast.com/editor/latest/toastui-editor.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/prism/1.23.0/themes/prism.min.css",
                "https://uicdn.toast.com/editor-plugin-code-syntax-highlight/latest/toastui-editor-plugin-code-syntax-highlight.min.css",
                "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css",
            )
        }
        js = (
            "https://uicdn.toast.com/editor/latest/toastui-editor-all.min.js",
            "https://uicdn.toast.com/editor-plugin-code-syntax-highlight/latest/toastui-editor-plugin-code-syntax-highlight-all.min.js",
            "https://cdn.jsdelivr.net/npm/latex.js/dist/latex.js",
            "script/latex_plugin.js",
            "script/content_editor_widget.js",
        )
