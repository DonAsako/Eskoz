from django.urls import path

from .views import (
    certifications_lists,
    writeup_detail,
    writeups_list,
)

app_name = "infosec"
urlpatterns = [
    path("writeup/<slug:slug>/", writeup_detail, name="writeup_detail"),
    path("writeups/<slug:slug>/", writeups_list, name="writeup_category_list"),
    path("writeups/", writeups_list, name="writeups_list"),
    path("certifications/", certifications_lists, name="certifications_lists"),
]
