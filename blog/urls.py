from django.urls import path
from .views import article_detail, articles_list


app_name = "blog"
urlpatterns = [
    path("article/<slug:slug>/", article_detail, name="article_detail"),
    path("articles/<slug:slug>/", articles_list, name="article_category_list"),
    path("articles/", articles_list, name="articles_list"),
]
