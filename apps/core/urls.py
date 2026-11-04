from django.urls import path

from .views import index, page_detail, search_view, tag_detail

app_name = "core"
urlpatterns = [
    path("", index, name="index"),
    path("search/", search_view, name="search"),
    path("tags/<slug:slug>/", tag_detail, name="tag_detail"),
    path("pages/<slug:slug>/", page_detail, name="page_detail"),
]
