from mozilla_django_oidc_db.backends import (
    OIDCAuthenticationBackend as _OIDCAuthenticationBackendDB,
)
from mozilla_django_oidc_db.models import OpenIDConnectConfig
from mozilla_django_oidc_db.typing import JSONObject


class OIDCAuthenticationBackend(_OIDCAuthenticationBackendDB):
    """
    TODO
    """

    def get_userinfo(
        self, access_token: str, id_token: str, payload: JSONObject
    ) -> JSONObject:
        self.config_class = OpenIDConnectConfig
        return super().get_userinfo(access_token, id_token, payload)
