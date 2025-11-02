from django.shortcuts import render

from blog.views import post_detail, posts_list

from .models import Certification, Writeup


def writeup_detail(request, slug):
    """
    Render the detail page of a specific writeup.

    Fetches the Writeup instance corresponding to the provided slug
    and renders it using the blog's post_detail view.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the writeup to retrieve.

    Returns:
        HttpResponse: The rendered writeup detail page.
    """
    return post_detail(request, Writeup, slug, "blog/post_detail.html")


def writeups_list(request, slug=None):
    """
    Render a list of writeups.

    Optionally filters writeups by a given category slug.
    Uses the blog's posts_list view for rendering.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str, optional): Optional slug to filter writeups. Defaults to None.

    Returns:
        HttpResponse: The rendered list of writeups page.
    """
    return posts_list(
        request,
        Writeup,
        slug,
        post_type="writeups",
        post_type_trans=_("Writeups"),
        detail_url_name="root:writeup_detail",
    )


def certifications_lists(request):
    """
    Render a list of all certifications.

    Fetches all Certification instances and passes them to the
    'infosec/certifications_lists.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered certifications list page.
    """
    certifications = Certification.objects.all()
    return render(
        request, "blog/certifications_lists.html", {"certifications": certifications}
    )
