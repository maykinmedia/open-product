import structlog
from mozilla_django_oidc.contrib.drf import OIDCAuthentication as _OIDCAuthentication
from mozilla_django_oidc.utils import parse_www_authenticate_header
from requests.exceptions import HTTPError
from rest_framework.exceptions import AuthenticationFailed

logger = structlog.stdlib.get_logger(__name__)


class OIDCAuthentication(_OIDCAuthentication):
    """
    Original OIDCAuthentication only checks for HTTP 401 but other 4xx status codes
    are re-raised which results in an 500 error for open product.
    """

    def authenticate(self, request):
        # `OIDCAuthenticationBackend.get_or_create_user` relies on the underlying
        # WSGIRequest
        self.backend.request = request._request

        try:
            return super().authenticate(request)
        except AssertionError:
            logger.exception("oidc_authentication_failed")
            raise AuthenticationFailed(
                "OIDC authentication failed: authentication is not properly configured."
            )
        except HTTPError as exc:
            resp = exc.response
            msg = "OIDC authentication failed with status code: {}".format(
                resp.status_code
            )
            if "www-authenticate" in resp.headers:
                data = parse_www_authenticate_header(resp.headers["www-authenticate"])
                error_description = data.get(
                    "error_description", "no error description in www-authenticate"
                )
                msg = "{} www_authenticate: {}".format(msg, error_description)

            logger.exception("oidc_authentication_failed")
            raise AuthenticationFailed(msg)
