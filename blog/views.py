from django.shortcuts import get_object_or_404, render, Http404
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q
from .models import Article, Category, Writeup


def post_detail(
    request,
    model_class,
    slug,
    template_detail,
    template_password="blog/post_password.html",
):
    post = get_object_or_404(model_class, slug=slug)

    if post.visibility == "private" and not request.user.is_authenticated:
        raise Http404

    if post.visibility == "protected":
        if request.method == "POST" and request.POST.get("password") == getattr(
            post, "password", ""
        ):
            return render(request, template_detail, {"post": post})
        return render(request, template_password)

    return render(request, template_detail, {"post": post})


def article_detail(request, slug):
    return post_detail(request, Article, slug, "blog/post_detail.html")


def writeup_detail(request, slug):
    return post_detail(request, Writeup, slug, "blog/post_detail.html")


def posts_list(
    request,
    model_class,
    slug=None,
    post_type="posts",
    post_type_trans="Posts",
    detail_url_name="blog:post_detail",
):
    posts = model_class.objects.filter(visibility="public").prefetch_related(
        "translations", "tags"
    )
    selected_category = None
    if slug:
        selected_category = get_object_or_404(Category, slug=slug)
        posts = posts.filter(category=selected_category)
    model_name = model_class.__name__.lower()
    category_filter_field = f"category__{model_name}__visibility"

    categories = Category.objects.annotate(
        num_posts=Count("category__id", filter=Q(**{category_filter_field: "public"}))
    ).filter(num_posts__gt=0)
    return render(
        request,
        "blog/posts_lists.html",
        {
            "posts": posts,
            "categories": categories,
            "selected_category": selected_category,
            "post_type_trans": post_type_trans,
            "post_type": post_type,
            "detail_url_name": detail_url_name,
        },
    )


def articles_list(request, slug=None):
    return posts_list(
        request,
        Article,
        slug,
        post_type="articles",
        post_type_trans=_("Articles"),
        detail_url_name="blog:article_detail",
    )


def writeups_list(request, slug=None):
    return posts_list(
        request,
        Writeup,
        slug,
        post_type="writeups",
        post_type_trans=_("Writeups"),
        detail_url_name="blog:writeup_detail",
    )
