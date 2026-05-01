import io
import zipfile

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def visibility_badge_field(field_name="visibility", description=None):
    """Build a ModelAdmin display callable that renders ``field_name`` as a
    color-coded ``status-badge`` span (CSS in ``static/admin/css/admin.css``).

    Drop into a ``list_display`` tuple — easier than writing the wrapper
    boilerplate on every model::

        class ArticleAdmin(admin.ModelAdmin):
            list_display = ("title", "visibility_badge", "published_on")
            visibility_badge = visibility_badge_field()
    """

    @admin.display(description=description or field_name.replace("_", " ").title(), ordering=field_name)
    def _display(self, obj):
        value = getattr(obj, field_name, None)
        if value in (None, ""):
            return ""
        # Boolean fields render to "active"/"inactive" badges.
        if value is True:
            css, label = "active", _("Active")
        elif value is False:
            css, label = "inactive", _("Inactive")
        else:
            css = str(value).lower()
            getter = getattr(obj, f"get_{field_name}_display", None)
            label = getter() if callable(getter) else value
        return format_html('<span class="status-badge status-badge--{}">{}</span>', css, label)

    return _display


@admin.action(description=_("Backup selected articles"))
def backup(self, request, queryset):
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for article in queryset:
            for translation in article.translations.all():
                lang = translation.language
                title = translation.title or f"article-{article.pk}"
                filename = f"{slugify(title)}/{lang}.md"

                content = f"# {translation.title}\n\n"
                if translation.description:
                    content += f"> {translation.description}\n\n"
                content += translation.content or ""

                zip_file.writestr(filename, content)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="articles_backup.zip"'
    return response
