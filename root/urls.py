from django.urls import path

from .views import content_preview, index, page_detail, well_known

app_name = "root"
urlpatterns = [
    path("", index, name="index"),
    path("pages/<slug:slug>/", page_detail, name="page_detail"),
    path(".well-known/<str:filename>", well_known, name="well_known"),
    path("content_preview/", content_preview, name="admin_content_preview"),
]
