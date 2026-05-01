from django.shortcuts import Http404, get_object_or_404, render

from apps.core.decorators import feature_active_required
from apps.core.views import group_by_year, paginate_queryset, redirect_to_available_translation

from .models import CTF, CVE, Category, Certification, Writeup


@feature_active_required(module_name="infosec", feature_name="writeups")
def writeup_detail(request, slug_category, slug_writeup):
    """
    Render the detail page of a specific writeup.

    Args:
        request (HttpRequest): The HTTP request object.
        slug_category (str): Slug identifying the category.
        slug_writeup (str): Slug identifying the writeup.

    Returns:
        HttpResponse: The rendered writeup detail page.
    """
    category = get_object_or_404(Category, slug=slug_category)
    writeup = get_object_or_404(Writeup, category=category, slug=slug_writeup)
    if writeup.visibility == "private" and not request.user.is_authenticated:
        raise Http404

    redirect_response = redirect_to_available_translation(writeup, "infosec:writeup_detail", [slug_category, slug_writeup])
    if redirect_response is not None:
        return redirect_response

    related = list(
        Writeup.objects.filter(visibility="public", category=category)
        .exclude(pk=writeup.pk)
        .select_related("category")
        .order_by("-published_on")[:4]
    )
    if len(related) < 4:
        seen = {w.pk for w in related} | {writeup.pk}
        fill = (
            Writeup.objects.filter(visibility="public")
            .exclude(pk__in=seen)
            .select_related("category")
            .order_by("-published_on")[: 4 - len(related)]
        )
        related += list(fill)

    context = {
        "writeup": writeup,
        "related_posts": related,
        "related_post_url_name": "infosec:writeup_detail",
    }

    if writeup.visibility == "protected":
        if request.method == "POST" and writeup.check_password(request.POST.get("password", "")):
            return render(request, "infosec/writeup_detail.html", context)

        return render(request, "infosec/writeup_password.html")

    return render(request, "infosec/writeup_detail.html", context)


@feature_active_required(module_name="infosec", feature_name="writeups")
def writeup_list(request, slug=None):
    """
    Render a list of writeups.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str, optional): Optional slug to filter writeups. Defaults to None.

    Returns:
        HttpResponse: The rendered list of writeups page.
    """
    writeups = (
        Writeup.objects.filter(visibility="public")
        .select_related("category", "ctf")
        .prefetch_related("translations", "tags")
        .order_by("-published_on")
    )
    selected_category = None
    if slug:
        selected_category = get_object_or_404(Category, slug=slug)
        writeups = writeups.filter(category=selected_category)

    ctfs = CTF.objects.all()

    categories = Category.objects.filter(writeups__isnull=False, writeups__visibility="public").distinct()

    GROUP_THRESHOLD = 40
    total = writeups.count()
    if total <= GROUP_THRESHOLD:
        page_obj = None
        groups = group_by_year(writeups)
    else:
        page_obj = paginate_queryset(request, writeups)
        groups = group_by_year(page_obj.object_list)

    return render(
        request,
        "infosec/writeup_list.html",
        {
            "writeups": page_obj if page_obj is not None else writeups,
            "writeup_groups": groups,
            "page_obj": page_obj,
            "categories": categories,
            "selected_category": selected_category,
            "ctfs": ctfs,
        },
    )


@feature_active_required(module_name="infosec", feature_name="certifications")
def certification_list(request):
    """
    Render a list of all certifications.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered certifications list page.
    """
    certifications = Certification.objects.all()
    return render(request, "infosec/certification_list.html", {"certifications": certifications})


@feature_active_required(module_name="infosec", feature_name="cves")
def cve_list(request):
    """
    Render a list of all CVEs

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered cve list page.
    """
    cves = CVE.objects.all().order_by("-published_date", "-id")
    page_obj = paginate_queryset(request, cves)
    return render(request, "infosec/cve_list.html", {"cves": page_obj, "page_obj": page_obj})
