from django.shortcuts import render, get_object_or_404, Http404
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User
from .models import Article, Category, Project


def article_detail(request, slug_category, slug_article):
    """
    Render the detail page for a specific article.

    Args:
        request (HttpRequest): The HTTP request object.
        slug_category (str): Slug identifying the category.
        slug_article (str): Slug identifying the article.

    Returns:
        HttpResponse: Rendered article detail page.
    """
    category = get_object_or_404(Category, slug=slug_category)
    article = get_object_or_404(Article, category=category, slug=slug_article)
    if article.visibility == "private" and not request.user.is_authenticated:
        raise Http404

    if article.visibility == "protected":
        if request.method == "POST" and request.POST.get("password") == getattr(
            article, "password", ""
        ):
            return render(request, "blog/article_detail.html", {"article": article})

        return render(request, "blog/article_password.html")

    return render(request, "blog/article_detail.html", {"article": article})


def article_list(request, slug=None):
    """
    Render a list of articles, optionally filtered by category slug.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str, optional): Slug of the category to filter articles. Defaults to None.

    Returns:
        HttpResponse: Rendered articles list page.
    """
    articles = Article.objects.all()
    selected_category = None
    if slug:
        selected_category = get_object_or_404(Category, slug=slug)
        articles = articles.filter(category=selected_category)

    categories = Category.objects.filter(articles__isnull=False).distinct()

    return render(
        request,
        "blog/article_list.html",
        {
            "articles": articles,
            "categories": categories,
            "selected_category": selected_category,
        },
    )


def member_list(request):
    """
    Render a list of all members.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered projects list page.
    """
    members = User.objects.select_related("profile").all()
    return render(request, "blog/member_list.html", {"members": members})


def project_list(request):
    """
    Render a list of all projects.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered projects list page.
    """
    projects = Project.objects.all()
    return render(request, "blog/project_list.html", {"projects": projects})
