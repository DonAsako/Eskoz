from django.conf import settings
from django.conf.urls.static import static
from apps.core.admin.site import admin_site
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL + "/", admin_site.urls),
    path("", include("apps.core.urls")),
    path("", include("apps.blog.urls")),
    path("", include("apps.infosec.urls")),
    path("education/", include("apps.education.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
