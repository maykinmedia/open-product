from typing import Dict, Optional

from django.middleware.locale import LocaleMiddleware as _LocaleMiddleware

from rest_framework.response import Response
from vng_api_common.middleware import (
    VERSION_HEADER,
    APIVersionHeaderMiddleware as _APIVersionHeaderMiddleware,
)

from openproduct.conf.base import (
    PRODUCTEN_API_MAJOR_VERSION,
    PRODUCTEN_API_VERSION,
    PRODUCTTYPEN_API_MAJOR_VERSION,
    PRODUCTTYPEN_API_VERSION,
)


class APILocaleMiddleware(_LocaleMiddleware):
    def process_request(self, request):
        if "api" in request.path:
            super().process_request(request)


def get_version_mapping() -> Dict[str, str]:
    return {
        f"/producten/api/v{PRODUCTEN_API_MAJOR_VERSION}": PRODUCTEN_API_VERSION,
        f"/producttypen/api/v{PRODUCTTYPEN_API_MAJOR_VERSION}": PRODUCTTYPEN_API_VERSION,
    }


class APIVersionHeaderMiddleware(_APIVersionHeaderMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.version_mapping = get_version_mapping()

    def __call__(self, request):
        if self.get_response is None:
            return None

        response = self.get_response(request)

        # not an API response, exit early
        if not isinstance(response, Response):
            return response

        # set the header
        version = self._get_version(request.path)
        if version is not None:
            response[VERSION_HEADER] = version

        return response

    def _get_version(self, path: str) -> Optional[str]:
        for prefix, version in self.version_mapping.items():
            if path.startswith(prefix):
                return version
        return None
