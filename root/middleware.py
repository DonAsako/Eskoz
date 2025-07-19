from django.conf import settings


class ActiveThemeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.theme = getattr(settings, "ACTIVE_THEME", "Eskoz")

        response = self.get_response(request)
        return response
