from .models import Theme, SiteSettings


def active_theme(request):
    light_theme = Theme.get_active_theme("light")
    dark_theme = Theme.get_active_theme("dark")
    return {"light_theme": light_theme, "dark_theme": dark_theme}


def site_settings(request):
    site_settings = SiteSettings.objects.first()
    return {"site_settings": site_settings}
