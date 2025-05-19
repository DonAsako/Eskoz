from django.urls import path
from .views import well_known, index, page_detail

app_name = "root"
urlpatterns = [
    path("", index, name="index"),
    path("pages/<slug:slug>/", page_detail, name="page_detail"),
    path(".well-known/<str:filename>", well_known, name="well_known"),
]
