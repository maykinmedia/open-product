from mozilla_django_oidc.contrib.drf import OIDCAuthentication as _OIDCAuthentication
from mozilla_django_oidc.utils import parse_www_authenticate_header
from requests.exceptions import HTTPError
from rest_framework.exceptions import AuthenticationFailed


class OIDCAuthentication(_OIDCAuthentication):
    """
    Original OIDCAuthentication only checks for HTTP 401 but other 4xx status codes
    are re-raised which results in an 500 error for open producten.
    """

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except HTTPError as exc:
            resp = exc.response
            msg = "OIDC authentication failed with status code: {}".format(
                resp.status_code
            )

            if "www-authenticate" in resp.headers:
                data = parse_www_authenticate_header(resp.headers["www-authenticate"])
                msg = f"{msg} www_authenticate: {data}"

            raise AuthenticationFailed(msg)
