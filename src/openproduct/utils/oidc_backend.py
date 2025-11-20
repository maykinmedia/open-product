from typing import List, Union

from django.contrib.auth import get_user_model

from drf_spectacular.extensions import OpenApiAuthenticationExtension, _SchemaType
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from mozilla_django_oidc_db.backends import (
    OIDCAuthenticationBackend as _OIDCAuthenticationBackendDB,
)
from mozilla_django_oidc_db.models import OIDCClient

User = get_user_model()


class OIDCAuthenticationBackend(_OIDCAuthenticationBackendDB):
    """
    `mozilla_django_oidc_db.backends.OIDCAuthenticationBackend` only load in the config_class within the authenticate method.
    The drf integration of the base package does not use this method and instead just calls the userinfo endpoint of the oidc provider.

    This class sets the config_class so that it is accessible in the get_userinfo method.
    """

    def get_or_create_user(self, access_token: str, id_token: str, payload):
        # FIXME is this the correct client?
        self.config = OIDCClient.objects.resolve("admin-oidc")
        return super().get_or_create_user(access_token, id_token, payload)


class JWTScheme(OpenApiAuthenticationExtension):
    target_class = "openproduct.utils.oidc_drf_middleware.OIDCAuthentication"
    name = "jwtAuth"

    def get_security_definition(
        self, auto_schema: "AutoSchema"
    ) -> Union[_SchemaType, List[_SchemaType]]:
        return build_bearer_security_scheme_object(
            header_name="Authorization", token_prefix="Bearer", bearer_format="JWT"
        )
