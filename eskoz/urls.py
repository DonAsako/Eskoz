from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path(settings.ADMIN_URL + "/", admin.site.urls),
    path("", include("root.urls")),
    path("", include("blog.urls")),
    path("", include("infosec.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
