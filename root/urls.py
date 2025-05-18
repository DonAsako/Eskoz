from django.urls import path
from .views import well_known


urlpatterns = [path(".well-known/<str:filename>", well_known)]
