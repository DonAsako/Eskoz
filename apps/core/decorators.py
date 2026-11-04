from functools import wraps

from django.http import Http404

from .models.settings import SiteSettings


def is_feature_active(site_settings, module_name, feature_name=None):
    """Return True if ``module_name`` (and ``feature_name``, if given) is enabled.

    Single source of truth for the "Activate X module" / "Show X page" toggles,
    shared by the view decorator below and by cross-app surfaces (search) that
    must not expose content from a disabled section.
    """
    module = getattr(site_settings, module_name, None)
    if not module or not module.is_active:
        return False
    if feature_name and not getattr(module, f"activate_{feature_name}_page", False):
        return False
    return True


def feature_active_required(module_name, feature_name=None):
    """
    Decorator to check if a module and optionally a feature is active.

    Args:
        module_name (str): Name of the module (OneToOne field on SiteSettings)
        feature_name (str, optional): Name of the feature field (BooleanField) in the module
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not is_feature_active(SiteSettings.objects.first(), module_name, feature_name):
                raise Http404
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
