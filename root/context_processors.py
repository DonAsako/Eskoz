from .models import Theme, SiteSettings


def active_theme(request):
    theme = Theme.objects.get(is_active=True)
    return {"active_theme": theme}


def site_settings(request):
    site_settings = SiteSettings.objects.first()
    return {"site_settings": site_settings}
