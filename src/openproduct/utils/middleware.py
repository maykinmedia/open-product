from django.middleware.locale import LocaleMiddleware as _LocaleMiddleware


class APILocaleMiddleware(_LocaleMiddleware):
    def process_request(self, request):
        if "api" in request.path:
            super().process_request(request)
