from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import Http404
from .models import WellKnownFile, Page


def index(request):
    return render(request, "root/index.html")


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    if page.visibility == 'private':
        if request.user.is_authenticated:
            return render(request, "root/page.html", {"page": page})
        else:
            raise Http404
            print('ok')
    else:
        return render(request, "root/page.html", {"page": page})


def well_known(request, filename):
    WellKnown_file = get_object_or_404(WellKnownFile, filename=filename)
    return HttpResponse(WellKnown_file.content, content_type="text/plain")
