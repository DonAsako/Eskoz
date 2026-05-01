from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import Http404, get_object_or_404, render
from django.urls import reverse
from django.utils import translation
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from apps.blog.models import Article, Project
from apps.infosec.models import Writeup

from .models import Page, WellKnownFile


def resolve_per_page(request):
    """
    Read ``?per_page=N`` from the request, validate it against
    ``settings.POSTS_PER_PAGE_CHOICES``, and fall back to
    ``settings.POSTS_PER_PAGE`` otherwise.
    """
    raw = request.GET.get("per_page")
    if raw is None:
        return settings.POSTS_PER_PAGE
    try:
        candidate = int(raw)
    except (TypeError, ValueError):
        return settings.POSTS_PER_PAGE
    if candidate in settings.POSTS_PER_PAGE_CHOICES:
        return candidate
    return settings.POSTS_PER_PAGE


def paginate_queryset(request, queryset, per_page=None):
    """
    Paginate ``queryset`` using the ``page`` and ``per_page`` GET parameters.

    Out-of-range pages clamp to first/last; a non-integer page falls back to 1.
    ``per_page`` is read from ``?per_page=`` when not provided explicitly and is
    validated against ``settings.POSTS_PER_PAGE_CHOICES``.

    Returns a ``django.core.paginator.Page`` ready to iterate in templates.
    """
    if per_page is None:
        per_page = resolve_per_page(request)
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def group_by_year(queryset, date_field="published_on"):
    """Bucket ``queryset`` items by year of ``date_field`` (descending).

    Returns a list of ``{"year": int|None, "items": [...]}`` dicts so
    templates can render archive-style sections without doing any
    grouping logic themselves. Items missing the date land in a
    trailing ``None`` bucket.
    """
    groups = []
    current = object()
    for obj in queryset:
        date = getattr(obj, date_field, None)
        year = date.year if date else None
        if year != current:
            groups.append({"year": year, "items": []})
            current = year
        groups[-1]["items"].append(obj)
    return groups


def index(request):
    page = Page.objects.filter(visibility="index").first()
    articles = Article.objects.filter(visibility="public").order_by("-published_on")[:5]
    writeups = Writeup.objects.filter(visibility="public").order_by("-published_on")[:5]
    projects = Project.objects.all().order_by("-date_beginning")[:5]
    context = {
        "articles": articles,
        "writeups": writeups,
        "projects": projects,
    }
    if page:
        return render(request, "core/page.html", {"page": page, **context})
    else:
        return render(request, "core/index.html", context)


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    if page.visibility == "private" and not request.user.is_authenticated:
        raise Http404
    return render(request, "core/page.html", {"page": page})


def tag_detail(request, slug):
    """List every public article + writeup whose tag title slugifies to slug.

    Article and writeup tags are stored as separate models with no
    explicit slug field. We compare slugify(tag.title) to the URL slug
    on the fly so the same `[kerberos]` tag in articles and writeups
    lands on the same page.
    """
    from django.utils.text import slugify

    from apps.blog.models import ArticleTag
    from apps.infosec.models import WriteupTag

    titles = set()
    for Tag in (ArticleTag, WriteupTag):
        for t in Tag.objects.all():
            if slugify(t.title) == slug:
                titles.add(t.title)

    if not titles:
        raise Http404

    articles = (
        Article.objects.filter(visibility="public", tags__title__in=titles)
        .select_related("category")
        .prefetch_related("translations", "tags")
        .distinct()
        .order_by("-published_on")
    )
    writeups = (
        Writeup.objects.filter(visibility="public", tags__title__in=titles)
        .select_related("category")
        .prefetch_related("translations", "tags")
        .distinct()
        .order_by("-published_on")
    )

    if not (articles.exists() or writeups.exists()):
        raise Http404

    # Pick the canonical display title (longest, prefer with capitals).
    display_title = sorted(titles, key=lambda t: (-len(t), t))[0]

    return render(
        request,
        "core/tag_detail.html",
        {
            "tag_title": display_title,
            "tag_slug": slug,
            "articles": articles,
            "writeups": writeups,
            "total": articles.count() + writeups.count(),
        },
    )


def well_known(request, filename):
    WellKnown_file = get_object_or_404(WellKnownFile, filename=filename)
    return HttpResponse(WellKnown_file.content, content_type="text/plain")


