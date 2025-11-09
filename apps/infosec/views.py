from django.shortcuts import Http404, get_object_or_404, render
from django.utils.translation import gettext_lazy as _

from apps.core.decorators import feature_active_required

from .models import CVE, Category, Certification, Writeup, CTF


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

    if writeup.visibility == "protected":
        if request.method == "POST" and request.POST.get("password") == getattr(
            writeup, "password", ""
        ):
            return render(request, "infosec/writeup_detail.html", {"writeup": writeup})

        return render(request, "infosec/writeup_password.html")

    return render(request, "infosec/writeup_detail.html", {"writeup": writeup})


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
    writeups = Writeup.objects.filter(visibility="public")
    selected_category = None
    if slug:
        selected_category = get_object_or_404(Category, slug=slug)
        writeups = writeups.filter(category=selected_category)

    ctfs = CTF.objects.all()

    categories = Category.objects.filter(
        writeups__isnull=False, writeups__visibility="public"
    ).distinct()

    return render(
        request,
        "infosec/writeup_list.html",
        {
            "writeups": writeups,
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
    return render(
        request, "infosec/certification_list.html", {"certifications": certifications}
    )


@feature_active_required(module_name="infosec", feature_name="cves")
def cve_list(request):
    """
    Render a list of all CVEs

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered cve list page.
    """
    cve = CVE.objects.all()
    return render(request, "infosec/cve_list.html", {"cve": cve})
