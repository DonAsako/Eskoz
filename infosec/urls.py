from django.urls import path
from .views import (
    writeups_list,
    writeup_detail,
    certifications_lists,
)


app_name = "infosec"
urlpatterns = [
    path("writeup/<slug:slug>/", writeup_detail, name="writeup_detail"),
    path("writeups/<slug:slug>/", writeups_list, name="writeup_category_list"),
    path("writeups/", writeups_list, name="writeups_list"),
    path("certifications/", certifications_lists, name="certifications_lists"),
]
