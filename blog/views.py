from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language
from .models import Article


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
                f"{request.theme}/blog/article_detail.html",
                {"article": article},
            )
        return render(request, f"{request.theme}/blog/article_password.html")

    return render(
        request, f"{request.theme}/blog/article_detail.html", {"article": article}
    )


def articles_list(request):
    articles = Article.objects.filter(visibility="public").prefetch_related(
        "translations", "tags"
    )
    return render(
        request, f"{request.theme}/blog/articles_list.html", {"articles": articles}
    )
