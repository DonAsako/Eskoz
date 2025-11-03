from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from root.views import post_detail, posts_list

from .models import Article, Category, Project


def article_detail(request, slug):
    """
    Render the detail page for a specific article.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): Slug identifying the article.

    Returns:
        HttpResponse: Rendered article detail page.
    """
    return post_detail(request, Article, slug, "blog/post_detail.html")


def article_list(request, slug=None):
    """
    Render a list of articles, optionally filtered by category slug.

    Uses the generic posts_list function with the Article model.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str, optional): Slug of the category to filter articles. Defaults to None.

    Returns:
        HttpResponse: Rendered articles list page.
    """
    return posts_list(
        request,
        Article,
        Category,
        slug,
        post_type="articles",
        post_type_trans=_("Articles"),
        detail_url_name="blog:article_detail",
    )


def project_list(request):
    """
    Render a list of all projects.

    Fetches all Project instances and passes them to the 'blog/project_list.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered projects list page.
    """
    projects = Project.objects.all()
    return render(request, "blog/project_list.html", {"projects": projects})
