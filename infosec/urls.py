from django.urls import path

from .views import (
    certification_list,
    writeup_detail,
    writeup_list,
    cve_list,
)

app_name = "infosec"
urlpatterns = [
    path(
        "writeups/<slug:category_slug>/<slug:writeup_slug>/",
        writeup_detail,
        name="writeup_detail",
    ),
    path("writeups/<slug:slug>/", writeup_list, name="writeup_category_list"),
    path("writeups/", writeup_list, name="writeup_list"),
    path("certifications/", certification_list, name="certification_list"),
    path("cves/", cve_list, name="cve_list"),
]
