from django.db.models import Count, Q
from django.shortcuts import Http404, get_object_or_404, render
from django.utils.translation import gettext_lazy as _

from .models import Article, Category, Project


def post_detail(
    request,
    model_class,
    slug,
    template_detail,
    template_password="blog/post_password.html",
):
    """
    Render the detail page of a single post instance.

    Handles visibility rules:
    - 'private' posts raise 404 for unauthenticated users.
    - 'protected' posts require a password submitted via POST.

    Args:
        request (HttpRequest): The HTTP request object.
        model_class (Model): The Django model class of the post (e.g., Article, Writeup).
        slug (str): Slug identifying the post instance.
        template_detail (str): Template used to render the post detail.
        template_password (str, optional): Template used to request password for protected posts. Defaults to "blog/post_password.html".

    Raises:
        Http404: If a private post is accessed by an unauthenticated user.

    Returns:
        HttpResponse: Rendered post detail page.
    """
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
    """
    Render the detail page for a specific article.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): Slug identifying the article.

    Returns:
        HttpResponse: Rendered article detail page.
    """
    return post_detail(request, Article, slug, "blog/post_detail.html")


def posts_list(
    request,
    model_class,
    slug=None,
    post_type="posts",
    post_type_trans="Posts",
    detail_url_name="blog:post_detail",
):
    """
    Render a list of posts, optionally filtered by category slug.

    Only public posts are included. Categories with zero public posts are excluded.

    Args:
        request (HttpRequest): The HTTP request object.
        model_class (Model): The Django model class for posts (e.g., Article, Writeup).
        slug (str, optional): Slug of the category to filter posts. Defaults to None.
        post_type (str, optional): String identifier for post type. Defaults to "posts".
        post_type_trans (str, optional): Translated string for the post type. Defaults to "Posts".
        detail_url_name (str, optional): Name of the URL to link to post detail page. Defaults to "blog:post_detail".

    Returns:
        HttpResponse: Rendered posts list page.
    """
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
        slug,
        post_type="articles",
        post_type_trans=_("Articles"),
        detail_url_name="blog:article_detail",
    )


def projects_lists(request):
    """
    Render a list of all projects.

    Fetches all Project instances and passes them to the 'blog/projects_lists.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered projects list page.
    """
    projects = Project.objects.all()
    return render(request, "blog/projects_lists.html", {"projects": projects})
