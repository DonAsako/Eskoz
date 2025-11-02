from django.urls import path
from .views import (
    article_detail,
    articles_list,
    writeups_list,
    writeup_detail,
    certifications_lists,
    projects_lists,
)


app_name = "blog"
urlpatterns = [
    path("article/<slug:slug>/", article_detail, name="article_detail"),
    path("articles/<slug:slug>/", articles_list, name="article_category_list"),
    path("articles/", articles_list, name="articles_list"),
    path("writeup/<slug:slug>/", writeup_detail, name="writeup_detail"),
    path("writeups/<slug:slug>/", writeups_list, name="writeup_category_list"),
    path("writeups/", writeups_list, name="writeups_list"),
    path("certifications/", certifications_lists, name="certifications_lists"),
    path("projects/", projects_lists, name="projects_lists"),
]
