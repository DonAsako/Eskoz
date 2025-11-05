from functools import wraps
from django.http import Http404
from root.models.settings import SiteSettings


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
            site_settings = SiteSettings.objects.first()
            module = getattr(site_settings, module_name, None)
            if not module or not module.is_active:
                raise Http404()

            if feature_name:
                feature_value = getattr(module, f"activate_{feature_name}_page", None)
                if not feature_value:
                    raise Http404()

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
