from django.conf import settings
from django.conf.urls.static import static
from core.admin.site import admin_site
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL + "/", admin_site.urls),
    path("", include("core.urls")),
    path("", include("blog.urls")),
    path("", include("infosec.urls")),
    path("education/", include("education.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
