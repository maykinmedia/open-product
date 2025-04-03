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
    """
    Test results are stored in utils.vc_cassettes

    To generate results, start the keycloak docker container located in open-product/keycloak
    & delete the files in vcr_cassettes
    """

    def setUp(self):
        ProductTypeFactory.create()
        UserFactory.create(superuser=True, username="testtest")

    def generate_token_with_password(self, config):

        payload = {
            "client_id": config.oidc_rp_client_id,
            "client_secret": config.oidc_rp_client_secret,
            "username": "testuser",
            "password": "testuser",
            "grant_type": "password",
            "scope": "openid",
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
            "scope": "openid",
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

    @vcr.use_cassette(str(TEST_FILES / "expired_token"))
    @mock_admin_oidc_config()
    def test_expired_token(self):
        expired_token = (
            "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0VU5RQWN2VWN2LURGVU94XzRPMWd0M"
            "TNPZEpTb3RxRUtQWnVyczJ2UVc4In0.eyJleHAiOjE3NDM1MTg5MzEsImlhdCI6MTc0MzUxODYzMSwian"
            "RpIjoiNTM0MmY0YWMtZWYzZi00YzE3LWEzZTItZDMzMWZmNGYyYmJiIiwiaXNzIjoiaHR0cDovL2xvY2F"
            "saG9zdDo4MDgwL3JlYWxtcy90ZXN0IiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImFhMTBjZmM3LTJjNGQt"
            "NDFmNi04ZmFjLTdiZjQwNWM1NzJjNCIsInR5cCI6IkJlYXJlciIsImF6cCI6InRlc3RpZCIsInNlc3Npb"
            "25fc3RhdGUiOiJlNmE0ZDU4ZC0yMzAzLTRhODUtODAyNC05ZmMzYTE2ZjI4MjAiLCJhY3IiOiIxIiwiYW"
            "xsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly8xMjcuMC4wLjE6ODAwMCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9"
            "sZXMiOlsiZGVmYXVsdC1yb2xlcy10ZXN0Iiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlv"
            "biJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiL"
            "CJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIGVtYW"
            "lsIHByb2ZpbGUga3ZrIGdyb3VwcyBic24iLCJzaWQiOiJlNmE0ZDU4ZC0yMzAzLTRhODUtODAyNC05ZmM"
            "zYTE2ZjI4MjAiLCJrdmsiOiIwMTIzNDU2NzgiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImxlZ2FsU3Vi"
            "amVjdElEIjoiMTIzNDU2NzgiLCJhY3RpbmdTdWJqZWN0SUQiOiI0Qjc1QTBFQTEwN0IzRDM2IiwibmFtZ"
            "V9xdWFsaWZpZXIiOiJ1cm46ZXRvZWdhbmc6MS45OkVudGl0eUNvbmNlcm5lZElEOkt2S25yIiwiZ3JvdX"
            "BzIjpbImRlZmF1bHQtcm9sZXMtdGVzdCIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24"
            "iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoidGVzdHVzZXIiLCJic24iOiIwMDAwMDAwMDAifQ.rlggtpiAr"
            "qtgrk9X4c9jkAS7l9bW4vLb0ujwDzSGfrUgOS5f7tnLukJzG-emDKIeEc4GkM1kYJB5KsE_v5Upioy3dQ"
            "7HDFwGtvfAF6Qtz5WsodPwMwp58a9XzyQXjUF5EI3EUS-g0QPkDV5T5duVCIaRnjQvSAZxxaPOAtG76Zz"
            "rPjJIBkfGsTgtZ6QwdbvbSooxUxcC4Eueq1FNgsw-Bk6LzgcYB8c_jiOR9tbYtzsLHX-88W6HG_AQ6hRb"
            "YfbWx0bIYx2a09bSWmYQxzx3N3O7Xw8ncwLLhtCXM8zIKmj6V0rpUGGPg0kHnocm-cfceyM1R42vwY54Z"
            "_955OCLfg"
        )
        response = self.client.get(
            reverse("producttype-list"),
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    @vcr.use_cassette(str(TEST_FILES / "missing_openid_scope"))
    @mock_admin_oidc_config()
    def test_missing_openid_scope(self):

        config = OpenIDConnectConfig.get_solo()

        payload = {
            "client_id": config.oidc_rp_client_id,
            "client_secret": config.oidc_rp_client_secret,
            "grant_type": "client_credentials",
        }

        response = requests.post(
            config.oidc_op_token_endpoint,
            data=payload,
        )

        token = response.json()["access_token"]

        response = self.client.get(
            reverse("producttype-list"), headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

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
