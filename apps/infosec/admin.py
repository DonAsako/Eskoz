from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import action as unfold_action

from apps.core.admin import (
    AbstractCategoryAdmin,
    AbstractCategoryTranslationAdmin,
    AbstractPostAdmin,
    AbstractPostTranslationAdmin,
    AbstractTagAdmin,
    AuthorsAdminMixin,
)
from apps.core.admin.site import admin_site
from apps.core.admin.utils import visibility_badge_field
from apps.infosec.nvd import NVDError, enrich_fields

from .models import (
    CTF,
    CVE,
    Category,
    CategoryTranslation,
    Certification,
    Issuer,
    Writeup,
    WriteupTag,
    WriteupTranslation,
)


class WriteupTranslationAdmin(AbstractPostTranslationAdmin):
    model = WriteupTranslation


class WriteupAdmin(AbstractPostAdmin):
    fieldsets = [
        *AbstractPostAdmin.fieldsets,
        ("CTF Information", {"fields": [("ctf", "difficulty", "points", "solver_count")]}),
    ]
    list_display = ("title", "ctf", "difficulty", "authors_list", "languages_list", "views_count", "visibility_badge")
    list_filter = (*AbstractPostAdmin.list_filter, "ctf", "difficulty")
    list_select_related = ("ctf",)
    inlines = [*AbstractPostAdmin.inlines, WriteupTranslationAdmin]


class CategoryTranslationAdmin(AbstractCategoryTranslationAdmin):
    model = CategoryTranslation


class CategoryAdmin(AbstractCategoryAdmin):
    inlines = [CategoryTranslationAdmin]


class TagAdmin(AbstractTagAdmin): ...


def _apply_nvd(cve):
    """Fetch from NVD and persist the populated fields on cve."""

    fields = enrich_fields(cve.cve_id)
    if fields:
        for name, value in fields.items():
            setattr(cve, name, value)
        cve.save(update_fields=list(fields))
    return list(fields)


@admin.action(description=_("Fetch from NVD"))
def fetch_from_nvd(modeladmin, request, queryset):
    """Bulk: enrich the selected CVEs from NVD (one failure never blocks the rest)."""
    updated, failed = 0, []
    for cve in queryset:
        try:
            applied = _apply_nvd(cve)
        except NVDError as exc:
            failed.append(f"{cve.cve_id} ({exc})")
            continue
        if applied:
            updated += 1
        else:
            failed.append(f"{cve.cve_id} (no data)")
    if updated:
        messages.success(request, _("%(n)d CVE(s) updated from NVD.") % {"n": updated})
    if failed:
        messages.warning(request, _("Could not fetch: %(items)s") % {"items": ", ".join(failed)})


class CVEAdmin(AuthorsAdminMixin, ModelAdmin):
    list_display = ("cve_id", "cvss_score", "published_date", "authors_list", "visibility_badge")
    list_filter = ("visibility", "published_date")
    date_hierarchy = "published_date"
    visibility_badge = visibility_badge_field("visibility")
    search_fields = ("cve_id", "vulnerable_product")
    actions = [fetch_from_nvd]
    actions_detail = ["fetch_from_nvd_detail"]

    @unfold_action(description=_("Fetch from NVD"), icon="cloud_download", permissions=["change"])
    def fetch_from_nvd_detail(self, request, object_id):
        """Single-CVE button shown at the top of the change page."""
        change_url = reverse(f"{self.admin_site.name}:infosec_cve_change", args=[object_id])
        cve = self.get_object(request, object_id)
        if cve is None:
            messages.error(request, _("CVE not found."))
            return redirect(change_url)
        try:
            applied = _apply_nvd(cve)
        except NVDError as exc:
            messages.warning(request, _("Could not fetch %(id)s: %(err)s") % {"id": cve.cve_id, "err": exc})
        else:
            if applied:
                messages.success(request, _("%(id)s updated from NVD.") % {"id": cve.cve_id})
            else:
                messages.warning(request, _("No data found on NVD for %(id)s.") % {"id": cve.cve_id})
        return redirect(change_url)

    class Media:
        js = ("admin/js/visibility_toggle.js",)


admin_site.register(Writeup, WriteupAdmin)
admin_site.register(CTF, ModelAdmin)
admin_site.register(Certification, ModelAdmin)
admin_site.register(Issuer, ModelAdmin)
admin_site.register(CVE, CVEAdmin)
admin_site.register(WriteupTag, TagAdmin)
admin_site.register(Category, CategoryAdmin)
