from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.admin.site import admin_site
from apps.core.sitemaps import sitemaps
from apps.core.views import robots_txt

# Routes that must stay un-prefixed regardless of language (admin tooling,
# crawler endpoints, language switcher).
urlpatterns = [
    path(settings.ADMIN_URL + "/", admin_site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("i18n/", include("django.conf.urls.i18n")),
]

# Public site routes — every URL is served under a /<lang>/ prefix
# (prefix_default_language=True keeps things symmetrical and is what Google
# expects for proper hreflang signaling).
urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path("", include("apps.blog.urls")),
    path("", include("apps.infosec.urls")),
    path("education/", include("apps.education.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
