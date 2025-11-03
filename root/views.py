import markdown
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import Http404, get_object_or_404, render
from django.utils.safestring import mark_safe

from .models import Page, WellKnownFile


def index(request):
    page = Page.objects.filter(visibility="index").first()

    if page:
        return render(request, "root/page.html", {"page": page})
    else:
        return render(request, "root/index.html")


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    if page.visibility == "private":
        if request.user.is_authenticated:
            return render(request, "root/page.html", {"page": page})
        else:
            raise Http404
            print("ok")
    else:
        return render(request, "root/page.html", {"page": page})


def well_known(request, filename):
    WellKnown_file = get_object_or_404(WellKnownFile, filename=filename)
    return HttpResponse(WellKnown_file.content, content_type="text/plain")


@login_required
def content_preview(request):
    if request.method == "POST":
        content = request.POST.get("content", "")
        html = markdown.markdown(
            content,
            extensions=[
                "extra",
                "codehilite",
                "fenced_code",
                "toc",
                "pymdownx.arithmatex",
            ],
            extension_configs={
                "pymdownx.arithmatex": {
                    "generic": True,
                }
            },
        )
        return JsonResponse({"html": mark_safe(html)})
    return HttpResponse(request, status="401")


def post_detail(
    request,
    post_model,
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
        post_model (Model): The Django model class of the post (e.g., Article, Writeup).
        slug (str): Slug identifying the post instance.
        template_detail (str): Template used to render the post detail.
        template_password (str, optional): Template used to request password for protected posts. Defaults to "blog/post_password.html".

    Raises:
        Http404: If a private post is accessed by an unauthenticated user.

    Returns:
        HttpResponse: Rendered post detail page.
    """
    post = get_object_or_404(post_model, slug=slug)

    if post.visibility == "private" and not request.user.is_authenticated:
        raise Http404

    if post.visibility == "protected":
        if request.method == "POST" and request.POST.get("password") == getattr(
            post, "password", ""
        ):
            return render(request, template_detail, {"post": post})
        return render(request, template_password)

    return render(request, template_detail, {"post": post})


def posts_list(
    request,
    post_model,
    category_model,
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
        post_model (Model): The Django model class for posts (e.g., Article, Writeup).
        category_model (Model): The Django model class for categories.
        slug (str, optional): Slug of the category to filter posts. Defaults to None.
        post_type (str, optional): String identifier for post type. Defaults to "posts".
        post_type_trans (str, optional): Translated string for the post type. Defaults to "Posts".
        detail_url_name (str, optional): Name of the URL to link to post detail page. Defaults to "blog:post_detail".

    Returns:
        HttpResponse: Rendered posts list page.
    """
    posts = post_model.objects.filter(visibility="public").prefetch_related(
        "translations", "tags"
    )
    selected_category = None
    if slug:
        selected_category = get_object_or_404(category_model, slug=slug)
        posts = posts.filter(category=selected_category)
    category_field = post_model._meta.get_field("category")
    related_name = category_field.remote_field.related_name

    categories = category_model.objects.annotate(
        num_posts=Count(
            related_name, filter=Q(**{f"{related_name}__visibility": "public"})
        )
    ).filter(num_posts__gt=0)

    return render(
        request,
        "blog/post_list.html",
        {
            "posts": posts,
            "categories": categories,
            "selected_category": selected_category,
            "post_type_trans": post_type_trans,
            "post_type": post_type,
            "detail_url_name": detail_url_name,
        },
    )
