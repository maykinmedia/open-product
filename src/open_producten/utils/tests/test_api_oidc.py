from functools import partial
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

import requests
import vcr
from mozilla_django_oidc_db.models import OpenIDConnectConfig
from rest_framework.exceptions import ErrorDetail
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from ...accounts.tests.factories import UserFactory
from ...producttypen.tests.factories import ProductTypeFactory
from .keycloak import mock_oidc_db_config

TEST_FILES = (Path(__file__).parent / "vcr_cassettes").resolve()

mock_admin_oidc_config = partial(
    mock_oidc_db_config,
    app_label="mozilla_django_oidc_db",
    model="OpenIDConnectConfig",
    id=1,
    make_users_staff=True,
    username_claim=["preferred_username"],
)


@override_settings()
class TestApiOidcAuthentication(TestCase):

    def setUp(self):
        ProductTypeFactory.create()
        UserFactory.create(superuser=True, username="testtest")

    def generate_token_with_password(self, config):

        payload = {
            "client_id": config.oidc_rp_client_id,
            "client_secret": config.oidc_rp_client_secret,
            "username": "testtest",
            "password": "test",
            "grant_type": "password",
        }

        response = requests.post(
            config.oidc_op_token_endpoint,
            data=payload,
        )

        return response.json()["access_token"]

    def generate_client_credentials(self, config):
        payload = {
            "client_id": config.oidc_rp_client_id,
            "client_secret": config.oidc_rp_client_secret,
            "grant_type": "client_credentials",
        }

        response = requests.post(
            config.oidc_op_token_endpoint,
            data=payload,
        )

        return response.json()["access_token"]

    @vcr.use_cassette(str(TEST_FILES / "valid_token"))
    @mock_admin_oidc_config()
    def test_valid_token(self):
        token = self.generate_token_with_password(OpenIDConnectConfig.get_solo())

        response = self.client.get(
            reverse("producttype-list"), headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    @vcr.use_cassette(str(TEST_FILES / "invalid_token"))
    @mock_admin_oidc_config()
    def test_invalid_token(self):
        token = self.generate_token_with_password(OpenIDConnectConfig.get_solo())
        token += "b"
        response = self.client.get(
            reverse("producttype-list"), headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data,
            {
                "detail": ErrorDetail(
                    string="Token verification failed", code="authentication_failed"
                )
            },
        )

    @vcr.use_cassette(str(TEST_FILES / "missing_scope"))
    @mock_admin_oidc_config()
    def test_token_missing_scope(self):
        config = OpenIDConnectConfig.get_solo()

        config.oidc_rp_client_id = "open-producten-hs"
        config.oidc_rp_client_secret = "4LhFMpZuMfWpOhjRTf5UgaeK7yDvkQwe"
        config.save()

        token = self.generate_token_with_password(config)
        response = self.client.get(
            reverse("producttype-list"), headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data,
            {
                "detail": ErrorDetail(
                    string="OIDC authentication failed with status code: 403 www_authenticate: {'Bearer realm': 'master', 'error': 'insufficient_scope', 'error_description': 'Missing openid scope'}",
                    code="authentication_failed",
                )
            },
        )

    @vcr.use_cassette(str(TEST_FILES / "valid_cc_token"))
    @mock_admin_oidc_config()
    def test_valid_client_credentials_token(self):

        UserFactory.create(username="service-account-open-producten", superuser=True)

        token = self.generate_client_credentials(OpenIDConnectConfig.get_solo())

        response = self.client.get(
            reverse("producttype-list"), headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
