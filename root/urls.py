from django.urls import path
from .views import well_known, index


urlpatterns = [
    path("", index),
    path(".well-known/<str:filename>", well_known),
]
