from typing import List, Union

from drf_spectacular.extensions import OpenApiAuthenticationExtension, _SchemaType
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from mozilla_django_oidc_db.backends import (
    OIDCAuthenticationBackend as _OIDCAuthenticationBackendDB,
)
from mozilla_django_oidc_db.config import lookup_config
from mozilla_django_oidc_db.typing import JSONObject


class OIDCAuthenticationBackend(_OIDCAuthenticationBackendDB):
    """
    `mozilla_django_oidc_db.backends.OIDCAuthenticationBackend` only loads in the config within the authenticate method.
    The drf integration of the base package does not use this method and instead just calls the userinfo endpoint of the oidc provider.

    This class sets the config so that it is accessible in the get_userinfo method.
    """

    def get_userinfo(
        self, access_token: str, id_token: str, payload: JSONObject
    ) -> JSONObject:
        # self.config = lookup_config(request)
        return super().get_userinfo(access_token, id_token, payload)


class JWTScheme(OpenApiAuthenticationExtension):
    target_class = "openproduct.utils.oidc_drf_middleware.OIDCAuthentication"
    name = "jwtAuth"

    def get_security_definition(
        self, auto_schema: "AutoSchema"
    ) -> Union[_SchemaType, List[_SchemaType]]:
        return build_bearer_security_scheme_object(
            header_name="Authorization", token_prefix="Bearer", bearer_format="JWT"
        )
