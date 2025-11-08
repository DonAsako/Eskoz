from django.urls import path

from .views import index, page_detail, well_known

app_name = "core"
urlpatterns = [
    path("", index, name="index"),
    path("pages/<slug:slug>/", page_detail, name="page_detail"),
    path(".well-known/<str:filename>", well_known, name="well_known"),
]
