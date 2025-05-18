from django.shortcuts import render, get_object_or_404, HttpResponse
from .models import WellKnownFile


def well_known(request, filename):
    WellKnown_file = get_object_or_404(WellKnownFile, filename=filename)
    return HttpResponse(WellKnown_file.content, content_type="text/plain")
