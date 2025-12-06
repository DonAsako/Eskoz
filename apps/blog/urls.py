from django.urls import path

from .views import article_detail, article_list, project_list, member_list

app_name = "blog"
urlpatterns = [
    path(
        "articles/<slug:slug_category>/<slug:slug_article>",
        article_detail,
        name="article_detail",
    ),
    path("articles/<slug:slug>/", article_list, name="article_category_list"),
    path("articles/", article_list, name="article_list"),
    path("projects/", project_list, name="project_list"),
    path("members/", member_list, name="member_list"),
]
