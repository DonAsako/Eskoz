from django.shortcuts import render, get_object_or_404
from .models import Article


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, "blog/article_detail.html", {"article": article})


def articles_list(request):
    articles = Article.objects.all()
    return render(request, "blog/articles_list.html", {"articles": articles})
