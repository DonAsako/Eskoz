from django.contrib.admin import AdminSite


class EskozAdminSite(AdminSite):
    site_header = "Eskoz"


admin_site = EskozAdminSite(name="admin")