def robots_txt(request):
    """Serve robots.txt with a Sitemap directive pointing at the live host."""
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        f"Disallow: /{settings.ADMIN_URL}/",
        "Disallow: /accounts/",
        "",
        f"Sitemap: {sitemap_url}",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def ratelimited(request, exception):
    """Render a 429 page when django-ratelimit blocks a request."""
    response = render(request, "429.html", status=429)
    response["Retry-After"] = "900"
    return response


def verify_2fa_view(request):
    """Second-factor gate for users who have ``User2FA.is_active=True``.

    Reached by ``Force2FAMiddleware`` after a successful password login.
    Accepts either a TOTP code or one of the user's backup codes (the
    backup code is consumed on success). Marks the session as verified so
    the rest of the admin opens up. Rate-limited at the IP level via the
    middleware that wraps the project (``RATELIMIT_2FA_IP``).
    """
    from django.contrib import messages
    from django_ratelimit.core import is_ratelimited
    from django_ratelimit.exceptions import Ratelimited

    from apps.core.models import User2FA

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("admin:login"))

    try:
        tfa = request.user.two_factor
    except User2FA.DoesNotExist:
        # User reached this view without 2FA configured — let them through.
        request.session["2fa_verified"] = True
        return HttpResponseRedirect(request.GET.get("next") or reverse("admin:index"))

    if not tfa.is_active:
        request.session["2fa_verified"] = True
        return HttpResponseRedirect(request.GET.get("next") or reverse("admin:index"))

    error = None
    if request.method == "POST":
        if is_ratelimited(
            request,
            group="verify-2fa",
            key="ip",
            rate=settings.RATELIMIT_2FA_IP,
            method="POST",
            increment=True,
        ):
            raise Ratelimited()

        code = (request.POST.get("code") or "").strip().replace(" ", "").replace("-", "")
        if tfa.verify_otp(code):
            request.session["2fa_verified"] = True
            return HttpResponseRedirect(request.GET.get("next") or reverse("admin:index"))
        if tfa.verify_backup_code(code):
            request.session["2fa_verified"] = True
            messages.warning(
                request,
                _("Backup code consumed. %(remaining)d codes remain — generate new ones soon.") % {"remaining": len(tfa.backup_codes)},
            )
            return HttpResponseRedirect(request.GET.get("next") or reverse("admin:index"))
        error = _("Invalid code. Try again.")

    # GET (or POST with bad code): render the form. We deliberately keep this
    # page reachable while authenticated-but-unverified — logout link is the
    # escape hatch for users who lost their device (and have no backup code).
    return render(
        request,
        "admin/verify_2fa.html",
        {
            "error": error,
            "username": request.user.get_username(),
            "next": request.GET.get("next", ""),
            "logout_url": reverse("admin:logout"),
        },
    )


def search_view(request):
    """Cross-app search across translated posts in the active language."""
    from apps.core.search import search_posts

    query = request.GET.get("q", "").strip()
    results = search_posts(query, get_language()) if query else None
    total = sum(len(v) for v in results.values()) if results else 0
    return render(
        request,
        "core/search.html",
        {
            "query": query,
            "results": results,
            "total": total,
        },
    )


def redirect_to_available_translation(post, url_name, url_args):
    """
    If the active language has no translation for ``post``, return a 301 to
    the same view in the configured default language; if that one is also
    missing, fall back to the first available translation alphabetically (so
    redirects are deterministic across requests).

    Returns ``None`` when the active language is already covered, in which
    case the caller renders the page normally.
    """
    available = set(post.translations.values_list("language", flat=True))
    if not available:
        return None  # Orphan post with zero translations — let the caller render.
    current = get_language()
    if current in available:
        return None
    if settings.LANGUAGE_CODE in available:
        target = settings.LANGUAGE_CODE
    else:
        target = sorted(available)[0]
    with translation.override(target):
        url = reverse(url_name, args=url_args)
    return HttpResponsePermanentRedirect(url)


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
        if request.method == "POST" and post.check_password(request.POST.get("password", "")):
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
    posts = post_model.objects.filter(visibility="public").prefetch_related("translations", "tags")
    selected_category = None
    if slug:
        selected_category = get_object_or_404(category_model, slug=slug)
        posts = posts.filter(category=selected_category)
    category_field = post_model._meta.get_field("category")
    related_name = category_field.remote_field.related_name

    categories = category_model.objects.annotate(num_posts=Count(related_name, filter=Q(**{f"{related_name}__visibility": "public"}))).filter(
        num_posts__gt=0
    )

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
