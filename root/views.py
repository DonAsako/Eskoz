import markdown
from django.contrib.auth.decorators import login_required
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
            content, extensions=["extra", "codehilite", "fenced_code"]
        )
        return JsonResponse({"html": mark_safe(html)})
    return HttpResponse(request, status="401")
