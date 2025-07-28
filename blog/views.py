from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language
from .models import Article, Category


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.visibility == "private":
        if not request.user.is_authenticated:
            raise Http404

    elif article.visibility == "protected":
        if (
            request.method == "POST"
            and request.POST.get("password") == article.password
        ):
            return render(
                request,
                f"blog/article_detail.html",
                {"article": article},
            )
        return render(request, f"blog/article_password.html")

    return render(request, f"blog/article_detail.html", {"article": article})


def articles_list(request, slug=None):
    articles = Article.objects.filter(visibility="public").prefetch_related(
        "translations", "tags"
    )
    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug)

        articles = articles.filter(category=category)

    return render(
        request,
        f"blog/articles_list.html",
        {"articles": articles, "category": category},
    )
