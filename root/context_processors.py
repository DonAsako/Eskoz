from .models import Theme, SiteSettings


def active_theme(request):
    theme = Theme.get_active_theme()
    return {"theme": theme}


def site_settings(request):
    site_settings = SiteSettings.objects.first()
    return {"site_settings": site_settings}
